---
title: Mô hình Nhân quả Cấu trúc Quan hệ cho Suy luận Nhân quả Tổng quát hóa
date: '2026-06-16T18:15:59+07:00'
lang: vi
slug: relational-structural-causal-models-for-generalizable-causal-reasoning
categories:
- AI Research / Causal Inference
tags:
- causal-inference
- structural-causal-models
- machine-learning
- research
- generalization
summary: Bài báo này mở rộng các structural causal models của Pearl sang bối cảnh
  quan hệ (relational), nơi các đối tượng và mối quan hệ giữa chúng thay đổi, qua
  đó cho phép suy luận nhân quả có thể tổng quát hóa sang những tổ hợp đối tượng chưa
  từng thấy. Các tác giả chỉ ra rằng các truy vấn nhân quả và quan sát trên những
  tổ hợp đối tượng mới là không thể nhận dạng (identifiable) nếu không có thêm giả
  định, sau đó giới thiệu relational causal graphs cùng với các tiêu chí nhận dạng
  mang tính biểu tượng (symbolic), bao gồm cả trong điều kiện có unobserved confounding.
  Họ đề xuất relational neural causal models, một phương pháp có thể chứng minh là
  đúng đắn và vượt trội hơn các baseline phi quan hệ trên các cảnh giao thông mô phỏng.
  Công trình này là một đóng góp lý thuyết có ý nghĩa hướng tới suy luận nhân quả
  mang tính tổ hợp (compositional) và có khả năng tổng quát hóa, mặc dù tác động thực
  tiễn trong ngắn hạn của nó vẫn còn ở giai đoạn nghiên cứu.
draft: false
---

Causal inference từ lâu đã mang trong mình một mâu thuẫn ngay tại cốt lõi. Các structural causal models (SCMs) của Pearl cho chúng ta một ngôn ngữ chặt chẽ để lập luận về interventions và counterfactuals, nhưng chúng giả định một tập biến cố định. Một khi đã định nghĩa model trên các biến `A`, `B` và `C`, thì đó chính là toàn bộ thế giới mà bạn có thể lập luận. Ngay khi thế giới chứa thêm những đối tượng khác, hoặc vẫn những đối tượng đó nhưng được sắp xếp theo một cấu hình mới, model không còn gì để nói nữa. Với những domain vốn dĩ mang tính relational — những scene đầy các đối tượng mà số lượng và quan hệ giữa chúng thay đổi từ instance này sang instance khác — đây là một hạn chế nghiêm trọng.

Một hướng nghiên cứu gần đây giải quyết trực diện vấn đề này bằng cách mở rộng structural causal models sang các relational setting, nơi cả các đối tượng lẫn các quan hệ giữa chúng đều biến thiên. Mục tiêu rất tham vọng: causal reasoning có khả năng *generalize tới những tổ hợp đối tượng chưa từng thấy*, thay vì bị khóa chặt vào những thực thể cụ thể hiện diện tại thời điểm training.

## Tại sao SCMs với tập biến cố định lại không đủ

SCM cổ điển là một hệ thống đóng. Causal graph của nó liệt kê một tập node cụ thể, và các kết quả identification — những định lý cho biết liệu một causal query có thể được tính toán từ observational data hay không — đều được phát biểu trên graph cố định đó. Đây chính xác là điều bạn cần khi hệ thống được nghiên cứu có các biến ổn định và được đặt tên rõ ràng.

Nó đổ vỡ khi các thực thể có thể hoán đổi cho nhau và mang tính tổ hợp. Hãy xét một scene gồm nhiều đối tượng tương tác với nhau. Train trên các scene với một cách sắp xếp đối tượng nhất định, rồi đặt ra một causal question về một scene chứa tổ hợp mà bạn chưa từng quan sát. Một SCM non-relational không thể transfer: nó không có cách biểu diễn cho "một đối tượng thuộc loại này" tách bạch với "đối tượng cụ thể này". Về mặt hình thức, mỗi tổ hợp mới là một model mới.

