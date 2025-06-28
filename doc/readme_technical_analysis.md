# Phân tích Kỹ thuật - Technical Analysis

## Tổng quan

Tab "Phân tích kỹ thuật" đã được nâng cấp để cung cấp giao diện phân tích chuyên sâu tương tự như trang CafeF, bao gồm:

## Tính năng chính

### 1. Biểu đồ Tương tác
- **Nến Nhật (Candlestick)**: Hiển thị giá mở, đóng, cao, thấp
- **Đường giá**: Biểu đồ đường đơn giản
- **Cột**: Biểu đồ cột thể hiện biến động

### 2. Chỉ báo Kỹ thuật

#### Đường Trung bình (Moving Averages)
- MA5, MA10, MA20, MA50, MA100, MA200
- EMA12, EMA26 cho tính toán MACD

#### Dao động (Oscillators)
- **RSI (14)**: Chỉ số sức mạnh tương đối
- **Stochastic %K, %D**: Dao động ngẫu nhiên
- **Williams %R**: Chỉ báo Williams
- **CCI (20)**: Chỉ số kênh hàng hóa

#### Momentum
- **MACD (12,26,9)**: Hội tụ phân kỳ đường trung bình
- **MACD Signal**: Đường tín hiệu
- **MACD Histogram**: Biểu đồ cột MACD

#### Volatility
- **Bollinger Bands**: Dải Bollinger (20, 2)
- **Độ biến động**: Tính toán dựa trên độ lệch chuẩn

### 3. Phân tích Tín hiệu

#### Tín hiệu Mua (BUY)
- Giá > Đường trung bình
- RSI < 30 (quá bán)
- MACD > Signal
- Giá gần dải Bollinger dưới

#### Tín hiệu Bán (SELL)
- Giá < Đường trung bình
- RSI > 70 (quá mua)
- MACD < Signal
- Giá gần dải Bollinger trên

#### Tín hiệu Trung tính (NEUTRAL)
- Các chỉ báo ở vùng trung gian
- Không có xu hướng rõ ràng

### 4. Thông tin Kỹ thuật Chi tiết

- **Hỗ trợ gần nhất**: Mức giá hỗ trợ trong 20 phiên
- **Kháng cự gần nhất**: Mức giá kháng cự trong 20 phiên
- **Xu hướng**: Đánh giá dựa trên sắp xếp đường trung bình
- **Độ biến động**: Phân loại từ Thấp đến Rất cao

### 5. Khuyến nghị Tổng thể

Hệ thống tự động tính toán khuyến nghị dựa trên:
- Số lượng tín hiệu mua vs bán
- Độ tin cậy của các tín hiệu
- Trạng thái thị trường tổng thể

## Cách sử dụng

### 1. Chọn mã chứng khoán
- Sử dụng dropdown để chọn mã cần phân tích
- Mặc định hiển thị VNINDEX nếu có

### 2. Chọn khoảng thời gian
- 1 tháng, 3 tháng, 6 tháng, 1 năm, hoặc Tất cả
- Mặc định: 6 tháng

### 3. Chọn loại biểu đồ
- Nến Nhật: Phù hợp cho phân tích chi tiết
- Đường giá: Dễ nhìn xu hướng tổng thể
- Cột: Thể hiện khối lượng và biến động

### 4. Đọc hiểu kết quả

#### Bảng chỉ báo
- **Xanh (🟢)**: Tín hiệu MUA
- **Đỏ (🔴)**: Tín hiệu BÁN  
- **Vàng (🟡)**: Tín hiệu TRUNG TÍNH

#### Khuyến nghị
- **MUA**: Nhiều tín hiệu tích cực
- **BÁN**: Nhiều tín hiệu tiêu cực
- **TRUNG TÍNH**: Tín hiệu trái chiều

## Lưu ý quan trọng

### 1. Giới hạn dữ liệu
- Cần ít nhất 20 điểm dữ liệu để tính toán
- Một số chỉ báo cần nhiều dữ liệu hơn (MA200 cần 200 điểm)

### 2. Tính chất tham khảo
- Đây chỉ là công cụ hỗ trợ phân tích
- Không thay thế cho nghiên cứu cơ bản
- Cần kết hợp với các yếu tố khác

### 3. Rủi ro
- Chỉ báo kỹ thuật có thể cho tín hiệu sai
- Thị trường có thể biến động bất thường
- Luôn quản lý rủi ro khi đầu tư

## Công nghệ sử dụng

- **Streamlit**: Giao diện web
- **Plotly**: Biểu đồ tương tác
- **Pandas**: Xử lý dữ liệu
- **NumPy**: Tính toán toán học
- **CSS**: Styling giao diện

## Cập nhật và Cải tiến

### Phiên bản hiện tại
- Giao diện tương tự CafeF
- 15+ chỉ báo kỹ thuật
- Tự động khuyến nghị
- Responsive design

### Kế hoạch phát triển
- Thêm chỉ báo Volume
- Tích hợp dữ liệu thời gian thực
- Cảnh báo tín hiệu
- Lưu và chia sẻ phân tích

## Hỗ trợ

Nếu gặp vấn đề hoặc có góp ý, vui lòng:
1. Kiểm tra dữ liệu đầu vào
2. Đảm bảo có đủ điểm dữ liệu
3. Thử refresh trang nếu biểu đồ không hiển thị
4. Liên hệ team phát triển nếu cần hỗ trợ