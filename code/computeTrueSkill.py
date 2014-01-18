# Starts from scratch, iterates over every match
# in the database, updates raw and starSeeded
# TrueSkill ratings foe every movie, then
# saves the mu and sigmas into the database
#
#
# This complete reset and recalculation of TrueSkill
# from the entire history of matches is necessary:
# At individual comparisons, TrueSkill is updated using
# the result of that match, BUT if it is not a new comparison,
# but revoting on a previously done comparison, the results
# will not be accurate. They won't be far from the actual
# results, but not 100% accurate. Since the design decision
# is made to treat every comparison with only a single outcome
# (and no repeat-matches), revoting on a match basically changes
# history (it deletes the old match from history). To find the
# accurate results with this change, a reset and recalculation
# is necessary. Of course, this 'revoting' should be a VERY RARE
# event, so running this script at a low frequency for corrections
# is completely fine.
#
#
# (This also gives a way to play with TrueSkill game parameters
# and see the final results.)
#



import sys, os

SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
WEBSITEDIR = SCRIPTPOS + '../Web/'
sys.path.append(WEBSITEDIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Web.settings")


from base.models import Movie, Fight
from django.db import transaction

import time

import trueskill as ts


def update_true_skill(match, true_skill_dict):
    """ incremental TrueSkill update function after one match
    """
    TrueSkill = true_skill_dict
    if match.isDraw():
        id1, id2 = match.movie1.imdb_id, match.movie2.imdb_id
    else:
        id1, id2 = match.winner().imdb_id, match.loser().imdb_id
    new_ratings = ts.rate_1vs1(TrueSkill[id1], TrueSkill[id2], drawn=match.isDraw())
    TrueSkill[id1], TrueSkill[id2] = new_ratings



def compute_true_skills():
    """ recalculate TrueSkills from the entire history of matches
    """
    # True Skill parameters for Movie ratings
    # Details and reasoning can be found at: 
    # https://www.evernote.com/Home.action#st=p&n=ea2365e1-fe1c-4f4c-97b6-18cf78431fa4
    ts.setup(mu=3.0, sigma=1.0, beta=0.3, tau=0.005, draw_probability=0.05)

    # initiate TrueSkill dictionaries
    rawTS, seededTS = {}, {}

    # initialize TrueSkill for each movie
    for value_dict in Movie.objects.values('imdb_id', 'starRating'):
        imdb_id = value_dict['imdb_id']
        starRating = value_dict['starRating']
        rawTS[imdb_id] = ts.Rating(mu=3.0, sigma=1.0)
        seededTS[imdb_id] = ts.Rating(mu=1.*starRating, sigma=0.5)

    # iterate over matches (over time) and incrementally update
    # TrueSkill dictionaries    
    count = 0
    for match in sorted(Fight.objects.all(),
                       key = lambda m: m.timestamp):
        count += 1
        update_true_skill(match, rawTS)
        update_true_skill(match, seededTS)
        if count % 100 == 0: print >> sys.stderr, '%i matches processed.' % count

    # record new ratings in the database
    count = 0
    for id_dict in Movie.objects.values('imdb_id'):
        count += 1
        imdb_id = id_dict['imdb_id']
        try:
            rawRating = rawTS[imdb_id]
            seededRating = seededTS[imdb_id]
        except KeyError:
            # this movie was just saved in between starting the TrueSkill
            # calculations and recording the results. we'll get it in the
            # next round.
            continue
        update_movie(imdb_id, rawRating, seededRating)
    print >> sys.stderr, '--- a total of %i ratings recorded. ---' % count


@transaction.atomic
def update_movie(imdb_id, rawRating, seededRating):
    movie = Movie.objects.get(imdb_id = imdb_id)
    movie.rawTrueSkillMu = rawRating.mu
    movie.rawTrueSkillSigma = rawRating.sigma
    movie.starSeededTrueSkillMu = seededRating.mu
    movie.starSeededTrueSkillSigma = seededRating.sigma
    movie.save()



if __name__ == '__main__':
    
    if len(sys.argv) > 1 and sys.argv[1] == '-c':
        # infinite loop
        while True:
            compute_true_skills()
            time.sleep(0.1)
    else:
            compute_true_skills()
        


