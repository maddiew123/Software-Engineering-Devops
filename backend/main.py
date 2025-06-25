from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.createDb import create_database
from backend.routes import routers
from backend.database import engine
from backend.database import Base

Base.metadata.create_all(bind=engine) 

# create_database()

app = FastAPI()

origins = ["https://software-engineering-agile-assignment-3.onrender.com","localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

app.include_router(routers.app, prefix="", tags=[""])

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

print("Using DB at:", engine.url)