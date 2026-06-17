---
title: Microsoft Copilot Cowork chuyển sang tính phí theo mức sử dụng và cân nhắc
  DeepSeek
date: '2026-06-17T08:32:45+07:00'
lang: vi
slug: microsoft-s-copilot-cowork-shifts-to-usage-based-billing-and-weighs-deepseek
categories:
- Industry & Business
tags:
- microsoft
- copilot
- deepseek
- pricing
- ai-economics
summary: Microsoft được cho là đang cân nhắc sử dụng một phiên bản fine-tune của DeepSeek
  V4 làm lựa chọn backend rẻ hơn cho Copilot Cowork, cho thấy sự cởi mở với các mô
  hình không phải của OpenAI vì lý do chi phí. Đồng thời, công ty đang chuyển Copilot
  Cowork từ mô hình tính phí cố định sang tính phí theo mức sử dụng, với người đứng
  đầu Copilot là Charles Lamanna lập luận rằng giá cố định là không bền vững đối với
  các workload AI dạng agentic. Sự thay đổi này phản ánh một sự nhìn nhận lại rộng
  hơn trong ngành rằng các AI agent ngốn nhiều compute đang gây áp lực lên các mô
  hình giá "all-you-can-eat". Cả hai động thái đều cho thấy áp lực về biên lợi nhuận
  đang định hình cách các sản phẩm AI được định giá và vận hành.
draft: false
---

## Microsoft's Copilot Cowork Tái Định Hình Cả Hóa Đơn Lẫn Bộ Não Của Nó

Hai động thái được đưa tin xoay quanh Copilot Cowork của Microsoft cùng lúc chạm tới một điểm nhạy cảm: vận hành agentic AI tốn kém đến mức nào, và ai là người gánh chi phí đó. Một thay đổi liên quan đến pricing. Thay đổi còn lại liên quan đến model nằm bên dưới. Đọc cùng nhau, chúng kể một câu chuyện vượt xa phạm vi một sản phẩm đơn lẻ.

### Sự dịch chuyển về pricing: flat rate gặp đối thủ xứng tầm

Microsoft đang chuyển Copilot Cowork từ mô hình flat-rate pricing sang hướng tính phí theo mức sử dụng (usage-based billing). Charles Lamanna, người đứng đầu mảng Copilot, lập luận rằng flat pricing là không bền vững đối với các workload của agentic AI.

Cách diễn giải đó quan trọng vì nó chỉ thẳng vào vấn đề. Mô hình SaaS pricing truyền thống giả định một tương quan tỷ lệ thuận tương đối giữa số tiền người dùng trả và chi phí để phục vụ họ — và, quan trọng nhất, một mức trần về mức tiêu thụ. License theo seat hoạt động được vì một con người chỉ có thể click một lượng nhất định trong ngày. Agentic AI phá vỡ giả định đó. Một agent không biết mệt, không nghỉ ăn trưa, và có thể ngốn compute chỉ với một chỉ thị duy nhất theo cách mà một con người tương tác với UI không bao giờ làm được.

Dưới mô hình flat rate, sự bất đối xứng đó là một gánh nặng cho nhà cung cấp. Những người dùng nặng nhất — chính là những người khai thác được nhiều giá trị nhất, và nhiều khả năng cũng là những người mà nhà cung cấp muốn giữ chân nhất — cũng là những người vượt qua bất kỳ biên lợi nhuận nào mà mức giá flat đã giả định. Mô hình pricing kiểu "ăn bao nhiêu tùy thích" âm thầm trợ giá cho các power user bằng chi phí của tất cả những người còn lại, và khi "thức ăn" là GPU time cho các tác vụ autonomous chạy dài, sự trợ giá này không còn bền vững nữa.

Usage-based billing tái cân bằng các động cơ. Chi phí bám sát mức tiêu thụ, nên rủi ro của nhà cung cấp co giãn theo workload thay vì tách rời khỏi nó. Cái giá phải đánh đổi là điều mà mọi dịch vụ tính phí theo đồng hồ cuối cùng đều phải đối mặt: tính dự đoán được. Flat rate dễ lập ngân sách; usage-based pricing biến mỗi lần chạy agent thành một dòng chi phí, và khách hàng buộc phải bắt đầu cân nhắc chi phí biên (marginal cost) của việc thả một agent ra làm một tác vụ.

### Câu hỏi về model: cởi mở vì lý do chi phí

