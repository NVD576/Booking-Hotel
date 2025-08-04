from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Numeric, Text
from sqlalchemy.orm import relationship, backref

from TTDHotel.TTDHotel import app, db

# import  dao
from TTDHotel.TTDHotel.utils import hash_password



class RoomStatus(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    room = relationship('Room', backref=backref('status', lazy=True))
    def __str__(self):
        return self.name

class CustomerType(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    customer = relationship('Customer', backref=backref('customer_type', lazy=True))
    def __str__(self):
        return self.name


class StatusAccount(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    account = relationship('Account', backref=backref('status_account', lazy=True))
    def __str__(self):
        return self.name


class Role(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    account = relationship('Account', backref=backref('account_role', lazy=True))
    def __str__(self):
        return self.name

class Category(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, default=0)
    image = Column(String(300), default="https://example.com/product_default.jpg")

    def __str__(self):
        return self.name

class Employee(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    cmnd = Column(String(20), unique=True, nullable=True)
    address = Column(String(255))
    account_id = Column(Integer, ForeignKey('account.id'), nullable = True)
    room_rented = relationship('RoomRented', backref=backref('employee', lazy=True))
    def __str__(self):
        return self.name

class Customer(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    cmnd = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(20),  nullable=True)
    customer_type_id = Column(Integer, ForeignKey('customer_type.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('account.id'), nullable=True)
    avatar = Column(String(200), default="https://hoanghaihotel.vn/Data/images/tintuc/10032021170917-gioi-thieu-ve-khach-san-hoang-hai.jpg")
    room_booked = relationship('RoomBooked', backref=backref('customer', lazy=True))
    booking_detail = relationship('BookingDetail', backref=backref('customer', lazy=True))
    renting_detail = relationship('RentingDetail', backref=backref('customer', lazy=True))

    def __str__(self):
        return self.name

class Room(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    status_room = Column(Integer, ForeignKey('room_status.id'), nullable=False)
    room_type_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    booking_detail = relationship('BookingDetail', backref=backref('room', lazy=True))
    renting_detail = relationship('RentingDetail', backref=backref('room', lazy=True))

    def __str__(self):
        return self.name

class RoomBooked(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    booking_date = Column(Date, nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    booking_detail = relationship('BookingDetail', backref=backref('room_booked', lazy=True))
    renting_detail = relationship('RoomRented', backref=backref('room_rented', lazy=True))

class BookingDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_booked_id = Column(Integer, ForeignKey('room_booked.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)


class RoomRented(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_booked_id = Column(Integer, ForeignKey('room_booked.id'))
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
    renting_detail = relationship('RentingDetail', backref=backref('room_rented', lazy=True))
    bill = relationship('Bill', backref=backref('room_rented', lazy=True))

class RentingDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_rented_id = Column(Integer, ForeignKey('room_rented.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)


class Bill(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_date = Column(Date)
    charge = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    room_rented_id = Column(Integer, ForeignKey('room_rented.id'), nullable=False)


class Account(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(Integer, ForeignKey('status_account.id'), nullable=False)
    role = Column(Integer, ForeignKey('role.id'), nullable=False, default=3)
    customer = relationship("Customer", backref=backref("account", lazy="joined"), uselist=False)
    employee = relationship("Employee", backref=backref("account", lazy="joined"), uselist=False)

    def get_id(self):
        return str(self.id)


if __name__ == "__main__":
    with app.app_context():
        db.drop_all()  # Xóa tất cả bảng cũ
        db.create_all()

        trang_thai_phong = [
            RoomStatus(id=1, name="Trống"),
            RoomStatus(id=2, name="Đang sử dụng"),
            RoomStatus(id=3, name="Đang bảo trì"),
        ]

        loai_khach_hang = [
            CustomerType(id=1, name="Nội Địa"),
            CustomerType(id=2, name="Nước Ngoài"),
        ]

        trang_thai_tai_khoan = [
            StatusAccount(id=1, name="Hoạt động"),
            StatusAccount(id=2, name="Đã khóa"),
        ]

        vai_tro = [
            Role(id=1, name="Admin"),
            Role(id=2, name="NhanVien"),
            Role(id=3, name="KhachHang"),
        ]

        loai_phong = [
            Category(
                id=1,
                name="Standard",
                price=500000,
                description="""
                    Phòng tại khách sạn này đơn giản, tiện nghi, phù hợp cho cá nhân hoặc gia đình nhỏ. Phòng không có ban công nhưng có cửa sổ lớn, giúp không 
                    gian thoáng đãng và dễ chịu. Nội thất gồm giường ngủ thoải mái, tivi, bàn làm việc nhỏ, tủ quần áo và tủ lạnh mini. Phòng tắm hiện đại và 
                    sạch sẽ. Ưu điểm của phòng là giá cả phải chăng, thiết kế tiện nghi và không gian thoáng đãng. Tuy nhiên, phòng thiếu sofa và không gian có 
                    thể cảm thấy hạn chế đối với những người yêu thích không gian rộng. Phòng phù hợp cho khách du lịch tiết kiệm, gia đình nhỏ và công tác ngắn hạn.
                """,
                image="https://q-xx.bstatic.com/xdata/images/hotel/840x460/483207820.jpg?k=d8955cd0981eea6cb5dcb5d749f370745f6393b6c86d85ffc643599318e0c49b&o="
            ),
            Category(
                id=2,
                name="Deluxe",
                price=1000000,
                description="""
                    Phòng khách sạn này thiết kế đơn giản, phù hợp cho cá nhân hoặc gia đình nhỏ, mang lại sự thoải mái và tiện nghi mà không quá xa hoa. Với cửa sổ 
                    lớn, không gian phòng thoáng đãng và dễ chịu, dù không có ban công. Nội thất gồm giường ngủ thoải mái, tivi, bàn làm việc, tủ quần áo và tủ lạnh 
                    mini, không gian rộng rãi nhưng không có sofa. Phòng tắm hiện đại, sạch sẽ. Phòng có giá cả phải chăng, thiết kế tiện nghi, phù hợp cho khách du 
                    lịch tiết kiệm, gia đình nhỏ và công tác ngắn hạn. Tuy nhiên, thiếu ban công và sofa có thể là nhược điểm cho những ai yêu thích không gian rộng 
                    rãi hơn.
                """,
                image="https://www.vietnambooking.com/wp-content/uploads/2021/02/khach-san-ho-chi-minh-14.jpg"),
            Category(
                id=3,
                name="VIP",
                price=2000000,
                description="""
                    Phòng VIP tại khách sạn này là lựa chọn lý tưởng cho những ai tìm kiếm sự sang trọng và tiện nghi bậc nhất. Phòng rộng rãi, với nội thất cao cấp, 
                    cửa sổ lớn mang đến tầm nhìn tuyệt đẹp ra thành phố. Nội thất phòng gồm giường lớn, tivi màn hình phẳng, minibar cao cấp, khu vực tiếp khách riêng 
                    biệt và phòng tắm với bồn tắm Jacuzzi. Các tiện ích bổ sung như máy pha cà phê, hệ thống chiếu sáng tự động và điều hòa thông minh hoàn thiện không 
                    gian.
                    """,
                      image="https://hoanghaihotel.vn/Data/images/tintuc/10032021170917-gioi-thieu-ve-khach-san-hoang-hai.jpg"),
        ]

        # Thêm dữ liệu mẫu vào bảng chính
        nhan_vien = [
            Employee(id=1, name="Nguyễn Văn A", cmnd="012345678901", address="Hà Nội", account_id=2),
            Employee(id=2, name="Trần Thị B", cmnd="987654321098", address="Hồ Chí Minh", account_id=3),
        ]

        khach_hang = [
            Customer(id=1, name="Lê Văn C", cmnd="123456789012", address="Đà Nẵng", customer_type_id=1, phone="0987654321",
                      account_id=4),
            Customer(id=2, name="Phạm Thị D", cmnd="210987654321", address="Huế", customer_type_id=2, phone="0987654321",
                      account_id=5),
            Customer(id=3, name="Trần Văn E", cmnd="140936674321", address="Phú Yên", customer_type_id=1, phone="0987654321"),
            Customer(id=4, name="Nguyễn Tấn L", cmnd="760987654321", address="Sài Gòn", customer_type_id=2, phone="0987654321"),

        ]

        phong = [
            Room(id=1,name='101', status_room=1, room_type_id=1),
            Room(id=2,name='102',  status_room=1, room_type_id=1),
            Room(id=3,name='103', status_room=1, room_type_id=3),
            Room(id=4,name='104',  status_room=1, room_type_id=2),
            Room(id=5,name='105',  status_room=1, room_type_id=2),
            Room(id=6,name='106',  status_room=1, room_type_id=3),
            Room(id=7,name='107',  status_room=1, room_type_id=1),
            Room(id=8, name='108', status_room=1, room_type_id=3),
            Room(id=9, name='109', status_room=1, room_type_id=1),
            Room(id=10, name='110', status_room=1, room_type_id=3),
            Room(id=11, name='201', status_room=1, room_type_id=2),
            Room(id=12, name='202', status_room=1, room_type_id=2),
            Room(id=13, name='203', status_room=1, room_type_id=3),
            Room(id=15, name='204', status_room=1, room_type_id=1),
            Room(id=16, name='205', status_room=1, room_type_id=1),
            Room(id=17, name='206', status_room=1, room_type_id=2),
            Room(id=18, name='207', status_room=1, room_type_id=1),
            Room(id=19, name='208', status_room=1, room_type_id=2),
            Room(id=20, name='209', status_room=1, room_type_id=3),
        ]

        # phieu_dat_phong = [
        #     RoomBooked(id=1, customer_id=1, booking_date="2024-12-01", check_in_date="2024-12-05",
        #                   check_out_date="2024-12-10"),
        # ]
        #
        # chi_tiet_dat_phong = [
        #     BookingDetail(id=1, room_booked_id=1, room_id=1, customer_id=1),
        # ]
        #
        # phieu_thue_phong = [
        #     RoomRented(id=1, room_booked_id=1, customer_id=1, check_in_date="2024-12-05",
        #                    check_out_date="2024-12-10",
        #                    employee_id=1),
        # ]
        #
        # chi_tiet_thue_phong = [
        #     RentingDetail(id=1, room_rented_id=1, room_id=1, customer_id=1),
        # ]
        #
        # hoa_don = [
        #     Bill(id=1, create_date="2024-12-11", charge=50000, total=550000, room_rented_id=1),
        # ]

        tai_khoan = [
            Account(id=1, username="admin", password=hash_password("123"),status=1,
                     role=1),
            Account(id=2, username="nhanvien1", password=hash_password("123"), status=1,
                     role=2),
            Account(id=3, username="nhanvien2", password=hash_password("123"), status=1,
                     role=2),
            Account(id=4, username="khachhang1", password=hash_password("123"),  status=1,
                     role=3),
            Account(id=5, username="khachhang2", password=hash_password("123"), status=1,
                     role=3),
        ]

        # Lưu tất cả vào database
        db.session.add_all(trang_thai_phong)
        db.session.add_all(loai_khach_hang)
        db.session.add_all(trang_thai_tai_khoan)
        db.session.add_all(vai_tro)
        db.session.add_all(tai_khoan)
        db.session.add_all(loai_phong)
        # db.session.commit()
        db.session.add_all(nhan_vien)
        db.session.add_all(khach_hang)
        db.session.add_all(phong)
        # db.session.add_all(phieu_dat_phong)
        # db.session.commit()
        # db.session.add_all(chi_tiet_dat_phong)
        # db.session.commit()
        # db.session.add_all(phieu_thue_phong)
        # db.session.commit()
        # db.session.add_all(chi_tiet_thue_phong)
        # db.session.commit()
        # db.session.add_all(hoa_don)
        db.session.commit()
