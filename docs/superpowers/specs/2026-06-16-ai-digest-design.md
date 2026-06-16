# AI Digest — Thiết kế hệ thống

**Ngày:** 2026-06-16
**Trạng thái:** Đã thống nhất, chờ review để lập kế hoạch triển khai
**Project root:** `~/Desktop/Workspace/ai-digest`

---

## 1. Mục tiêu & bối cảnh

Xây một hệ **multi-agent + automation** vừa để **học** (cách điều phối agent, định tuyến model) vừa **ra sản phẩm thật, tái sử dụng được** (một nền tảng nhỏ nhưng hoàn chỉnh).

Sản phẩm: một hệ chạy theo lịch (và khám phá nguồn động) mỗi ngày để:
1. Thu thập + khám phá nội dung về AI/công nghệ từ RSS và web search.
2. Xử lý hàng loạt bằng model local rẻ (Gemma/Ollama).
3. Tổng hợp & viết blog chất lượng cao bằng Claude.
4. Xuất bản blog song ngữ (EN + VI) lên website tĩnh qua Git, với CI/CD tự động deploy.
5. Có vòng phê duyệt human-in-the-loop qua Telegram (bật/tắt được).

### Hạ tầng người dùng
- **Claude Max subscription** gọi qua `claude -p` (Claude Code CLI), **không dùng API key**.
- **Gemma** chạy local qua **Ollama** (HTTP API, OpenAI-compatible).
- Máy Linux cá nhân (tự host, có cron + systemd).

### Ràng buộc kiến trúc cốt lõi
- `claude -p` là **CLI tương tác**, hợp vai "một lời gọi reasoning chất lượng cao theo lịch", **không** hợp làm backend gọi liên tục/real-time. → Claude = tier "smart" (việc khó, ít lần). Gemma = tier "cheap" (việc nhiều, rẻ).

### Tại sao project này
- Dạy đúng bài học cốt lõi của multi-agent: phân vai, chạy song song, **định tuyến model theo chi phí/độ khó**.
- Cái lõi (Orchestrator + Model Router + Search interface) **tái sử dụng** được cho các hướng sau (RAG, automation theo sự kiện...).

---

## 2. Tech stack

| Thành phần | Lựa chọn |
|---|---|
| Ngôn ngữ orchestrator | **Python** |
| Model worker (cheap) | **Gemma** qua **Ollama** HTTP API |
| Model lead (smart) | **Claude** qua `claude -p` (subprocess) |
| Search/discovery | **Tavily** (free tier; bọc qua interface để đổi backend) |
| Lập lịch | **cron** (cấu hình được) |
| Phê duyệt | **Telegram Bot** + long-polling service (**systemd**) |
| Xuất bản | **Git CLI** (commit/push) |
| Website | **Hugo** (static site, i18n EN/VI built-in) |
| Hosting + CI/CD | **GitHub Pages** + **GitHub Actions** (free) |

---

## 3. Kiến trúc tổng thể

Hai entrypoint, tách vai rõ ràng:
- **`orchestrator.py`** — chạy theo cron: sinh nội dung. **Không tự đăng khi chế độ duyệt bật.**
- **`approver.py`** — service long-polling: nhận quyết định phê duyệt qua Telegram và mới được phép publish.

