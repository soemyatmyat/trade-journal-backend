## Description 
Trade journal for recording your trading activites. It's now always easy to track your trade performance. 

## Iteration 0
- [ ] UI Design Mockup 
- [ ] SQLArchemy ORM + Pydamtic Schema Design 
- [ ] 


## Iteration 0.1
- [ ] User OAuth 
- [ ] Fast REST API (CRUD positions) 
- [ ] FAST REST API (fetch price from yahoo finance) 
- [ ] VUE Boiler-plate 
- [ ] 

## Iteration 0.2
- [ ] Service Worker + manifest 
- [ ] Settings 


## API Documments: 
Interactive API docs:
http://127.0.0.1:8000/docs (by Swagger UI)

http://127.0.0.1:8000/redoc (by ReDoc)

uvicorn main:app -- reload

## References 

## Credits: 

## Registeration
In HTTP there are two ways to POST data: 
- application/x-www-form-urlencoded (This format is typically used when submitting form data from HTML forms. Form data is encoded as a query string with key-value pairs separated by &. Keys and values are URL-encoded, meaning special characters are replaced with % followed by their hexadecimal representation. Example: key1=value1&key2=value2and)
- multipart/form-data (Form data is split into multiple parts, each representing a form field or file.)

# Todo:
- [ ] need to check on the authentication flow of tokens 
- [ ] Tidy up the code (do we really need to check user for every API endpoints - seem like a waste of time)


# Why FastAPI?
- Uses Starlette and Pydantic (validation, serializaiton/deserialization) under the hood for blazing-fast performance.
- Minimizes boilerplate with a simple declaration of routes and inputs.
- Automatic generation of OpenAPI schemas and docs.
