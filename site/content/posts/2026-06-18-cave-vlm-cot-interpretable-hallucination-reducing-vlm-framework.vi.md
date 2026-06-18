---
title: 'Tóm tắt CaVe-VLM-CoT: framework VLM giúp diễn giải được, giảm hallucination'
date: '2026-06-18T17:36:03+07:00'
lang: vi
slug: cave-vlm-cot-interpretable-hallucination-reducing-vlm-framework
categories:
- Research
tags:
- vision-language
- rag
- hallucination
- interpretability
- research
summary: CaVe-VLM-CoT là một agentic-RAG framework dạng module, dựa trên cơ chế reflection,
  giúp giảm hiện tượng hallucination trong các vision-language model bằng cách buộc
  quá trình reasoning phải dựa trên bằng chứng thông qua một vòng lặp khép kín gồm
  năm giai đoạn (Extractor, Retriever, Solver, Citation Injector, Verifier), trong
  đó các phát biểu không có cơ sở sẽ kích hoạt việc re-retrieval có chủ đích. Framework
  này giới thiệu 23 chỉ số đo lường theo từng thành phần, được neo bởi một điểm tổng
  hợp CaVeScore. Hệ thống báo cáo độ chính xác 87,1% trên ScienceQA và 55,2% trên
  MMMU mà không cần chỉnh sửa kiến trúc hay prompt. Việc nhấn mạnh vào tính diễn giải
  (interpretability) và việc neo bằng trích dẫn (citation grounding) đã giải quyết
  một lỗ hổng quan trọng về độ tin cậy trong reasoning đa phương thức (multimodal).
draft: false
---

Here's the improved translation:

---

Vision-language models (VLMs) có một vấn đề về độ tin cậy. Chúng có thể mô tả một biểu đồ, trả lời câu hỏi về một sơ đồ, hoặc reasoning qua một bài toán khoa học với sự tự tin trôi chảy — nhưng vẫn bịa ra các chi tiết hỗ trợ. Đối với multimodal reasoning, nơi một khẳng định lẽ ra phải gắn với thứ gì đó thực sự hiện diện trong hình ảnh hoặc một nguồn được retrieve, khoảng cách giữa sự trôi chảy (fluency) và tính trung thực (faithfulness) chính là rủi ro cốt lõi về độ tin cậy. CaVe-VLM-CoT là một framework được xây dựng riêng để thu hẹp khoảng cách đó.

## Ý tưởng cốt lõi: buộc reasoning phải tự chứng minh bằng evidence

Hầu hết các nỗ lực giảm hallucination trong VLMs đều dựa vào một trong hai đòn bẩy: retrain model hoặc viết lại prompt. CaVe-VLM-CoT không làm cả hai. Đây là một framework **agentic-RAG** dạng module, dựa trên reflection, bao quanh một model có sẵn và áp đặt reasoning được grounding bằng evidence từ bên ngoài — không thay đổi kiến trúc, không can thiệp prompt.

Cơ chế là một closed loop gồm năm giai đoạn. Mỗi giai đoạn có một nhiệm vụ duy nhất, được định nghĩa rõ ràng, và đầu ra của vòng lặp là reasoning trong đó các khẳng định được gắn với evidence được retrieve thay vì được đưa ra dựa trên niềm tin:

- **Extractor** — trích xuất nội dung nổi bật mà câu hỏi thực sự phụ thuộc vào.
- **Retriever** — lấy về evidence hỗ trợ cho nội dung đó.
- **Solver** — reasoning để đi đến câu trả lời bằng cách dùng tài liệu đã retrieve.
- **Citation Injector** — gắn các citation evidence vào các khẳng định trong chuỗi reasoning.
- **Verifier** — kiểm tra xem mỗi khẳng định có thực sự được grounding hay không.

Cụm từ "closed loop" thực sự có ý nghĩa ở đây. Khi Verifier phát hiện một khẳng định không được grounding, nó không chỉ đơn giản đánh dấu rồi bỏ qua — nó kích hoạt **targeted re-retrieval**. Hệ thống quay lại và cố tìm evidence cụ thể cho chính khẳng định đã thất bại trong việc grounding. Reasoning không thể chứng minh được sẽ được đưa lại qua vòng lặp một lần nữa thay vì chuyển thẳng đến người dùng. Đây chính là cơ chế reflection: framework tự phê bình đầu ra của chính nó và tự động hành động dựa trên phê bình đó.

## Vì sao vòng lặp lại quan trọng