```
cron ──► orchestrator.py
   ┌──────────┐   ┌──────────────┐
   │ Collector│   │ Discovery    │   (RSS + Tavily search)
   │ (RSS)    │   │ (Tavily)     │
   └────┬─────┘   └──────┬───────┘
        └──────┬─────────┘
               ▼
        ┌──────────────┐   gom nhóm tin trùng (clustering, Gemma)
        │ Processor ×N │  (Gemma, song song): tóm tắt + category + tags + chấm liên quan
        └──────┬───────┘
               ▼
        ┌──────────────────┐
        │ Lead Analyst     │ (Claude): tổng hợp digest, chốt category, xếp ưu tiên
        └──────┬───────────┘
               ▼
        ┌──────────────────┐
        │ Writer           │ (Claude): viết blog EN (Markdown trung lập + citations)
        └──────┬───────────┘
               ▼
        ┌──────────────────┐
        │ Translator       │ (Gemma nháp → Claude hiệu đính): blog VI, giữ thuật ngữ EN
        └──────┬───────────┘
               ▼
        ┌──────────────────┐
        │ Quality Gate     │ (Claude): kiểm bịa đặt / bám nguồn trước khi cho publish
        └──────┬───────────┘
               ▼
   approval_required?
     ├── true  ─► trạng thái pending_approval ─► Telegram (inline buttons) ─► approver.py
     └── false ─► Publisher publish thẳng
               ▼
        ┌──────────────────┐
        │ Publisher        │ ghi .md vào site/ → git commit + push
        └──────┬───────────┘
               ▼
   push lên GitHub ─► GitHub Actions build Hugo ─► deploy GitHub Pages ─► web cập nhật
               │
        ┌──────▼───────────┐
        │ Reporter         │ (Gemma): báo cáo tóm tắt/lỗi (nguyên nhân + khắc phục) qua Telegram
        └──────────────────┘
```

### Cái lõi tái sử dụng
1. **Model Router** — `router.run(task, tier)` với `tier ∈ {cheap, smart}`; code không cần biết đang gọi Gemma hay Claude.
2. **Search interface** — `search(query)` bọc Tavily; đổi backend chỉ thay 1 lớp.
3. **Orchestrator** — định nghĩa các bước, chạy song song, lưu output trung gian.

---

## 4. Các thành phần (mỗi agent = 1 module, 1 nhiệm vụ, test độc lập)

| Agent | Tier | Nhiệm vụ |
|---|---|---|
| **Collector** | — | Đọc `feeds.yaml`, lấy bài mới, loại bài trong `seen.json` |
| **Discovery** | cheap | Search Tavily theo keyword trong config → URL ứng viên, lọc trùng + chấm liên quan (Gemma) |
| **Processor** | cheap | Mỗi bài: tóm tắt + gợi ý category + tags + điểm chính (song song) |
| **Clustering** | cheap | Gom các bài cùng chủ đề → 1 blog/chủ đề (tránh trùng/loãng) |
| **Lead Analyst** | smart | Tổng hợp digest EN, chốt category, xếp ưu tiên |
| **Writer** | smart | Viết blog EN: Markdown chuẩn (CommonMark) + front-matter trung lập + citations |
| **Translator** | cheap→smart | Gemma dịch nháp → Claude hiệu đính; bản VI **giữ nguyên thuật ngữ tiếng Anh** |
| **Quality Gate** | smart | Kiểm bịa đặt / bám nguồn trước khi cho publish |
| **Publisher** | — | Ghi `.md` vào `site/content/posts/`, commit, push |
| **Reporter** | cheap | Soạn báo cáo Telegram (thành công / lỗi: gì → nguyên nhân → khắc phục) |
| **Approver** (`approver.py`) | — | Service long-polling: xử lý nút bấm Telegram, thực thi publish/held/discard |

### Quy tắc bất biến cho tính di động (migration)
> **Writer CHỈ sinh Markdown chuẩn (CommonMark) + front-matter trung lập** (`title, date, lang, tags, category, slug, summary`). **Cấm dùng shortcode đặc thù Hugo.** Đây là điều kiện để migrate sang Astro/React/Next... về sau chỉ phải làm lại lớp giao diện, không đụng nội dung và không đụng orchestrator.

---

## 5. Cấu trúc thư mục (mono-repo)

```
ai-digest/
├── digest/                       # orchestrator (Python)
│   ├── config/
│   │   ├── feeds.yaml            # danh sách RSS + chủ đề
│   │   └── settings.yaml         # hành vi (commit được)
│   ├── core/
│   │   ├── router.py             # Model Router (cheap/smart)
│   │   ├── ollama_backend.py     # gọi Gemma qua HTTP
│   │   ├── claude_backend.py     # gọi `claude -p` qua subprocess
│   │   └── search.py             # interface search (Tavily)
│   ├── agents/
│   │   ├── collector.py  discovery.py  processor.py  clustering.py
│   │   ├── analyst.py    writer.py     translator.py  quality_gate.py
│   │   ├── publisher.py  reporter.py
│   ├── state/
│   │   ├── seen.json             # idempotent: bài đã xử lý
│   │   ├── posts.json            # state machine bài viết
│   │   └── runs/                 # log + output trung gian mỗi lần chạy
│   ├── orchestrator.py           # entrypoint cron
│   ├── approver.py               # entrypoint service (systemd)
│   ├── tests/
│   ├── .env                      # secret/path (KHÔNG commit)
│   └── .env.example
├── site/                         # Hugo
│   ├── content/posts/            # ◄── nội dung sinh ra (.en.md / .vi.md)
│   └── hugo.toml
├── .github/workflows/deploy.yml  # build site/ → GitHub Pages
└── README.md
```

