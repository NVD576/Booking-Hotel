import math
import random
# from crypt import methods
from datetime import datetime
from utils import hash_password
from authlib.integrations.flask_client import OAuth
from django.contrib.messages import success
from flask import render_template, request, redirect, url_for, session, flash, jsonify
import os
import unicodedata
from flask_login import login_user, logout_user, current_user, login_required

import dao
from TTDHotel.TTDHotel import app, oauth, facebook, admin, login, db
import cloudinary.uploader


def check_login():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        session['next'] = request.url
    return logged_in


@app.route('/home')
def index():
    return render_template('welcome.html', logged_in=check_login())


@app.template_filter('dict_without_key')
def dict_without_key(d, key):
    return {k: v for k, v in d.items() if k != key}


@app.route('/booking')
def show_categories():
    categories = dao.get_all_categories()
    list_category = dao.get_all_categories()
    room_standard_available = dao.get_available_room_standard_count()
    room_deluxe_available = dao.get_available_room_deluxe_count()
    room_vip_available = dao.get_available_room_vip_count()

    return render_template('index.html', categories=categories, list_category=list_category,
                           room_standard_available=room_standard_available,
                           room_deluxe_available=room_deluxe_available, room_vip_available=room_vip_available,
                           logged_in=check_login())


@app.route('/filter_category', methods=['POST'])
def filter_category():
    selected_value = request.form.get('loai_phong')  # Get selected category ID
    list_category = dao.get_all_categories()
    category = dao.get_all_categories()
    room_standard_available = dao.get_available_room_standard()
    room_deluxe_available = dao.get_available_room_deluxe()
    room_vip_available = dao.get_available_room_vip()
    if selected_value:
        categories = dao.get_category_by_id(selected_value)
        categories = [categories] if categories else []
    else:
        categories = dao.get_all_categories()

    return render_template('index.html', list_category=list_category, categories=categories, category=category,
                           selected_value=selected_value,
                           room_standard_available=room_standard_available, room_deluxe_available=room_deluxe_available,
                           room_vip_available=room_vip_available, logged_in=check_login())


@app.route('/rules')
def rules():
    rules = dao.load_rules()
    return render_template('rules.html', logged_in=check_login(), rules=rules)


@app.route('/contacts')
def contacts():
    contacts = dao.load_contacts()
    return render_template('contacts.html', logged_in=check_login(), contacts=contacts)


@app.route('/rents', methods=['GET', 'POST'])
def rents():
    enriched_bookings = []
    data = {}
    if request.method == 'POST':
        room_booked_id = request.form.get('maDatPhong')
        room_booked = dao.get_room_booked_by_id(room_booked_id)
        print(room_booked_id)
        if room_booked:
            booking_detail = dao.get_booking_detail_by_booked_id(room_booked_id)
            room = dao.get_room_by_id(booking_detail[0].room_id)

            data = {
                'room': room.name,
                'check_in_date': room_booked.check_in_date.strftime('%d/%m/%Y'),
                'check_out_date': room_booked.check_out_date.strftime('%d/%m/%Y'),
                'booking_date': room_booked.booking_date.strftime('%d/%m/%Y'),
            }
            # # Tạo danh sách khách hàng liên quan đến từng booking
            for booking in booking_detail:
                customer = dao.get_customer_by_id(booking.customer_id)
                enriched_bookings.append({
                    'id': booking.id,
                    'customer_name': customer.name,
                    'customer_phone': customer.phone,
                    'customer_address': customer.address,
                    'customer_cmnd': customer.cmnd,
                    'customer_type': "Nội địa" if customer.customer_type_id == 1 else 'Ngoại địa',
                })

            if data and enriched_bookings:
                session['data'] = data
                session['enriched_bookings'] = enriched_bookings
                session['room_booked_id']=room_booked_id
    return render_template(
        'rents.html',
        room_booked=enriched_bookings,
        data=data,
        logged_in=check_login()
    )


@app.route('/category/<int:id>')
def details(id):
    category = dao.get_category_by_id(id)
    categories = dao.get_category_by_another_id(id)
    session['category_id'] = id
    customer = dao.get_customer_by_account_id(session.get('user_id'))
    return render_template('product-details.html', customer=customer, category=category, categories=categories,
                           logged_in=check_login())


