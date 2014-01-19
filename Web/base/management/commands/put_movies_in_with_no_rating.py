from django.core.management.base import BaseCommand, CommandError

from base.models import Movie

from django.db import transaction

# absolute path to this script
import os.path, sys
SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
sys.path.append(SCRIPTPOS+"../../../../code/")

from retrieve_movie_from_the_web import retrieve_movie_from_the_web



@transaction.atomic
def put_in_with_no_rating(imdb_id):
    # parse the imdb page
    movie = retrieve_movie_from_the_web(imdb_id)
    # give it a not-rated rating
    movie.starRating = 0
    # save it
    movie.save()


class Command(BaseCommand):
    args = '<movielistfile> (each line is an id)'
    help = 'save movie info and poster in the db, with no rating.'

    def handle(self, movielistfile, **options):

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

