---
title: Kiến trúc
summary: AI Digest hoạt động end-to-end thế nào — một multi-agent pipeline self-hosted.
---

AI Digest là một **multi-agent pipeline** chạy trên máy cá nhân. Mỗi ngày nó thu thập
tin AI/công nghệ, xử lý bằng model rẻ, viết và dịch blog bằng model mạnh, qua một
quality gate, rồi xuất bản một site tĩnh song ngữ — với tùy chọn duyệt thủ công
(human-in-the-loop) qua Telegram.

![Kiến trúc AI Digest](architecture.png)

## Lõi tái sử dụng: Model Router

Mỗi agent chỉ yêu cầu một *tier* — `cheap` hoặc `smart` — không gắn cứng provider nào.
**Model Router** ánh xạ tier sang backend, cấu hình qua `model_mode`:

- **claude_only** — cả hai tier → Claude (nhanh, không nóng GPU local)
- **both** — cheap → Gemma (Ollama, local), smart → Claude
- **ollama_only** — cả hai tier → Gemma (full local)

Một seam thứ hai, **Search interface**, bọc nhà cung cấp web-search (Tavily).

## Các bước pipeline

| Bước | Tier | Vai trò |
|------|------|---------|
| Collect | — | Đọc RSS (lỗi 1 feed không làm sập run) |
| Discover | cheap | Search web hằng ngày + lọc liên quan |
| Ingest | — | Gộp nguồn, khử trùng, bỏ bài đã xử lý |
| Process | cheap | Tóm tắt + category + tags mỗi bài |
| Cluster | cheap | Gom các bài cùng một câu chuyện |
| Analyze | smart | Tổng hợp + xếp ưu tiên thành digest |
| Write | smart | Mỗi câu chuyện một bài, kèm trích nguồn |
| Translate | cheap→smart | EN→VI, giữ thuật ngữ tiếng Anh |
| Quality gate | smart | Chặn bài bịa / không bám nguồn |
| Publish | — | Render Markdown, commit, push |

## Xuất bản & CI/CD

Publisher ghi Markdown **trung lập** (CommonMark + front-matter, không dùng shortcode
Hugo) để có thể đổi site generator sau này. Khi push, GitHub Actions build site Hugo
(trang chủ theo ngày, i18n EN/VI, taxonomy category/tag) và deploy lên GitHub Pages.

## Độ bền

Mọi agent gọi model đều **degrade gracefully** khi output lỗi — một feed hỏng, search
thất bại, hay bài bị từ chối đều không làm sập run. Báo cáo Telegram hằng ngày tóm tắt
số liệu, thời gian từng bước, và các vấn đề kèm nguyên nhân + cách khắc phục.
