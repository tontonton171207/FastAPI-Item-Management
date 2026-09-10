from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Web!"}

@app.get("/hello/{name}")          # path parameter
def hello(name: str):
    return {"greeting": f"Hello {name}"}

@app.get("/add")                  # query params: /add?a=2&b=3
def add(a: int, b: int):
    return {"a": a, "b": b, "sum": a + b}