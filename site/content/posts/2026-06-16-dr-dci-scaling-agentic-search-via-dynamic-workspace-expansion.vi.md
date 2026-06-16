---
title: 'Dr-DCI: mở rộng quy mô tìm kiếm agentic thông qua mở rộng workspace động'
date: '2026-06-16'
lang: vi
slug: dr-dci-scaling-agentic-search-via-dynamic-workspace-expansion
categories:
- AI Research
tags:
- agentic-search
- retrieval
- rag
- benchmarks
- research
summary: Dr-DCI là một framework được điều hướng bởi retriever cho agentic search,
  cho phép một agent tự động kéo các tài liệu liên quan vào một local workspace đang
  phát triển và chạy các thao tác Direct Corpus Interaction có thể thực thi qua shell
  tại đó, thay vì trên toàn bộ corpus. Thiết kế này kết hợp khả năng recall ở cấp
  retriever với độ chính xác theo phong cách DCI trong khi vẫn duy trì khả năng scale
  khi các corpus mở rộng. Nó đạt 71.2% trên BrowseComp-Plus (73.3% với context reset)
  và vẫn hiệu quả từ 100K đến 20M tài liệu, vượt trội hơn DCI thuần, BM25 và các baseline
  search-agent đã được train trong khi giảm số lượng tool call, thời gian và chi phí.
  Những cải thiện về benchmark và các tuyên bố về hiệu suất khiến nó trở thành một
  đóng góp đáng chú ý cho các retrieval-augmented agent, mặc dù các kết quả vẫn chưa
  được kiểm chứng độc lập.
draft: true
---

Search agents có một vấn đề về scaling không tự bộc lộ ra cho đến khi corpus trở nên lớn. Vòng lặp retrieve-then-read hoạt động ổn trên một index đã được tuyển chọn kỹ, nhưng các failure mode thay đổi khi document store phình to từ một collection cỡ demo thành thứ gì đó giống với thế giới thực. Dr-DCI là một đề xuất gần đây đối mặt trực diện với vấn đề scaling này, và ý tưởng cốt lõi của nó đơn giản đến mức gây ngộ nhận: thay vì để agent reason trên toàn bộ corpus, hãy cho nó một workspace nhỏ, luôn biến đổi, và để nó tự quyết định cần đưa gì vào đó.

## Mâu thuẫn mà Dr-DCI đang cố giải quyết

Có hai chiến lược lớn để grounding một agent trong một khối văn bản đồ sộ, và mỗi chiến lược đều có một điểm yếu đặc trưng.

Chiến lược thứ nhất là retrieval. Một retriever — dense, sparse, hay hybrid — giỏi về *recall*. Ném một query vào nó và nó sẽ làm nổi lên các candidate từ khắp toàn bộ corpus. Nhưng retrieval thì thô. Nó đưa cho agent một danh sách đã được rank rồi dừng lại ở đó; mọi thứ phía sau đều phụ thuộc vào việc danh sách đó tốt đến đâu, và agent có rất ít khả năng tự mình thẩm vấn corpus theo cách của riêng nó.

Chiến lược thứ hai là Direct Corpus Interaction (DCI), trong đó agent chạy các thao tác shell-executable trực tiếp lên chính các document. Điều này mang lại *precision*: agent có thể grep, filter, slice và inspect với độ chính xác của một command line thay vì sự mơ hồ của một similarity score. Vấn đề nằm ở scale. Thao tác trực tiếp trên toàn bộ corpus trở nên đắt đỏ và cồng kềnh hơn khi corpus lớn lên, và thứ hoạt động tốt ở một trăm nghìn document chưa chắc sống sót qua một bước nhảy hai bậc độ lớn.

Recall mà không có precision, hoặc precision mà không có scale. Canh bạc của Dr-DCI là bạn không nhất thiết phải chọn một trong hai.

## Retriever-steered, workspace-local

Framework này được mô tả là *retriever-steered*. Retriever không phải là toàn bộ câu chuyện — nó là cơ chế lái. Thay vì trả về một tập kết quả tĩnh, retriever được dùng để kéo các document liên quan vào một workspace cục bộ do agent sở hữu một cách động (dynamically). Workspace đó là đối tượng kiến trúc then chốt. Nó nhỏ so với corpus, nó biến đổi khi task diễn ra, và nó là nơi agent thực sự làm việc.

Bên trong workspace đó, agent chạy các thao tác DCI — chính những tương tác shell-executable làm cho DCI hấp dẫn — nhưng nó chạy chúng trên một lát document có trọng tâm và dễ quản lý thay vì trên tất cả. Retriever cung cấp recall bằng việc quyết định cái gì được đưa vào workspace; DCI cung cấp precision bằng việc cho agent các thao tác chính xác một khi document đã ở đó.

