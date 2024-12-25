from fastapi import FastAPI
from app.routes import auth_routes

app = FastAPI()

@app.get('/')
def welcome():
    return {'message': 'Welcome to the FastAPI Migration Learning!'}

app.include_router(auth_routes.auth_router)