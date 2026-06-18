---
title: 'Tàu vũ trụ NAVI-Orbital: màn trình diễn vision-language model đầu tiên trên
  quỹ đạo'
date: '2026-06-18T17:36:11+07:00'
lang: vi
slug: navi-orbital-first-in-orbit-vision-language-model-demonstration
categories:
- Research
tags:
- vision-language
- earth-observation
- edge-ai
- gemma
- space
summary: NAVI-Orbital là một hệ thống phần mềm được triển khai trên một tàu vũ trụ
  ở quỹ đạo Trái Đất tầm thấp (Low Earth Orbit) mà vào ngày 16 tháng 4 năm 2026 đã
  đạt được màn trình diễn đầu tiên được biết đến về việc một vision-language model
  chạy hoàn toàn tự động suy luận multi-modal ngay trên tàu khi đang ở trong quỹ đạo.
  Nó kết hợp một VLM cục bộ (Gemma 3) với một state machine LangGraph để phân loại
  cảnh, tạo mô tả và phản hồi các prompt bằng tiếng Anh thông thường từ người vận
  hành, qua đó cho phép tái phân công nhiệm vụ bằng ngôn ngữ tự nhiên. Bằng cách nén
  dữ liệu quan sát Trái Đất theo ngữ nghĩa ngay trên quỹ đạo, nó đảo ngược mô hình
  băng thông thu thập-rồi-truyền-xuống thông thường. Đây là một minh chứng đáng chú
  ý cho edge AI trong các môi trường tự động bị hạn chế về băng thông.
draft: false
---

## Khi Vệ Tinh Tự Quyết Định Điều Gì Đáng Gửi Về

Kể từ khi chúng ta đưa những chiếc camera lên quỹ đạo, quy trình vận hành gần như cứng nhắc đến mức buồn cười: hướng sensor về mục tiêu, chụp lại mọi thứ, rồi đổ toàn bộ dữ liệu thô xuống trạm mặt đất mỗi khi có cửa sổ downlink. Con tàu vũ trụ chỉ là một con mắt vô tri. Toàn bộ phần "suy nghĩ" diễn ra sau đó, dưới mặt đất, sau khi bandwidth đã bị tiêu tốn hết. Vào ngày 16 tháng 4 năm 2026, một hệ thống có tên NAVI-Orbital đã phá vỡ khuôn mẫu đó bằng cách làm một điều chưa từng được chứng minh trên quỹ đạo: nó chạy một vision-language model ngay trên tàu, hoàn toàn tự động, để con tàu vũ trụ suy luận về những gì nó đang nhìn thấy *trước khi* quyết định truyền gì về.

Đây là lần đầu tiên được ghi nhận một VLM thực hiện autonomous multi-modal inference ngay trên con tàu vũ trụ ở Low Earth Orbit. Đó là một mệnh đề khá dài, nên đáng để mổ xẻ vì sao mỗi từ đều quan trọng.

### NAVI-Orbital thực chất là gì

NAVI-Orbital là một hệ thống phần mềm được triển khai trên một con tàu vũ trụ LEO. Về cốt lõi, nó kết hợp hai thành phần:

- Một **local vision-language model** — Gemma 3 — chạy trực tiếp trên con tàu vũ trụ, không cần bất kỳ vòng round trip nào xuống mặt đất.
- Một **LangGraph state machine** điều phối hành vi của model thành một pipeline mạch lạc, có thể lặp lại.

Kết hợp lại, chúng thực hiện ba việc ngay trên tàu:

1. **Phân loại cảnh (classify scenes)** — xác định loại đối tượng mà con tàu vũ trụ đang nhìn thấy.
2. **Tạo mô tả (generate descriptions)** — sinh ra những bản tóm tắt bằng ngôn ngữ tự nhiên về các quan sát đó.
3. **Phản hồi các prompt tiếng Anh thông thường từ operator** — tiếp nhận chỉ dẫn được viết theo cách một con người diễn đạt, và hành động dựa trên chúng.

Khả năng thứ ba mới chính là điều âm thầm thay đổi mô hình vận hành. Nó cho phép **re-tasking bằng ngôn ngữ tự nhiên**: thay vì upload một chuỗi lệnh được mã hóa tỉ mỉ để chuyển hướng sự chú ý của con tàu vũ trụ sang đối tượng khác, operator có thể mô tả ý định của mình bằng tiếng Anh thông thường và để hệ thống trên tàu tự diễn giải.

