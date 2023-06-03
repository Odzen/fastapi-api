from project.schemas import MovieRequestModel, MovieResponseModel
from project.database import Movie
from fastapi import APIRouter

router = APIRouter(prefix='/movies')

# Movies
@router.post('/', response_model= MovieResponseModel)
async def create_movie(movie: MovieRequestModel):
        
        movie = Movie.create(
            title = movie.title
        )
        
        return movie