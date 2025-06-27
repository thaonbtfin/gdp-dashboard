Bạn sẽ có các Sheet cố định sau:

1. Sheet: Input_Data
Bạn nhập dữ liệu gốc vào đây. Bao gồm:

Trường	Ý nghĩa	Ghi chú
Ticker	Mã cổ phiếu	Ví dụ: FPT
Current Price	Giá đóng cửa hiện tại	Ví dụ: 117100
EPS ttm	Lợi nhuận sau thuế / số CP 4 quý gần nhất	Ví dụ: 6350
Book Value	Giá trị sổ sách / CP	Ví dụ: 29800
ROE	Trung bình 5 năm gần nhất (%)	20
Debt/Equity	Tỷ lệ nợ	Ví dụ: 0.4
Free Cash Flow	TTM hoặc 1 năm gần nhất	Tính bằng VND
Market Cap	Tổng vốn hóa thị trường	Tính bằng VND
EPS 3 năm gần nhất	EPS từng năm	2022 = 5000, 2023 = 5900, 2024 = 6350
Giá 5 năm	Giá đóng cửa theo ngày (sheet khác)	Dùng cho MA, MACD, RSI

2. Sheet: Value_Analysis
Công thức:

Chỉ số	Công thức Excel	Diễn giải
P/E	=Input_Data!B2 / Input_Data!B3	Giá / EPS
P/B	=Input_Data!B2 / Input_Data!B4	Giá / Book
ROE Check	=IF(Input_Data!B5>=15,"✔️","❌")	Kiểm tra ROE tốt
Debt/Equity Check	=IF(Input_Data!B6<0.5,"✔️","❌")	Tỷ lệ nợ thấp
FCF Yield	=Input_Data!B7 / Input_Data!B8	FCF / Market Cap
FCF Check	=IF(Value_Analysis!B6>=0.05,"✔️","❌")	Tốt nếu >5%
Intrinsic Value (Graham)	=EPS * (8.5 + 2 * growth%)	Ví dụ: =B3*(8.5 + 2*15)
Buy/Hold/Sell	=IF(Current Price < 70% IV, "BUY", ...)	Dựa theo Margin of Safety

3. Sheet: CANSLIM_Analysis
Công thức:

Chỉ số	Công thức	Ghi chú
EPS Growth YoY	=(EPS_this - EPS_last) / EPS_last	Mỗi năm
3Y CAGR	=POWER(EPS_2024 / EPS_2021, 1/3) - 1	Tăng trưởng trung bình EPS
Check Growth >25%	=IF(CAGR>=0.25, "✔️", "❌")	Theo CANSLIM
RSI, MA, Volume	Lấy từ Sheet Technical_Chart	Tự động tính nếu có dữ liệu giá

4. Sheet: Trendline_Analysis
MA20, MA50, MA200 → Tính bằng =AVERAGE(LAST_20_DAYS)

MACD, RSI: dùng công thức Excel (có thể mình giúp bạn gắn sẵn)

Xác định tín hiệu:

excel
Copy
Edit
=IF(AND(Price > MA20, MACD > Signal), "BUY", "HOLD")
🎯 Kết quả tự động:
Ở Sheet Summary_Report, bạn dùng các công thức IF, LOOKUP, hoặc INDEX/MATCH để tự động hiển thị:

BUY / HOLD / SELL theo từng trường phái

Tóm tắt lý do nếu cần