### Repo blog (trong cùng mono-repo)
```
site/content/posts/
├── 2026-06-16-ai-weekly.en.md
└── 2026-06-16-ai-weekly.vi.md
```
Front-matter chuẩn: `title, date, lang, tags, category, slug, summary`. Hugo dùng taxonomy built-in → tự sinh trang `/categories/<x>/`, `/tags/<y>/`, homepage section theo ngày, trang chi tiết, nút chuyển EN/VI.

---

## 6. Cấu hình tập trung (2 lớp)

### `.env` — secret & path máy (không commit)
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
CLAUDE_BIN=claude
BLOG_SITE_PATH=site
GIT_REMOTE=origin
TAVILY_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### `config/settings.yaml` — hành vi (commit được)
```yaml
schedule: daily                  # daily | every_2_days | weekly
languages: [en, vi]
vi_keep_english_terms: true
articles_per_run: 8
translator_mode: draft_then_review   # gemma_only | draft_then_review | claude_only
approval_required: true          # true: chờ duyệt Telegram; false: đăng thẳng
categories: [Research, Tools, Industry, Tutorial, Opinion]
discovery:
  enabled: true
  keywords: ["multi-agent LLM", "AI automation", "agentic workflows"]
steps:                           # bật/tắt từng phần
  digest: true
  blog: true
  publish: true                  # false = dry-run (sinh file, không commit/push)
notify:
  telegram_daily_summary: true
  telegram_error_alert: true
```

---

## 7. Category & Tag
- **Category**: taxonomy có kiểm soát (cố định trong config), chọn đúng 1 / bài.
- **Tags**: tự do, Gemma gợi ý → Analyst chuẩn hóa khi tổng hợp.
- Hugo render trang category/tag + lọc trên homepage.

---

## 8. Vòng phê duyệt qua Telegram (human-in-the-loop)

State machine mỗi bài: `draft → pending_approval → published | held | discarded` (lưu `state/posts.json`).

Khi `approval_required: true`:
```
Telegram gửi mỗi bài: tiêu đề + tóm tắt + category + link nguồn
  + inline buttons: [✅ Publish] [✏️ Sửa sau] [❌ Bỏ]

✅ Publish → Publisher commit+push → CI deploy → Telegram báo "Đã đăng: <link>"
✏️ Sửa sau → giữ draft trong repo, không đăng (đăng tay sau)
❌ Bỏ      → xóa draft, ghi seen.json để không sinh lại
```

Khi `approval_required: false`: bỏ qua nút duyệt, Publisher đăng thẳng. `approver.py` vẫn có thể chạy chỉ để gửi báo cáo.

**Cơ chế chạy approver:** long-polling bằng `python-telegram-bot`, chạy nền qua **systemd** (tức thì, free, không cần mở cổng ra internet). Token trong `.env`.

---

## 9. CI/CD

```
orchestrator/approver push thay đổi trong site/
  → GitHub Actions (deploy.yml) trigger
  → cài Hugo, build site/, deploy GitHub Pages
  → web cập nhật sau 1–2 phút (không thao tác tay)
```
Free cho repo public (quota rộng cho private).

---

## 10. Xử lý lỗi & độ bền (chạy không người giám sát)

Nguyên tắc: **một bài/feed hỏng không làm sập cả lần chạy.**

