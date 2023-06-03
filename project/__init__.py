from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from project.database import database as connection
from project.database import User, Movie, UserReview
from fastapi.security import OAuth2PasswordRequestForm
from project.routers.common import create_access_token

from project.routers import user_router, reviews_router, movies_router

# Create servicio web
app = FastAPI(title="Project para reseñar peliculas",
              description="Este proyecto otorga la lógica para reseñar peliculas",
              version="0.1")

api = APIRouter(prefix='/api')

# Add rutas
# I can inlude routes inside other routes
api.include_router(user_router)
api.include_router(reviews_router)
api.include_router(movies_router)

# Validación de credenciales
# OAuth2PasswordRequestForm tiene username y password attributes
# OAuth2PasswordRequestForm es de forma application/x-www-form-urlencode
@api.post('/auth')
async def auth(data: OAuth2PasswordRequestForm = Depends()):
    user = User.authenticate(data.username, data.password)
    if user:
        return {
            'access_token':  create_access_token(user),
            'token_type': 'Bearer'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username or password incorrectos",
            headers={
                'WWW-Athenticate': 'Bearer'
            }
        )
    
app.include_router(api)

# Events
@app.on_event('startup')
def startup():
    """
    Function that executes when the server is about to start
    """
    if connection.is_closed():
        connection.connect()
        print("Connecting DB...")
    
    # Si las tablas ya existen, no pasa nada, si no existen hay que crearlas
    connection.create_tables([User, Movie, UserReview])

@app.on_event('shutdown')
def shutdown():
    """
    Function that executes when the server is about to finish
    """
    if not connection.is_closed():
        connection.close()

 # First route
 # Async -> Para poder procesar y resolver en dado caso que múltiples peticiones se realicen al mismo tiempo
 # de forma asíncrona
@app.get('/')
async def index():
    return 'Hi from dev, movies api'