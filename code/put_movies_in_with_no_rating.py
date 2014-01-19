import sys, os

SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
WEBSITEDIR = SCRIPTPOS + '../Web/'
sys.path.append(WEBSITEDIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Web.settings")


from base.models import Movie
from base.views import retrieve_movie_from_the_web

from django.db import transaction



@transaction.atomic
def put_in_with_no_rating(imdb_id):
    # parse the imdb page
    movie = retrieve_movie_from_the_web(imdb_id)
    # give it a not-rated rating
    movie.starRating = 0
    # save it
    movie.save()


if __name__ == '__main__':

    movielistfile = '../data/popular_movies_300.txt'

    with open(movielistfile, 'r') as movielist:
    
        for line in movielist:

            imdb_id = line.strip()
            # first check if it already exists.
            # we don't want to overwrite any ratings
            try:
                movie = Movie.objects.get(pk=imdb_id)
                
            except Movie.DoesNotExist:
                put_in_with_no_rating(imdb_id)

            else:
                # it's already in, don't worry about it
                pass

        