Thay vào đó, điều bạn mong muốn là một model nắm bắt được causal mechanism *ở cấp độ loại đối tượng và quan hệ*, sao cho cùng một mechanism áp dụng được bất kể đối tượng cụ thể nào hiện thực hóa nó. Đó chính là lời hứa của tính compositional: học các mảnh ghép một lần, rồi tái tổ hợp chúng một cách tự do.

## Generalization không phải là thứ cho không

Kết quả thực chất đầu tiên của công trình này lại là một kết quả mang tính phủ định, và nó đáng để ta dừng lại suy ngẫm. Các causal và observational query trên những tổ hợp đối tượng *mới lạ* là **không identifiable nếu không có các giả định bổ sung**.

Điều này quan trọng vì nó đập tan một trực giác phổ biến. Người ta có thể hy vọng rằng nếu học được đúng relational mechanism thì khả năng generalize tới các tổ hợp mới sẽ tự động theo sau. Nhưng không phải vậy. Tồn tại một sự mơ hồ thực sự: nhiều underlying model có thể nhất trí về mọi thứ bạn đã quan sát nhưng lại bất đồng về các query liên quan đến những cấu hình chưa từng thấy. Nếu không có thêm cấu trúc hoặc giả định, những query đó là underdetermined.

Việc xác lập điều này ngay từ đầu là thứ khiến phần còn lại của đóng góp mang tính nguyên tắc thay vì heuristic. Nếu bỏ qua phần phân tích identifiability, bạn có nguy cơ xây dựng một phương pháp trông như thể generalize tốt trên benchmark nhưng lại không có bảo đảm nào — và không hề đặc trưng hóa được *khi nào* nó có khả năng hoạt động.

## Relational causal graphs và symbolic identification

Để identification trở nên khả thi về mặt tính toán, các tác giả giới thiệu **relational causal graphs** được trang bị các **symbolic identification criteria**. Sự chuyển dịch từ "graph trên các biến cụ thể" sang "graph trên cấu trúc relational" là nước đi then chốt: các tiêu chí được phát biểu một cách symbolic, nên chúng áp dụng được cho cả những họ tổ hợp đối tượng thay vì một instantiation đơn lẻ.

Quan trọng nhất, phân tích identification mở rộng tới cả trường hợp **unobserved confounding** — tình huống mà các nguyên nhân chung ẩn liên kết các biến với nhau, vốn chính xác là nơi causal inference ngây thơ sai lầm nặng nề nhất. Việc xử lý confounding một cách symbolic, trong relational setting, là thứ tạo nên sức mạnh thực sự cho framework. Nó có nghĩa là các tiêu chí có thể cho bạn biết liệu một query trên một tổ hợp mới lạ có identifiable hay không, ngay cả khi không phải mọi thứ liên quan đều được quan sát.

Nói cách khác, framework làm hai việc cùng một lúc:

- Nó cho bạn biết *những* causal query nào trên các tổ hợp đối tượng chưa từng thấy là có thể trả lời được, với các giả định đã nêu.
- Nó làm điều đó ở cấp độ symbolic, relational, nên câu trả lời transfer được qua các cấu hình thay vì phải tính lại cho từng instance.

## Relational neural causal models

Lý thuyết đặc trưng hóa identifiability cần một phương pháp đồng hành để thực sự ước lượng các đại lượng. Ở đây đó là **relational neural causal models**, được trình bày như một cách tiếp cận **đúng đắn có chứng minh (provably correct)** — nghĩa là nó được thiết kế để tôn trọng các identification criteria thay vì chỉ đơn thuần fit data rồi hy vọng vào điều tốt đẹp nhất.

Sự kết hợp này chính là điểm mấu chốt. Một model thuần neural có thể generalize tốt về mặt thực nghiệm nhưng không đưa ra bảo đảm nào rằng các câu trả lời của nó tương ứng với những causal quantity hợp lệ. Một framework thuần symbolic đặc trưng hóa được những gì có thể trả lời nhưng lại không ước lượng nó từ data. Ghép cặp chúng lại tạo ra một phương pháp mà tính đúng đắn gắn liền với identification theory, trong khi vẫn có thể học được.

