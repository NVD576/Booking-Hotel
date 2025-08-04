# from urllib import request
from flask import request

from flask import redirect, flash
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from TTDHotel.TTDHotel import app, db
from models import Category, Account, RoomStatus, CustomerType, StatusAccount, Role, Employee, Customer, Room, \
    RoomBooked, RoomRented, Bill, BookingDetail, RentingDetail
import dao
from flask_login import current_user, login_user, logout_user


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html', msg="Hello")


admin = Admin(app, name="TTDHotel", template_mode="bootstrap4")


class AuthenticatedView(ModelView):
    def is_visible(self):
        return current_user.is_authenticated and current_user.role == 1

    def __init__(self, model, session, **kwargs):
        # Lấy tất cả các cột từ model
        self.column_list = [column.key for column in model.__table__.columns]

        # # Thêm các cột từ các quan hệ (nếu có)
        # for relation in model.__mapper__.relationships.keys():
        #     self.column_list.append(relation)

        super(AuthenticatedView, self).__init__(model, session, **kwargs)


admin.add_view(AuthenticatedView(Account, db.session, category='Quản lý tài khoản'))
admin.add_view(AuthenticatedView(Customer, db.session, category='Quản lý khách hàng'))
admin.add_view(AuthenticatedView(RoomStatus, db.session, category='Quản lý phòng'))
admin.add_view(AuthenticatedView(CustomerType, db.session, category='Quản lý khách hàng'))
admin.add_view(AuthenticatedView(StatusAccount, db.session, category='Quản lý tài khoản'))
admin.add_view(AuthenticatedView(Role, db.session, category='Quản lý tài khoản'))
admin.add_view(AuthenticatedView(Category, db.session, category='Quản lý phòng'))
admin.add_view(AuthenticatedView(Employee, db.session, category='Quản lý nhân sự'))
admin.add_view(AuthenticatedView(Room, db.session, category='Quản lý phòng'))
admin.add_view(AuthenticatedView(RoomBooked, db.session, category='Quản lý đặt phòng'))
admin.add_view(AuthenticatedView(RoomRented, db.session, category='Quản lý thuê phòng'))
admin.add_view(AuthenticatedView(Bill, db.session, category='Quản lý hóa đơn'))
admin.add_view(AuthenticatedView(BookingDetail, db.session, category='Quản lý đặt phòng'))
admin.add_view(AuthenticatedView(RentingDetail, db.session, category='Quản lý thuê phòng'))


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(BaseView):
    @expose('/')
    def index(self):
        selected_month = request.args.get('months')
        selected_year = request.args.get('years')
        stats = dao.doanh_thu_theo_thang(thang=selected_month, nam=selected_year)
        # stats = hotelapp.dao.get_room_statistics(selected_month, selected_year)
        # if f"Không có dữ liệu doanh thu cho tháng {selected_month}, năm {selected_year}." == stats:
        #     stats = ''
        total = 0
        print(stats)
        try:
            total = sum([s[2] for s in stats if s[2]])  # Tính tổng doanh thu
        except Exception as e:
            total = 0

        return self.render('admin/stats.html', stats=stats)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 1


admin.add_view(StatsView(name="Doanh thu", category='Thống kê'))

admin.add_view(LogoutView(name='Đăng xuất'))


class TanSuatView(BaseView):
    @expose('/')
    def index(self):
        selected_month = request.args.get('months')
        selected_year = request.args.get('years')
        stats = dao.tan_suat_theo_thang(selected_month, selected_year)
        # if f"Không có dữ liệu doanh thu cho tháng {selected_month}, năm {selected_year}." == stats:
        #     stats = ''
        # total = 0
        # print(stats)
        # try:
        #     total = sum([s[2] for s in stats if s[2]])  # Tính tổng doanh thu
        # except Exception as e:
        #     total = 0

        return self.render('admin/tanSuat.html', stats=stats)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 1


admin.add_view(TanSuatView(name="Tần suất", category='Thống kê'))


class QuyDinhView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        rules = dao.load_rules()
        if request.method == 'POST':
            try:
                rules['dat_phong_khach_san']['thoi_gian_nhan_phong_toi_da'] = int(
                    request.form['thoi_gian_nhan_phong_toi_da'])
                rules['suc_chua_phong']['so_khach_toi_da'] = int(request.form['so_khach_toi_da'])
                rules['gia_phong']['so_khach_co_ban'] = int(request.form['so_khach_co_ban'])
                rules['gia_phong']['phu_phi_khach_them'] = float(request.form['phu_phi_khach_them'])
                rules['gia_phong']['he_so_khach_nuoc_ngoai'] = float(request.form['he_so_khach_nuoc_ngoai'])
                dao.save_rules(rules)
                flash('Quy định đã được cập nhật thành công!', 'success')
            except Exception as e:
                flash(f"Đã xảy ra lỗi: {str(e)}", 'danger')
        return self.render('admin/rules.html', rules=rules)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 1


admin.add_view(QuyDinhView(name="Quy định", endpoint='update-rules'))

if __name__ == "__main__":
    app.run(debug=True)
