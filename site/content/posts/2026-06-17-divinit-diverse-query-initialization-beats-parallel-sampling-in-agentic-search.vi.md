---
title: 'Tối ưu hóa khởi tạo đa dạng: khởi tạo query đa dạng vượt trội hơn parallel
  sampling trong agentic search'
date: '2026-06-17T18:47:43+07:00'
lang: vi
slug: divinit-diverse-query-initialization-beats-parallel-sampling-in-agentic-search
categories:
- Research
tags:
- agentic search
- retrieval
- multi-hop QA
- DivInit
- research
summary: Bài báo này xác định việc trùng lặp truy vấn ở lượt đầu tiên (first-turn
  query redundancy) là nguyên nhân gây ra hiệu suất giảm dần khi mở rộng độ rộng (breadth)
  trong agentic search, bởi vì các parallel rollouts có xu hướng đưa ra những truy
  vấn mở đầu gần như giống hệt nhau và truy xuất các bằng chứng chồng chéo. Các tác
  giả giới thiệu DivInit, một phương pháp training-free lấy mẫu nhiều ứng viên truy
  vấn đầu tiên từ một lần gọi duy nhất, chọn ra k seeds đa dạng, và chạy chúng như
  các quỹ đạo song song (parallel trajectories). Trên năm open-weight models và tám
  benchmarks, DivInit mang lại mức cải thiện trung bình từ năm đến bảy điểm trên multi-hop
  QA với mức compute tương đương. Phương pháp này hấp dẫn vì không yêu cầu retraining
  và có thể áp dụng rộng rãi cho các retrieval-augmented agents.
draft: false
---

## Thuế Ẩn của Việc Scale Breadth trong Agentic Search

Khi cấp thêm compute cho một agent retrieval-augmented, nước đi trực giác là scale *breadth*: khởi chạy nhiều rollout song song, để mỗi rollout khám phá câu hỏi theo cách riêng, rồi tổng hợp evidence mà chúng mang về. Nhiều trajectory hơn, độ phủ rộng hơn, câu trả lời tốt hơn. Đó là lý thuyết.

Trong thực tế, lợi ích nhanh chóng chững lại. Bạn nhân đôi số lần chạy song song nhưng câu trả lời gần như không khá hơn. Compute thì có thật; còn lợi ích thì không. Bài báo này chỉ ra chính xác lý do — và thủ phạm đơn giản đến mức gần như đáng xấu hổ.

## Vấn đề nằm ở query đầu tiên

Các rollout song song lẽ ra phải làm đa dạng hóa quá trình search. Nhưng chúng có xu hướng *hội tụ ngay ở nước đi đầu tiên*. Với cùng một câu hỏi, các trajectory được sample độc lập lại đưa ra những opening query gần như giống hệt nhau một cách áp đảo. Và khi opening query giống nhau, evidence được retrieve sẽ trùng lặp nặng nề.

Đây là insight cốt lõi: **first-turn query redundancy** chính là nút thắt cổ chai. Bạn có thể chạy tám trajectory song song, nhưng nếu bảy trong số đó về bản chất đều mở đầu bằng cùng một search, thì bạn đã trả tiền cho tám rollout mà chỉ mua được độ phủ tương đương khoảng hai. Breadth chỉ là trên danh nghĩa. Bên dưới lớp vỏ, các agent chen chúc vào cùng một góc của không gian retrieval trước khi kịp có cơ hội phân hóa.

Điều này định hình lại đường cong diminishing-returns. Vấn đề chưa bao giờ là parallelism không có ích — mà là parallelism ngây thơ lãng phí phần lớn budget vào việc re-fetch lại evidence mà nó đã có. Sự dư thừa tập trung ở turn đầu tiên, nơi nó gây thiệt hại lớn nhất, vì opening query neo giữ mọi thứ phía sau.

## DivInit: đa dạng hóa từ seed, chứ không phải từ sampler

Giải pháp đi thẳng ra từ chẩn đoán. Nếu thất bại nằm ở các opening query dư thừa, thì hãy ép các nước mở đầu tách xa nhau trước khi cam kết compute cho các trajectory đầy đủ.

DivInit làm đúng điều này, qua ba bước:

1. **Sample các candidate từ một lần gọi model duy nhất.** Thay vì khởi chạy k rollout đầy đủ rồi hy vọng chúng phân hóa, hãy sinh ra nhiều first-query candidate ngay từ đầu chỉ với một model call.
2. **Chọn k seed đa dạng.** Từ pool candidate đó, chọn một tập opening query được lựa vì tính đa dạng của chúng — những góc tiếp cận khác biệt về câu hỏi, thay vì k cách diễn đạt lại của cùng một search.
3. **Chạy các seed đa dạng như những trajectory song song.** Mỗi seed được chọn trở thành điểm khởi đầu cho rollout riêng của nó, nhờ vậy parallelism giờ đây bắt đầu từ những vị trí thực sự khác nhau trong không gian evidence.

