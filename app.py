# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


# Создали схему Movie
class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


# Создаем представлениe для всех фильмов
@movies_ns.route('/')
class MoviesView(Resource):
    def get(self):
        # Проверяем наличие ключей в url
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        # Если есть ключ director_id - получаем его и выводим список фильмов. Если список пустой - выводим "Empty"
        if director_id:
            movies = Movie.query.filter(Movie.director_id == director_id).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return 'Empty', 200
        # Если есть ключ genre_id - получаем его и выводим список фильмов. Если список пустой - выводим "Empty"
        elif genre_id:
            movies = Movie.query.filter(Movie.genre_id == genre_id).all()
            if movies:
                return movies_schema.dump(movies), 200
            else:
                return 'Empty', 200

        else:
            all_movies = Movie.query.all()
            return movies_schema.dump(all_movies), 200


# Создаем представление для фильма по его id
@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.filter(Movie.id == mid).one()
        return movie_schema.dump(movie), 200


if __name__ == '__main__':
    app.run(debug=True)