@app.route('/booked', methods=['POST'])
def booked():
    room_details = []
    if request.method == "POST":
        category_id = session.get('category_id')
        check_in_date = datetime.strptime(request.form['check_in_date'], '%d/%m/%Y')
        check_out_date = datetime.strptime(request.form['check_out_date'], '%d/%m/%Y')

        category = dao.get_category_by_id(category_id)

        available_rooms = dao.check_room_availability(check_in_date, check_out_date, 1, category_id)

        if len(available_rooms) < 1:
            # Lưu các thông tin đã nhập vào session
            session['booking_data'] = {
                'customer_data': request.form.to_dict(flat=False)  # Lưu toàn bộ thông tin khách hàng
            }
            flash("Không còn đủ phòng trống trong khoảng thời gian bạn chọn!", "warning")
            return redirect(request.referrer)


        for idx, maPhong in enumerate(available_rooms, start=1):
            customer_name = request.form.getlist('name[]')
            customer_phone = request.form.getlist('phone[]')
            customer_id_card = request.form.getlist('cmnd[]')
            customer_address = request.form.getlist("address[]")
            customer_type = [request.form.get(f"option_{i + 1}") for i in range(len(customer_name))]

            if not(len(customer_name) == len(customer_phone) == len(customer_id_card)):
                return jsonify({"message": "Lỗi tên, số, cc"}), 400

            count = 0
            for i in range(len(customer_name)):
                count += 1
                room_details.append({
                    "maPhong": maPhong,
                    "customer_name": customer_name[i],
                    "customer_phone": customer_phone[i],
                    "customer_id_card": customer_id_card[i],
                    "customer_type": customer_type[i],
                    "customer_address": customer_address[i]
                })

        booking_data = {
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        }

        room= dao.get_room_by_id(room_details[0]["maPhong"])

        room_booked=dao.add_booking(room_details, booking_data)

        booking_details = dao.get_booking_detail_by_booked_id(room_booked)
        count = 0
        customer_type = 1
        for i in booking_details:
            customer = dao.get_customer_by_id(i.customer_id)
            if customer.customer_type_id == 2:
                customer_type = app.config['foreigner']
            count = count + 1

        ExtraGuest = (100 if count < 3 else (app.config['ExtraGuest'])) / 100

        number_of_days = (check_out_date - check_in_date).days

        original_price = number_of_days * category.price
        charge = original_price * (ExtraGuest) * customer_type - original_price

        total = original_price + charge
        return render_template('booking_details.html', category_id=category_id, total=total, charge=charge
                           , booking_data=booking_data, room_details=room_details, room=room , category=category)

    return render_template('booking_details.html', category_id=None
                           , booking_data=[], room_detail=[])

@app.route('/save_export', methods=['GET', 'POST'])
def save_export():
    if request.method == 'POST':
        data =session.get('data')
        employee=dao.get_employee_by_account_id(session.get('user_id'))
        room_booked= dao.get_room_booked_by_id(session.get('room_booked_id'))
        check_in_date = datetime.strptime(data['check_in_date'], "%d/%m/%Y")
        check_out_date = datetime.strptime(data['check_out_date'], "%d/%m/%Y")
        room_renting=dao.set_room_rented(room_booked_id=room_booked.id, customer_id=room_booked.customer_id,
                                         check_in_date=check_in_date
                                         , check_out_date=check_out_date, employee_id=employee.id)
        db.session.add(room_renting)
        db.session.commit()

        booking_details=dao.get_booking_detail_by_booked_id(room_booked.id)
        count=0
        customer_type=1
        for i in booking_details:
            booking_detail=dao.set_renting_details(room_renting_id=room_renting.id,room_id= i.room_id,customer_id= i.customer_id)
            customer=dao.get_customer_by_id(i.customer_id)
            if customer.customer_type_id==2:
                customer_type=app.config['foreigner']
            count=count+1

        ExtraGuest=(100 if count<3 else (app.config['ExtraGuest']))/100

        room=dao.get_room_by_id(booking_details[0].room_id)
        number_of_days = (check_out_date - check_in_date).days

        category= dao.get_category_by_id(room.room_type_id)

        original_price= number_of_days * category.price
        charge = original_price * ExtraGuest * customer_type - original_price

        total=original_price+charge
        print("tien goc" + str(original_price))

        dao.set_bill(create_date = check_in_date,charge=charge,total=total,room_rented_id=room_renting.id)
        return redirect(url_for('rents'))  # Chuyển hướng đến một trang thành công hoặc tải file

    return render_template('rent.html')


