---
title: 'Hồ sơ hiệu năng trong PyTorch (Phần 2): từ nn.Linear đến một fused MLP'
date: '2026-06-16'
lang: vi
slug: profiling-in-pytorch-part-2-from-nn-linear-to-a-fused-mlp
categories:
- Engineering / Performance
tags:
- pytorch
- profiling
- kernel-fusion
- performance
- tutorial
summary: 'Bản dịch tiếng Việt:


  Phần thứ hai trong loạt bài về profiling PyTorch này hướng dẫn cách tối ưu hóa một
  MLP từ việc xếp chồng các module nn.Linear một cách ngây thơ thành một implementation
  fused duy nhất. Bài viết sử dụng các công cụ profiling của PyTorch để xác định các
  điểm nghẽn hiệu năng và cho thấy cách kernel fusion giảm overhead và cải thiện throughput.
  Đây là một hướng dẫn thực hành, mang tính ứng dụng dành cho những người đang tối
  ưu hóa inference và training của model. Bài viết mang lại giá trị giáo dục vững
  chắc nhưng không có tính thời sự rộng rãi.'
draft: true
---

## MLP được viết theo cách ngây thơ

Đây là phần thứ hai trong loạt bài về profiling code PyTorch. Ở phần đầu, chúng ta đã thiết lập công cụ và học cách đọc một profile; còn ở đây, chúng ta đưa nó vào thực chiến với một bài toán optimization cụ thể. Đối tượng là một multilayer perceptron — một building block hết sức bình thường của deep learning — và hành trình sẽ đi từ một stack `nn.Linear` ngây thơ đến một bản triển khai fused duy nhất. Trên suốt chặng đường đó, profiler làm điều nó giỏi nhất: cho ta biết thời gian thực sự trôi về đâu, thay vì nơi ta tưởng nó trôi về.

## MLP viết theo cách ngây thơ

Hầu hết chúng ta đều viết một MLP theo cách hiển nhiên nhất. Bạn với tay lấy `nn.Linear`, xếp chồng vài lớp với activation xen giữa, rồi gói tất cả vào `nn.Sequential`:

```python
import torch
import torch.nn as nn

mlp = nn.Sequential(
    nn.Linear(in_features, hidden),
    nn.ReLU(),
    nn.Linear(hidden, hidden),
    nn.ReLU(),
    nn.Linear(hidden, out_features),
)
```

Cách này đúng, dễ đọc, và là thứ bạn cần trong hầu hết trường hợp. Nhưng nó cũng để lại phần performance chưa được khai thác, và câu hỏi thú vị là *ở đâu*. Mỗi `nn.Linear` là một module riêng với forward call riêng. Mỗi activation lại là một module nữa. Dưới góc nhìn của PyTorch, chạy MLP này nghĩa là dispatch một chuỗi operation rời rạc, mỗi cái tự chạy phần việc của mình rồi chuyển kết quả trung gian sang cái kế tiếp.

Cấu trúc đó vô hình khi bạn chỉ nhìn vào wall-clock time. Nó trở nên hữu hình ngay khi bạn profile.

## Để profiler tự tìm ra bottleneck

Điểm cốt lõi của một loạt bài về profiling là bạn không đoán. Thay vì lý luận xem cái gì *đáng lẽ* phải chậm, bạn instrument model và để các phép đo lên tiếng. Công cụ profiling của PyTorch cho phép bạn ghi lại một forward pass (hoặc một training step) rồi phân rã runtime theo từng operation: mỗi kernel chạy bao nhiêu lần, mất bao lâu, và chiếm bao nhiêu phần trong tổng thời gian.

Khi bạn profile MLP ngây thơ này, một khuôn mẫu lặp đi lặp lại thường hiện ra. Một phần đáng kể thời gian không dành cho phần toán học thực sự — những phép matrix multiply làm công việc chính — mà cho overhead bao quanh chúng. Mỗi operation riêng lẻ đều mang một chi phí cố định: dispatch lời gọi, launch kernel, đọc và ghi các tensor trung gian. Tính riêng thì mỗi chi phí đều nhỏ. Nhưng cộng dồn qua nhiều operation nhỏ, chúng tích lại, và với một MLP có kích thước layer khiêm tốn, chúng có thể chiếm phần áp đảo.

Đây chính là bài học cốt lõi của profiling với tư cách một kỷ luật. Bottleneck hiếm khi nằm ở nơi trực giác chỉ tới. Bạn phải nhìn vào số liệu.

## Vì sao fusion lại hữu ích

