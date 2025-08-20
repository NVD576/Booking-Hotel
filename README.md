## Booking-Hotel

Ứng dụng web quản lý đặt phòng khách sạn (đặt phòng, thuê phòng, hóa đơn, lịch sử, thống kê). Dự án được xây dựng bằng Flask, SQLAlchemy, Flask-Login, Authlib và sử dụng MySQL làm cơ sở dữ liệu.

### Tính năng chính
- **Đặt phòng**: Chọn loại phòng (Standard/Deluxe/VIP), kiểm tra phòng trống theo khoảng ngày, hỗ trợ nhiều khách/phiếu.
- **Tính phí**: Tự động tính phụ phí khách thêm, hệ số khách nước ngoài theo quy định trong `data/rules.json`.
- **Tài khoản**: Đăng ký/đăng nhập, đổi mật khẩu, quên mật khẩu (mã OTP hiển thị trên giao diện), đăng xuất.
- **Đăng nhập xã hội**: Google, Facebook (qua Authlib) — cần cấu hình khóa ứng dụng.
- **Quản trị**: Trang quản trị, thống kê doanh thu theo phòng và tần suất sử dụng theo tháng (DAO đã có hàm).
- **Quản lý dữ liệu**: Cloudinary để lưu ảnh đại diện khách hàng khi đăng ký.

### Công nghệ
- **Backend**: Flask, Flask-Login, Flask-SQLAlchemy
- **DB**: MySQL (PyMySQL driver)
- **OAuth**: Authlib (Google/Facebook)
- **Media**: Cloudinary
- **Template**: Jinja2, Bootstrap (qua template có sẵn)

### Cấu trúc thư mục
```
Booking-Hotel/
  └─ TTDHotel/
     ├─ requirements.txt
     └─ TTDHotel/
        ├─ __init__.py        # Khởi tạo app Flask, cấu hình DB, OAuth, Cloudinary, quy định
        ├─ index.py           # Định nghĩa routes chính, entrypoint ứng dụng
        ├─ models.py          # Khai báo SQLAlchemy models + seed dữ liệu (khi chạy như module)
        ├─ dao.py             # Lớp truy cập dữ liệu và logic liên quan
        ├─ utils.py           # Tiện ích (hash_password, ...)
        ├─ data/
        │  ├─ rules.json      # Quy định: số khách, phụ phí, hệ số
        │  ├─ contacts.json   # Thông tin liên hệ hiển thị ở trang contacts
        │  └─ categories.json # (Không bắt buộc) dữ liệu mẫu loại phòng
        ├─ templates/         # Giao diện Jinja2 (user + admin)
        └─ static/            # CSS/JS/Images
```

### Yêu cầu hệ thống
- Python 3.10+ (khuyến nghị 3.11)
- MySQL 8.x
- Pip, venv

### Cài đặt (Windows)
1) Tạo môi trường ảo và cài dependencies
```bash
cd TTDHotel
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Tạo cơ sở dữ liệu MySQL và cấu hình kết nối
- Tạo database:
```sql
CREATE DATABASE hoteldb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
- Cập nhật chuỗi kết nối trong `TTDHotel/TTDHotel/__init__.py` nếu cần:
```
mysql+pymysql://<USER>:<PASSWORD>@<HOST>/hoteldb?charset=utf8mb4
```
  Mặc định dự án đang dùng `root` và password mẫu. Hãy đổi sang tài khoản/ mật khẩu của bạn.

3) Cấu hình Cloudinary (tùy chọn nhưng nên bật nếu dùng upload ảnh)
- Mở `TTDHotel/TTDHotel/__init__.py` và thay `cloud_name`, `api_key`, `api_secret` bằng thông tin của bạn.

4) Cấu hình OAuth Google/Facebook (tùy chọn)
- Trong `TTDHotel/TTDHotel/__init__.py`, điền `client_id`, `client_secret` (đang comment). Đăng ký ứng dụng và cấu hình redirect URL khớp với các route `/authorize` (Google) và `/authorize_facebook` (Facebook).

### Khởi tạo dữ liệu mẫu (seed)
Chạy lệnh sau từ thư mục gốc repository để tạo bảng và seed dữ liệu mẫu:
```bash
# Từ thư mục Booking-Hotel
set PYTHONPATH=%CD%
python -m TTDHotel.TTDHotel.models
```
Lệnh trên sẽ: tạo bảng, thêm các bản ghi danh mục, phòng, tài khoản mẫu, v.v.

### Chạy ứng dụng
Do cách tổ chức import, nên chạy theo cách dưới đây để tránh lỗi import:
```bash
# Từ thư mục Booking-Hotel
cd TTDHotel\TTDHotel
set PYTHONPATH=%CD%\..    
python index.py
```
Ứng dụng mặc định chạy tại: `http://localhost:5000`

Nếu bạn muốn chạy bằng module:
```bash
# Từ thư mục Booking-Hotel
set PYTHONPATH=%CD%
python -m TTDHotel.TTDHotel.index
```
Lưu ý: nếu gặp lỗi import `utils`, hãy dùng cách chạy đầu tiên.

### Tài khoản mẫu
- Admin: `admin` / `123`
- Nhân viên: `nhanvien1` / `123`, `nhanvien2` / `123`
- Khách hàng: `khachhang1` / `123`, `khachhang2` / `123`

### Các route chính (tham khảo)
- Trang chủ: `/`
- Đặt phòng: `/booking` (lọc theo loại phòng: `/filter_category` - POST)
- Chi tiết loại phòng: `/category/<id>`
- Lưu phiếu đặt: `/booked` (POST)
- Lập phiếu thuê + hóa đơn: `/rents` (GET/POST), `/save_export` (POST)
- Lịch sử đặt/thuê: `/history`
- Quy định/ liên hệ: `/rules`, `/contacts`
- Tài khoản: `/register`, `/login`, `/logout`, `/changePassword`, `/forgot_pass`, `/forgot_password`, `/verify_code`, `/change_password`
- OAuth: `/login_google`, `/authorize`, `/login_facebook`, `/authorize_facebook`
- Liệt kê toàn bộ routes: `/routes`

### Ghi chú và lưu ý
- Mã mẫu để học tập: một số thông tin nhạy cảm đang được viết cứng trong mã (`__init__.py`). Khi triển khai thực tế, hãy đưa các khóa/DSN vào biến môi trường và nạp qua `python-dotenv`.
- Các thống kê (doanh thu, tần suất) đã có sẵn trong `dao.py` (`doanh_thu_theo_thang`, `tan_suat_theo_thang`).
- Nếu gặp lỗi import `admin` khi chạy, cần đảm bảo biến môi trường `PYTHONPATH` trỏ tới thư mục gốc repo (để Python nhìn thấy gói `TTDHotel`).
- Khi thay đổi `rules.json`, ứng dụng sẽ đọc lại để áp dụng phụ phí/giới hạn khách tương ứng.

### Bản quyền
Chưa chỉ định giấy phép. Hãy thêm giấy phép (ví dụ MIT) nếu bạn dự định phát hành công khai.
