import sys, os

SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
WEBSITEDIR = SCRIPTPOS + '../Web/'
sys.path.append(WEBSITEDIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Web.settings")


from main.models import Movie


allMovies = sorted(Movie.objects.all(),
                   key = lambda m: m.starRating,
                   reverse=True)

for movie in allMovies:
    asciiStars = '*' * movie.starRating
    print '%s\t%s\t%.2f +- %.2f\t%.2f +- %.2f' % (movie.name,
                                                  asciiStars,
                                                  movie.rawTrueSkillMu,
                                                  movie.rawTrueSkillSigma,
                                                  movie.starSeededTrueSkillMu,
                                                  movie.starSeededTrueSkillSigma,
                                                  )


