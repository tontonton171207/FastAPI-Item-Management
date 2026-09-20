const API_URL = "http://127.0.0.1:8000/items";

// 1. Tải danh sách items từ API
async function fetchData() {
    const q = document.getElementById("search-q").value.trim();
    const minPrice = document.getElementById("min-price").value;
    const maxPrice = document.getElementById("max-price").value;
    const sortBy = document.getElementById("sort-by").value;
    const order = document.getElementById("order").value;

    // Build URL với query params
    let url = `${API_URL}?sort_by=${sortBy}&order=${order}`;
    if (q.length >= 2) url += `&q=${encodeURIComponent(q)}`;
    if (minPrice) url += `&min_price=${minPrice}`;
    if (maxPrice) url += `&max_price=${maxPrice}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Không thể tải dữ liệu");

        // Nhận dữ liệu dạng Envelope Pattern
        const data = await response.json();

        // Hiển thị tổng số lượng tìm thấy
        document.getElementById("total-info").innerText = `Tổng số sản phẩm: ${data.total}`;

        // Render bảng dữ liệu
        renderTable(data.items);
    } catch (error) {
        console.error("Lỗi fetch data:", error);
        alert("Lỗi khi kết nối đến server!");
    }
}

// 2. Render danh sách ra HTML
function renderTable(items) {
    const tbody = document.getElementById("item-tbody");
    tbody.innerHTML = "";

    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;">Không tìm thấy sản phẩm nào</td></tr>`;
        return;
    }

    items.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.price.toLocaleString("vi-VN")}</td>
            <td>
                <button onclick="editItem(${item.id}, '${item.name}', ${item.price})">Sửa</button>
                <button class="btn-danger" onclick="deleteItem(${item.id})">Xóa</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 3. Thêm mới sản phẩm (POST)
async function createItem() {
    const nameInput = document.getElementById("new-name");
    const priceInput = document.getElementById("new-price");
    const errorEl = document.getElementById("form-error");
    errorEl.innerText = "";

    const name = nameInput.value.trim();
    const price = parseFloat(priceInput.value);

    if (!name || isNaN(price)) {
        errorEl.innerText = "Vui lòng nhập tên và giá hợp lệ!";
        return;
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, price })
        });

        if (response.status === 409) {
            const errData = await response.json();
            errorEl.innerText = `❌ ${errData.detail}`; // Lỗi trùng tên
            return;
        }

        if (!response.ok) throw new Error("Lỗi khi thêm mới");

        // Reset form & reload danh sách
        nameInput.value = "";
        priceInput.value = "";
        fetchData();
    } catch (error) {
        console.error("Lỗi create item:", error);
        errorEl.innerText = "Có lỗi xảy ra!";
    }
}

// 4. Sửa sản phẩm (PATCH)
async function editItem(id, currentName, currentPrice) {
    const newName = prompt("Nhập tên mới (để trống nếu giữ nguyên):", currentName);
    const newPriceStr = prompt("Nhập giá mới (để trống nếu giữ nguyên):", currentPrice);

    let payload = {};
    if (newName && newName.trim() !== currentName) {
        payload.name = newName.trim();
    }
    if (newPriceStr && !isNaN(parseFloat(newPriceStr)) && parseFloat(newPriceStr) !== currentPrice) {
        payload.price = parseFloat(newPriceStr);
    }

    // Nếu không thay đổi gì thì dừng
    if (Object.keys(payload).length === 0) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.status === 409) {
            const errData = await response.json();
            alert(`❌ Không thể sửa: ${errData.detail}`); // Lỗi trùng tên khi sửa
            return;
        }

        if (!response.ok) throw new Error("Lỗi khi cập nhật");

        fetchData();
    } catch (error) {
        console.error("Lỗi patch item:", error);
        alert("Cập nhật thất bại!");
    }
}

// 5. Xóa sản phẩm (DELETE)
async function deleteItem(id) {
    if (!confirm("Bạn có chắc muốn xóa sản phẩm này không?")) return;

    try {
        const response = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
        if (!response.ok) throw new Error("Lỗi khi xóa");

        fetchData();
    } catch (error) {
        console.error("Lỗi delete item:", error);
        alert("Xóa thất bại!");
    }
}

// Gọi nạp dữ liệu lần đầu khi vào trang
document.addEventListener("DOMContentLoaded", fetchData);