### Đảo ngược mô hình bandwidth

Kiến trúc quan sát Trái Đất thông thường là *thu thập rồi mới downlink* (acquire-then-downlink). Bạn thu thập hình ảnh thô, đẩy nó xuống mặt đất, và phần thông tin có giá trị được trích xuất ở đầu bên kia của một đường ống rất hẹp và gián đoạn. Bandwidth là nút thắt cổ chai cố hữu, và phần lớn những gì được truyền đi đều vô vị — mây che phủ, đại dương trống rỗng, những cảnh chẳng ai yêu cầu.

NAVI-Orbital đảo ngược điều này bằng cách **nén các quan sát Trái Đất về mặt ngữ nghĩa (semantically), ngay trên quỹ đạo**. Thay vì gửi đi từng pixel và hy vọng tín hiệu hữu ích sống sót, con tàu vũ trụ hiểu cảnh trước, rồi có thể truyền đạt ý nghĩa thay vì dữ liệu thô. Một mô tả ngữ nghĩa về nội dung trong một khung hình rẻ hơn nhiều bậc về mặt truyền tải so với chính khung hình đó — và hữu ích hơn hẳn, một khi model đã quyết định rằng khung hình đó đáng được mô tả.

Đây chính là cốt lõi khái niệm của màn trình diễn. Nút thắt cổ chai không bị loại bỏ; nó được di dời. Computation được đẩy ra edge để nguồn tài nguyên khan hiếm — downlink bandwidth — được chi cho thông tin thay vì cho dữ liệu.

### Tại sao chạy nó *ngay trên tàu* mới là phần khó

Thật dễ để đọc "VLM trong không gian" như một chi tiết triển khai đơn thuần. Không phải vậy. Môi trường quỹ đạo là một trong những môi trường khắc nghiệt nhất có thể hình dung đối với loại workload inference mà các VLM thường chạy: năng lượng bị giới hạn, compute bị ràng buộc, kết nối gián đoạn theo thiết kế, và không có operator nào túc trực để can thiệp theo thời gian thực. Tính tự động ở đây không phải là một tính năng xa xỉ — nó là một yêu cầu bắt buộc, bởi mặt đất có thể đơn giản là nằm ngoài tầm với vào đúng lúc cần ra một quyết định.

Đó là điều khiến việc điều phối bằng LangGraph trở nên có ý nghĩa, bên cạnh bản thân model. Một VLM trần trụi chỉ là một thành phần; một state machine bao bọc quanh nó là một *hệ thống* — một hệ thống có thể chuyển một cách tất định (deterministically) giữa việc phân loại, mô tả, và phản hồi, và làm như vậy mà không cần con người trong vòng lặp. Chính sự kết hợp này đã biến một model tình cờ nằm trên con tàu vũ trụ thành một con tàu vũ trụ thực sự có thể suy nghĩ về những gì nó nhìn thấy.

### Một minh chứng cho edge AI dưới những ràng buộc thực tế

Lùi lại khỏi những đặc thù của quỹ đạo, NAVI-Orbital đọc lên như một minh chứng rõ ràng cho một luận điểm rộng hơn: rằng AI có năng lực có thể chạy **ở edge, một cách tự động, trong những môi trường bị giới hạn bandwidth** — và rằng làm được như vậy sẽ thay đổi bài toán kinh tế của toàn bộ hệ thống xung quanh nó. Cùng một logic khiến semantic compression trở nên hấp dẫn trên quỹ đạo cũng áp dụng cho bất cứ nơi nào mà đường link quay về data center là đắt đỏ, chậm, hoặc không đáng tin cậy: các sensor từ xa, các khu công nghiệp bị ngắt kết nối, bất cứ nơi nào mà chi phí di chuyển dữ liệu thô lớn hơn nhiều so với chi phí hiểu nó tại chỗ.

Điều mà màn trình diễn ngày 16 tháng 4 thiết lập được là: đây không chỉ là một lập luận kiến trúc trên bảng trắng. Một local VLM, được điều phối thành một pipeline tự động, đã thực sự chạy inference ngay trên một con tàu vũ trụ và tự re-task chính mình từ tiếng Anh thông thường. Con mắt đã học được cách quyết định điều gì đáng để nhìn — và điều gì đáng để gửi về nhà.

## Sources
- https://arxiv.org/abs/2606.18271
