# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có | dùng có điều kiện |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không | loại khỏi gate |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Người | “em… nha” và “anh check giúp em” quá suồng sã trong hỗ trợ khách hàng; judge bỏ sót cách xưng hô. |
| 2 | H-017 | PASS | FAIL | Người | Gọi khách là “bạn” không phù hợp ngữ cảnh/tuổi tác; bổ sung tiêu chí xưng hô phù hợp, không đồng nhất thân thiện với chuyên nghiệp. |
| 3 | H-029 | PASS | FAIL | Người | “không cần nhắn thêm” là câu ra lệnh/gạt khách đi dù mở đầu có “Dạ, vui lòng”; rubric phải xét toàn câu và thái độ, không chỉ từ khóa lịch sự. |
| 4 | H-042 | FAIL | PASS | Judge | Câu trả lời ngắn vẫn xác nhận hoàn tiền và thời gian nhận tiền; không bắt buộc lời xin lỗi theo mẫu khi không có sai sót hay bất tiện cần xin lỗi. |
| 5 | H-051 | FAIL | PASS | Judge | “refund” là từ CS được phép; thêm vào glossary chấp nhận và không phạt riêng việc dùng thuật ngữ tiếng Anh được duyệt. |

## Kết luận
- `tone_ok` đạt cả ba floor (κ=0.757, P=0.857, R=0.800), phù hợp dùng hỗ trợ kiểm tra tone trên dữ liệu tương tự, không thay thế đánh giá người.
- Loại `helpful` khỏi gate: ma trận `{tp: 9, fp: 0, fn: 21, tn: 70}` cho thấy precision 1.000 nhưng recall chỉ 0.300 và κ=0.375. Judge bỏ sót 21/30 câu người gắn FAIL, chủ yếu là trả sai số tiền nhưng vẫn viết lịch sự; precision cao không bù được âm tính giả nghiêm trọng. Tỷ lệ FAIL quan sát được 0.09 được Rogan–Gladen hiệu chỉnh thành 0.30.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
