---
title: 'Tiếng Việt translation:


  GLM-5.2 được công bố là open-weights model đầu tiên vượt 80% trên Terminal-Bench'
date: '2026-06-17T08:32:39+07:00'
lang: vi
slug: glm-5-2-claimed-as-first-open-weights-model-past-80-on-terminal-bench
categories:
- Models & Research
tags:
- glm
- open-weights
- terminal-bench
- agentic-coding
- benchmarks
summary: Đăng GLM-5.2 trên Reddit/LocalLLaMA tuyên bố đây là open-weights model đầu
  tiên vượt 80% trên Terminal-Bench, vượt trội hơn tất cả các open model khả dụng
  khác và được cho là đánh bại Gemini với chi phí chỉ bằng một phần nhỏ. Tuyên bố
  này bắt nguồn từ một bài đăng của Cline trên X và định vị GLM-5.2 như một open model
  ở tầm frontier cho các tác vụ agentic coding. Nếu được xác minh, điều này sẽ đánh
  dấu một bước thu hẹp đáng kể khoảng cách giữa các frontier model open và closed
  trên các benchmark agentic. Việc nguồn tin đến từ cộng đồng và cách diễn giải dựa
  trên một benchmark duy nhất đòi hỏi sự thận trọng cho đến khi có xác nhận độc lập.
draft: false
---

## GLM-5.2 và ngưỡng 80% trên Terminal-Bench

Một bài đăng trên subreddit LocalLLaMA đưa ra một tuyên bố đáng để dừng lại ngẫm nghĩ: GLM-5.2, theo lời đồn, là open-weights model đầu tiên vượt mốc 80% trên Terminal-Bench. Nếu điều này được xác nhận, đó không chỉ là một bước nhích nhỏ trên bảng xếp hạng — mà là một dấu mốc cho thấy các open model đã tiến xa đến đâu trong loại công việc thực sự giống với một ngày làm việc của developer.

### Vì sao Terminal-Bench là benchmark đáng chinh phục

Có rất nhiều benchmark đo lường liệu một model có thể tạo ra một function chính xác trong điều kiện biệt lập hay không. Terminal-Bench thuộc một phạm trù khác: đây là một đánh giá *agentic*. Model không chỉ phun code ra trong chân không — mà vận hành trong một terminal, thực hiện các hành động, quan sát kết quả, và nối các bước lại để đạt tới mục tiêu. Điều đó khiến nó trở thành một proxy gần gũi hơn nhiều với công việc engineering thực tế, nơi thành công phụ thuộc vào tool use, error recovery, và lập kế hoạch multi-step thay vì sinh ra kết quả chỉ trong một lượt.

Đó cũng chính là điều khiến con số 80% trở nên đáng chú ý. Đạt điểm cao ở đây hàm ý sự thành thạo trên toàn bộ agentic loop, chứ không chỉ là code completion. Đó là sự khác biệt giữa "viết một script nghe có vẻ hợp lý" và "dẫn dắt một task tới hoàn thành trong một môi trường live."

### Góc nhìn open-vs-closed

Tuyên bố này làm hai việc cùng lúc. Thứ nhất, nó định vị GLM-5.2 vượt lên trên mọi open-weights model hiện có khác trên benchmark này. Thứ hai — và đây là phần gây xôn xao hơn — nó được cho là đánh bại Gemini, một closed frontier model, trong khi chi phí chỉ bằng một phần nhỏ.

Nếu chính xác, chính sự kết hợp đó mới là câu chuyện thực sự. Khoảng cách giữa open và closed frontier model trên các agentic task vốn là một trong những lằn ranh dai dẳng nhất trong lĩnh vực này. Các closed lab nhìn chung vẫn giữ thế dẫn đầu ở đúng loại công việc phức tạp, dùng tool, multi-step mà Terminal-Bench cố gắng nắm bắt. Một open-weights model vượt mốc 80% và nhỉnh hơn một đối thủ closed sẽ đánh dấu một sự thu hẹp thực sự của khoảng cách đó — và góc độ chi phí lại càng làm nó sắc nét hơn. Ngang bằng về hiệu năng là một chuyện; ngang bằng về hiệu năng với chi phí thấp hơn lại định hình lại bài toán cho bất kỳ ai đang cân nhắc nên triển khai cái gì trên thực tế.

### Tuyên bố đến từ đâu — và vì sao điều đó quan trọng

Đây là phần cần một cái đầu lạnh hơn. Chuỗi nguồn dẫn đáng để lần theo:

- Dòng tít nằm trong một bài đăng trên Reddit/LocalLLaMA.
- Bài đăng đó truy nguyên tuyên bố về một bài đăng của Cline trên X.
- Toàn bộ khung lập luận dựa trên một benchmark duy nhất.

Không điều nào trong số đó khiến tuyên bố trở thành sai. Nhưng nó còn cách rất xa một sự xác nhận độc lập, có thể tái lập. Những con số được cộng đồng truyền tay thường có cách đông cứng thành "sự thật" thông qua sự lặp lại, trước khi có bất kỳ ai chạy lại bài eval. Và việc dựng khung lập luận trên một benchmark duy nhất là một cái bẫy quen thuộc: một model có thể được tinh chỉnh, dù cố ý hay không, để tỏa sáng trên một bài đánh giá trong khi lại tầm thường ở những chỗ khác. Một con số đơn lẻ hiếm khi khái quát hóa thành "model này ở tầm frontier" trên mọi mặt.

Một vài câu hỏi đáng để bỏ ngỏ cho đến khi có ai đó ngoài nguồn gốc ban đầu trả lời:

- Kết quả 80%+ có tái lập được dưới điều kiện kiểm thử độc lập không?
- GLM-5.2 trụ vững ra sao trên *các* agentic và coding benchmark khác, chứ không chỉ riêng cái này?
- Liệu các tuyên bố so sánh chi phí và đối đầu trực tiếp với Gemini có trụ vững qua sự soi xét trên cùng một mặt bằng không?

### Điều rút ra

Hãy coi đây là một tín hiệu, chứ không phải một kết quả đã ngã ngũ. Hướng mà nó chỉ tới — các open-weights model vươn vào lãnh địa mà cho đến gần đây vẫn là độc quyền của các closed frontier lab trên những agentic coding task — là nhất quán với nơi mà lĩnh vực này vẫn đang hướng tới. Một con số 80% đã được xác minh trên Terminal-Bench từ một open model sẽ là một cột mốc có ý nghĩa cho quỹ đạo đó.

Nhưng từ khóa then chốt là *đã được xác minh*. Hiện tại, tư thế đúng đắn là quan tâm nhưng tay vẫn đặt trên phanh: một tuyên bố mạnh, một hướng đi hợp lý, và một chuỗi nguồn dẫn mỏng đến mức nước đi khôn ngoan là chờ ai đó khác chạy lại các con số.

## Nguồn
- https://www.reddit.com/r/LocalLLaMA/comments/1u7mexd/glm52_is_the_first_openweights_model_to_cross_80/