Một RAG pipeline tiêu chuẩn retrieve một lần, reasoning một lần, rồi trả lời. Nếu việc retrieval không đầy đủ hoặc model trôi dạt khỏi nguồn của nó giữa chừng quá trình reasoning, không có gì bắt được lỗi đó. Dù thế nào thì kết quả vẫn đọc lên đầy thẩm quyền.

CaVe-VLM-CoT coi grounding là một thuộc tính cần được verify, chứ không phải mặc nhiên giả định. Bằng cách tách citation injection khỏi verification, nó có thể phân biệt giữa một khẳng định *có* citation và một khẳng định *thực sự được hỗ trợ* bởi citation đó. Và bằng cách làm cho re-retrieval có mục tiêu (targeted), nó dồn nỗ lực đúng vào nơi grounding bị đổ vỡ thay vì chạy lại toàn bộ pipeline một cách mù quáng. Kiến trúc này biến việc giảm hallucination thành một quá trình sửa lỗi thay vì một kỳ vọng one-shot.

## Đo lường interpretability, không chỉ accuracy

Một trong những bài toán khó hơn trong lĩnh vực này là evaluation. Accuracy trên một benchmark cho bạn biết liệu câu trả lời cuối cùng có đúng hay không, nhưng không nói gì về *tại sao* nó đúng — hoặc liệu một câu trả lời đúng có dựa trên reasoning bịa đặt hay không. Một model có thể đúng vì những lý do sai, và đó chính là failure mode mà công việc interpretability nhắm tới phơi bày.

CaVe-VLM-CoT giới thiệu **23 component-wise metrics**, được neo bởi một **CaVeScore** tổng hợp. Thiết kế component-wise rất quan trọng: thay vì gộp hiệu năng thành một con số duy nhất, nó cho phép bạn kiểm tra cách mỗi giai đoạn của vòng lặp đóng góp — extraction cô lập đúng nội dung tốt đến đâu, các citation được grounding chặt chẽ ra sao, verification bắt các khẳng định không grounding đáng tin cậy thế nào. Sau đó CaVeScore cuộn những thứ này lại thành một tín hiệu tổng hợp duy nhất để so sánh tổng thể. Đây là một triết lý evaluation nhắm vào đúng khoảng cách độ tin cậy thực sự, chứ không chỉ là bảng xếp hạng (leaderboard).

## Kết quả mà không chạm vào model

Framework báo cáo **87.1% accuracy trên ScienceQA** và **55.2% trên MMMU** — và làm được điều đó **mà không cần chỉnh sửa kiến trúc hay prompt**. Ràng buộc đó mới là điểm nhấn chính, không phải một chú thích nhỏ. Nó có nghĩa là phần cải thiện đến từ lớp orchestration: vòng lặp extract-retrieve-solve-cite-verify cùng cơ chế re-retrieval sửa lỗi của nó, chứ không phải từ một base model được tinh chỉnh tốt hơn hay một prompt được thiết kế khéo léo.

Hệ quả thực tiễn là tính portability. Một framework cải thiện grounding mà không cần retrain hay viết lại prompt thì về nguyên tắc có thể đặt lên trên các base model khác nhau. Phần cải thiện độ tin cậy nằm ở cấu trúc agentic bao quanh, vốn rẻ hơn nhiều để áp dụng so với một lần training mới.

## Vì sao hướng đi này đáng để theo dõi

Điều thú vị nhất về CaVe-VLM-CoT là thứ mà nó tối ưu hóa. Rất nhiều hệ thống chạy theo accuracy thuần túy; ít hệ thống hơn đặt **interpretability và citation grounding** làm mục tiêu thiết kế hạng nhất. Bằng cách khăng khăng rằng các khẳng định phải chỉ ngược về evidence, và bằng cách xây verification cùng re-retrieval trực tiếp vào vòng lặp reasoning, framework coi faithfulness là thứ cần được áp đặt và đo lường thay vì chỉ trông chờ.

Đối với bất kỳ ai triển khai VLMs trong các bối cảnh mà một câu trả lời sai một cách tự tin gây ra cái giá thực sự, sự thay đổi trọng tâm đó — từ "câu trả lời có đúng không?" sang "câu trả lời có được grounding không, và chúng ta có thể trình bày được cơ sở của nó không?" — chính xác là câu hỏi quan trọng về độ tin cậy. CaVe-VLM-CoT là một lập luận cụ thể cho thấy câu trả lời có thể là có ở cả hai phương diện, mà không cần xây dựng lại model bên dưới.

## Sources
- https://arxiv.org/abs/2606.18385
