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
WEBSITEDIR = SCRIPTPOS + '../Website/'
sys.path.append(WEBSITEDIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieRatingsSite.settings")


from main.models import Movie, VersusMatch
import trueskill as ts



def update_true_skill(match, true_skill_dict):
    """ incremental TrueSkill update function after one match
    """
    TrueSkill = true_skill_dict
    if match.isDraw():
        id1, id2 = match.movie1.id, match.movie2.id
    else:
        id1, id2 = match.winner().id, match.loser().id
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
    for movie in Movie.objects.all():
        rawTS[movie.id] = ts.Rating(mu=3.0, sigma=1.0)
        seededTS[movie.id] = ts.Rating(mu=1.*movie.starRating, sigma=0.5)

    # iterate over matches (over time) and incrementally update
    # TrueSkill dictionaries    
    count = 0
    for match in sorted(VersusMatch.objects.all(),
                       key = lambda m: m.timestamp):
        count += 1
        update_true_skill(match, rawTS)
        update_true_skill(match, seededTS)
        if count % 100 == 0: print >> sys.stderr, '%i matches processed.' % count

    # record new ratings in the database
    count = 0
    for movie in Movie.objects.all():
        count += 1
        rawRating = rawTS[movie.id]
        seededRating = seededTS[movie.id]
        movie.rawTrueSkillMu = rawRating.mu
        movie.rawTrueSkillSigma = rawRating.sigma
        movie.starSeededTrueSkillMu = seededRating.mu
        movie.starSeededTrueSkillSigma = seededRating.sigma
        movie.save()
        if count % 100 == 0: print >> sys.stderr, '%i ratings recorded.' % count


if __name__ == '__main__':
    
    compute_true_skills()


