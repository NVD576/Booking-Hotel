import json
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import cast, func, Integer, and_, exists,  extract
from datetime import datetime

from utils import hash_password
from TTDHotel.TTDHotel import app, db
from models import Category, Account, RentingDetail, RoomStatus, CustomerType, StatusAccount, Role, Employee, Customer, \
    Room, RoomBooked, RoomRented, Bill, BookingDetail
from sqlalchemy import func

def auth_user(username, password):
    password_hash = hash_password(password)
    return (
        Account.query.options(
            db.joinedload(Account.customer),
            db.joinedload(Account.employee),
        )
        .filter(func.binary(Account.username) == username, func.binary(Account.password) == password_hash)
        .first()
    )


def add_booking(room_details, booking_data):
    try:
        phieu_dat = None

        for customer in room_details:
            # Add customer first
            cus = Customer(
                name=customer["customer_name"],
                cmnd=customer["customer_id_card"],
                address=customer["customer_address"],
                phone=customer["customer_phone"],
                customer_type_id=1 if customer["customer_type"] == "1" else 2
            )
            db.session.add(cus)
            db.session.flush()  # Ensures the customer ID is generated

            # Create the RoomBooked entry only after we have the customer ID
            if not phieu_dat:
                phieu_dat = RoomBooked(
                    customer_id=cus.id,  # Correctly associate the customer_id
                    booking_date=datetime.now(),
                    check_in_date=booking_data["check_in_date"],
                    check_out_date=booking_data["check_out_date"]
                )
                db.session.add(phieu_dat)
                db.session.flush()  # Ensures the room booking ID is generated

            # Add BookingDetail for each room the customer books
            chi_tiet = BookingDetail(
                room_booked_id=phieu_dat.id,
                room_id=customer["maPhong"],  # Ensure room_id corresponds to an actual room
                customer_id=cus.id
            )
            db.session.add(chi_tiet)

        db.session.commit()

        return phieu_dat.id  # Return the RoomBooked ID

    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi khi lưu phiếu đặt: {ex}")
        raise ex



def get_or_create_user(user_info):
    """Tạo mới người dùng nếu chưa tồn tại."""
    account = Account.query.filter(Account.username.__eq__(user_info['email'])).first()

    if not account:
        account = Account(
            username=user_info['email'],
            password=hash_password(user_info['email']),
            status=1,
            role=3
        )
        db.session.add(account)
        db.session.commit()

        kh = Customer(name=user_info['name'], customer_type_id=1, account_id=account.id, avatar=user_info['picture'])
        db.session.add(kh)
        db.session.commit()

    return account

def add_user(name,phone, username  , password ,address, customer_type_id ,cmnd =None,avatar=None):
    password = hash_password(password)
    tk = Account(username=username, password=password, status=1, role=3)
    db.session.add(tk)
    db.session.commit()

    kh = Customer(name = name, address = address ,phone=phone ,cmnd=cmnd,
                  customer_type_id = customer_type_id, account_id = tk.id,avatar=avatar) #cần giao diện để nhập thông tin
    if avatar:
        kh.avatar = avatar
    db.session.add(kh)
    db.session.commit()



def update_user(id, name=None, phone=None, password=None):
    """Cập nhật thông tin người dùng."""
    customer = Customer.query.filter(Customer.account_id == id).first()
    employee = Employee.query.filter(Employee.account_id == id).first()

    if customer:
        if name:
            customer.name = name
        if phone:
            customer.phone = phone
        db.session.commit()

    if employee:
        if name:
            employee.name = name
        if phone:
            employee.phone = phone
        db.session.commit()

    if password:
        account = Account.query.filter(Account.id == id).first()
        if account:
            account.password = hash_password(password)
            db.session.commit()

    return True

def check_room_availability(ngay_nhan_phong, ngay_tra_phong, so_luong_phong, loai_phong_id):
    """
    Kiểm tra và trả về danh sách phòng trống cho một loại phòng cụ thể.
    """
    # Danh sách các phòng đã được đặt trong khoảng thời gian yêu cầu
    booked_rooms = db.session.query(BookingDetail.room_id).join(RoomBooked).filter(
        and_(
            RoomBooked.check_in_date < ngay_tra_phong,
            RoomBooked.check_out_date > ngay_nhan_phong
        )
    ).all()
    booked_room_ids = [room[0] for room in booked_rooms]

    # Lấy danh sách phòng trống
    available_rooms = db.session.query(Room.id).filter(
        Room.room_type_id == loai_phong_id,
        Room.status_room.is_(True),
        ~Room.id.in_(booked_room_ids)
    ).order_by(Room.id).limit(so_luong_phong).all()

    return [room[0] for room in available_rooms]  # Trả về danh sách mã phòng trống

