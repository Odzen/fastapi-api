from peewee import PostgresqlDatabase, Model, CharField, DateTimeField, ForeignKeyField, TextField, IntegerField
from datetime import datetime
from hashlib import md5 

database = PostgresqlDatabase('fastapi-project', 
                              user='user', 
                              password='password', 
                              host='localhost', 
                              port='5432')

class User(Model):
    username = CharField(max_length=50, unique= True)
    password = CharField(max_length=50)
    created_at = DateTimeField(default=datetime.now())
    
    def __str__(self):
        return self.username
    
    # cls hace referencia a la clase perse
    @classmethod
    def authenticate(cls, username, password):
        user = cls.select().where(User.username == username).first()
        
        if user and user.password == cls.create_password(password):
            return user
        
    
    @classmethod
    def create_password(cls, password):
        md5().update(password.encode('utf-8'))
        
        return md5().hexdigest()
    
    class Meta:
        database = database
        table_name= 'users'
    

class Movie(Model):
    title =  CharField(max_length=50)
    created_at = DateTimeField(default=datetime.now())
    
    def __str__(self):
        return self.title
    
    class Meta:
        database = database
        table_name= 'movies'

# backref="reviews" significa que objectos de tipo User y Movie
# podrá acceder a sus reseñas sin problema
class UserReview(Model):
    user = ForeignKeyField(User, backref="reviews")
    movie = ForeignKeyField(Movie, backref="reviews")
    review = TextField()
    score = IntegerField()
    created_at = DateTimeField(default=datetime.now())
    
    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'
    
    class Meta:
        database = database
        table_name= 'reviews'