Phần thưởng của sự phân chia này là scalability. Bởi vì các thao tác chính xác, vốn có khả năng đắt đỏ, diễn ra trong một workspace có giới hạn thay vì trên toàn bộ store, chi phí của chúng phần lớn được tách rời khỏi kích thước của corpus. Retriever hấp thụ áp lực scaling; workspace vẫn giữ nhỏ. Đó là lý do mang tính cấu trúc giải thích vì sao cách tiếp cận này được kỳ vọng sẽ trụ vững khi corpus lớn lên.

## Các con số nói gì

Trên BrowseComp-Plus, Dr-DCI báo cáo đạt **71.2%**, tăng lên **73.3%** khi sử dụng context reset. Biến thể context-reset đáng được lưu ý riêng: nó gợi ý rằng việc định kỳ xóa state đã tích lũy — thay vì để context của agent phình to đơn điệu qua một quá trình search dài — không chỉ là một tiện ích quản lý bộ nhớ mà còn là thứ có thể cải thiện kết quả của task. Trong một agentic loop dài, context cũ là một gánh nặng, và một lần reset sạch quanh workspace đang biến đổi dường như có ích.

Tuyên bố thú vị hơn đối với một practitioner là về dải (range). Dr-DCI được báo cáo là vẫn hiệu quả từ **100K đến 20M document** — một khoảng trải rộng 200×. Giữ được performance trên dải đó chính là thuộc tính phân biệt một phương pháp thực sự scale với một phương pháp chỉ hoạt động trên một index cỡ benchmark. Nhiều kỹ thuật xuống cấp âm thầm khi corpus lớn lên; điểm nhấn ở đây là phương pháp này được tuyên bố là không như vậy.

So với các baseline, Dr-DCI được báo cáo là vượt trội hơn:

- **raw DCI** — cách tiếp cận precision-first nhưng không có retriever lái nó,
- **BM25** — baseline sparse-retrieval mạnh mẽ, cạnh tranh dai dẳng,
- **trained search-agent baselines** — các agent được train riêng cho task search.

Và nó làm được điều đó trong khi *giảm số tool call, thời gian và chi phí*. Đây là phần đáng để một builder chú ý. Những cải thiện về accuracy trong các agentic system thường phải đánh đổi bằng nhiều step hơn — nhiều retrieval hơn, nhiều lần gọi tool hơn, nhiều thời gian wall-clock hơn, nhiều chi phí hơn. Một kết quả vừa đẩy accuracy lên *vừa* kéo đường cong chi phí *xuống* cùng lúc là sự kết hợp đáng quan tâm, bởi nó chỉ ra một operating point thực sự tốt hơn chứ không phải một vị trí khác trên cùng một trade-off frontier.

## Vì sao kiến trúc, chứ không chỉ điểm số, mới là đóng góp

Sẽ rất dễ để đọc Dr-DCI như một mục nữa trên bảng leaderboard. Nhưng ý tưởng bền vững hơn nằm ở thiết kế: xem environment của agent như một *dynamic workspace* mà retriever đổ đầy vào, và giới hạn các thao tác chính xác trong workspace đó thay vì trên toàn bộ corpus.

Điều này tái định hình mối quan hệ giữa retrieval và agentic reasoning. Trong pipeline thông thường, retrieval là một bước preprocessing nạp dữ liệu cho agent rồi tránh sang một bên. Ở đây, nó là một tín hiệu lái liên tục, không ngừng định hình những gì agent có thể thấy và tác động lên. Workspace trở thành đơn vị của scaling: giữ nó có giới hạn, và các thao tác chính xác đắt đỏ vẫn rẻ bất kể store nền tảng lớn đến đâu. Đó là một sự phân tách mối quan tâm rõ ràng — recall là việc của retriever, precision là việc của DCI, và scalability nảy ra từ việc giữ chúng tách biệt.

## Mức độ hoài nghi phù hợp

Các kết quả là đáng chú ý, nhưng đồng thời, theo chính cách framework tự định khung, chúng **chưa được kiểm chứng độc lập**. Lưu ý đó quan trọng và nên điều tiết cách đọc các con số. Những cải thiện trên benchmark có thể nhạy cảm với cách thiết lập đánh giá; các tuyên bố về hiệu quả phụ thuộc rất nhiều vào cái gì đang được đếm và đếm ra sao; và một dải scalability 200× chính là loại tuyên bố xứng đáng được tái lập trước khi được coi là đã ngã ngũ. Tóm tắt một cách trung thực thì Dr-DCI trình bày một sự kết hợp thuyết phục giữa accuracy và efficiency, với một kiến trúc mà logic dễ theo dõi — và bước tiếp theo là để những người khác xác nhận nó.

Nếu các kết quả trụ vững, bài học rút ra cho bất kỳ ai đang xây dựng các retrieval-augmented agent là rất cụ thể: corpus không phải là workspace. Hãy để một retriever lái một environment cục bộ nhỏ, luôn biến đổi, chạy các thao tác chính xác của bạn ở đó, và bạn có thể đạt được recall, precision và scale cùng một lúc — với chi phí thấp hơn cái loop bạn đang chạy hôm nay.

## Sources
- https://arxiv.org/abs/2606.14885