def get_booking_detail_by_booked_id(booked_id):
    return BookingDetail.query.filter(BookingDetail.room_booked_id == booked_id).all()

def get_available_room_standard():
    return Room.query.filter(Room.status_room==1 , Room.room_type_id==1).all()

def get_available_room_deluxe():
    return Room.query.filter(Room.status_room==1 , Room.room_type_id==2).all()

def get_available_room_vip():
    return Room.query.filter(Room.status_room==1 , Room.room_type_id==3).all()

def get_available_room_standard_count():
    return Room.query.filter(Room.status_room==1 , Room.room_type_id==1).count()

def get_available_room_deluxe_count():
    return Room.query.filter(Room.status_room==1 , Room.room_type_id==2).count()

def get_available_room_vip_count():
    return Room.query.filter(Room.status_room==1 , Room.room_type_id==3).count()

def get_user_by_id(user_id):
    return Account.query.get(user_id)

def get_room_status_by_id(room_status_id):
    return RoomStatus.query.get(room_status_id)


def get_all_room_status():
    return RoomStatus.query.all()


def get_customer_type_by_id(customer_type_id):
    return CustomerType.query.get(customer_type_id)


def get_all_customer_types():
    return CustomerType.query.all()


def get_customer_by_phone(phone):
    return Customer.query.filter(Customer.phone==phone).first()


def get_status_account_by_id(status_account_id):
    return StatusAccount.query.get(status_account_id)


def get_all_status_accounts():
    return StatusAccount.query.all()


def get_role_by_id(role_id):
    return Role.query.get(role_id)


def get_all_roles():
    return Role.query.all()

def get_category_by_another_id(id):
    return Category.query.filter(Category.id!=id).all()

def get_category_by_id(category_id):
    return Category.query.get(category_id)

def get_category_by_name(p):
    return Category.query.filter_by(name=p).first()

def get_all_categories():
    return Category.query.all()


def get_employee_by_id(employee_id):
    return Employee.query.get(employee_id)

def get_employee_by_account_id(account_id):
    return Employee.query.filter(Employee.account_id == account_id).first()


def get_all_employees():
    return Employee.query.all()


def get_customer_by_id(customer_id):
    return Customer.query.get(customer_id)


def get_all_customers():
    return Customer.query.all()


def get_room_by_id(room_id):
    return Room.query.get(room_id)


def get_all_rooms():
    return Room.query.all()


def get_room_booked_by_id(room_booked_id):
    return RoomBooked.query.get(room_booked_id)


def get_all_room_booked():
    return RoomBooked.query.all()

def get_all_room_booked_by_account_id(id):
    customer = get_customer_by_account_id(id)
    return RoomBooked.query.filter(RoomBooked.customer_id==customer.id).all()

def get_room_rented_by_id(room_rented_id):
    return RoomRented.query.get(room_rented_id)


def get_all_room_rented():
    return RoomRented.query.all()


def get_bill_by_id(bill_id):
    return Bill.query.get(bill_id)


def get_all_bills():
    return Bill.query.all()


def get_account_by_id(account_id):
    return Account.query.get(account_id)


def get_account_by_username(username):
    return Account.query.filter_by(username=username).first()


def get_all_accounts():
    return Account.query.all()

def get_customer_by_account_id(account_id):
    return Customer.query.filter_by(account_id=account_id).first()


# --- Set methods ---
def set_room_status(name):
    room_status = RoomStatus(name=name)
    db.session.add(room_status)
    db.session.commit()

    return room_status


def set_customer_type(name):
    customer_type = CustomerType(name=name)
    db.session.add(customer_type)
    db.session.commit()

    return customer_type


def set_status_account(name):
    status_account = StatusAccount(name=name)

    db.session.add(status_account)
    db.session.commit()

    return status_account


def set_role(name):
    role = Role(name=name)

    db.session.add(role)
    db.session.commit()

    return role


def set_category(name, description, price, image):
    category = Category(name=name, description=description, price=price, image=image)
    db.session.add(category)
    db.session.commit()

    return category


def set_employee(name, cmnd, address, account_id):
    employee = Employee(name=name, cmnd=cmnd, address=address, account_id=account_id)
    db.session.add(employee)
    db.session.commit()

    return employee


def set_customer(name, cmnd, address, phone, customer_type_id, account_id=None):
    customer = Customer(name=name, cmnd=cmnd, address=address, phone=phone, customer_type_id=customer_type_id,
                        account_id=account_id)
    db.session.add(customer)
    db.session.commit()

    return customer


def set_room(status_room, room_type_id):
    room = Room(status_room=status_room, room_type_id=room_type_id)
    db.session.add(room)
    db.session.commit()

    return room


