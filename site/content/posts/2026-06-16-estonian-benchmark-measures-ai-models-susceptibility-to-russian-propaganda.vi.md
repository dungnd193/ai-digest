---
title: Estonia ra mắt benchmark đo lường mức độ dễ bị ảnh hưởng của các AI model trước
  tuyên truyền của Nga
date: '2026-06-16T19:11:50+07:00'
lang: vi
slug: estonian-benchmark-measures-ai-models-susceptibility-to-russian-propaganda
categories:
- AI Safety & Security
tags:
- disinformation
- benchmark
- AI safety
- propaganda
- evaluation
summary: Viện Ngôn ngữ Estonia đã phát hành một benchmark mới nhằm định lượng mức
  độ dễ dàng mà các large language model có thể bị tác động bởi các luận điệu disinformation
  của Nga. Bài kiểm tra này khảo sát mức độ mà các model tiếp thu, lặp lại hoặc không
  phản bác lại cách diễn đạt mang tính tuyên truyền. Nó bổ sung vào một khối lượng
  công trình ngày càng tăng về đánh giá tính toàn vẹn thông tin (information-integrity),
  và đáng chú ý vì đến từ một viện ngôn ngữ quốc gia nhỏ hơn thay vì một lab lớn.
  Khi các chiến dịch gây ảnh hưởng do nhà nước bảo trợ ngày càng nhắm vào generative
  AI, các chỉ số đo lường mức độ dễ bị tác động được chuẩn hóa như thế này đang trở
  thành một công cụ quản trị thiết thực.
draft: false
---

## Khi một viện ngôn ngữ quốc gia bắt đầu công bố các AI benchmark, đó là điều đáng chú ý. Viện Ngôn ngữ Estonia (Institute of the Estonian Language) vừa phát hành một benchmark mới đo lường mức độ dễ bị "dẫn dắt" của các large language model trong việc lặp lại thông tin sai lệch (disinformation) của Nga. Đây là một đóng góp tuy nhỏ nhưng sắc bén cho một vấn đề đang nóng lên nhanh chóng: khi các chiến dịch gây ảnh hưởng (influence operation) do nhà nước bảo trợ chuyển hướng sang generative AI, chúng ta cần những cách thức chuẩn hóa để đo lường khả năng kháng cự của model trước chúng.

## Benchmark này thực sự đo lường điều gì

Phần lớn công việc đánh giá language model hiện nay vẫn xoay quanh một bộ trục quen thuộc — reasoning, coding, khả năng nhớ lại sự kiện (factual recall), và hành vi từ chối (refusal) đối với nội dung bị cấm rõ ràng. Mức độ dễ bị tác động bởi tuyên truyền (propaganda) lại là một mục tiêu khác, và trơn trượt hơn nhiều. Vấn đề không nằm ở việc model có xuất ra thứ gì đó công khai bị cấm hay không, mà ở chỗ liệu một model, khi được đưa cho một khung diễn giải (framing) thiên lệch, có lặng lẽ tiếp nhận nó hay không.

Benchmark của Estonia thăm dò chính xác điều này. Thay vì hỏi liệu model có *biết* một sự kiện hay không, nó kiểm tra cách model hành xử khi tiếp xúc với framing tuyên truyền. Có ba hành vi nằm trong phạm vi xét:

- **Absorption (Hấp thụ)** — model có nội tâm hóa các tiền đề của narrative và lập luận dựa trên chúng như thể đó là bối cảnh nền trung lập hay không?
- **Repetition (Lặp lại)** — model có tái tạo các luận điểm tuyên truyền khi được prompt trong một chủ đề lân cận hay không?
- **Failure to push back (Không phản biện)** — khi một khung diễn giải sai lệch hoặc mang tính thao túng được đưa ra, model có để nó tồn tại mà không thách thức hay không?

Hành vi thứ ba mới là điều tinh tế. Một model có thể chính xác về mặt sự kiện khi xét riêng lẻ mà vẫn thất bại ở đây, bởi failure mode không phải là bịa đặt — mà là sự thụ động. Một hệ thống không chủ động phản bác một khung diễn giải gây hiểu lầm, trên thực tế, đang tiếp tay tạo độ tin cậy cho nó.

## Vì sao "không phản biện" là trường hợp khó

Hãy nghĩ về cách disinformation thực sự lan truyền qua một model. Một influence operation hiếm khi cần model khẳng định một điều dối trá trắng trợn. Chỉ cần khiến model chấp nhận một tuyên bố gây tranh cãi như một tiền đề mặc định, lặp lại một cách nói uyển ngữ (euphemism), hoặc trình bày "cả hai phía" của một vấn đề vốn không thực sự có hai phía là đủ. Đây là các hiệu ứng framing, và chúng lọt qua những đánh giá được xây dựng quanh các phán quyết đúng/sai rạch ròi.