@app.route('/booking_details')
def booking_details():
    category_id= session['category_id']
    booking_data=session['booking_data']
    room_detail=session['room_details']


    return render_template('booking_details.html',category_id=category_id
                           ,booking_data=booking_data,room_detail=room_detail)


@app.route('/history')
def history():
    bookings = dao.get_all_room_booked()

    # Tạo danh sách khách hàng liên quan đến từng booking
    enriched_bookings = []
    for booking in bookings:
        customer = dao.get_customer_by_id(booking.customer_id)
        enriched_bookings.append({
            'id': booking.id,
            'customer_name': customer.name,
            'customer_phone': customer.phone,
            'booking_date': booking.booking_date,
            'check_in_date': booking.check_in_date,
            'check_out_date': booking.check_out_date,
            'customer_type': customer.customer_type_id,
        })

    return render_template('history.html', bookings=enriched_bookings)


@app.route('/admin-login', methods=['GET', 'POST'])
def process_admin_login():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username, password)
        if user:
            set_user_session(user)
            login_user(user)
        return redirect('/admin')


@login.user_loader
def get(user_id):
    return dao.get_user_by_id(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login_my_user():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username, password)
        if user:
            set_user_session(user)
            login_user(user)
            next_page = session.get('next', '/')
            return redirect(next_page)
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/forgot_pass')
def forgot_pass():
    return render_template('forgot_password.html')

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    if request.method.__eq__('POST'):
        phone = request.form.get('phone')
        customer = dao.get_customer_by_phone(phone)
        if customer:
            session['account_id'] = customer.account_id
            code = random.randint(100000, 999999)
            session['code'] = code
            flash(f'Mã xác thực: {code}', 'danger')
            return render_template('verify_code.html')

    flash('Số điện thoại không tồn tại', 'danger')
    return redirect(request.referrer)


@app.route('/verify_code', methods=['POST'])
def verify_code():
    if request.method.__eq__('POST'):
        otp = request.form.get('otp')
        code = session.get('code')
        print(otp,code)
        if otp.__eq__(code):
            return render_template('change_password.html')

    flash('Mã xác thực không đúng', 'danger')
    return render_template('verify_code.html')


@app.route('/change_password', methods=['POST'])
def change():
    if request.method.__eq__('POST'):
        new_password = request.form.get('new-password')
        confirm = request.form.get('confirm-password')

        if new_password != confirm:
            flash('Không trùng khớp.', 'danger')
            return render_template('change_password.html')

        id = session.get('account_id')
        user = dao.get_user_by_id(id)
        if user:
            success = dao.update_user(id, password=new_password)
            if success:
                flash('Cập nhật mật khẩu thành công.', 'success')
                return render_template('login.html')
            else:
                flash('Đã xảy ra lỗi khi cập nhật mật khẩu. Vui lòng thử lại.', 'danger')
                return render_template('change_password.html')

    flash('Đã xảy ra lỗi','danger')
    return render_template('change_password.html')


def set_user_session(user):
    session['user_id'] = user.id
    session['user_role'] = user.role
    session['user_name'] = (
        user.customer.name if user.customer else
        user.employee.name if user.employee else
        "Admin"
    )
    session['logged_in'] = True
    # session['phone'] = user.phone if user else None
    session['address'] = user.customer.address if user.customer else "None"
    if user.role==3:
        cus = dao.get_customer_by_account_id(user.id)
        session['avatar'] = cus.avatar


@app.context_processor
def get_user():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    phone = session.get('phone')
    role = session.get('user_role')
    logged_in = session.get('logged_in')
    avatar = session.get('avatar')
    return dict(user_id=user_id, user_name=user_name, phone=phone, role=role, avatar=avatar, logged_in=logged_in)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(request.referrer or '/')