Động thái thứ hai được đưa tin thì âm thầm hơn nhưng có lẽ nói lên nhiều điều hơn. Microsoft được cho là đang cân nhắc một phiên bản fine-tuned của DeepSeek V4 như một lựa chọn backend rẻ hơn cho Copilot Cowork.

Từ đáng chú ý ở đây là *rẻ hơn*. Đây không được định khung như một nước cờ về năng lực hay một biện pháp phòng ngừa rủi ro phụ thuộc một nhà cung cấp duy nhất trên nguyên tắc — đây là một quyết định về chi phí. Và nó báo hiệu sự sẵn lòng nhìn ra ngoài OpenAI để tìm các model vận hành Copilot, khi bài toán kinh tế chỉ về hướng đó.

Đó là một lập trường đáng kể đối với một công ty mà câu chuyện AI của họ vốn gắn chặt với một nhà cung cấp model duy nhất. Việc coi model backend như một thành phần có thể hoán đổi và nhạy cảm với chi phí — một thứ bạn fine-tune và lắp vào vì nó hợp toán — định khung lại lớp model như một hạ tầng cần được tối ưu thay vì một sự phụ thuộc cố định. Nếu unit economics của các workload agentic đang chịu áp lực, thì bản thân model trở thành một trong những đòn bẩy lớn nhất bạn có thể kéo về phía chi phí.

### Hai động thái, một nguyên nhân gốc

Sẽ rất dễ để đọc thay đổi về billing và việc đánh giá model như những mẩu tin sản phẩm không liên quan đến nhau. Nhưng chúng không phải vậy. Cả hai đều chỉ về áp lực biên lợi nhuận, tiếp cận từ hai đầu đối lập của cùng một phương trình:

- **Phía doanh thu:** usage-based billing làm tăng số tiền mà những người tiêu thụ nặng phải trả, nên doanh thu bám sát chi phí phục vụ họ.
- **Phía chi phí:** một backend fine-tuned rẻ hơn làm giảm chi phí để tạo ra mỗi đơn vị công việc ngay từ đầu.

Bạn kéo cả hai đòn bẩy khi khoảng chênh lệch giữa hai bên trở nên mỏng — khi các agent ngốn compute khiến giả định cũ, rằng một mức giá cố định thừa sức bao phủ một chi phí cố định, không còn đúng nữa.

### Cuộc thanh toán sòng phẳng rộng lớn hơn

Ý nghĩa ở đây là đây thực ra không phải một câu chuyện riêng của Microsoft. Nó phản ánh một cuộc đối diện trên toàn ngành với những gì mà các AI agent ngốn compute gây ra cho các mô hình pricing kiểu "ăn bao nhiêu tùy thích". Những động lực tương tự — các workload autonomous không có mức trần tiêu thụ tự nhiên, chạy trên compute đắt đỏ — áp dụng cho bất kỳ ai đang ship các sản phẩm agentic, bất kể logo của ai nằm trên hộp.

Nếu một công ty với quy mô và các mối quan hệ nhà cung cấp như Microsoft thấy rằng flat pricing là không bền vững đối với agentic AI và bắt đầu đi "mua sắm" ở lớp model để tiết kiệm chi phí, thì đó là một tín hiệu về bài toán kinh tế nền tảng, chứ không chỉ là chiến lược của một doanh nghiệp. Kỷ nguyên mà các tính năng AI có thể được gói gọn vào một subscription flat và âm thầm được trợ giá chéo có lẽ đang nhường chỗ cho một thứ gì đó được tính phí theo đồng hồ nhiều hơn và ít phụ thuộc model hơn — được định giá như một dịch vụ tiện ích có chi phí biến đổi đúng như bản chất của nó, và được vận hành bởi bất kỳ model nào giúp bài toán đó cộng ra kết quả.

Câu hỏi thú vị cho tất cả những người khác đang xây dựng trong không gian này không phải là liệu những động thái cụ thể này có thành công hay không. Mà là liệu chúng có phải là những dấu mốc sớm về hướng đi của cả pricing lẫn architecture của agentic AI: tính phí theo mức sử dụng ở cửa trước, tối ưu chi phí ở phía sau, và ngày càng thờ ơ với việc model nào đang làm công việc đó, miễn là những con số cộng lại hợp lý.

## Sources
- https://the-decoder.com/microsofts-copilot-cowork-moves-to-usage-based-billing-and-may-tap-deepseek/
