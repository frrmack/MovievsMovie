from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from random import randint

from datetime import datetime
from django.utils.timezone import utc

def now():
    return datetime.utcnow().replace(tzinfo=utc)


import HTMLParser


class RandomManager(models.Manager):
    def random(self):
        count = self.aggregate(count=models.Count('imdb_id'))['count']
        if count == 0:
            raise self.model.DoesNotExist("There is not a single %s to pick randomly." % self.model.__name__)
        random_index = randint(0, count-1)
        return self.all()[random_index]



class Movie(models.Model):

    imdb_id = models.CharField(max_length=255, primary_key=True)

    name = models.CharField(max_length=500)
    year = models.CharField(max_length=100, default="N/A")
    director = models.CharField(max_length=500, default="N/A")
    description = models.TextField(default="N/A")

    starRating = models.IntegerField(default=0)

    rawTrueSkillMu = models.FloatField(default=3.0)
    rawTrueSkillSigma = models.FloatField(default=1.0)
    starSeededTrueSkillMu = models.FloatField(default=3.0)
    starSeededTrueSkillSigma = models.FloatField(default=1.0)

    poster_name = models.CharField(max_length=255, default="_empty_poster.jpg")

    objects = models.Manager()
    randoms = RandomManager()

    class Meta:
        ordering = ["name", "-starRating"]

    def unicode_star_rating(self):
        return u'\u2605' * self.starRating

    unicode_star_rating.admin_order_field = 'starRating'
    unicode_star_rating.short_description = 'Star Rating'


    def raw_true_skill(self):
        return u'%.2f  \u00B1 %.1f' % (self.rawTrueSkillMu, 2*self.rawTrueSkillSigma)

    raw_true_skill.admin_order_field = 'rawTrueSkillMu'
    
    def seeded_true_skill(self):
        return u'%.2f  \u00B1 %.1f' % (self.starSeededTrueSkillMu, 2*self.starSeededTrueSkillSigma)

    seeded_true_skill.admin_order_field = 'starSeededTrueSkillMu'


    def readable_name(self):
        """
        Name with the html entities like &nbsp;
        converted to ascii
        """
        h = HTMLParser.HTMLParser()
        return h.unescape(self.name) 

    readable_name.admin_order_field = 'name'
    readable_name.short_description = 'Title'
    

    def won_against(self):
        """
        The opponents this guy has won a VersusMatch against
        """
        matches = self.versusmatch_set.all()
        did_I_win = lambda match: match.winner() == self
        matches_won = filter(did_I_win, matches)
        return [match.loser() for match in matches_won]

    def drawn_with(self):
        """
        The opponents this guy has drawn in a VersusMatch with
        """
        matches = self.versusmatch_set.all()
        did_I_draw = lambda match: match.isDraw()
        matches_drawn = filter(did_I_draw, matches)
        drawn_opponents = []
        for match in matches_drawn:
            opponent = match.contestants.exclude(id=self.id)
            drawn_opponents.append(opponent)
        return drawn_opponents

    def lost_to(self):
        """
        The opponents this guy has lost a VersusMatch to
        """
        matches = self.versusmatch_set.all()
        did_I_lose = lambda match: match.loser() == self
        matches_lost = filter(did_I_lose, matches)
        return [match.winner() for match in matches_lost]

        


    def __unicode__(self):
        return self.readable_name()


class VersusMatch(models.Model):
    """ The Result of a Movie vs Movie Comparison
        Result legend:
        0    it's a draw
        1    movie1 wins
        2    movie2 wins
    """

    movie1 = models.ForeignKey(Movie, related_name='movie_1')
    movie2 = models.ForeignKey(Movie, related_name='movie_2')
    timestamp  = models.DateTimeField(default=now)
    result = models.IntegerField(default=-1)

    # A list of the two compared movies
    # 1) Lets Movies reach all matches they were involved in
    # 2) Allows more straightforward queries for matches
    #    (since order of movie1 and movie2 shouldn't matter)
    contestants = models.ManyToManyField(Movie)

    def winner(self):
        if self.result == 0:
            return None
        elif self.result == 1:
            return self.movie1
        elif self.result ==2:
            return self.movie2

    def loser(self):
        if self.result == 0:
            return None
        elif self.result == 1:
            return self.movie2
        elif self.result ==2:
            return self.movie1

    def isDraw(self):
        return not bool(self.result)

    isDraw.boolean = True
    isDraw.short_description = "Draw?"


    def save(self, *args, **kwargs):
        # When you save, make sure contestants is
        # the two compared movies
        super(VersusMatch, self).save(*args, **kwargs)
        self.contestants = [self.movie1, self.movie2]

    def report(self):
        name1 = self.movie1.readable_name()
        name2 = self.movie2.readable_name()
        announcement = {1: "%s beats %s" % (name1, name2),
                        2: "%s loses to %s" % (name1, name2),
                        0: "%s and %s draw" % (name1, name2)
                        }
        return announcement[self.result]

    def __unicode__(self):
        return self.report()


