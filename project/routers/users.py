from fastapi import HTTPException, APIRouter, status, Response, Depends
from fastapi.security import HTTPBasicCredentials
from project.database import User
from project.schemas import UserRequestModel, UserResponseModel, ReviewResponseModel
from typing import List
from project.routers.common import get_current_user
import jwt

router = APIRouter(prefix='/users')

# response_model valida el model de respuesta
# automaticamente se serializa el modelo-objeto de respuesta para enviarlo en formato json
@router.post('', response_model = UserResponseModel)
async def create_user(user: UserRequestModel):
    
    if User.select().where(User.username == user.username).exists():
        return HTTPException(status.HTTP_409_CONFLICT, 'Username ya se encuentra en uso')
    
    hashed_password = User.create_password(user.password)
    
    
    user = User.create(
        username = user.username,
        password = hashed_password
    )
    
    # si queremos retornar el user directamente, desde el ORM Model de peewee
    # Para poder enviar objetos al cliente, DEBE SER UN DICT. Revisar schema
    return user
    
    # El modelo automaticamente se convierte a un dict
    # return UserResponseModel(id=user.id, username=user.username)

# HTTPBasicCredentials from FastAPI
# HTTPBasicCredentials tiene username y password
# Como http es stateless, debemos guardar la sesión en una cookie para enviar al cliente
# y que este no se tenga que volver a poner sus credenciales
# Para esto usamos el response de FastAPI
@router.post('/login', response_model = UserResponseModel)
async def login(credentials: HTTPBasicCredentials, response: Response):
    
    user = User.select().where(User.username == credentials.username).first()
    
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'User not found')
    
    # Como md5 es de una sola via, toca encode de credentials.password para compararla con la que está saved in BD
    if user.password != User.create_password(credentials.password):
        raise HTTPException(status.HTTP_409_CONFLICT, 'Password Error') 

    # Enviar cookies, podemos enviar varias
    response.set_cookie(key='user_id', value=user.id) # Debería de retornarse un token y relacionarlo con el user autenticado
    
    return user
# Chek this by using curl in bash like this:
# curl -X 'POST'   'http://127.0.0.1:8000/api/users/login'   -H 'accept: application/json'   -H 'Content-Type: application/json'   -d '{
#   "username": "string",
#   "password": "string"
# }' -i

# Response should be
# HTTP/1.1 200 OK
# date: Sat, 03 Jun 2023 04:43:55 GMT
# server: uvicorn
# content-length: 28
# content-type: application/json
# set-cookie: user_id=3; Path=/; SameSite=lax

# Get reviews from authenticated user
# user_id debe ser igual que el que seteamos en la cookie
# @router.get('/reviews', response_model=List[ReviewResponseModel])
# async def get_user_reviews(user_id: int = Cookie(None)):
#     user = User.select().where(User.id == user_id).first()
    
#     if user is None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, 'User not found')
    
#     # Puedo acceder a user.reviews porque en el modelo de peewee hay un backref="reviews"
#     return [user_review for user_review in user.reviews]

# WITH JWT

# El token viene del encabezado de la request que se le pasa a get_current_user
@router.get('/reviews', response_model=List[ReviewResponseModel])
async def get_user_reviews(user: User = Depends(get_current_user)):
    
    return [user_review for user_review in user.reviews]
    