Một khi profile cho thấy overhead — chứ không phải phần số học — mới là yếu tố giới hạn, thì chiến lược optimization sẽ tự nhiên hiện ra. Nếu chi phí phát sinh theo từng operation, hãy giảm số lượng operation. Đó chính xác là điều mà **kernel fusion** làm: nó gộp nhiều operation riêng biệt thành một, để phần việc trước kia cần nhiều lần dispatch và nhiều lượt đi vòng qua memory giờ diễn ra trong một lượt duy nhất.

Một MLP fused áp dụng cùng ý tưởng đó cho cả khối. Thay vì xem mỗi linear projection và mỗi activation như một module tách biệt, bạn biểu đạt phép tính sao cho bộ máy bên dưới có thể thực thi nhiều phần của nó cùng lúc. Phần toán học không đổi — vẫn các projection đó, vẫn các activation đó, vẫn output đó. Cái thay đổi là *hình dạng* của phần việc giao cho phần cứng: ít kernel launch hơn, ít tensor trung gian bị materialize chỉ để rồi bị tiêu thụ ngay lập tức, ít overhead cố định hơn trên mỗi phần tử của phép tính có ích.

Phần thưởng hiện ra theo hai cách. Overhead giảm, đơn giản vì có ít "thuế" theo từng operation phải trả hơn. Và throughput cải thiện, vì phần cứng dành tỉ lệ thời gian lớn hơn cho phép tính thực sự quan trọng, thay vì cho việc ghi sổ giữa các bước.

## Đo lường thành quả

Fusion nghe có vẻ thỏa mãn về mặt lý thuyết, nhưng loạt bài này khăng khăng phải khép kín vòng lặp. Sau khi viết lại MLP ở dạng fused, bạn profile lại trong cùng điều kiện và so sánh. Đây là phần mà các practitioner bỏ qua thì lãnh hậu quả: một optimization chỉ là thật khi phép đo xác nhận điều đó. Profile lại cho bạn biết liệu overhead bạn nhắm tới có thực sự co lại hay không, liệu thời gian có thực sự dịch chuyển về phía các kernel hữu ích hay không, và liệu thay đổi đó có xứng đáng với độ phức tạp mà nó thêm vào hay không.

Phép so sánh trước-và-sau đó chính là toàn bộ phương pháp luận thu nhỏ:

- **Profile** bản triển khai hiện tại và xác định nơi thời gian thực sự được tiêu tốn.
- **Đặt ra một giả thuyết** về nguyên nhân — ở đây là overhead theo từng operation đến từ nhiều kernel nhỏ.
- **Thay đổi** bản triển khai để tấn công đúng nguyên nhân cụ thể đó — ở đây là fusion.
- **Profile lại** để xác nhận thời gian đã dịch chuyển đúng như bạn dự đoán.

## Những điều rút ra cho model của riêng bạn

MLP fused chỉ là một ví dụ thực hành, nhưng những thói quen này có thể tổng quát hóa cho bất kỳ code inference hay training nào mà bạn muốn tăng tốc.

- **Mặc định ưu tiên code rõ ràng, optimize dựa trên bằng chứng.** Stack `nn.Linear` ngây thơ là điểm xuất phát đúng đắn. Hãy với tay tới fusion khi profiler biện minh cho điều đó, chứ không phải trước đó.
- **Phân biệt overhead với computation.** Nhiều chỗ chậm trong thực tế không phải vì làm quá nhiều phép toán, mà vì chia nó thành quá nhiều mảnh nhỏ. Profiling là cách bạn phân biệt được hai điều này.
- **Ít operation hơn nhưng lớn hơn thường thắng thế.** Giảm số lượng kernel riêng biệt — qua fusion hay cách khác — cắt giảm chi phí dispatch và lưu lượng memory, vốn là nơi throughput thường âm thầm bị thất thoát.
- **Luôn đo lại.** Một optimization mà không có một lần profile theo sau chỉ là một phỏng đoán khoác lên vẻ tự tin.

Không điều nào ở đây đòi hỏi công cụ kỳ lạ hay phải viết lại training loop của bạn. Nó chỉ đòi hỏi sự sẵn lòng đo trước, thay đổi sau, và đo lại lần nữa. Hãy lấy chính cái MLP bạn đang có, profile nó, và xem liệu overhead có đang ngốn mất throughput hay không — rồi quyết định, với dữ liệu trong tay, liệu một phiên bản fused có đáng để xây dựng hay không.

## Nguồn
- https://huggingface.co/blog/torch-mlp-fusion
