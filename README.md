## Description 
Trade journal for recording trading activites. It has never been easy to track your trading activites. 

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
- [ ] Query Optimization 
- [ ] 
- [ ] 

## Interactive API Documments: 
- http://127.0.0.1:8000/docs (by Swagger UI)
- http://127.0.0.1:8000/redoc (by ReDoc)


## References 
- [OAuth 2.0](https://oauth.net/2/)

## Why FastAPI?
- Uses Starlette and Pydantic (validation, serializaiton/deserialization) under the hood for blazing-fast performance.
- Minimizes boilerplate with a simple declaration of routes and inputs.
- Automatic generation of OpenAPI schemas and docs.
