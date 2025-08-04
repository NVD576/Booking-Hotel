document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatar');
    const customFileUpload = document.querySelector('.custom-file-upload');

    avatarInput.addEventListener('change', function(event) {
        const [file] = event.target.files;
        if (file) {
            const preview = document.createElement('img');
            preview.src = URL.createObjectURL(file);
            preview.style.width = '100px';
            preview.style.height = '100px';
            preview.style.borderRadius = '50%';
            preview.style.objectFit = 'cover';
            preview.style.marginTop = '10px';

            // Kiểm tra và xóa ảnh cũ
            customFileUpload.querySelectorAll('img').forEach(img => img.remove());

            // Thêm ảnh mới
            customFileUpload.appendChild(preview);
        }
    });
});