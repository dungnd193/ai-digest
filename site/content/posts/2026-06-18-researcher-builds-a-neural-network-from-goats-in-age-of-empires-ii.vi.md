---
title: 'Bản dịch tiếng Việt:


  Nhà nghiên cứu xây dựng một neural network từ những con dê trong Age of Empires
  II'
date: '2026-06-18T17:36:04+07:00'
lang: vi
slug: researcher-builds-a-neural-network-from-goats-in-age-of-empires-ii
categories:
- Commentary & Critique
tags:
- critique
- anthropomorphism
- methodology
- microsoft
- neural-networks
summary: Một nhà nghiên cứu của Microsoft đã xây dựng một neural network hoạt động
  được bằng cách sử dụng dê, cầu và đường dốc băng trong trình chỉnh sửa bản đồ của
  Age of Empires II như một lời phê phán sắc bén về phương pháp luận nghiên cứu AI.
  Ông lập luận rằng hơn một nửa trong số 315 bài báo mà ông phân tích đã mặc định
  rằng các language model sở hữu những đặc điểm giống con người trước khi bất kỳ thí
  nghiệm nào bắt đầu. Phần trình diễn dựa trên đàn dê cho thấy phần toán học nền tảng
  hoàn toàn giống với một LLM, nhưng khi loại bỏ giao diện chat thì ảo giác về việc
  đang trò chuyện với một bộ óc cũng biến mất. Đây là một sự khiêu khích đáng nhớ
  về vấn đề nhân cách hóa (anthropomorphism) và tính nghiêm ngặt trong khoa học AI.
draft: false
---

## Khi Toán Học Bước Đi Trên Bốn Chân

Một neural network không cần đến silicon. Nó không cần GPU, không cần tensor library, thậm chí không cần điện theo nghĩa thông thường. Thứ nó cần là một substrate có khả năng lưu giữ state, lan truyền tín hiệu, và kết hợp các tín hiệu đó theo những weights nhất định. Một nhà nghiên cứu của Microsoft đã chứng minh điều này theo cách hiển nhiên đến mức khó tin: ông đã xây dựng một neural network chạy được bên trong trình chỉnh sửa bản đồ của *Age of Empires II*, dùng dê, cầu, và dốc băng làm các bộ phận chuyển động.

Đây không phải một màn trình diễn chỉ để gây chú ý. Nó là một luận điểm — một sự phê phán sắc bén nhắm vào cách nghiên cứu AI đang được thực hiện — được diễn đạt qua một đàn gia súc.

### Cấu trúc của cỗ máy

Các thành phần là những vật thể game thông thường được tái sử dụng làm các đơn vị tính toán nguyên thủy. Dê đóng vai trò những tín hiệu di chuyển xuyên qua hệ thống. Cầu và dốc băng định tuyến và dẫn các tín hiệu đó theo những đường đi đã định sẵn. Sắp đặt đủ nhiều thành phần theo đúng cấu trúc, và bạn có được chính dòng chảy của các weighted activations vốn định nghĩa nên mọi neural network.

Luận điểm cốt lõi nói về sự đồng nhất, chứ không phải sự tương tự. Phần toán học nền tảng của cỗ máy dê là *giống hệt* phần toán học bên trong một large language model. Không có thứ gia vị bí mật nào phân biệt phiên bản silicon với phiên bản dê ở cấp độ tính toán. Nhân, cộng, threshold, lan truyền. Những con dê làm chính xác những gì các số floating-point làm.

### Điều gì biến mất khi khung chat biến mất

Đây chính là điểm khiêu khích. Khi bạn lột bỏ giao diện chat của một language model — con trỏ nhấp nháy, sự luân phiên đối thoại, những phản hồi ở ngôi thứ nhất — một thứ gì đó cũng bốc hơi theo. Ảo giác rằng bạn đang trò chuyện với một *tâm trí* biến mất.

Hãy nhìn những con dê lạch bạch băng qua dốc băng, và chẳng ai bị cám dỗ để hỏi liệu lũ dê có hiểu bạn không, liệu chúng có ý định gì không, hay liệu chúng có đang reasoning về câu hỏi của bạn không. Vậy mà phần tính toán lại giống hệt với hệ thống mà, khi khoác lên một chat UI, sẵn sàng mời gọi cả ba giả định đó. Giao diện đang đảm nhận một công việc thuyết phục khổng lồ mà bản thân phần toán học chưa bao giờ đòi hỏi.

Đây là trọng tâm của màn trình diễn. Anthropomorphism không phải là một thuộc tính của model. Nó là một thuộc tính của cách model được *trình bày* cho chúng ta, và của những định kiến (priors) mà chúng ta mang theo khi tiếp xúc.

