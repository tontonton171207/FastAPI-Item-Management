document.getElementById('priceForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const area = document.getElementById('area').value;
    const bedrooms = document.getElementById('bedrooms').value;
    const location = document.getElementById('location').value;
    const resultDiv = document.getElementById('result');

    // Gọi trực tiếp đường dẫn tương đối /predict
const url = `/predict?area=${encodeURIComponent(area)}&bedrooms=${encodeURIComponent(bedrooms)}&location=${encodeURIComponent(location)}`;
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`Lỗi HTTP từ máy chủ: ${response.status}`);
        }

        const data = await response.json();

        // Định dạng tiền tệ VND
        const formattedPrice = new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(data.predicted_price);

        resultDiv.className = 'success';
        resultDiv.style.display = 'block';
        resultDiv.textContent = `Giá dự đoán: ${formattedPrice}`;

    } catch (err) {
        resultDiv.className = 'error';
        resultDiv.style.display = 'block';
        resultDiv.textContent = `Không thể kết nối API: ${err.message}`;
    }
});