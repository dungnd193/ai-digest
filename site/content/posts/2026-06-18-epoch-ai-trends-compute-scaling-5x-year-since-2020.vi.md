---
title: 'Epoch AI trends: compute scaling ~5x/năm kể từ 2020'
date: '2026-06-18T17:36:06+07:00'
lang: vi
slug: epoch-ai-trends-compute-scaling-5x-year-since-2020
categories:
- Research
tags:
- epoch-ai
- compute
- scaling
- trends
- data
summary: Trends in Artificial Intelligence của Epoch AI theo dõi các chỉ số scaling
  tiên tiến, cho thấy training compute tăng khoảng 5 lần mỗi năm kể từ năm 2020 và
  tổng lượng AI chip tăng 3,4 lần mỗi năm. Hiệu quả pre-training compute cải thiện
  khoảng 3,0 lần mỗi năm trong khi hiệu năng chip trên mỗi đô la tăng 37% mỗi năm,
  và các data center tiên tiến hiện có quy mô khoảng 500k–1,1 triệu H100-equivalents.
  Những con số này cung cấp một cơ sở định lượng nghiêm ngặt để hiểu nhịp độ và yếu
  tố kinh tế của AI scaling. Dữ liệu này được trích dẫn rộng rãi trong các thảo luận
  về chiến lược và chính sách liên quan đến quỹ đạo của compute.
draft: false
---

## Những Con Số Đằng Sau Câu Chuyện Scaling

Trong nhiều năm, "AI đang scaling rất nhanh" là kiểu nhận định ai cũng nhắc đến nhưng không ai định lượng được. Báo cáo *Trends in Artificial Intelligence* của Epoch AI ra đời để khắc phục điều đó. Nó theo dõi những frontier metric thực sự dẫn dắt lĩnh vực này — bao nhiêu compute được đổ vào training, có bao nhiêu chip tồn tại để chạy chúng, và cả hai đang cải thiện hiệu quả đến đâu — rồi biến những phát biểu chung chung thành các tốc độ mà bạn có thể lập luận trên đó.

Con số nổi bật cũng là con số đáng ghi nhớ trước tiên: kể từ năm 2020, lượng compute dùng để train các frontier model đã tăng khoảng **5x mỗi năm**. Đây không phải một cú nhảy vọt nhất thời, mà là một xu hướng bền vững, tích lũy qua từng năm, và nó định hình lại cách bạn nên nghĩ về gần như mọi thứ phía sau.

## 5x Mỗi Năm Thực Sự Có Nghĩa Là Gì

Sự tích lũy theo cấp số nhân (compounding) rất dễ bị đánh giá thấp. Tốc độ tăng trưởng 5x mỗi năm không chỉ có nghĩa là "model lớn hơn". Qua vài năm, nó đồng nghĩa với những lần training vượt trội so với các thế hệ trước tới nhiều bậc độ lớn. Mỗi thế hệ frontier model không phải là một bước tiến nhỏ so với thế hệ trước — nó được xây trên một ngân sách compute lớn gấp nhiều lần.

Đây là lăng kính quan trọng nhất để đọc hiểu frontier AI. Khi một model mới xuất hiện với những năng lực trông như đột biến, đường cong compute thường là lời giải thích thầm lặng. Con số 5x cho bạn một kỳ vọng cơ sở: nếu không có mức tăng trưởng đó, bạn sẽ bất ngờ trước một bước nhảy; nhưng có nó, bước nhảy ấy gần như đúng những gì xu hướng dự đoán.

Nó cũng đặt ra một bài toán hóc búa cho bất kỳ ai dự báo về lĩnh vực này. Một tốc độ dốc như vậy không thể tiếp tục mãi mà không đụng phải những bức tường vật lý và kinh tế — điện năng, vốn, nguồn cung chip. Biết được tốc độ là bước đầu tiên để lập luận về thời điểm và cách thức nó sẽ uốn cong.

## Các Yếu Tố Đầu Vào: Chip và Hiệu Quả

Training compute là đầu ra. Dữ liệu của Epoch cũng theo dõi các yếu tố đầu vào tạo ra nó, và chúng kể một câu chuyện nhiều sắc thái hơn.

- **Tổng lượng chip AI đang tăng khoảng 3.4x mỗi năm.** Đây là năng lực công nghiệp thô của lĩnh vực này — lượng accelerator đã được lắp đặt và sẵn sàng làm việc. Lưu ý rằng nó tăng chậm hơn so với chính training compute, điều này hàm ý rằng các lần training frontier đang chiếm một phần ngày càng lớn của compute khả dụng, tập trung hóa nó thay vì chỉ đơn thuần ăn theo đà tăng trưởng phần cứng tổng thể.

