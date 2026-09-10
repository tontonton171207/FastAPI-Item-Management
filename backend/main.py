from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 1. Xác định đường dẫn tuyệt đối
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# 2. Phục vụ các file tĩnh (style.css, script.js)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# 3. Trả về trực tiếp trang HTML khi truy cập http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return FileResponse(FRONTEND_DIR / "house_form.html")

# 4. Logic tính giá nhà
def predict_price(area: float, bedrooms: int, location: str) -> float:
    base = 500_000_000.0 + (area * 15_000_000.0) + (bedrooms * 50_000_000.0)
    loc = location.strip().lower()
    if loc == "hanoi":
        base *= 1.3
    elif loc == "hcmc":
        base *= 1.25
    return round(base, -6)

# 5. Route GET /predict
@app.get("/predict")
def get_predict(area: float, bedrooms: int, location: str = "other"):
    return {
        "area": area,
        "bedrooms": bedrooms,
        "location": location,
        "predicted_price": predict_price(area, bedrooms, location)
    }