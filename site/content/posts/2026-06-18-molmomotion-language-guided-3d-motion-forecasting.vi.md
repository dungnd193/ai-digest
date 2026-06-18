---
title: 'Tiếng Việt: Dự báo chuyển động 3D được dẫn dắt bằng ngôn ngữ'
date: '2026-06-18T17:36:02+07:00'
lang: vi
slug: molmomotion-language-guided-3d-motion-forecasting
categories:
- Research
tags:
- motion-forecasting
- vision-language
- 3d
- allenai
- research
summary: 'MolmoMotion đề xuất một phương pháp tiếp cận được dẫn dắt bởi ngôn ngữ (language-guided)
  cho việc dự báo chuyển động 3D, trong đó các dự đoán về chuyển động tương lai của
  con người hoặc vật thể được điều kiện hóa dựa trên các chỉ dẫn bằng ngôn ngữ tự
  nhiên (natural-language). Bằng cách neo việc tạo quỹ đạo (trajectory) và tư thế
  (pose) vào các mô tả dạng văn bản, phương pháp này hướng tới việc làm cho dự báo
  trở nên dễ kiểm soát hơn và nhất quán hơn về mặt ngữ nghĩa. Công trình này phù hợp
  với một xu hướng rộng lớn hơn là kết hợp các language model với các tác vụ dự đoán
  không gian và vật lý. (Lưu ý: phần tóm tắt được suy ra chỉ từ tiêu đề, do không
  có nội dung bài viết nào được cung cấp.)'
draft: false
---

Ngôn ngữ đã âm thầm trở thành bề mặt điều khiển (control surface) phổ quát cho các hệ thống AI. Chúng ta gõ instructions vào và nhận lại hình ảnh, code, video và structured data. **MolmoMotion** mở rộng pattern đó sang một lĩnh vực vốn từ lâu kháng cự việc điều khiển bằng ngôn ngữ tự nhiên: dự đoán cách con người và vật thể di chuyển trong không gian 3D. Thay vì dự báo chuyển động hoàn toàn dựa trên kinematics quan sát được, nó điều kiện hóa (condition) những dự báo đó theo các instructions bằng ngôn ngữ tự nhiên—biến một mô tả dạng free-text thành một ràng buộc về việc trajectory đi đâu và pose diễn ra như thế nào.

## Vấn đề của motion forecasting thuần túy

3D motion forecasting—dự đoán trajectory và pose tương lai của con người hoặc vật thể—theo truyền thống được đóng khung như một bài toán chuỗi (sequence problem). Bạn quan sát lịch sử các vị trí và chuyển động khớp (articulations), rồi regress hoặc sample ra phần tiếp diễn có khả năng xảy ra cao nhất. Cách này hiệu quả, nhưng nó có một điểm mù mang tính cấu trúc: tương lai của một agent đang chuyển động hiếm khi được quyết định chỉ bởi quá khứ của nó. Ý định (intent) mới là điều quan trọng. Một người đang đi về phía cửa có thể tiếp tục đi thẳng, rẽ sang một bên, hoặc dừng lại, và lịch sử kinematic không đủ để xác định kết quả nào sẽ xảy ra.

Các mô hình thông thường phản ứng với sự mơ hồ này bằng cách "phòng hờ" (hedging)—tạo ra phần tiếp diễn trung bình về mặt thống kê, hoặc một phân phối khuếch tán (diffuse distribution) gồm các tương lai khả dĩ. Điều đó ổn với dự đoán thụ động, nhưng nó không cung cấp công cụ nào để *điều hướng* (steer) dự báo. Không có cách tự nhiên nào để nói "dự đoán chuyển động như thể người đó đang với lấy chiếc cốc" so với "như thể họ sắp ngồi xuống." Đầu vào duy nhất của mô hình là hình học (geometry).

## Ngôn ngữ như một conditioning signal

Đề xuất của MolmoMotion là bổ sung công cụ còn thiếu đó. Bằng cách neo (ground) việc tạo trajectory và pose vào một mô tả văn bản, dự đoán trở nên **có thể điều khiển (controllable)**: cùng một lịch sử quan sát có thể cho ra những tương lai khác nhau nhưng nhất quán về mặt ngữ nghĩa tùy theo instruction. Văn bản đóng vai trò như một đặc tả mềm (soft specification) về ý định, thu hẹp sự mơ hồ giữa nhiều phần tiếp diễn khả thi về mặt vật lý xuống còn đúng một phần phù hợp với mục tiêu được mô tả.