### Cáo buộc về mặt phương pháp luận

Cỗ máy dê là bề mặt dễ nhớ của một luận điểm sâu sắc hơn về tính chặt chẽ khoa học. Nhà nghiên cứu đã phân tích 315 bài báo và phát hiện rằng hơn một nửa trong số đó mặc định language model sở hữu những đặc tính giống con người — trước khi bất kỳ thí nghiệm nào được tiến hành.

Hãy nghĩ xem điều đó có ý nghĩa gì đối với cả một khối nghiên cứu. Nếu một nghiên cứu khởi đầu bằng việc giả định rằng hệ thống "biết", "tin", "muốn", hay "reasons" theo nghĩa của con người, thì thiết kế thí nghiệm, các metrics, và việc diễn giải kết quả đều thừa hưởng giả định đó. Kết luận đã được nhào nặn sẵn ngay trong tiền đề. Bạn không còn đang kiểm tra liệu đặc tính đó có tồn tại hay không; bạn đang đo lường một thực thể mà bạn đã quyết định trước rằng nó giống như có tâm trí. Đó không phải một phát hiện. Đó là một cách đóng khung được lén đưa vào dưới lốt một phát hiện.

Những con dê là liều thuốc giải cho cách đóng khung đó. Chúng kéo câu hỏi trở về hình thức trung thực của nó: *cái gì đang thực sự được tính toán, và chúng ta được quyền tuyên bố điều gì về nó?* Khi câu trả lời là "dê băng qua cầu", thì sự cám dỗ thuật lại hệ thống như một tác nhân biết tư duy lập tức sụp đổ khi va vào thực tế.

### Vì sao sự khiêu khích này có sức nặng

Có một truyền thống lâu đời về việc xây dựng máy tính từ những substrate phi lý — bi ve, nước, quân domino, cellular automata — nhằm chứng minh rằng computation là độc lập với substrate. Màn trình diễn này thừa kế dòng dõi đó nhưng nhắm tới một điểm sắc bén hơn. Nó không chỉ đơn thuần nói "nhìn này, bất cứ thứ gì cũng có thể tính toán." Nó đang nói "hãy nhìn xem bạn dễ dàng gán một tâm trí cho substrate này mà không gán cho substrate kia đến mức nào, dù phép tính toán là như nhau."

Sự bất đối xứng trong trực giác của chúng ta chính là cái bug mà nhà nghiên cứu đang chỉ ra. Giao diện chat là một thiết bị nạp định kiến (prior-loading) đầy sức mạnh. Nó mồi cho chúng ta đối xử với các outputs như những lời phát ngôn, lời phát ngôn như những niềm tin, và niềm tin như bằng chứng về một đời sống nội tâm. Không điều nào trong số đó được phần toán học cho phép. Lũ dê chứng minh điều này, bởi lũ dê làm phần toán học mà chẳng cho phép điều nào trong số đó cả.

### Bài học cho những người xây dựng và nghiên cứu các hệ thống này

Kỷ luật được đòi hỏi ở đây dễ phát biểu nhưng khó thực hành: đừng giả định sẵn kết luận ngay trong khâu thiết lập. Nếu bạn đang nghiên cứu liệu một model có "reasons", "deceives", hay "understands" hay không, thí nghiệm của bạn phải có khả năng phân biệt những đặc tính đó với việc pattern completion tinh vi mà chỉ *trông giống* như chúng qua lăng kính đối thoại. Một giả định được đưa ra trước phép đo đầu tiên không phải là sự chặt chẽ; nó là sự vắng mặt của chặt chẽ.

Lũ dê thật buồn cười. Đó chính là điều khiến chúng đọng lại trong trí nhớ. Nhưng luận điểm bên dưới lại là một nguyên tắc vệ sinh khoa học nghiêm túc: hãy giữ giao diện và phần tính toán ở hai cột tư duy riêng biệt, và hãy hoài nghi bất kỳ tuyên bố nào về tâm trí của một model mà sẽ bốc hơi ngay khoảnh khắc bạn thay khung chat bằng một đàn thú đi băng qua băng.

Phần toán học là như nhau trong cả hai trường hợp. Chỉ có một phiên bản là biết tâng bốc bản năng của chúng ta khi muốn nhìn thấy một con người ở đầu bên kia.

## Sources
- https://the-decoder.com/microsoft-researcher-builds-a-working-neural-network-out-of-goats-in-age-of-empires-ii-to-critique-ai-science/
