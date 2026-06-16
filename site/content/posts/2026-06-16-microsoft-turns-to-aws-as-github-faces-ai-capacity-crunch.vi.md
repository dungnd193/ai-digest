---
title: Microsoft chuyển sang AWS khi GitHub đối mặt với khủng hoảng năng lực AI
date: '2026-06-16T08:04:00'
lang: vi
slug: microsoft-turns-to-aws-as-github-faces-ai-capacity-crunch
categories:
- Infrastructure
tags:
- cloud
- infrastructure
- compute-capacity
- microsoft
- aws
- github
summary: Microsoft đang hợp tác với đối thủ Amazon Web Services để đảm bảo high-performance
  compute mà họ thiếu cho các tính năng AI của GitHub, cho thấy rằng ngay cả các hyperscalers
  cũng không thể tự cung cấp đầy đủ GPU capacity mà các AI workloads hiện đại yêu
  cầu. Thỏa thuận này đáng chú ý vì nó kết hợp hai đối thủ cloud trực tiếp, nhấn mạnh
  mức độ nghiêm trọng của tình trạng thiếu hụt AI compute. Nó phản ánh một mô hình
  rộng hơn trong ngành về sự hợp tác giữa các nhà cung cấp và multi-cloud sourcing
  để đáp ứng nhu cầu đang tăng vọt. Đối với người dùng GitHub, điều này cho thấy việc
  mở rộng tính năng AI bị hạn chế bởi khả dụng của phần cứng nhiều hơn là do phần
  mềm.
draft: false
---

## Khi "Đám Mây" Cũng Cạn Kiệt

Có một sự trớ trêu nhất định khi chứng kiến một trong những cloud provider lớn nhất thế giới phải đi thuê compute từ chính đối thủ đáng gờm nhất của mình. Thế nhưng đó lại chính xác là những gì đang diễn ra: Microsoft đang chuyển sang dùng Amazon Web Services để có được lượng high-performance compute cần thiết nhằm vận hành các tính năng AI của GitHub. Một công ty vốn bán GPU capacity cho cả phần còn lại của ngành lại đang thiếu hụt chính nguồn lực này ở ít nhất một góc trong đế chế của mình.

Với bất kỳ ai đã dành vài năm qua theo dõi quá trình xây dựng hạ tầng AI, đây không hẳn là một diễn biến bất ngờ, mà là một sự xác nhận. Nút thắt cổ chai chưa bao giờ thực sự nằm ở phần mềm.

### Chuyện gì thực sự đang diễn ra

Các tính năng AI của GitHub phụ thuộc vào loại high-performance compute — tức là những accelerator vừa khan hiếm, vừa đắt đỏ, lại đang có nhu cầu cực cao — mà mọi AI workload hiện nay đều đang tranh giành. Microsoft, công ty mẹ của GitHub, rõ ràng không thể tự cung cấp đủ năng lực đó từ đội ngũ hạ tầng của riêng mình. Vì vậy, họ tìm đến AWS để có được nó.

Nếu gạt bỏ các thương hiệu và thỏa thuận rườm rà, bản chất sự việc rất bình thường: một workload cần phần cứng, và bên vận hành sẽ tìm nguồn cung phần cứng đó ở bất cứ đâu có thể. Điều khiến nó đáng chú ý là *ai* đang đứng ở mỗi bên của giao dịch. Microsoft và Amazon là đối thủ trực tiếp trong lĩnh vực cloud infrastructure. Azure và AWS tiêu tốn rất nhiều nguồn lực để giành lấy cùng một tệp khách hàng. Khi hai đối thủ ở tầm cỡ đó hợp tác về capacity, điều đó cho thấy mức độ khan hiếm hiện nay đủ lớn để lấn át cả những bản năng cạnh tranh thông thường.

### Ngay cả hyperscaler cũng không thể tự cung tự cấp

Giả định mặc định về những công ty như Microsoft, Amazon hay Google là họ sở hữu nguồn tài nguyên gần như vô tận — rằng khan hiếm chỉ là vấn đề của các bên "downstream". Sự sắp xếp này đã phá vỡ giả định đó.

