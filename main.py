from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from tickers.router import router as ticker_router
from positions.router import router as pos_router
from database import engine, Base

app = FastAPI()
origins = ["*"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Specify the allowed HTTP methods
    allow_headers=["*"],  # Specify the allowed headers
)

app.include_router(auth_router, prefix="/auth")
app.include_router(pos_router, prefix="/positions")
app.include_router(ticker_router, prefix="/tickers")
Base.metadata.create_all(bind=engine)