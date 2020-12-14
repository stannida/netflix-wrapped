import imdb

def get_genres(name):
    genres = {}
    ia = imdb.IMDb()
    movies = ia.search_movie(name)
    _id = movies[0].movieID
    movie = ia.get_movie(_id)
    display(movie)
    if movie['genres']:
        return movie['genres']
    