Nếu một hyperscaler với tiềm lực tài chính, quy mô data-center và mạng lưới quan hệ nhà cung cấp như Microsoft mà vẫn phải tìm nguồn lực từ bên ngoài chỉ để phục vụ tính năng AI của một sản phẩm duy nhất, thì "cứ xây thêm capacity" không phải là một đòn bẩy đơn giản như vẻ ngoài của nó. Việc tự cung ứng có những giới hạn nhất định. Và những giới hạn đó đang bị chạm tới ngay ở đỉnh của hệ thống, chứ không chỉ ở tầng các startup đang chật vật tìm vài trăm GPU.

### Một xu hướng, không phải trường hợp cá biệt

Thỏa thuận Microsoft–AWS khớp với một mô hình rộng lớn hơn đang dần hình thành trên toàn ngành: cross-provider cooperation và multi-cloud sourcing như một phản ứng trước nhu cầu bùng nổ. Khi một nhà cung cấp đơn lẻ — kể cả hạ tầng nội bộ của chính bạn — không thể thỏa mãn cơn khát của một AI workload, bạn sẽ tìm nguồn cung từ bất kỳ ai còn dư high-performance compute.

Một vài điều rút ra khi mô hình này trở thành chuẩn mực thay vì ngoại lệ:
- **Ranh giới cạnh tranh trở nên mờ nhạt dưới áp lực khan hiếm.** Sự đối đầu vẫn còn ở tầng bán hàng và sản phẩm, nhưng ở tầng raw-capacity, nguồn cung lấn át lòng trung thành.
- **Multi-cloud không còn thuần túy là một lựa chọn kiến trúc.** Nó trở thành một chiến lược procurement, bị chi phối bởi nơi phần cứng thực sự tồn tại và sẵn sàng.
- **Câu hỏi "Cái này chạy ở đâu?" có một câu trả lời phức tạp hơn.** Nhà cung cấp có tên trên sản phẩm chưa chắc đã là nhà cung cấp sở hữu silicon đang thực sự xử lý công việc.

### Điều này có ý nghĩa gì với người dùng GitHub

Bài học hữu ích nhất cho những ai thực sự dùng các tính năng AI của GitHub là cách nhìn nhận lại những rào cản đang giới hạn họ.

Mô hình tư duy tự nhiên là các khả năng AI sẽ mở rộng cùng phần mềm: tung ra một model tốt hơn, tối ưu serving stack, và tính năng sẽ nhanh hơn, rộng hơn. Nhưng sự sắp đặt này gợi ý rằng binding constraint nằm ở một lớp bên dưới tất cả những thứ đó. Việc mở rộng tính năng AI bị chi phối bởi availability của phần cứng nhiều hơn là bởi mức độ sẵn sàng của phần mềm.

Trên thực tế, điều đó có nghĩa là tốc độ các tính năng AI mở rộng, tăng tốc hay triển khai đến nhiều người dùng hơn lại gắn với một yếu tố kém linh hoạt hơn nhiều so với việc deploy code — đó là nguồn cung high-performance compute, bất kể có thể tìm thấy nó ở đâu. Khi bạn chạm trần về capacity hoặc thấy tiến độ triển khai chậm hơn dự kiến, lời giải thích có thể ít liên quan đến kỹ thuật mà liên quan nhiều hơn đến cuộc chạy đua toàn cầu để giành lấy các accelerator.

### Tín hiệu thầm lặng

Sẽ rất dễ để đọc câu chuyện này như chuyện về hai công ty và một sản phẩm. Nhưng tín hiệu bền vững hơn là điều mà thỏa thuận này hé lộ về giai đoạn hiện tại: nhu cầu về AI compute đã vượt xa khả năng cung ứng của ngay cả những đối thủ lớn nhất và có mức độ tích hợp theo chiều dọc (vertically integrated) cao nhất.

Khi Microsoft đi thuê từ Amazon để duy trì hoạt động cho AI của GitHub, thông điệp ở đây không phải là Microsoft đã sai lầm. Mà là tình trạng thiếu hụt AI compute đã trở nên trầm trọng đến mức ngay cả những nhà cung cấp lớn nhất ngành giờ đây cũng đang lặng lẽ trở thành khách hàng của nhau.

## Sources
- https://runtimewire.com/article/microsoft-github-aws-ai-capacity-crunch
