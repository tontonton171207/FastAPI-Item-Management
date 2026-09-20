from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="Item Management API")

# Cấu hình CORS để tránh bị chặn khi gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CẤU HÌNH STATIC FILES & ROUTE ROOT (SỬA LỖI 404) ---
# Tự động xác định vị trí tuyệt đối của thư mục 'frontend' nằm cùng cấp với 'backend'
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Phục vụ tất cả file trong thư mục frontend (app.js, style.css,...) tại đường dẫn /static
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Khi truy cập http://127.0.0.1:8000/ sẽ trả về file index.html
@app.get("/")
def read_root():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        return {"error": f"Không tìm thấy file index.html tại {index_file}"}
    return FileResponse(index_file)


# --- PYDANTIC MODELS (PART D) ---

class ItemBase(BaseModel):
    name: str
    price: float

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class ItemPublic(ItemBase):
    id: int

# Envelope Response Model (Part D)
class ItemListResponse(BaseModel):
    items: List[ItemPublic]
    total: int
    skip: int
    limit: int


# --- FAKE DATABASE ---

db_items = [
    {"id": 1, "name": "Bàn phím Mech", "price": 500000.0},
    {"id": 2, "name": "Chuột máy tính", "price": 250000.0},
    {"id": 3, "name": "Màn hình 24 inch", "price": 3000000.0},
    {"id": 4, "name": "Tai nghe Bluetooth", "price": 850000.0},
    {"id": 5, "name": "Lót chuột RGB", "price": 150000.0},
]
next_id = 6


# --- HELPER FUNCTIONS (PART C) ---

def check_duplicate_name(name: str, exclude_id: Optional[int] = None):
    """Kiểm tra trùng tên (case-insensitive) - Part C"""
    for item in db_items:
        if exclude_id is not None and item["id"] == exclude_id:
            continue
        if item["name"].lower() == name.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Item with this name already exists"
            )


# --- API ENDPOINTS ---

# 1. GET /items (Filtering, Searching, Sorting & Envelope Response - Part B & D)
@app.get("/items", response_model=ItemListResponse)
def get_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    q: Optional[str] = Query(None, min_length=2),
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    filtered_items = db_items.copy()

    # Filtering (Giá & Từ khóa)
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]

    if q is not None:
        filtered_items = [item for item in filtered_items if q.lower() in item["name"].lower()]

    # Sorting
    is_reverse = (order == "desc")
    filtered_items.sort(key=lambda item: item[sort_by], reverse=is_reverse)

    # Total count (Tính sau filter nhưng TRƯỚC khi cắt trang / slicing - Part D)
    total_count = len(filtered_items)

    # Slicing / Pagination
    paginated_items = filtered_items[skip : skip + limit]

    return {
        "items": paginated_items,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }


# 2. POST /items (Tạo mới & Check trùng 409 Conflict - Part C)
@app.post("/items", response_model=ItemPublic, status_code=status.HTTP_201_CREATED)
def create_item(item_in: ItemCreate):
    global next_id

    # Check trùng tên (Case-insensitive)
    check_duplicate_name(item_in.name)

    new_item = {
        "id": next_id,
        "name": item_in.name,
        "price": item_in.price
    }
    db_items.append(new_item)
    next_id += 1

    return new_item


# 3. PATCH /items/{item_id} (Partial Update & Check trùng khi đổi tên - Part C)
@app.patch("/items/{item_id}", response_model=ItemPublic)
def update_item_partial(item_id: int, item_update: ItemUpdate):
    target_item = next((item for item in db_items if item["id"] == item_id), None)
    
    if not target_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    # Lấy các trường client thực sự gửi lên
    update_data = item_update.model_dump(exclude_unset=True)

    # Nếu có đổi tên -> Kiểm tra trùng tên với các item khác
    if "name" in update_data:
        new_name = update_data["name"]
        if new_name.lower() != target_item["name"].lower():
            check_duplicate_name(new_name, exclude_id=item_id)

    # Cập nhật
    target_item.update(update_data)
    return target_item


# 4. DELETE /items/{item_id}
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    global db_items
    target_item = next((item for item in db_items if item["id"] == item_id), None)
    
    if not target_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    db_items = [item for item in db_items if item["id"] != item_id]
    return None