from fastapi import FastAPI
from src.database.db import Base, engine
from src.router import routes
import uvicorn


def create_app():
    app = FastAPI(title="RCT system api",
              description="Rest api",
              version="0.1.0",
              openapi_url="",
              docs_url="/docs",  # swagger UI
              redoc_url="/redoc")  # ReDoc

    Base.metadata.create_all(bind=engine)
    app.include_router(routes.router)
    return app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)