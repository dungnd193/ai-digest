---
title: Bản mở model open-weights chưng cất từ bản preview Fable-5 ngắn ngủi của Anthropic
date: '2026-06-16'
lang: vi
slug: open-weights-model-distilled-from-anthropic-s-short-lived-fable-5-preview
categories:
- Open-Source AI
tags:
- open-weights
- distillation
- export-controls
- unverified
- huggingface
summary: 'Một lập trình viên trong cộng đồng đã phát hành Qwable-v1, một model Qwen3.6-35B-A3B
  open-weights được cho là đã distill từ bản preview Fable-5 ngắn ngủi của Anthropic
  bằng cách sử dụng 4.659 cleartext agentic-coding traces, với model, các bản GGUF
  quantization, và bộ dữ liệu SFT được công bố trên Hugging Face theo giấy phép AGPL-3.0.
  Bài đăng tuyên bố rằng Fable-5 (80,3% SWE-bench Pro) đã bị đình chỉ trên toàn cầu
  sau khoảng bốn ngày theo các chỉ thị kiểm soát xuất khẩu (export-control) của Hoa
  Kỳ, và rằng tool surface của nó (ví dụ: str_replace_editor) đã rò rỉ vào các distilled
  weights. Đây là những tuyên bố chưa được kiểm chứng từ cộng đồng, có nguồn gốc từ
  Reddit và nên được tiếp nhận một cách thận trọng. Nếu đúng, điều này đặt ra những
  câu hỏi đáng chú ý về việc distill từ các preview model, vấn đề kiểm soát xuất khẩu,
  và sự rò rỉ ngoài ý muốn của các tool interface độc quyền.'
draft: true
---

Open weights có những cách xuất hiện ở những nơi không ai lường trước. Ví dụ mới nhất, nếu các tuyên bố là đúng, là một small distilled model được cho là mang dấu vết của một frontier preview đã bị gỡ offline gần như ngay khi vừa xuất hiện. Câu chuyện này đáng để xem xét không phải vì các chi tiết đã được xác nhận — chúng chưa được xác nhận — mà vì những câu hỏi nó đặt ra nếu bất kỳ phần nào trong đó là thật.

## Những gì được cho là đã phát hành

Một developer trong cộng đồng đã công bố một model có tên **Qwable-v1**, được mô tả là một open-weights `Qwen3.6-35B-A3B` checkpoint. Theo bản phát hành, nó được distilled từ bản preview ngắn ngủi **Fable-5** của Anthropic bằng **4.659 cleartext agentic-coding traces**. Tác giả đã công bố model weights, các bản GGUF quantization phục vụ local inference, và bộ dữ liệu supervised fine-tuning (SFT) trên Hugging Face, tất cả dưới giấy phép **AGPL-3.0**.

Bài đăng kèm theo đưa ra một số tuyên bố đáng chú ý:

- Fable-5 được cho là đạt **80,3% trên SWE-bench Pro**.
- Bản preview được cho là đã bị **đình chỉ trên toàn cầu sau khoảng bốn ngày**, với lý do được nêu là **các chỉ thị export-control của Hoa Kỳ**.
- **Tool surface** của model — bao gồm một editing tool tên là `str_replace_editor` — được cho là đã **rò rỉ vào distilled weights**.

Trước khi đi xa hơn, cần lưu ý: **đây là những tuyên bố chưa được kiểm chứng từ cộng đồng, có nguồn từ Reddit.** Không một con số, mốc thời gian, hay lời giải thích về export-control nào được xác nhận độc lập. Hãy coi mọi nội dung tiếp theo là lập luận có điều kiện về một kịch bản giả định, chứ không phải tường thuật về sự thật đã được xác lập.

## Tại sao distillation từ một bản preview lại đáng chú ý

Distillation — huấn luyện một "student" model nhỏ hơn để bắt chước outputs của một "teacher" model lớn hơn — là một kỹ thuật đã quá quen thuộc. Điều khiến trường hợp này đáng chú ý là *nguồn* được cho là đã sử dụng: một frontier preview chỉ khả dụng trong thời gian ngắn.

Vài nghìn agentic-coding traces là một bộ dữ liệu nhỏ theo tiêu chuẩn pretraining, nhưng với SFT nhắm vào một hành vi cụ thể — agentic coding — chừng đó có thể đủ để chuyển giao một phần năng lực đáng kể. Quy trình được ngụ ý khá đơn giản:

1. Thu thập các transcript của model preview khi thực hiện các coding task (các "traces").
2. Định dạng chúng thành các supervised example.
3. Fine-tune một open base model để tái tạo hành vi của teacher.

Nếu các traces được thu thập ở dạng cleartext trong khoảng thời gian preview, việc đình chỉ model upstream cũng không xóa bỏ được những gì đã thu thập. Dữ liệu, một khi đã được thu thập, sẽ tồn tại lâu hơn API. Sự bất đối xứng đó — quyền truy cập tạm thời, artifacts bền vững — chính là cốt lõi của toàn bộ sự việc.

