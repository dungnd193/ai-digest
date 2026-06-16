---
title: Tôi Định nghĩa về Giải thích Tốt và Những Thách thức khi Giải thích Đầu ra
  của LLM
date: '2026-06-16'
lang: vi
slug: a-definition-of-good-explanations-and-the-challenges-explaining-llm-outputs
categories:
- Research
tags:
- interpretability
- explainability
- research
- xai
summary: Bài báo này giải quyết vấn đề triết học và thực tiễn về việc định nghĩa điều
  gì khiến một AI explanation trở nên "tốt", đề xuất một framework dựa trên counterfactuals
  và prior beliefs của người đối thoại. Nó coi explainability là mang tính tương quan
  với khán giả thay vì là một thuộc tính cố định của model output. Công trình đóng
  góp sự rõ ràng về mặt khái niệm cho các tài liệu nghiên cứu về interpretability
  và XAI. Ảnh hưởng ngắn hạn của nó chủ yếu mang tính học thuật, mặc dù nó có thể
  định hướng cho các tiêu chuẩn explainability trong tương lai.
draft: true
---

Hãy tự hỏi: khi một hệ thống AI đưa cho bạn một lời giải thích (explanation), làm sao bạn biết nó có tốt hay không? Không phải nó nghe có trôi chảy hay tự tin không—mà là nó có thực sự *giải thích* hay không. Câu hỏi tưởng chừng đơn giản ấy hóa ra lại chưa có câu trả lời ngã ngũ, và một bài báo gần đây lập luận rằng cả lĩnh vực này đã và đang xem nó như một thuộc tính của model, trong khi thực ra nó là thuộc tính của cuộc đối thoại.

## Vấn đề khi xem "explainability" như một danh từ

Chúng ta thường nói về explainability như thể nó là một núm vặn trên model: vặn lên, thì output trở nên dễ diễn giải (interpretable) hơn. Khung tư duy mà công trình này đề xuất phản bác mạnh mẽ trực giác đó. Một explanation, theo lập luận của họ, không phải là một thuộc tính cố định mà một output hoặc có hoặc không. Nó mang tính **audience-relative** (phụ thuộc vào người nhận)—chất lượng của nó phụ thuộc vào ai đang tiếp nhận và họ đã tin sẵn điều gì.

Cách tái định hình này quan trọng bởi vì phần lớn công cụ của chúng ta ngầm giả định điều ngược lại. Attribution map, saliency score, và feature attribution được tính toán một lần rồi trình ra cho tất cả mọi người, như thể một sản phẩm duy nhất có thể phục vụ một chuyên gia trong lĩnh vực (domain expert), một nhà quản lý (regulator), và một end user đều tốt như nhau. Nếu chất lượng explanation là tương đối so với người đối thoại (interlocutor), thì một "explanation tốt" tách rời khỏi audience của nó là một lỗi phạm trù (category error)—giống như hỏi một câu có phải là một câu trả lời tốt hay không mà không biết câu hỏi là gì.

## Hai thành phần: counterfactual và prior

Khung này đặt nền tảng cho một explanation tốt dựa trên hai thứ phối hợp với nhau.

Thứ nhất là **counterfactual**. Một explanation chứng minh giá trị của mình bằng cách cho bạn biết điều gì lẽ ra đã thay đổi kết quả—kết quả sẽ khác đi như thế nào dưới những điều kiện thay thế. Đây là một bước đi quen thuộc trong văn liệu về interpretability, và có lý do chính đáng: cấu trúc counterfactual chính là thứ phân biệt một explanation với một mô tả đơn thuần. Nói "model output ra X" là mô tả; nói "nếu điều này đã khác đi, thì output lẽ ra đã là Y" mới là giải thích.

Thành phần thứ hai mới là thứ làm công việc tái định hình: **prior belief (niềm tin có trước) của người đối thoại**. Cùng một counterfactual có thể khai sáng với người này nhưng vô dụng với người khác, tùy thuộc vào điều họ vốn đã cho là đúng. Nhiệm vụ của một explanation là dịch chuyển người nghe khỏi vị trí niềm tin hiện tại của họ, và bạn không thể đo lường sự dịch chuyển đó nếu không biết điểm xuất phát.

Gộp lại, đề xuất đại khái như sau: một explanation tốt là một explanation mà nội dung counterfactual của nó tác động một cách hiệu quả lên những prior cụ thể của người mà nó hướng đến. Chất lượng nằm ở khoảng cách giữa điều họ tin trước đó và điều họ tin sau đó—chứ không phải trong bản thân sản phẩm.

```
explanation quality
   = f( counterfactual content , interlocutor's prior beliefs )

   not
   = g( model output )
```

Sự dịch chuyển nhỏ về ký hiệu đó—từ một hàm của output sang một hàm của output *và* audience—chính là cốt lõi khái niệm của đóng góp này.

## Vì sao LLM khiến điều này khó một cách gay gắt

