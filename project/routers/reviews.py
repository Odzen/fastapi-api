from fastapi import HTTPException, status, APIRouter, Depends
from project.database import User, Movie, UserReview
from project.schemas import ReviewRequestModel, ReviewResponseModel, ReviewRequestPutModel
from typing import List
from project.routers.common import get_current_user

router = APIRouter(prefix='/reviews')

# page and limit are by default put into the url as query strings
# /reviews?page=1&limit=10    
@router.get('/', response_model= List[ReviewResponseModel])
async def get_reviews(page: int = 1, limit: int = 10):
    reviews = UserReview.select().paginate(page, limit)  # Select * FROM user_reviews;   
    
    # No puedo retornar return reviews, porque sale error ya que reviews no es de tipo List
    
    # Toca hacer un list comprehension or parse a list las reviews de la sigiente forma
    return [user_review for user_review in reviews]

@router.get('/{review_id}', response_model= ReviewResponseModel)
async def get_review_by_id(review_id: int):
    
    user_review = UserReview().select().where(UserReview.id == review_id).first()
    
    if user_review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    
    return user_review

@router.post('/', response_model= ReviewResponseModel)
async def create_review(user_review: ReviewRequestModel, user: User = Depends(get_current_user)):
    print(user.id)
    
    if User.select().where(User.id == user.id).first() is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if Movie.select().where(Movie.id == user_review.movie_id).first() is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Movie not found")
    
    
    user_review = UserReview.create(
        user_id = user.id, # Owner a quien pertenece el recurso
        movie_id= user_review.movie_id,
        review = user_review.review,
        score = user_review.score
    )
    
    return user_review

@router.put('/{review_id}', response_model= ReviewResponseModel)
async def update_review_by_id(review_id: int, review_request: ReviewRequestPutModel, user: User = Depends(get_current_user)):
    user_review = UserReview().select().where(UserReview.id == review_id).first()
    
    if user_review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    
    # Verify ownership
    if user_review.user_id != user.id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No eres el propietario")
    
    user_review.review = review_request.review
    user_review.score = review_request.score
    
    user_review.save()
    
    return user_review

@router.delete('/{review_id}', response_model= ReviewResponseModel)
async def delete_review_by_id(review_id: int,  user: User = Depends(get_current_user)):
    user_review = UserReview().select().where(UserReview.id == review_id).first()
    
    if user_review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")
    
    # Verify ownership
    if user_review.user_id != user.id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No eres el propietario")
    
    user_review.delete_instance()
    
    return user_review
    