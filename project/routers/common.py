import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from project.database import User
from fastapi import Depends, HTTPException, status


SECRET_KEY = 'whatrulookingat?'

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/api/auth')

# Days es cuándo expirará el token
def create_access_token(user, days=7):
    data = {
        'user_id': user.id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(days=days)
    }
    
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")

def decode_access_token(token):
    
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as err:
        print(err)
        # si por cualquier el razón el access token no puede ser decodificado
        # Ya sea porque ya caducó o el access token fue corrompido
        return None 

# Este token viene del encabezado de la request
def get_current_user(token: str = Depends(oauth2_schema)) -> User:
    data = decode_access_token(token)
    
    if data:
        return User.select().where(User.id == data['user_id']).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Access Token Invalid',
        )