Khung này có tính tổng quát, nhưng bài báo nhắm vào một trường hợp cụ thể và đầy bất tiện: giải thích output của các large language model. Vài thứ cùng hợp lực khiến điều này khó hơn so với việc giải thích quyết định của một classifier.

- **Không có điểm bám counterfactual rõ ràng nào.** Với một model dạng bảng (tabular), bạn có thể nhiễu loạn (perturb) một feature và xem dự đoán dịch chuyển. Với một LLM tạo ra văn bản mở (open-ended), đơn vị nào bạn thay đổi, và outcome nào bạn dùng để đo lường sự thay đổi đó? Bộ máy counterfactual làm nền cho định nghĩa khó vận hành hóa (operationalize) hơn khi cả input lẫn output đều là ngôn ngữ phi cấu trúc.
- **Người đối thoại là ẩn số và đa dạng.** LLM được triển khai cho những audience khổng lồ, không đồng nhất. Nếu chất lượng explanation phụ thuộc vào prior belief, thì một explanation tinh chỉnh cho không một ai cụ thể tức là tinh chỉnh cho chẳng ai cả.
- **Bản thân explanation lại do chính loại hệ thống đó tạo ra.** Khi model có thể tạo ra một lý lẽ (rationale) trôi chảy, nghe có vẻ hợp lý theo yêu cầu, thì sức thuyết phục bề mặt có thể đội lốt chất lượng giải thích thực sự. Một định nghĩa neo vào sự thay đổi niềm tin thực sự—chứ không vào độ thuyết phục của văn bản đọc lên—là một sự điều chỉnh hữu ích ở đây, bởi nó từ chối chấm điểm một explanation dựa trên sự hùng biện.

Sợi chỉ kết nối những điều này là: bối cảnh LLM tước bỏ những tiện lợi từng cho phép chúng ta *giả vờ* rằng explanation là một thuộc tính của model. Nó buộc audience phải quay trở lại trong bức tranh.

## Đây là gì, và không phải là gì

Cũng nên thành thật về loại đóng góp mà công trình này mang lại. Giá trị của nó là **sự sáng tỏ về mặt khái niệm** (conceptual clarity)—nó làm sắc nét điều chúng ta muốn nói khi gọi một explanation là tốt, và nó trao cho văn liệu interpretability và XAI một nền tảng vững chắc hơn so với "nhìn có vẻ interpretable đối với tôi." Điều đó là thật, nhưng nó không phải một method mới, một benchmark, hay một công cụ mà bạn có thể `pip install` ngày mai.

Ảnh hưởng ngắn hạn của chính bài báo, theo cách định hình của nó, chủ yếu mang tính học thuật. Con đường khả dĩ hơn dẫn đến tác động thực tiễn chạy qua các tiêu chuẩn (standards): nếu các yêu cầu về explainability có bao giờ được viết vào quy định pháp lý hay chuẩn mực ngành, thì một định nghĩa nghiêm ngặt, audience-relative chính là loại nền móng mà những tiêu chuẩn đó cần dựa vào. Một định nghĩa trụ vững qua sự soi xét lúc này chính là thứ giữ cho các quy định tương lai khỏi bị xây trên tiền đề lung lay rằng explanation là một thuộc tính bạn có thể chứng nhận một lần rồi giao cho tất cả mọi người.

## Điều rút ra cho người làm thực hành

Nếu bạn xây dựng hay đánh giá các hệ thống explanation, sự dịch chuyển có thể hành động được là ngừng hỏi "explanation này có tốt không?" và bắt đầu hỏi "**tốt cho ai, đối chiếu với prior nào?**"

Cách tái định hình đó có sức nặng. Nó gợi ý rằng đánh giá một explanation mà không mô hình hóa audience của nó là không hoàn chỉnh ngay từ trong cấu trúc. Nó gợi ý rằng nội dung counterfactual là cần nhưng chưa đủ—cùng một counterfactual phải tác động vào một tập niềm tin cụ thể thì mới làm được việc gì. Và nó gợi ý rằng riêng với LLM, nơi audience thì rộng lớn còn output thì đủ trôi chảy để ngụy tạo chính sự biện minh của nó, ta nên hồ nghi nhất với những explanation trông tốt với tất cả mọi người, bởi một explanation được hiệu chỉnh (calibrate) cho tất cả mọi người tức là được hiệu chỉnh cho chẳng ai cả.

Không điều nào trong số này khiến việc giải thích output của LLM dễ hơn. Nhưng gọi tên cái khó một cách chính xác—định vị nó trong mối quan hệ giữa counterfactual và prior thay vì trong một feature nào đó còn thiếu của model—là bước đi đầu tiên để xử lý nó một cách trung thực. Bạn không thể xây dựng những explanation tốt cho đến khi bạn nói được điều gì làm nên một explanation tốt, và nói được *điều đó* khó hơn, và tương đối hơn, so với những gì công cụ của lĩnh vực này cho đến nay vẫn thừa nhận.

## Sources
- https://arxiv.org/abs/2606.14838
