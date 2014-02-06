from django.core.management.base import BaseCommand, CommandError

from base.models import Movie

from django.db import transaction

# absolute path to this script
import os.path, sys
SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
sys.path.append(SCRIPTPOS+"../../../code/")

from retrieve_movie_from_the_web import retrieve_movie_from_the_web


@transaction.atomic
def put_movie_in(imdb_id, popularity_rank):
    # parse the imdb page
    movie = retrieve_movie_from_the_web(imdb_id)
    # set popularity
    movie.popularity = popularity_rank
    # save it
    movie.save()


@transaction.atomic
def set_popularity(imdb_id, popularity_rank):
    movie = Movie.objects.get(pk=imdb_id)
    movie.popularity = popularity_rank
    movie.save()


class Command(BaseCommand):
    args = '<movielistfile> (each line is an id)'
    help = 'save movie info and poster in the db.'

    def handle(self, movielistfile, **options):

        with open(movielistfile, 'r') as movielist:
            lines = movielist.readlines()
            
        popularity_rank = len(lines)
        for line in lines:

            imdb_id = line.strip()
            # first check if it already exists.
            # we don't want to overwrite any ratings
            try:
                set_popularity(imdb_id, popularity_rank)

            except Movie.DoesNotExist:
                put_movie_in(imdb_id, popularity_rank)

            else:
                # it's already in, don't worry about it
                pass

            popularity_rank -= 1

