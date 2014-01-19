import sys, os

SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
WEBSITEDIR = SCRIPTPOS + '../Web/'
sys.path.append(SCRIPTPOS)
sys.path.append(WEBSITEDIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Web.settings")


import movie_search
from base.models import Movie

from django.conf import settings


def retrieve_movie_from_the_web(imdb_id):

    # connect and parse the imdb page
    url = movie_search.get_imdb_url(imdb_id)
    soup = movie_search.connect(url)
    name, year, director = movie_search.parse_name_year_director(soup)
    description = movie_search.parse_description(soup).replace('\n', ' ')

    # download the poster temporarily (if there is a poster)
    try:
        imdb_poster_url = movie_search.parse_poster_url(soup)
        
    except movie_search.NotFoundError:

        poster_name = '_empty_poster.jpg'
        
    else:

        poster_name = '%s.jpg' % imdb_id
        poster_location = os.path.join(settings.PROJECT_ROOT,
                                       'base/static/posters/%s' % poster_name)
        if not os.path.isfile(poster_location):
            # download poster if you haven't already
            movie_search.download(imdb_poster_url, poster_location)

    # create and return model instance
    movie = Movie(imdb_id = imdb_id,
                  name=name,
                  year=year,
                  director=director,
                  description=description,
                  poster_name=poster_name)

    return movie
