from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from auth.router import router as auth_router
from tickers.router import router as ticker_router
from positions.router import router as pos_router
from database import engine, Base
import testing.init_db as init_db
import settings

app = FastAPI(debug=False, title="Stock Options Analytics API", version="1.0.0", description="API for stock options analytics and portfolio management")

app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.ORIGINS,  # Allow requests from origins
  allow_credentials=True, # Allow Credentials (Authorization headers, Cookies, etc) to be included in the requests
  allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Specify the allowed HTTP methods
  allow_headers=["*"],  # Specify the allowed headers
)

# Redirect to Swagger
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
  return RedirectResponse(url="/docs")

app.include_router(auth_router, prefix="/auth")
app.include_router(pos_router, prefix="/positions")
app.include_router(ticker_router, prefix="/tickers")
Base.metadata.create_all(bind=engine) # 
init_db.initialize_data() # load test data (render is redeploying everything) # this will be removed later