---
title: Kiến trúc
summary: AI Digest hoạt động end-to-end thế nào — một multi-agent pipeline self-hosted.
---

AI Digest là một **multi-agent pipeline** chạy trên máy cá nhân. Mỗi sáng bạn chạy một
lệnh; nó thu thập tin AI/công nghệ, xử lý bằng model rẻ, viết và dịch blog bằng model
mạnh, qua một quality gate, rồi xuất bản site song ngữ này — có tùy chọn duyệt thủ công
qua Telegram.

![Kiến trúc AI Digest](architecture.png)

## Vận hành hằng ngày

`./scripts/daily.sh` là idempotent: tự kill service cũ, chỉ bật Ollama nếu mode cần
(đỡ nóng/tốn điện), chạy pipeline một lần, và ghi thời gian từng bước vào
`digest/state/runs/`. Sau đó bạn duyệt trên Telegram (nếu bật approval) rồi tắt máy.

## Lõi tái sử dụng: Model Router

Mỗi agent chỉ yêu cầu một *tier* — `cheap` hoặc `smart` — không gắn cứng provider.
**Model Router** ánh xạ tier sang backend qua `model_mode`:

- **claude_only** — cả hai tier → Claude (nhanh, không nóng GPU) — *mặc định*
- **both** — cheap → Gemma (Ollama, local), smart → Claude
- **ollama_only** — cả hai tier → Gemma (full local)

Seam thứ hai, **Search interface**, bọc nhà cung cấp web-search (Tavily).

## Pipeline theo từng bài

| Bước | Tier | Vai trò |
|------|------|---------|
| Collect | — | Đọc RSS (lỗi 1 feed không làm sập run) |
| Discover | cheap | Search web hằng ngày + lọc liên quan |
| Ingest | — | Gộp nguồn, khử trùng, bỏ bài đã xử lý |
| Process | cheap | Tóm tắt + category + tags mỗi bài |
| Cluster | cheap | Gom các bài cùng một câu chuyện |
| Analyze | smart | Tổng hợp + xếp ưu tiên thành digest |
| Write | smart | Mỗi câu chuyện một bài, kèm trích nguồn (không bịa) |
| Translate | cheap→smart | EN→VI, giữ thuật ngữ tiếng Anh |
| Quality gate | smart | Chặn bài bịa / không bám nguồn |
| Publish | — | Render Markdown, commit, push |

Mỗi bài được xử lý end-to-end và **đo thời gian từng sub-step** (write · gate · vi),
báo cáo hằng ngày qua Telegram.

## Chế độ xuất bản & chống trùng

`approval_required: false` (mặc định) auto-publish; `true` gửi mỗi bài lên Telegram kèm
nút ✅/✏️/❌. Chạy lại không bao giờ tạo trùng: bài khử trùng theo URL (`seen.json`) và
câu chuyện theo `date:slug` (`posts.json`); trùng trong ngày được Clusterer gộp lại.

## Xuất bản & CI/CD

Publisher ghi Markdown **trung lập** (CommonMark + front-matter, không shortcode Hugo)
để đổi generator dễ dàng. Khi push, GitHub Actions build site Hugo (trang chủ theo ngày,
i18n EN/VI, taxonomy) và deploy lên GitHub Pages.

## Độ bền

Mọi agent gọi model đều degrade gracefully khi output lỗi — một feed hỏng, search thất
bại, hay bài bị từ chối đều không làm sập run. Quality Gate là tuyến phòng thủ cuối
chống nội dung bịa đặt.