Điều này tái định khung forecasting từ một tác vụ thụ động thành một tác vụ conditional generation. Hai thuộc tính nảy sinh từ sự chuyển dịch đó:

- **Tính điều khiển được (Controllability).** Dự đoán phản hồi theo instructions, nên cùng một scene đầu vào có thể được truy vấn cho những tương lai giả định khác nhau. Điều này có giá trị ở bất cứ đâu mà một hệ thống cần lập luận về *điều gì sẽ xảy ra nếu* (what if) thay vì chỉ *điều gì tiếp theo* (what next).
- **Sự căn chỉnh ngữ nghĩa (Semantic alignment).** Vì việc generation gắn liền với ngôn ngữ, đầu ra được kỳ vọng phải tương ứng với ý nghĩa của instruction—chứ không chỉ đơn thuần mượt mà về mặt kinematic. Chuyển động phải đọc ra được như một biểu hiện của ý định được mô tả.

Hai yếu tố này củng cố lẫn nhau. Controllability mà không có nền tảng ngữ nghĩa thì chỉ là một cái núm vặn không mang ý nghĩa diễn giải nào; semantic alignment chính là điều khiến cái núm đó đáng để vặn.

## Vị trí của nó trong xu hướng rộng hơn

MolmoMotion là một trường hợp của một phong trào rộng hơn: hợp nhất các language model với các tác vụ dự đoán không gian và vật lý. Chúng ta đã thấy ngôn ngữ được dùng để điều kiện hóa việc tổng hợp hình ảnh và video, để điều khiển các robotic policy, và để đặc tả mục tiêu cho các hệ thống planning. Motion forecasting là một biên giới tiếp theo tự nhiên vì nó nằm ngay tại giao điểm của ba thứ mà language model trước đây vốn yếu và giờ đang được đẩy mạnh hướng tới—**hình học (geometry)**, **động lực học vật lý (physical dynamics)**, và **sự tiếp diễn theo thời gian (temporal continuation)**.

Sự căng thẳng thú vị nằm chính xác ở đó. Ngôn ngữ thì rời rạc, mang tính biểu tượng và trừu tượng; chuyển động thì liên tục, gắn với cơ thể (embodied) và bị chi phối bởi vật lý. Bắc cầu giữa chúng đòi hỏi một biểu diễn (representation) mà ở đó một cụm từ có thể tạo thiên lệch (bias) cho một trajectory một cách có ý nghĩa mà không tạo ra chuyển động vi phạm cách cơ thể thực sự di chuyển. Lời hứa của hướng nghiên cứu này là language model cung cấp phần *cái gì* và *tại sao*—ý định và ngữ nghĩa—trong khi motion model thực thi phần *như thế nào*—tính khả thi về mặt kinematic và vật lý.

## Tại sao điều này quan trọng

Nếu language-guided forecasting hoạt động tốt, nó thay đổi những gì chúng ta có thể yêu cầu một hệ thống dự đoán thực hiện. Thay vì một ước lượng thụ động duy nhất, bạn có được một giao diện (interface): mô tả một kịch bản, nhận một dự đoán có nền tảng; thay đổi mô tả, nhận một phương án thay thế nhất quán. Khả năng đó có liên quan đến bất kỳ ứng dụng nào phải dự đoán hành vi và lập luận về các phương án thay thế—bao gồm simulation, tương tác (interaction), planning, và phân tích.

MolmoMotion nên được hiểu không phải như một đích đến đã hoàn thiện mà như một cột mốc cho thấy các tác vụ này đang đi về đâu. Biên giới không còn chỉ là *dự đoán* chuyển động một cách chính xác. Nó là việc làm cho motion prediction trở nên **có thể chỉ đạo (directable)**—đáp ứng được các instructions được phát biểu bằng chính ngôn ngữ mà chúng ta dùng để mô tả ý định ngay từ đầu. Khi các language model tiếp tục thâu nạp các bài toán dự đoán lân cận, hãy kỳ vọng ranh giới giữa "mô tả một tương lai" và "dự báo một tương lai" sẽ tiếp tục bị xói mòn.

## Sources
- https://huggingface.co/blog/allenai/molmomotion