def set_room_booked(customer_id, booking_date, check_in_date, check_out_date):
    room_booked = RoomBooked(customer_id=customer_id, booking_date=booking_date, check_in_date=check_in_date,
                             check_out_date=check_out_date)
    db.session.add(room_booked)
    db.session.commit()

    return room_booked

def set_booking_details(room_booked_id, room_id, customer_id):
    booking_datails = BookingDetail(room_booked_id=room_booked_id, room_id=room_id, customer_id=customer_id)
    db.session.add(booking_datails)
    db.session.commit()

def set_renting_details(room_renting_id, room_id, customer_id):
    renting_detail = RentingDetail(room_rented_id=room_renting_id, room_id=room_id, customer_id=customer_id)
    db.session.add(renting_detail)
    db.session.commit()


def set_room_rented(room_booked_id, customer_id, check_in_date, check_out_date, employee_id):
    room_rented = RoomRented(room_booked_id=room_booked_id, customer_id=customer_id, check_in_date=check_in_date,
                             check_out_date=check_out_date, employee_id=employee_id)
    db.session.add(room_rented)
    db.session.commit()

    return room_rented


def set_bill(create_date, charge, total, room_rented_id):
    bill = Bill(create_date=create_date, charge=charge, total=total, room_rented_id=room_rented_id)
    db.session.add(bill)
    db.session.commit()

    return bill


def set_account(username, password, status, role):
    account = Account(username=username, password=password, status=status, role=role)
    db.session.add(account)
    db.session.commit()

    return account

def load_categories():
    # Đọc dữ liệu từ file categories.json
    with open('categories.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        categories = [Category(
            id=category['id'],
            name=category['name'],
            price=category['price'],
            description=category['description'],
            image=category['image']
        ) for category in data]
        return categories


def load_room_type(id=None):
    query = Category.query
    if id:
        query = query.filter(Category.id == id)
    return query.all()



def load_contacts():
    return read_json('data/contacts.json')

def load_rules():
    return read_json('data/rules.json')


def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_rules(rules):
    with open('data/rules.json', 'w') as f:
        json.dump(rules, f, indent=4)


def doanh_thu_theo_thang(thang: int = None, nam: int = None):
    try:
        if thang is None or nam is None:
            today = datetime.today()
            thang = thang or today.month
            nam = nam or today.year

        doanh_thu = (
            db.session.query(
                Room.id.label("maPhong"),
                Category.name.label("tenLoaiPhong"),
                func.coalesce(func.sum(Bill.total ), 0).label("doanhThu")  # Sử dụng coalesce để thay 0 cho phòng không có doanh thu
            )
            .join(Category, Category.id == Room.room_type_id)  # Liên kết đến bảng Loại Phòng
            .outerjoin(RentingDetail, RentingDetail.room_id == Room.id)  # Sử dụng outerjoin
            .outerjoin(RoomRented, RoomRented.id == RentingDetail.room_rented_id)  # Sử dụng outerjoin
            .outerjoin(Bill, Bill.room_rented_id == RoomRented.id)  # Sử dụng outerjoin
            .filter(
                extract('month', Bill.create_date) == thang,
                extract('year', Bill.create_date) == nam
            )
            .group_by(Room.id, Category.name)
            .order_by(Room.id)
            .all()
        )

        if not doanh_thu:
            return ""

        return doanh_thu

    except SQLAlchemyError as e:
        db.session.rollback()  # Rollback nếu xảy ra lỗi
        return f"Đã xảy ra lỗi khi truy vấn dữ liệu: {str(e)}"

def tan_suat_theo_thang(thang: int = None, nam: int = None):
    try:
        if thang is None or nam is None:
            today = datetime.today()
            thang = thang or today.month
            nam = nam or today.year

        tan_suat = (
            db.session.query(
                Category.id.label("maLoaiPhong"),
                Category.name.label("tenLoaiPhong"),
                func.coalesce(func.count(RentingDetail.room_id), 0).label("soLanSuDung")
            )
            .outerjoin(Room, Category.id == Room.room_type_id)
            .outerjoin(RentingDetail, RentingDetail.room_id == Room.id)
            .outerjoin(RoomRented, RoomRented.id == RentingDetail.room_rented_id)
            .filter(
                (extract('month', RoomRented.check_in_date) == thang) | (RoomRented.check_in_date == None),
                extract('year', RoomRented.check_in_date) == nam
            )
            .group_by(Category.id, Category.name)
            .order_by(func.count(RentingDetail.room_id).desc())
            .all()
        )

        if not tan_suat:
            return ""

        return tan_suat
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Đã xảy ra lỗi khi truy vấn dữ liệu: {str(e)}"

def save_contacts(contacts):
    with open('data/contacts.json', 'w') as f:
        json.dump(contacts, f, indent=3)