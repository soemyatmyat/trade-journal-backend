## Description 
Back-end Trade journal for analyzing trading activites. 
```
server/
├── main.py           # Application entry point
├── redis.py   # Redis client initialization
├── database.py       # SQLALCHEMY session initialization
├── tickers/             
│   ├── __init__.py
│   ├── models.py     
│   └── router.py     
|   └── schemas.py  
|   └── service.py     
├── auth/             
│   ├── __init__.py
│   ├── models.py     
│   └── router.py     
|   └── schemas.py  
|   └── service.py     
├── positions/             
│   ├── __init__.py
│   ├── models.py     
│   └── router.py     
|   └── schemas.py  
|   └── service.py  
└── settings.py       # Initializer
└── .env              # Environment variables
└── Dockerfile         
└── README
```

## Iteration 0
- [X] UI Design Mockup 
- [X] SQLArchemy ORM + Pydamtic Schema Design 

## Iteration 0.1
- [X] User OAuth (JWT Token: Bearer)
- [X] Fast RESTful APIs (CRUD trade positions) 
- [X] Fast RESTful APIs (fetch last closing price from yahoo finance for trade positions) 
- [X] Setup CI/CD 

## Iteration 0.2
- [X] Revisit authentication flow of tokens (Register, Logout, Refresh Token)
- [X] Add test data for render
- [ ] Query Optimization 

## Iteration 0.3
- [X] Technical Indiators and metrics for stock analysis
  - [X] Volume, Average Volume, Market Cap
  - [X] Beta, PE, EPS
  - [ ] IV, HV, VWAP
  - [X] Put/Call Ratio = option_chain.puts['volume'].sum() / option_chain.calls['volume'].sum()
  - [X] Dividend (Dividend Rate=Dividends per Share (DPS), Dividend Yield, Ex Dividend Date)
  - [X] Upcoming Earnings Date 
- [X] Incorporate Redis cache for Stock Analysis 
  - [X] Fixed to work with or without Redis. Caching should not break the app.
- [X] Loggings or output streams should be handled by the execution environment, collated together with all other streams from the app, and routed to one or more final destinations for viewing and long-term archival. Source: [The Twelve-Factor App](https://12factor.net/logs)

## Interactive API Documments: 
- http://{localhost}:{port}/docs (by Swagger UI)
- http://{localhost}:{port}/redoc (by ReDoc)


## References 
- [OAuth 2.0](https://oauth.net/2/)

## Why FastAPI?
- Uses Starlette and Pydantic (validation, serializaiton/deserialization) under the hood for blazing-fast performance.
- Minimizes boilerplate with a simple declaration of routes and inputs.
- Automatic generation of OpenAPI schemas and docs.