Đây cũng là lý do vì sao hành vi này khó huấn luyện để chống lại mà không bị điều chỉnh thái quá (overcorrect). Hãy tinh chỉnh một model để hoài nghi và đối đầu tối đa với mọi prompt thiên lệch, và bạn sẽ làm suy giảm tính hữu dụng của nó trên những chủ đề thực sự gây tranh cãi một cách chính đáng. Vùng lý tưởng nằm ở khoảng giữa: một model nhận ra framing thao túng và phản biện một cách tương xứng, mà không trở nên chống đối theo phản xạ. Một benchmark có thể định vị một model trên phổ đó đang đo lường một thứ thực sự hữu ích — và là thứ mà phần lớn các eval hiện có không nắm bắt được.

## Ý nghĩa của việc nó đến từ đâu

Có một điểm mang tính cấu trúc đáng để dừng lại suy ngẫm. Benchmark này đến từ một viện ngôn ngữ quốc gia tương đối nhỏ, chứ không phải một lab lớn. Điều đó quan trọng vì vài lý do.

Thứ nhất, threat model mang tính cục bộ. Những narrative nhắm vào không gian thông tin vùng Baltic không giống với những narrative mà một lab lớn, lấy tiếng Anh làm trung tâm, để tâm nhất. Một tổ chức gắn liền với ngôn ngữ và bối cảnh khu vực có vị thế tốt để hiểu tuyên truyền thực sự trông như thế nào ở đó — framing nào có sức nặng, euphemism nào báo hiệu một lập trường cụ thể, tuyên bố lịch sử nào đang bị tranh cãi và theo chiều hướng nào. Các đánh giá an toàn (safety evaluation) chung chung, được sản xuất tập trung, thường bỏ lỡ lớp chi tiết tinh vi này.

Thứ hai, đây là một dấu hiệu lành mạnh cho hệ sinh thái đánh giá. Các benchmark đo lường tính toàn vẹn thông tin (information integrity) không nên đều bắt nguồn từ cùng một nhóm nhỏ các tổ chức vốn cũng chính là những nơi xây dựng model. Việc phân tán quyền tác giả của hoạt động đánh giá — bao gồm cả từ khu vực công và các tổ chức quốc gia — mang lại sự độc lập và đa dạng góc nhìn mà một nền văn hóa đơn nhất (monoculture) gồm các benchmark do lab sản xuất không thể có được.

## Các chỉ số về mức độ dễ bị tác động như một hạ tầng quản trị

Lùi lại một bước, bức tranh lớn hơn hiện ra rõ ràng. Các influence operation ngày càng nhắm vào generative AI như một bề mặt phân phối (delivery surface) — không chỉ như một mục tiêu để jailbreak, mà như một kênh có thể "tẩy trắng" và khuếch đại một narrative ở quy mô lớn. Trong môi trường đó, một chỉ số chuẩn hóa về mức độ dễ bị tác động không còn là một thứ tò mò mang tính học thuật mà bắt đầu trông giống một hạ tầng quản trị (governance infrastructure).

Một khi có thể định lượng mức độ dễ dàng mà một model hấp thụ tuyên truyền, bạn có thể làm những việc trước đây không thể:

- **So sánh (Compare)** các model với nhau trên một chiều mà việc mua sắm (procurement) và chính sách thực sự quan tâm.
- **Theo dõi (Track)** xem khả năng kháng cự của một model nhất định cải thiện hay thoái lui qua các phiên bản.
- **Đặt ngưỡng (Set thresholds)** — một bên triển khai (deployer), cơ quan quản lý, hoặc tổ chức công có thể nêu ra một mức tối thiểu mà một model phải vượt qua trước khi được dùng trong một bối cảnh nhạy cảm.

Không điều nào trong số đó khả thi khi mức độ dễ bị tác động vẫn còn là một nỗi lo mơ hồ, mang tính định tính. Đo lường là điều kiện tiên quyết cho trách nhiệm giải trình (accountability). Benchmark này là một phần của khối lượng công việc đang gia tăng nhằm thúc đẩy việc đánh giá information-integrity theo hướng đó.

## Điều cần giữ trong góc nhìn cân bằng

Một benchmark là một proxy, không phải là chính lãnh thổ. Một con số duy nhất mô tả cách một model xử lý một tập corpus các framing tuyên truyền là một ảnh chụp nhanh, không phải một sự bảo đảm — đối thủ luôn thích nghi, các narrative luôn thay đổi, và bất kỳ tập kiểm thử cố định nào rồi cũng bị "gài" (gamed) hoặc trở nên lỗi thời. Giá trị ở đây không phải là một điểm số vĩnh viễn; mà là việc thiết lập một trục có thể đo lường được, cùng một minh chứng rằng các tổ chức bên ngoài các lab lớn cũng có thể xây dựng những công cụ đáng tin cậy dọc theo trục đó.

Minh chứng đó có lẽ là đóng góp bền vững nhất. Vấn đề disinformation trong generative AI sẽ không được giải quyết bởi một lab, một quốc gia, hay một benchmark duy nhất. Nó sẽ đòi hỏi một nỗ lực phân tán để xây dựng và duy trì các phép đo phản ánh nhiều threat model và nhiều ngôn ngữ khác nhau. Một viện ngôn ngữ quốc gia công bố một benchmark về mức độ dễ bị tác động chính là kiểu đóng góp mà hệ sinh thái đó cần có nhiều hơn.

## Sources
- https://the-decoder.com/how-easily-can-russian-propaganda-fool-ai-models-a-new-benchmark-finds-out/