## Tool surface bị rò rỉ

Tuyên bố hé lộ nhiều nhất về mặt kỹ thuật là việc được cho là rò rỉ một **tool interface** độc quyền vào student weights. Các agentic model vận hành thông qua tools: các structured function call như file editor, shell runner, và search utility. Cách một model được dạy để đặt tên và gọi những tools đó là một phần trong scaffolding của nó.

Ví dụ được nêu tên, `str_replace_editor`, chính xác là loại artifact có thể rò rỉ qua distillation. Nếu các traces của teacher chứa những lệnh gọi đến một editing tool có tên cụ thể, một student được huấn luyện để bắt chước các traces đó sẽ học cách phát ra cùng những lệnh gọi ấy — bao gồm cả tên tool và calling convention. Student không "biết" rằng tool đó là độc quyền; nó chỉ tái tạo những pattern mà nó được cho xem.

Đây là một dạng rò rỉ tinh vi. Nó không phải là đánh cắp weight, cũng không phải là một bản prompt dump. Nó là **behavioral residue**: distilled model vô tình mã hóa hình dạng của một interface mà những người tạo ra nó chưa bao giờ công bố. Đối với bất kỳ ai đang reverse-engineer cách một frontier agent được nối dây, residue đó là thông tin có giá trị.

## Những câu hỏi đáng suy ngẫm

Giả sử, để phục vụ lập luận, rằng phần cốt lõi của câu chuyện là chính xác. Khi đó, một số vấn đề sau đây nảy sinh.

**Distillation từ các bản preview.** Quyền truy cập preview thường được định khung là để đánh giá, chứ không phải như một training corpus. Nếu một khoảng thời gian truy cập ngắn ngủi cũng đủ để thu được năng lực agentic có thể chuyển giao, thì ranh giới giữa "thử một model" và "khai thác một model" trở nên mong manh. Các điều khoản dịch vụ thường cấm việc dùng outputs để huấn luyện các model cạnh tranh, nhưng việc thực thi đối với một bản phát hành cộng đồng ẩn danh lại là một vấn đề hoàn toàn khác.

**Export controls như một đòn bẩy phân phối.** Tuyên bố rằng một model bị rút lại theo các chỉ thị export-control — nếu đúng — chỉ ra một căng thẳng mà giới compute và chính sách đã cảnh báo từ lâu: controls có thể chi phối một API endpoint, nhưng chúng chi phối *các artifacts phái sinh* kém rõ ràng hơn nhiều. Một model bị đình chỉ vì lý do chính sách không thu hồi được những gì đã được distilled từ nó trong vòng đời ngắn ngủi của nó, và một bản phát hành AGPL-3.0 được thiết kế để lan truyền tự do.

**Rò rỉ interface ngoài ý muốn.** Chi tiết `str_replace_editor` là lời nhắc rằng proprietary scaffolding có thể thoát ra qua hành vi, chứ không chỉ qua code hay weights. Các team phát hành agentic model có lẽ cần nhìn nhận tool naming và calling convention như một bề mặt có thể quan sát được, có khả năng bị phục dựng bởi bất kỳ ai thu thập đủ số lượng transcript.

## Đọc câu chuyện này một cách có trách nhiệm

Rất dễ để một câu chuyện sống động — một frontier model bị gỡ trong bốn ngày, các traces bí mật, một tool name bị rò rỉ — lấn át vai trò của bằng chứng. Nhưng không nên để điều đó xảy ra. Con số benchmark, việc đình chỉ, lý do export-control, và việc rò rỉ đều là những khẳng định từ một bài đăng cộng đồng chưa được kiểm chứng, và bất kỳ điều nào trong đó cũng có thể sai, bị phóng đại, hoặc bịa đặt.

Điều khiến sự việc này đáng bàn luận không phải là liệu bản phát hành cụ thể này có đúng như mô tả hay không. Mà là *cơ chế* hoàn toàn hợp lý đằng sau nó: quyền truy cập tạm thời, cộng với việc thu thập bền vững, cộng với cấp phép thoáng, tạo ra những artifacts tồn tại lâu hơn các điều kiện đã sinh ra chúng. Dù Qwable-v1 có đúng như tác giả nói hay không, cơ chế đó là có thật, và các câu hỏi về governance xoay quanh nó sẽ không biến mất.

Vậy nên hãy giữ các chi tiết một cách lỏng lẻo và các câu hỏi mang tính cấu trúc một cách chắc chắn. Nếu một model có thể được distilled một cách đáng kể chỉ từ một khoảng thời gian truy cập bốn ngày — và nếu weights của nó có thể âm thầm mang theo tool interface của một đối thủ cạnh tranh — thì những vấn đề khó khăn không nằm ở một bản upload ẩn danh nào đó. Chúng nằm ở việc "preview" và "withdrawal" thực sự có nghĩa là gì một khi outputs đã bắt đầu tuôn ra ngoài.

## Sources
- https://www.reddit.com/r/LocalLLaMA/comments/1u6zj79/claude_fable_5_distilled/
