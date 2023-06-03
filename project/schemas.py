from pydantic import BaseModel, validator
from pydantic.utils import GetterDict
from typing import Any
from peewee import ModelSelect

# Convertir o Parsear Objecto de tipo Model de Pewee
# A un Dict válido para enviarlo como respuesta a nuestro cliente
# Esta clase sólo sirve para un Model de Peewee
# Si quisieramos hacer lo mismo con otro ORM, toca crear otro modelo
# Esta clase basicamente sirve para convertir modelo de Peewee a modelo de Pydantic
class PeeweeGetterDict(GetterDict):
    def get(self, key: Any, default: Any = None):
        
        res = getattr(self._obj, key, default)
        if isinstance(res, ModelSelect):
            return list(res)
        
        return res
    
class ResponseModel(BaseModel):
    # FastAPI por sí mismo no implementa ningún ORM
    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict # Llama esta clase para convertir el objeto Model de peewee a UserResponseModel        

class UserRequestModel(BaseModel):
    username: str
    password: str
    
    # método de clase para validación
    @validator('username')
    def username_validator(cls, username):
        if len(username) < 3 or len(username) > 50:
            raise ValueError('La lingitud debe encontrarse entre 3 y 50 caracteres.')
        
        return username
    

class UserResponseModel(ResponseModel):
    id: int
    username: str
    
# Movies
class MovieRequestModel(BaseModel):
    title: str
    
class MovieResponseModel(ResponseModel):
    id: int
    title: str
    
# Review

class ReviewValidator():
    @validator('score')
    def score_validator(cls, score):
        
        if score < 1 or score > 5:
            raise ValueError('El rango para score es de 1 a 5')
        
        return score
        
class ReviewRequestModel(BaseModel, ReviewValidator):
    movie_id: int
    review: str
    score: int
    
class ReviewResponseModel(ResponseModel):
    id: int
    movie: MovieResponseModel
    review: str
    score: int

class ReviewRequestPutModel(BaseModel, ReviewValidator):
    review: str
    score: int

