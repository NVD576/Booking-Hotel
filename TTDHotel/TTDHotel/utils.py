import hashlib
def hash_password(password):
    """Mã hóa mật khẩu bằng cách sử dụng MD5."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()