Về mặt thực nghiệm, các relational neural causal models được đánh giá trên **các traffic scene mô phỏng** và **vượt trội hơn các baseline non-relational**. Giao thông là một testbed tự nhiên cho loại khẳng định này: các scene biến thiên về số lượng agent cũng như các quan hệ không gian và tương tác giữa chúng, nên generalize tới các tổ hợp chưa từng thấy chính xác là thách thức đặt ra. Đánh bại các baseline non-relational là dấu hiệu được kỳ vọng của một phương pháp đã nắm bắt được mechanism ở cấp độ relational thay vì học thuộc lòng các cấu hình cụ thể.

## Đây là gì, và đây không phải là gì

Cần nói rõ về ý nghĩa của công trình này. Đây là một **đóng góp lý thuyết** hướng tới compositional, generalizable causal inference. Điểm mạnh của nó là sự rõ ràng và chặt chẽ về mặt khái niệm: nó hình thức hóa các relational SCM, chứng minh rằng generalization ngây thơ là không identifiable, cung cấp các symbolic criteria (bao gồm cả dưới điều kiện confounding), và hậu thuẫn chúng bằng một phương pháp ước lượng provably correct đã được kiểm chứng trong mô phỏng.

Còn đây không phải là — ít nhất là chưa phải — một công cụ thực tiễn đã được triển khai. Việc đánh giá diễn ra trên các scene mô phỏng, và tác động thực tiễn trong ngắn hạn vẫn còn ở **giai đoạn nghiên cứu**. Cách diễn đạt trung thực là công trình này thúc đẩy phần nền tảng: nó cho chúng ta biết compositional causal reasoning *có thể* trông như thế nào và dưới những giả định nào thì nó được đặt vấn đề một cách chỉnh chu, trong khi con đường đến với các hệ thống thực tế đầy phức tạp vẫn còn ở phía trước.

## Tại sao nó vẫn quan trọng

Ý nghĩa rộng hơn là nó kết nối hai mạch nghiên cứu mà giới học thuật phần lớn vẫn giữ tách biệt. Causal inference mang lại sự chặt chẽ về interventions và counterfactuals nhưng giả định một tập biến tĩnh. Compositional và relational modeling mang lại khả năng generalization qua các đối tượng biến thiên nhưng thường không có bảo đảm về mặt causal. Bằng cách mở rộng SCMs vào lãnh địa relational — và thẳng thắn về các rào cản identifiability — công trình này phác thảo hình hài của một sự hợp nhất khả dĩ.

Đối với những practitioner đang xây dựng hệ thống trong các domain vốn dĩ mang tính relational, những điều rút ra có giá trị tức thời ngay cả trước khi các phương pháp này chín muồi:

- Generalize các causal claim tới những tổ hợp đối tượng chưa từng thấy *không* phải là điều tự động; hãy chuẩn bị tinh thần cần đến các giả định bổ sung rõ ràng, và biết rằng nếu thiếu chúng thì các query của bạn có thể là underdetermined.
- Identification, bao gồm cả dưới điều kiện unobserved confounding, có thể được lập luận một cách symbolic ở cấp độ relational thay vì phải suy diễn lại cho từng cấu hình.
- Các phương pháp gắn liền với identification criteria mang lại cho bạn những bảo đảm về tính đúng đắn mà một neural model được fit tự do không thể cung cấp.

Giấc mơ compositional — học các causal mechanism trên các loại đối tượng một lần, rồi lập luận về bất kỳ cách sắp xếp nào của chúng — trong thực tiễn vẫn còn là một giấc mơ. Nhưng công trình này khiến nó trở thành một giấc mơ chặt chẽ hơn, với một bản đồ rõ ràng về những phần nào có thể trả lời được và những phần nào đòi hỏi chúng ta phải đặt giả định lên bàn.

## Sources
- https://arxiv.org/abs/2606.14892