@app.route('/info', methods=['GET', 'POST'])
def update_user():
    if request.method == 'POST':
        id = session.get('user_id')
        name = request.form.get('name')
        phone = request.form.get('phone')

        if len(phone) < 10 or not phone.isdigit():
            flash('Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại gồm ít nhất 10 chữ số.', 'danger')
            return redirect(request.referrer)

        if not name or not phone:
            flash('Tên và số điện thoại không được để trống.', 'danger')
            return redirect(request.referrer)

        success = dao.update_user(id, name=name, phone=phone)
        if success:
            session['user_name'] = name
            session['phone'] = phone
            flash('Cập nhật thông tin thành công.', 'success')
        else:
            flash('Đã xảy ra lỗi khi cập nhật thông tin. Vui lòng thử lại.', 'danger')

    return redirect(request.referrer)


@app.route('/changePassword', methods=['GET', 'POST'])
def update_password():
    if request.method == 'POST':
        id = session.get('user_id')
        old_password = request.form.get('oldPassword')
        new_password = request.form.get('newPassword')
        confirm = request.form.get('confirm')

        if new_password != confirm:
            flash('Không trùng khớp.', 'danger')
            return redirect(request.referrer)

        user = dao.get_user_by_id(id)
        if user:
            if user.password == hash_password(old_password):
                success = dao.update_user(id, password=new_password)
                if success:
                    flash('Cập nhật mật khẩu thành công.', 'success')
                else:
                    flash('Đã xảy ra lỗi khi cập nhật mật khẩu. Vui lòng thử lại.', 'danger')
            else:
                flash('Mật khẩu hiện tại không đúng.', 'danger')
        return redirect(request.referrer)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar = request.files.get('avatar')
        address = request.form.get('address')
        cmnd = request.form.get('cmnd')
        customer_type = request.form.get('option')
        avatar_path = None
        role = request.form.get('role')  # Nhận role từ form

        if password != confirm:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('register.html')

        if dao.auth_user(username, password):
            flash('Username already exists. Please try a different username.', 'danger')
            return render_template('register.html')

        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']

        dao.add_user(name=name, phone=phone, username=username, password=password,
                               customer_type_id=customer_type, address=address, cmnd=cmnd,  avatar=avatar_path)

        flash('Account created successfully!', 'success')
        return redirect('/login')


    return render_template('register.html')


@app.route('/')
def home():
    logged_in = session.get('logged_in', False)
    if not logged_in:
        session['next'] = request.url
    return render_template('welcome.html', logged_in=logged_in)


###################



@app.route('/login_google')
def login_google():
    google = oauth.create_client('google')  # create the Google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the Google oauth client
    token = google.authorize_access_token()  # Access token from Google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    user = oauth.google.userinfo()   # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    user = dao.get_or_create_user({
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture')
    })
    # and set ur own data in the session not the profile from Google
    session['profile'] = user_info
    session['user_id']= user.id
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    session['logged_in'] = True
    session['user_name'] = user_info['name']
    next_page = session.get('next')
    return redirect(next_page)


@app.route('/logout_google')
def logout_google():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')



@app.route('/login_facebook')
def login_facebook():
    redirect_uri = url_for('authorize_facebook', _external=True)
    return facebook.authorize_redirect(redirect_uri)


@app.route('/authorize_facebook')
def authorize_facebook():
    token = facebook.authorize_access_token()  # Lấy access token từ Facebook
    resp = facebook.get('me?fields=id,name,email,picture')  # Truy vấn thông tin người dùng
    user_info = resp.json()

    # Xử lý thông tin người dùng
    user = dao.get_or_create_user({
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture', {}).get('data', {}).get('url')
    })

    # Lưu thông tin vào session
    session['profile'] = user_info
    session['user_id']= user.id
    session['logged_in'] = True
    session['user_name'] = user_info['name']
    next_page = session.get('next')
    return redirect(next_page)


@app.route('/logout_facebook')
def logout_facebook():
    session.pop('logged_in', None)
    session.pop('profile', None)
    return redirect('/')


@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        url = urllib.parse.unquote(f"{rule}")
        output.append(f"{rule.endpoint}: {url} [{methods}]")
    return "<br>".join(output)

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
