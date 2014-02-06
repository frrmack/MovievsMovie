from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from random import randint

from datetime import datetime
from django.utils.timezone import utc

from django.contrib.auth.models import User


def now():
    return datetime.utcnow().replace(tzinfo=utc)


import HTMLParser


class RandomManager(models.Manager):
    def random(self, skip_obj=None, filter=None, exclude=None):
        # skip_obj: You can give a model instance, and random
        # will return a random one, anything BUT this guy
        # (useful when you need a random guy outside myself, etc.)
        # exclude: a dict of exclude kwargs following Django DRM
        # filter: a dict of filter kwargs following Django DRM
        if exclude is None:
            objects = self
        else:
            objects = self.exclude( **exclude )
        if filter is not None:
            objects = objects.filter( **filter )

        #count = objects.aggregate(count=models.Count('imdb_id'))['count']
        count = objects.count()
        if count == 0 or (count == 1 and skip_obj is not None):
            raise objects.model.DoesNotExist("There is not a single %s to pick randomly." % objects.model.__name__)
        random_index = randint(0, count-1)
        lucky_guy = objects.all()[random_index]
        while lucky_guy == skip_obj:
            random_index = randint(0, count-1)
            lucky_guy = objects.all()[random_index]
        return lucky_guy


class Movie(models.Model):

    imdb_id = models.CharField(max_length=255, primary_key=True)

    name = models.CharField(max_length=500)
    year = models.CharField(max_length=100, default="N/A")
    director = models.CharField(max_length=500, default="N/A")
    description = models.TextField(default="N/A")

    # Aggregate score
    scoreMu = models.FloatField(default=3.0)
    scoreSigma = models.FloatField(default=1.0)

    poster_name = models.CharField(max_length=255, default="_empty_poster.jpg")

    objects = models.Manager()
    randoms = RandomManager()

    class Meta:
        ordering = ["name", "-scoreMu"]

    def conservative_score(self):
        return self.scoreMu - 2.* self.scoreSigma

    def unicode_score(self):
        return u'%.2f  \u00B1 %.1f' % (self.scoreMu, 2*self.scoreSigma)

    def readable_name(self):
        """
        Name with the html entities like &nbsp;
        converted to ascii
        """
        h = HTMLParser.HTMLParser()
        return h.unescape(self.name) 

    readable_name.admin_order_field = 'name'
    readable_name.short_description = 'Title'
    
    def did_already_fight(self, opponent):
        """
        Returns true if this movie had a previous
        fight with this opponent
        """
        prev_matches = Fight.objects.filter(user=user).filter(contestants=self).filter(contestants=opponent)
        return bool(prev_matches)

    def fought_opponents(self, user):
        fights = Fight.objects.filter(user=user).filter(contestants=self).order_by('?')
        fought = []
        for fight in fights:
            if self == fight.movie1:
                fought.append(fight.movie2)
            else:
                fought.append(fight.movie1)
        return fought

    def not_fought_opponents(self, user):
        potentials = Score.objects.filter(user=user).exclude(starRating=0).exclude(movie=self).order_by('?')
        fought = self.fought_opponents(user)
        not_fought = []
        for score in potentials:
            movie = score.movie
            if movie not in fought:
                not_fought.append(movie)
        return not_fought


    def won_against(self, user):
        """
        The opponents this guy has won a Fight against
        """
        matches = self.fight_set.filter(user=user)
        did_I_win = lambda match: match.winner() == self
        matches_won = filter(did_I_win, matches)
        return [match.loser() for match in matches_won]

    def drawn_with(self, user):
        """
        The opponents this guy has drawn in a Fight with
        """
        matches = self.fight_set.filter(user=user)
        did_I_draw = lambda match: match.isDraw()
        matches_drawn = filter(did_I_draw, matches)
        drawn_opponents = []
        for match in matches_drawn:
            opponent = match.contestants.exclude(id=self.id)
            drawn_opponents.append(opponent)
        return drawn_opponents

    def lost_to(self, user):
        """
        The opponents this guy has lost a Fight to
        """
        matches = self.fight_set.all()
        did_I_lose = lambda match: match.loser() == self
        matches_lost = filter(did_I_lose, matches)
        return [match.winner() for match in matches_lost]

    def __unicode__(self):
        return self.readable_name()



class Score(models.Model):
    """ A user's underlying score (bayesian model) for a movie
    """
    star_seeded_sigma = 0.5
    raw_sigma = 1.0

    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie)
    starRating = models.IntegerField(default=0)
    mu = models.FloatField(default=3.0)
    sigma = models.FloatField(default=1.0)

    objects = models.Manager()
    randoms = RandomManager()

    def movie_imdb_id(self):
        return self.movie.imdb_id

    def movie_name(self):
        return self.movie.name

    def unicode_star_rating(self):
        return u'\u2605' * self.starRating

    def unicode_score(self):
        return u'%.2f  \u00B1 %.1f' % (self.mu, 2*self.sigma)

    def __unicode__(self):
        return '%s -> %s: %s' % (self.user, self.movie.name, self.unicode_score())

    def conservative(self):
        return self.mu - 2.* self.sigma



class Fight(models.Model):
    """ The Result of a Movie vs Movie Comparison
        Result legend:
        0    it's a draw
        1    movie1 wins
        2    movie2 wins
    """

    user = models.ForeignKey(User)
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
        super(Fight, self).save(*args, **kwargs)
        self.contestants = [self.movie1, self.movie2]

    def report(self):
        name1 = self.movie1.readable_name()
        name2 = self.movie2.readable_name()
        announcement = {1: "[%s] beats [%s]" % (name1, name2),
                        2: "[%s] loses to [%s]" % (name1, name2),
                        0: "[%s] and [%s] draw" % (name1, name2)
                        }
        return announcement[self.result]

    def __unicode__(self):
        return u'<User %s: %s>' % (self.user, self.report())


