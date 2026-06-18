---
title: DeepMind cảnh báo về rủi ro của tương tác agent-to-agent quy mô lớn
date: '2026-06-18T17:36:09+07:00'
lang: vi
slug: deepmind-warns-about-risks-of-mass-agent-to-agent-interaction
categories:
- AI Policy & Safety
tags:
- deepmind
- ai-safety
- agents
- alignment
- multi-agent
summary: Google DeepMind đang tài trợ cho nghiên cứu về các rủi ro của những hệ sinh
  thái nơi hàng triệu AI agent tự hành tương tác trực tuyến mà không có sự giám sát
  của con người. Rohin Shah, người đứng đầu bộ phận nghiên cứu an toàn và alignment
  AGI của công ty, cảnh báo rằng sự xuất hiện đại trà của các agent thực hiện nhiệm
  vụ và chuyển tiếp chỉ dẫn cho nhau là một mối lo ngại ngày càng lớn về an toàn.
  Việc tập trung vào các động lực multi-agent mang tính trỗi dậy đánh dấu một sự chuyển
  dịch đáng chú ý từ alignment cho mô hình đơn lẻ sang rủi ro mang tính hệ thống.
  Điều này cho thấy nghiên cứu an toàn đang bắt đầu dự liệu trước làn sóng triển khai
  mang tính agentic.
draft: false
---

## Khi Các Agent Bắt Đầu Trò Chuyện Với Nhau

Trong gần suốt thập kỷ qua, nghiên cứu về AI safety đã có một đơn vị phân tích gọn gàng: model. Bạn lấy một hệ thống đơn lẻ, thăm dò hành vi của nó, nghiên cứu cách các mục tiêu của nó đi chệch khỏi ý định của người thiết kế, và cố gắng align artifact đơn lẻ đó trước khi nó được phát hành. Google DeepMind hiện đang phát đi tín hiệu rằng cách định khung này, dù không sai, có thể ngày càng trở nên chưa đủ. Công ty đang tài trợ cho nghiên cứu về một câu hỏi khác và khó hơn — điều gì xảy ra khi hàng triệu AI agent tự hành tương tác với nhau trên mạng, phần lớn nằm ngoài tầm giám sát trực tiếp của con người.

### Sự dịch chuyển từ một model sang nhiều model

Mối lo ngại này đang được nêu ra từ chính bên trong nỗ lực AGI safety và alignment của DeepMind, do Rohin Shah dẫn dắt. Điều ông cảnh báo không phải là một model thông minh hơn hay một hệ thống đơn lẻ có năng lực cao hơn, mà là sự xuất hiện đại trà của các *agent* — phần mềm không chỉ trả lời câu hỏi mà còn hành động trên các task, và quan trọng hơn, chuyển tiếp các chỉ thị cho những agent khác trong quá trình đó.

Chi tiết cuối cùng đó chính là điểm xoay chuyển. Một model đơn lẻ đã được align là một mục tiêu kỹ thuật khả thi. Nhưng một quần thể các agent giao việc và ra chỉ thị cho nhau lại là một loại đối tượng hoàn toàn khác. Rủi ro không còn nằm trọn vẹn bên trong weights hay training objective của bất kỳ hệ thống đơn lẻ nào; nó có thể nổi lên từ chính các *tương tác* giữa những hệ thống mà mỗi cái, xét riêng lẻ, ít nhiều đều đang hành xử đúng như thiết kế.

Đây là một cách định khung lại đáng chú ý. Nó dịch chuyển trọng tâm của nghiên cứu safety từ alignment của một model đơn lẻ sang một thứ gần hơn với **systemic risk** — việc nghiên cứu cách cả một hệ sinh thái hành xử, thay vì cách một thành phần đơn lẻ hành xử.

### Vì sao tương tác làm thay đổi bài toán

Nếu bạn từng làm việc với distributed systems, trực giác này sẽ thấy quen thuộc ngay cả khi lĩnh vực còn mới. Những thuộc tính đúng với một node đơn lẻ thường sụp đổ một khi bạn có nhiều node trao đổi thông điệp với nhau. Các feedback loop xuất hiện. Hành vi cục bộ hoàn toàn hợp lý khi đứng riêng lại tổ hợp thành hành vi toàn cục mà không ai chỉ định hay mong muốn. Các động lực emergent, gần như theo định nghĩa, là những thứ bạn không thiết kế ra và không thể dự đoán đầy đủ từ các bộ phận thành phần.

Các agent chuyển tiếp chỉ thị cho nhau chính xác là loại hệ thống tổ hợp như vậy. Khi output của một agent trở thành input của một agent khác — và điều đó nối chuỗi qua một quần thể lớn — bạn có được một hệ thống mà hành vi của nó là sản phẩm của cả mạng lưới, chứ không chỉ của từng thành viên riêng lẻ. Đơn vị phân tích không còn là agent mà trở thành hệ sinh thái.

Và cách định khung ở đây bổ sung thêm một điểm sắc bén: sự tương tác này đang diễn ra **không có sự giám sát của con người** trong vòng lặp. Quy mô đang được bàn đến — hàng triệu agent — chính xác là quy mô mà việc con người review từng tương tác không còn khả thi nữa. Bất cứ điều gì nổi lên đều nổi lên nhanh chóng và với khối lượng lớn.

### Đón đầu làn sóng triển khai

Điều khiến chuyện này đáng chú ý là *thời điểm* của lời cảnh báo. Nghiên cứu safety thường bị mô tả — dù công bằng hay không — là mang tính phản ứng, đến sau khi một năng lực đã được triển khai ở quy mô lớn. Việc tài trợ nghiên cứu về động lực agent-to-agent đại trà ngay từ bây giờ có thể được hiểu như một nỗ lực đón đầu: dự đoán làn sóng triển khai agentic thay vì phản ứng lại sau khi sự việc đã rồi.

Đó cũng là một tín hiệu về nơi mà lĩnh vực này cho rằng biên giới đang hướng tới. Khoản đầu tư này ngụ ý một cú đặt cược rằng các agent hành động trên các task và phối hợp với nhau sẽ trở thành một hiện thực đại trà, chứ không phải một ngách. Nếu bạn giả định tương lai đó, thì việc nghiên cứu hành vi emergent của các hệ sinh thái agent không phải là việc dọn dẹp mang tính suy đoán — đó là bài toán tiếp theo một cách tự nhiên.

### Câu hỏi còn bỏ ngỏ

Không điều nào trong số này đi kèm một câu trả lời gọn gàng, và bản thân cách định khung mới chính là đóng góp: sự thừa nhận rằng việc align từng agent một cách riêng lẻ có thể không đủ để khiến cả một *quần thể* các agent trở nên an toàn. Systemic risk trong các hệ sinh thái multi-agent là một chương trình nghiên cứu thực sự khác biệt so với alignment của một model đơn lẻ, với những câu hỏi riêng của nó về emergence, sự giám sát ở quy mô lớn, và rốt cuộc thì việc một system-of-systems được "align" có nghĩa là gì.

Tóm tắt một cách trung thực thì lĩnh vực này đang bắt đầu đặt ra câu hỏi, chứ chưa giải quyết được nó. Nhưng đặt ra câu hỏi đó ngay từ bây giờ — trước khi hàng triệu agent thường xuyên chuyển tiếp chỉ thị cho nhau ngoài thực địa — mới chính là điều quan trọng.

## Sources
- https://www.technologyreview.com/2026/06/11/1138794/google-deepmind-is-worried-about-what-happens-when-millions-of-agents-start-to-interact/