Sự dịch chuyển về mặt khái niệm thì nhỏ nhưng có hệ quả lớn. Parallel sampling tiêu chuẩn đa dạng hóa nhờ *may rủi* — nó dựa vào stochastic decoding để đẩy các trajectory tách xa nhau, và tại turn đầu tiên mang tính quyết định, decoding hiếm khi chịu hợp tác. DivInit đa dạng hóa bằng *cấu trúc*. Nó chuyển quyết định về tính đa dạng đến đúng nơi mang lại lợi ích lớn nhất, và làm điều đó một cách tường minh thay vì phó mặc cho sampling temperature.

Quan trọng là phương pháp này **training-free**. Không fine-tuning, không reward model, không objective mới. Bạn đang định hình lại cách agent được khởi tạo, chứ không phải những gì nó đã học. Điều đó giúp phương pháp dễ portable trên bất kỳ retrieval-augmented agent nào bạn đang có sẵn.

## Phần đánh giá cho thấy điều gì

Các tác giả thử nghiệm phương pháp trên năm open-weight model và tám benchmark. Trên multi-hop QA — bối cảnh mà độ phủ của evidence khác biệt quan trọng nhất, vì câu trả lời phụ thuộc vào việc nối chuỗi các fact mà không một query đơn lẻ nào có khả năng làm lộ ra — DivInit mang lại mức cải thiện trung bình **năm đến bảy điểm ở cùng mức compute**.

Vế "cùng mức compute" mới là phần đáng dừng lại để ngẫm. Đây không phải câu chuyện chi nhiều hơn để được nhiều hơn. Phép so sánh giữ cố định budget và chỉ thay đổi cách phân bổ budget đó ở turn đầu tiên. Cùng số lượng trajectory, cùng số retrieval call — nhưng được seed để phân hóa thay vì va chạm vào nhau. Lợi ích đến từ việc chi cùng một budget đang có cho những evidence không trùng lặp thay vì những lần fetch dư thừa.

Việc multi-hop là nơi phương pháp này tỏa sáng là điều nhất quán với chẩn đoán. Các câu hỏi single-hop thường có thể được trả lời chỉ từ một query tốt, nên opening-query redundancy tốn rất ít. Các câu hỏi multi-hop cần vài mảnh evidence độc lập, và đó chính xác là nơi mà bảy first query gần như giống hệt nhau khiến agent đói khát đúng những fact mà nó thực sự cần.

## Vì sao điều này quan trọng vượt ra ngoài benchmark

Hai điều khiến DivInit hấp dẫn trên diện rộng.

Thứ nhất, **nó miễn phí để áp dụng**. Không cần retraining nghĩa là không có data pipeline, không tốn compute cho fine-tuning, và không có rủi ro làm suy giảm các năng lực khác của model. Nếu hôm nay bạn đang chạy một retrieval-augmented agent, phương pháp này lắp vừa khít như một thay đổi ở giai đoạn initialization.

Thứ hai, **nó generalize được**. Vì kỹ thuật này nhắm vào một thuộc tính cấu trúc của parallel agentic search — các nước mở đầu dư thừa — chứ không phải một đặc tính riêng của bất kỳ model nào, nên nó áp dụng rộng rãi trên các retrieval-augmented agent. Kết quả tái lập được trên năm model và tám benchmark củng cố cho độ phủ rộng đó, thay vì chỉ là một cấu hình may mắn đơn lẻ.

Có một bài học tổng quát hơn đáng để rút ra. Khi việc scale một chiều của inference ngừng mang lại lợi ích, phản xạ thường là đặt câu hỏi liệu chiều đó có quan trọng hay không. DivInit gợi ý một câu hỏi đầu tiên tốt hơn: *việc scale thực sự đang mua về sự đa dạng, hay chỉ là sự lặp lại?* Parallelism chỉ có ích trong chừng mực các nhánh song song làm những việc khác nhau. Hãy chi diversity budget của bạn vào nơi các nhánh lần đầu phân hóa — nước đi mở đầu — và phần breadth còn lại mà bạn vốn đã trả tiền sẽ bắt đầu xứng với đồng tiền bỏ ra.

## Sources
- https://arxiv.org/abs/2606.17209
