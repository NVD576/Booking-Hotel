    function toggleDescription() {
       var description = document.getElementById('description-text');
       var link = document.getElementById('toggle-description');

       if (description.classList.contains('description-short')) {
           description.classList.remove('description-short');
           link.textContent = 'Thu gọn';
       } else {
           description.classList.add('description-short');
           link.textContent = 'Xem thêm';
       }
   }

let customerCount = 1;
const customerFields = document.getElementById('customer-fields');
const addCustomerBtn = document.getElementById('add-customer-btn');

addCustomerBtn.addEventListener('click', function () {
    if (customerCount < 3) {
        customerCount++;

        const newCustomer = document.createElement('div');
        newCustomer.classList.add('card', 'mb-3');
        newCustomer.id = `customer-${customerCount}`;
        newCustomer.innerHTML = `
            <div class="card-header bg-gradient-primary text-black">
                Khách hàng ${customerCount}
                <button type="button" class="btn-close ms-2" aria-label="Close" onclick="removeCustomer(${customerCount})"></button>
            </div>
            <div class="card-body">
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="fullname-${customerCount}" name="name[]" placeholder="Họ và Tên" required>
                    <label for="fullname-${customerCount}">Họ và Tên</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="tel" class="form-control" id="phone-${customerCount}" name="phone[]" placeholder="Số Điện Thoại" required>
                    <label for="phone-${customerCount}">Số Điện Thoại</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="address-${customerCount}" name="address[]" placeholder="Địa chỉ" required>
                    <label for="address-${customerCount}">Địa chỉ</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="cmnd-${customerCount}" name="cmnd[]" placeholder="Căn cước/chứng minh thư" required>
                    <label for="cmnd-${customerCount}">Căn cước/chứng minh thư</label>
                </div>
                <div class="mb-4">
                    <label class="form-label">Loại khách hàng</label>
                    <div class="custom-radio-container">
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="option_${customerCount}" checked id="option1-${customerCount}" value="1" required>
                            <label class="form-check-label" for="option1-${customerCount}">Nội địa</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" type="radio" name="option_${customerCount}" id="option2-${customerCount}" value="2">
                            <label class="form-check-label" for="option2-${customerCount}">Ngoại địa</label>
                        </div>
                    </div>
                </div>
            </div>
        `;
        customerFields.appendChild(newCustomer);
    } else {
        alert('Tối đa 3 khách hàng');
    }
});


function removeCustomer(customerId) {
    const customerElement = document.getElementById(`customer-${customerId}`);
    if (customerElement) {
        customerElement.remove();
        customerCount--;
    }
}

const bookingModal = document.getElementById('bookingModal');
bookingModal.addEventListener('hidden.bs.modal', function () {
    // Reset customer fields to default
    customerFields.innerHTML = `
        <div class="card mb-3" id="customer-1">
            <div class="card-header">Khách hàng 1
                <button type="button" class="btn-close ms-2" aria-label="Close" onclick="removeCustomer(1)"></button>
            </div>
            <div class="card-body">
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" value="" id="fullname-1" name="name[]"
                           placeholder="Họ và Tên" required>
                    <label for="fullname-1">Họ và Tên</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="tel" class="form-control" value="" id="phone-1" name="phone[]"
                           placeholder="Số Điện Thoại" required>
                    <label for="phone-1">Số Điện Thoại</label>
                </div>
                 <div class="form-floating mb-3">
                    <input type="text" class="form-control" value="" id="address-1" name="address[]"
                           placeholder="Địa chỉ" required>
                    <label for="address-1">Địa chỉ</label>
                </div>
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" value="" id="cmnd-1" name="cmnd[]"
                           placeholder="Căn cước/chứng minh thư" required>
                    <label for="cmnd-1">Căn cước/chứng minh thư</label>
                </div>
                <div class="mb-4">
                    <label class="form-label">Loại khách hàng</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="option" id="option1"
                               value="1" checked>
                        <label class="form-check-label" for="option1">Nội địa</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="option" id="option2"
                               value="2">
                        <label class="form-check-label" for="option2">Ngoại địa</label>
                    </div>
                </div>
            </div>
        </div>
    `;
    customerCount = 1;
});

//   function toggleDescription() {
//    const desc = document.getElementById("description-text");
//    desc.style.transition = "max-height 0.5s ease";
//    desc.classList.toggle("expanded");
//}

document.getElementById('bookingModal').addEventListener('show.bs.modal', function () {
    document.getElementById('loader').style.display = 'block';
    setTimeout(() => {
        document.getElementById('loader').style.display = 'none';
    }, 1000);
});

document.addEventListener('DOMContentLoaded', function () {
        const decreaseRoom = document.getElementById('decrease-room');
        const increaseRoom = document.getElementById('increase-room');
        const roomQuantity = document.getElementById('room-quantity');

        decreaseRoom.addEventListener('click', function () {
            let quantity = parseInt(roomQuantity.value);
            if (quantity > 1) {
                roomQuantity.value = quantity - 1;
            }
        });

        increaseRoom.addEventListener('click', function () {
            let quantity = parseInt(roomQuantity.value);
            if (quantity < 5) {
                roomQuantity.value = quantity + 1;
            }
        });
    });

    const bookingButton = document.querySelector('[data-bs-target="#bookingModal"]');
    const roomQuantityModal = document.getElementById('room-quantity-modal');

    bookingButton.addEventListener('click', function () {
        const roomQuantity = document.getElementById('room-quantity').value;
        roomQuantityModal.value = roomQuantity;
    });

