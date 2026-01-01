# Trade Journal API 

## Description 
Trade Journal API is a personal modular project built with FastAPI application to help track and analyze trading performance. The project includes structured modules for trades, positions, and performance analytics, following clean architecture principles with SQLAlchemy, Pydantic models, and dependency-injected database sessions. It provides endpoints to record trades, manage open and closed positions, and review historical data for self-evaluation.

**Tech Stack**
- FastAPI – High-performance web framework for building APIs
- SQLAlchemy – ORM for database interaction
- SQLite – Lightweight relational database for local storage
- Pydantic – Data validation and serialization
- Docker (optional) – Containerization for easy deployment
- Uvicorn – ASGI server for running the application

## Features 

### Basic Features 
| Feature                         | Status | Notes                                                                 |
|---------------------------------|--------|-----------------------------------------------------------------------|
| **JWT Authentication**          | ✅     | Access token in `Authorization` header; refresh token in cookie      |
| **Refresh Token in Cookie**     | ✅     | Stored in `HttpOnly` cookie to prevent JavaScript access             |
| **CSRF Protection**             | ✅     | CSRF token in cookie + `X-CSRF-Token` header                |
| **Rate Limiting (per client)**  | ✅     | Sliding window; Redis-backed with SQLite fallback                    |
| **Custom Error Handling**       | ✅     | Clean JSON error responses with consistent structure                 |

---

### User Endpoints (Login Required)

**Docs**
- Swagger / OpenAPI: `{{base-url}}/docs#/`
- Redoc: `{{base-url}}/redoc`

### Security

#### JWT Authentication
- **Access Token** must be sent via the `Authorization: Bearer <token>` header for every requests.
- **Refresh Token** is send and receive in an `HttpOnly` cookie - this prevents access from JavaScript, helping mitigate **XSS attacks**.

#### CSRF Protection
- A **CSRF token** will be issued as a normal (non-HttpOnly) cookie.
- The requests must send this token back in the `X-CSRF-Token` header for `/auth/refresh`. This is to provent **Cross-Site Request Forgery** attacks.
- The domain name must be set as an environment variable to share across sub domains.

#### Example using `curl` (adapt accordingly for client calls):
```bash
# authenticate and store the http cookies into txt
curl --verbose -c cookies.txt https://localhost:<port>/auth/token \
  -d 'username=<api-key>&password=<password>'

# Use stored cookie and send CSRF token in header
curl --verbose -b cookies.txt -c cookies.txt -X POST \
  https://localhost:<port>/auth/refresh \
  -H "X-CSRF-Token: <csrf-token>"
```

## How to Run Locally

1. Clone the repository:
  ```bash
  git clone <repo-url>
  cd server
  ```
2. Create a python virtual environment and activate it:
  ```bash
  python3 -m venv venv
  . venv/bin/activate
  ```
2. Install the dependencies: 
  ```bash
  pip install -r requirements.txt
  ```
3. Set up environment variables in a `.env` file (example):
  ```
  # ============================
  # Environment Constants
  # ============================
  ORIGINS="abc,def"
  SQLALCHEMY_DATABASE_URL=sqlite:///./<your-sqlite3>.db
  SECRET_KEY="<your-secret-key>"
  ALGORITHM="<your-jwt-algorithm>"
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  COOKIE_SECURE=True  # Set to True if using HTTPS
  COOKIE_DOMAIN=""  # Domain for the cookie, require this for cookies shared across subdomains

  # ============================
  # Redis Constants
  # ============================
  REDIS_URL="<redis-url>"                     # Optional: the hostname/IP address of your Redis server for caching. If not defined, cache falls back to SQLite. This is for rate-limiting. If redis is not available, rate-limit falls back to sql. 
  REDIS_PASSWORD="<redis-pass>"               # If Redis requires authentication, put the password here
  REDIS_PORT=6379
  REDIS_EX=600                                # Optional: Set the expiration time (in seconds) for Redis keys
  ```
4. Run the application with reload:
  ```bash
  uvicorn main:app --reload
  ```
  With local certs
  ```bash
  uvicorn main:app --host 127.0.0.1 --port 8000 --reload --ssl-keyfile=key.pem --ssl-certfile=cert.pem
  ```

The API will be available at `http://127.0.0.1:8000`.

### File Structure
```
server/
├── main.py           # Application entry point
├── auth/             # Users Management
│   ├── token.py     # manage the token lifecycle
│   ├── models.py     # database models
|   ├── schemas.py    # Pydantic models
|   ├── service.py    # Business Logic     
|   ├── repository.py # Database CRUD operations    
│   └── router.py     # routes and wiring  
├── tickers/          # Stock Tickers Management (login not required)
│   ├── models.py     # database models 
|   ├── schemas.py    # Pydantic models for data validation & serialization
|   ├── service.py    # Business Logic     
|   ├── repository.py # Database CRUD operations    
│   └── router.py     # routes and wiring (request validation, dependency injection, response serialization)
├── positions/        # Positions Management     
│   ├── models.py     # database models
|   ├── schemas.py    # Pydantic models
|   ├── service.py    # Business Logic     
│   └── router.py     # routes and wiring
├── core/
│   ├── settings.py   # Initializer
│   ├── database.py   # SQLALCHEMY session initialization
|   └── redis.py  
├── .env
├── requirements.txt
├── Dockerfile
└── README
```



## References  
This project follows: 
1. 