- **Hiệu quả pre-training compute đang cải thiện khoảng 3.0x mỗi năm.** Đây là khía cạnh thuật toán: đạt được cùng một năng lực với ít compute hơn nhờ các phương pháp, architecture và công thức training tốt hơn. Nó cho thấy một phần đáng kể của tiến bộ không đến từ việc chi nhiều hơn, mà từ việc chi thông minh hơn.

- **Hiệu năng chip trên mỗi đô la đang tăng khoảng 37% mỗi năm.** Đây là cơn gió thuận về mặt kinh tế. Phần cứng không chỉ nhanh hơn; nó còn rẻ hơn trên mỗi đơn vị công việc hữu ích, điều này dần dần hạ thấp mức sàn chi phí cho bất kỳ lần training nào.

Ghép những điều này lại với nhau, bạn sẽ thấy vì sao frontier dịch chuyển nhanh đến vậy. Những lần training lớn hơn được tiếp sức đồng thời bởi nhiều chip hơn, thuật toán tốt hơn, và compute rẻ hơn. Mức tăng trưởng 5x của training compute là tích của nhiều đường cong compounding cùng kéo về một hướng — chứ không phải một đòn bẩy đơn lẻ.

## Frontier Vật Lý: Data Center Tính Theo H100-Equivalent

Những tốc độ tăng trưởng trừu tượng rốt cuộc sẽ trở thành hạ tầng cụ thể. Dữ liệu của Epoch đặt frontier data center ở mức khoảng **500k đến 1.1M H100-equivalent**.

Biểu thị năng lực theo H100-equivalent là một cách chuẩn hóa hữu ích: nó cho phép bạn so sánh các cơ sở thuộc những thế hệ phần cứng khác nhau trên cùng một đơn vị. Và chính độ lớn mới là điểm mấu chốt. Chúng ta đang nói về những cluster có quy mô đo bằng hàng trăm nghìn đến hơn một triệu accelerator hàng đầu — một quy mô kéo theo những hệ quả trực tiếp về tiêu thụ điện năng, chi phí vốn đầu tư, và việc bố trí vật lý của compute.

Đây là nơi bài toán kinh tế thôi không còn là một biểu đồ mà bắt đầu trở thành những tòa nhà, trạm biến áp và chuỗi cung ứng. Bản thân khoảng dao động — trải rộng khoảng gấp đôi — cũng cho thấy "frontier" không phải là một điểm đơn lẻ, mà là một dải các bên có nguồn lực tương đương nhau.

## Vì Sao Một Đường Cơ Sở Nghiêm Ngặt Lại Quan Trọng

Giá trị trong công trình của Epoch không nằm ở bất kỳ con số đơn lẻ nào — mà ở chỗ các con số được đo lường chứ không phải được khẳng định suông. Sự khác biệt đó cực kỳ quan trọng ngay khi những con số này rời khỏi giới nghiên cứu.

Những xu hướng này giờ đây được trích dẫn rộng rãi trong các cuộc thảo luận về chiến lược và chính sách liên quan đến hướng đi của compute. Khi nảy sinh các câu hỏi về kiểm soát xuất khẩu, nhu cầu năng lượng, động lực cạnh tranh, hay tính khả thi của các năng lực tương lai, cuộc trò chuyện ngày càng dựa vào những đường cơ sở định lượng như thế này. Một bộ tốc độ tăng trưởng chung và nghiêm ngặt cho phép mọi người tranh luận về các hệ quả, thay vì tranh cãi về chính các dữ kiện.

Đối với những người thực hành, bài học rút ra là hãy xem các tốc độ này như một mô hình làm việc. Nếu bạn đang lập kế hoạch hạ tầng, đánh giá năng lực có thể đạt tới đâu trong vài năm tới, hay kiểm thử áp lực cho một dự báo, hãy bắt đầu từ các xu hướng đã được đo lường:

- Training compute: ~5x/năm
- Lượng chip AI: ~3.4x/năm
- Hiệu quả pre-training: ~3.0x/năm
- Hiệu năng trên mỗi đô la: +37%/năm
- Quy mô cluster frontier: ~500k–1.1M H100-equivalent

Không điều nào trong số này đảm bảo cho tương lai — mọi đường cong compounding rồi cũng sẽ gặp một ràng buộc. Nhưng bắt đầu từ những con số có cơ sở vẫn tốt hơn là bắt đầu từ trực giác. Đó mới là đóng góp thực sự ở đây: không phải một lời tiên đoán, mà là một đường cơ sở đã được đo lường, làm nền tảng để đưa ra những dự đoán trung thực.

## Sources
- https://epoch.ai/trends