| Tình huống | Xử lý |
|---|---|
| 1 feed RSS chết/timeout | Bỏ qua, log cảnh báo, tiếp tục feed khác |
| Tavily lỗi/hết quota | Bỏ qua bước discovery, vẫn chạy RSS |
| Gemma lỗi trên 1 bài | Bỏ bài đó, không dừng batch |
| `claude -p` lỗi/timeout/hết quota | Retry có giới hạn (vd 2 lần, backoff); vẫn lỗi → lưu digest nháp, bỏ bước viết blog, báo lỗi |
| Dịch VI lỗi | Vẫn xuất bản bản EN, đánh dấu VI "pending" |
| Quality gate trượt | Không publish, đưa vào held, báo Telegram |
| Git push lỗi | Retry; vẫn lỗi → giữ file local, lần sau push tiếp |
| Không có bài mới | Thoát sạch, không commit rỗng |

Bổ trợ:
- **Logging có cấu trúc** ra `state/runs/<date>.log`.
- **Idempotent** qua `seen.json`.
- **Output trung gian** lưu `state/` → lỗi bước sau không phải chạy lại bước trước (tiết kiệm token Claude).
- **Theo dõi usage**: log số lần gọi Claude/Gemma mỗi lần chạy (tránh chạm giới hạn Max).
- **Reporter** gửi Telegram: báo cáo thành công (mỗi ngày) + báo lỗi (gì → nguyên nhân → khắc phục).

---

## 11. Kiểm thử
- Mỗi agent là **hàm thuần** → unit test với fixtures input/output.
- **Router test với backend mock** → kiểm logic định tuyến không tốn token.
- **Dry-run mode** (`steps.publish: false`) → chạy full pipeline, in file local, không commit/push.
- **Fixtures RSS mẫu** để test lặp lại ổn định.

---

## 12. Phạm vi (scope)

**Có trong phiên bản đầu (🟢):**
- Pipeline đầy đủ: Collector + Discovery → Processor → Clustering → Analyst → Writer → Translator → Quality Gate → Publisher → Reporter.
- Model Router (cheap/smart), Search interface (Tavily).
- Song ngữ EN/VI (VI giữ thuật ngữ EN), citations bắt buộc, category/tags, SEO front-matter.
- Hugo + GitHub Actions + Pages.
- Telegram: báo cáo + phê duyệt inline buttons (long-polling/systemd).
- Config 2 lớp, `approval_required` bật/tắt, dry-run, logging, usage tracking, idempotent.

**Tùy chọn / vòng sau (🟡):**
- **Tier escalation** trong Router (cheap trượt quality gate → tự nâng smart).

**Để sau (🔴 — YAGNI hiện tại):**
- Weekly roundup, multi-author, comments, analytics nâng cao, migrate sang Astro/React.

### Trang Kiến trúc & Tài liệu dự án (làm CUỐI CÙNG)
- Tạo một trang/phần doc về **kiến trúc dự án** + tài liệu tổng quan, dùng skill
  `/home/dungnd/Desktop/Workspace/ai-digest/.claude/skills/generate-architecture-diagrams`
  (sinh sơ đồ kiến trúc PNG + Draw.io bằng Python `diagrams` library).
- **Thời điểm:** Đây là **task cuối cùng**, chỉ thực hiện **sau khi tất cả task/fix khác đã được approve và hoàn tất**.
- **Lý do:** Tránh phải rework/cập nhật sơ đồ + doc liên tục theo code thay đổi; chốt một lần trên codebase cuối cùng.

---

## 13. Quyết định đã chốt (tóm tắt)
- Project khởi đầu: Daily Research Digest + tự viết blog (giao A+C+D).
- Mono-repo, không tách repo.
- Nguồn: RSS (bắt đầu) + Discovery động bằng Tavily.
- Output: Markdown → Git → Hugo → GitHub Pages, có CI/CD.
- Song ngữ EN/VI; bản VI giữ thuật ngữ tiếng Anh.
- Phân vai model: Gemma (cheap) / Claude qua `claude -p` (smart).
- Telegram: báo cáo + phê duyệt có nút; `approval_required` bật/tắt qua config.
- Approver: long-polling + systemd.
- Quy tắc bất biến: Writer chỉ sinh Markdown trung lập (không shortcode Hugo) để đảm bảo di động.
