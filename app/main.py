from fastapi import FastAPI
from app.packages.router import router as router_packages


app = FastAPI()


@app.get("/")
def home_page():
    return {"message": "Стартовая страница"}


app.include_router(router_packages)
