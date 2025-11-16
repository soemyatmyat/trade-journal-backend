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

## How to Run Locally


### File Structure
```
server/
├── main.py           # Application entry point
├── core/
│   ├── settings.py   # Initializer
│   ├── database.py   # SQLALCHEMY session initialization
|   └── redis.py  
├── tickers/          # Stock Tickers Management (login not required)
│   ├── models.py     # database models 
|   ├── schemas.py    # Pydantic models for data validation & serialization
|   ├── service.py    # Business Logic     
|   ├── repository.py # Database CRUD operations    
│   └── router.py     # routes and wiring (request validation, dependency injection, response serialization)
├── auth/             # Users Management
│   ├── models.py     # database models
|   ├── schemas.py    # Pydantic models
|   ├── service.py    # Business Logic     
|   ├── repository.py # Database CRUD operations    
│   └── router.py     # routes and wiring  
├── positions/        # Positions Management     
│   ├── models.py     # database models
|   ├── schemas.py    # Pydantic models
|   ├── service.py    # Business Logic     
│   └── router.py     # routes and wiring
├── .env
├── requirements.txt
├── Dockerfile
└── README
```

### schema 
