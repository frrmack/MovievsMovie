""" Views for the base application """

from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse

from django.conf import settings

from django.views.generic import ListView, DetailView

from django.db import transaction

from base.models import Movie, Fight, Score, User

from datetime import datetime
from django.utils.timezone import utc

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

import json
from itertools import chain
import os, sys, shutil
# absolute path to this script
SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
sys.path.append(SCRIPTPOS+"/../code/")

import movie_search
from retrieve_movie_from_the_web import retrieve_movie_from_the_web


def now():
    return datetime.utcnow().replace(tzinfo=utc)


def home(request):
    """ Default view for the root """
    return render(request, 'base/home.html')


def logout(request):
    user = request.user
    auth_logout(request)
    err_title = 'Logged out'
    err_msg = 'User %s is logged out now.' % user
    return error_page(request, err_title, err_msg)


def redirect_to_login(next_url_name=None, args=None, kwargs=None):
    login_path = reverse('social:begin', args=('google-oauth2',))
    if next_url_name:
        next_path = '?next=%s' % reverse(next_url_name, args=args, kwargs=kwargs)
    else:
        next_path = ''
    return HttpResponseRedirect(login_path + next_path)


class RankingsView(ListView):

    context_object_name = "score_list"
    template_name = "base/movie_list.html"

    def get_queryset(self):
        return Score.objects.filter(user=self.request.user).exclude(starRating=0).order_by('-mu')

    def dispatch(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated():
            return redirect_to_login('movie_list')

        if not self.get_queryset():
            err_title = 'No movies rated'
            err_msg = 'You did not rate any movies, so there are ' + \
                      'no movies to list.\n\n You can rate some ' + \
                      'at "<a href="/rate">Rate Movies</a>" or ' +\
                      'by using the search bar to find a movie ' + \
                      'and clicking on the stars in its page.'
            return error_page(request, err_title, err_msg)

        else:
            return super(RankingsView, self).dispatch(request, *args, **kwargs)


class RateMoviesView(ListView):

    context_object_name = "movies_to_rate"
    template_name = "base/rate_movies.html"

    def get_queryset(self):
        # movies not rated yet
        not_rated = Movie.objects.exclude(score__user=self.request.user.id).order_by('?')
        # movies rated 0 stars
        rated_0 = Movie.objects.filter(score__user=self.request.user.id, score__starRating=0).order_by('?')
        # chain these together and return them
        # (as a list so the template can iterate over them multiple times)
        return list(chain(not_rated, rated_0))
            
    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            return redirect_to_login('rate_movies')

        # check if there are any not-rated movies in the db
        if not self.get_queryset():
            
            err_title = 'No movies to rate'
            err_msg = 'You already rated all of the available (most popular) ' + \
                      'movies, but you can find and rate more using the search bar.'
            return error_page(request, err_title, err_msg)

        else:
            return super(RateMoviesView, self).dispatch(request, *args, **kwargs)



class MovieDetailView(DetailView):

    model = Movie
    template_name = "base/movie_detail.html"

    def get_object(self, *args, **kwargs):

        # GET MOVIE
        try:
            # get it from the db
            movie = super(MovieDetailView, self).get_object()

        except Http404:
            # not in the db
            imdb_id = self.request.path.strip('/')
            try:
                movie = retrieve_movie_from_the_web( imdb_id )
            except movie_search.NotFoundError:
                raise Http404( imdb_id )

        # GET SCORE
        try:
            # A) Already in the db, retrieve it
            score = Score.objects.get(user=self.request.user, movie=movie)
            print 'found old score in the database'
            
        except Score.DoesNotExist:
            # B) Not in the db, saving it for the first time
            score = Score(user=self.request.user,
                          movie=movie)
            print 'created new score'

        return score
                

    def dispatch(self, request, *args, **kwargs):

        if not request.user.is_authenticated():
            return redirect_to_login('movie_detail', args=args, kwargs=kwargs)

        try:
            return super(MovieDetailView, self).dispatch(request, *args, **kwargs)

        except Http404 as e:
            imdb_id =  request.path.strip('/')
            err_title = 'Movie not found'
            err_msg = 'There is no movie with the id ' +\
                      '<strong>%s</strong>.\n\n' % (imdb_id) +\
                      'You can try searching a movie by name, ' +\
                      '(or even id) through the search bar. ' +\
                      'This can help you find what you are looking ' +\
                      'for, even if you don\'t know the name/id exactly.'
            return error_page(request, err_title, err_msg)
        

    def get_context_data(self, **kwargs):
        score = kwargs['object']
        movie = score.movie
        # Call the base implementation first to get a context
        context = super(MovieDetailView, self).get_context_data(**kwargs)
        # Add in a poster url
        context['score'] = score
        context['movie'] = movie
        context['poster_url'] = "%sposters/%s" % (settings.STATIC_URL,
                                                  movie.poster_name) 
        return context



def error_page(request, title, message):

    message = message.replace('\n','<br>')
    context = {'error_title': title,
               'error_message': message}
    return render(request, 'base/error_message.html', context)




def search(request):

    if not request.user.is_authenticated():
        return redirect_to_login()

    query = request.GET['query']

    try:
        # google search within the imdb.com domain
        title, content, url = movie_search.find(query)
        if movie_search.get_imdb_type(url) != "title":
            raise movie_search.NotFoundError
        imdb_id = movie_search.get_imdb_id(url)

    except movie_search.NotFoundError:

        # either no search result returned, or the returned
        # result is not a title (but an actor, character, etc.)
        err_title = 'Not found'
        err_msg = 'No movie matching the query "%s" was found.' % query
        return error_page(request, err_title, err_msg)

    else:

        # check if the found movie is already in the db
        try:
            # A) already in the db, show it
            movie = Movie.objects.get(pk=imdb_id)

        except Movie.DoesNotExist:

            # B) not in the db, parse the imdb page
            movie = retrieve_movie_from_the_web(imdb_id)

        # from our db or imdb, we have a poster
        # put together the url for it
        poster_url = '%sposters/%s' % (settings.STATIC_URL,
                                       movie.poster_name)


        # now we have a movie (and a poster), either retrieved from our db
        # or parsed from imdb. Show its details. Render, baby, render.
        #
        # [If the rating is changed in this view, the movie will be saved.
        #  If it was already in our db, only the score will change. If it
        #  wasn't in there, it will get in at this point. This is handled by
        #  the save_movie_rating view.]

        # GET SCORE
        try:
            # A) Already in the db, retrieve it
            score = Score.objects.get(user=request.user.id, movie=movie)
            print 'found old score in the database'
            print score.unicode_score()
            
        except Score.DoesNotExist:
            # B) Not in the db, saving it for the first time
            score = Score(user=request.user,
                          movie=movie)
            print 'created new score', score.unicode_score()
        
            
        context = {'score' : score,
                   'movie' : movie,
                   'poster_url': poster_url}

        return render(request, 'base/movie_detail.html', context)


@transaction.atomic
def save_movie_rating(request, movie_id):

    if not request.user.is_authenticated():
        return redirect_to_login('save_rating', args=args, kwargs=kwargs)

    rating = request.POST['rating']
    name = request.POST['name']

    # Check if the movie is already in the db
    try:
        # A) Already in the db, retrieve it
        movie = Movie.objects.get(pk=movie_id)
        print 'retrieved %s from database' % name

    except Movie.DoesNotExist:
        # sB) Not in the db, saving it for the first time
        movie = Movie(imdb_id = request.POST['imdb_id'],
                      name= request.POST['name'],
                      year= request.POST['year'],
                      director= request.POST['director'],
                      description= request.POST['description'],
                      poster_name = request.POST['poster_name'])
        # no need for this (below) anymore, I stopped doing a tmp download
        # --------------------------------------------------------
        # tmp_poster = os.path.join(settings.PROJECT_ROOT,
        #                           'base/static/posters/tmp.jpg')
        # permanent_poster = os.path.join(settings.PROJECT_ROOT,
        #                                 'base/static/posters/%s' \
        #                                 % request.POST['poster_name'])
        # shutil.copy(tmp_poster, permanent_poster)
        print 'initialized new model for %s' % name
        # save it!
        movie.save()

    # Check if the score is already in the db
    try:
        # A) Already in the db, retrieve it
        score = Score.objects.get(user=request.user.id, movie=movie)
        print 'found old score in the database'

    except Score.DoesNotExist:
        # B) Not in the db, saving it for the first time
        score = Score(user=request.user,
                      movie=movie)

    # set the rating and save
    score.starRating = int(rating)
    score.mu = float(rating)
    score.sigma = score.star_seeded_sigma
    score.save()
    print 'saved new rating %s for %s' % (rating, name)

    # done
    return HttpResponse(json.dumps({'rating': rating}),
                        content_type="application/json")



def fight(request, movie_1_id=None, movie_2_id=None):

    # Choose movie 2 randomly if the same id is given
    # manually for both fighters. Can't fight yourself!
    if movie_1_id == movie_2_id and movie_2_id != None:
        movie_2_id = None        

    # Decide on lock based on the arguments:
    # default is no lock
    if movie_1_id != None and movie_2_id == None:
        lock = '1'
        lock_id = movie_1_id
        redir_kwargs = {'movie_1_id': movie_1_id}
    elif movie_1_id == None and movie_2_id != None:
        lock = '2'
        lock_id = movie_2_id
        redir_kwargs = {'movie_2_id': movie_2_id}
    else:
        lock = '0'
        lock_id = None
        redir_kwargs = {}

    if not request.user.is_authenticated():
        return redirect_to_login('fight', kwargs=redir_kwargs)

    if request.user.score_set.count() < 2:

        err_title = 'No movies to fight'
        err_msg = 'You did not rate any movies, so there are ' + \
                  'no movies to fight against each other.\n\n' + \
                  'A fight is only meaningful between movies ' + \
                  'you have seen. Without rated movies, it is ' + \
                  'impossible to know which ones you did see. ' + \
                  'Also, the first step for finding how a movie ' + \
                  'ranks for you among others is to give it a ' + \
                  'star rating.\n\n' + \
                  'You can rate movies ' + \
                  'at "<a href="/rate">Rate Movies</a>" or ' +\
                  'by using the search bar to find a movie ' + \
                  'and clicking on the stars in its page.'
        return error_page(request, err_title, err_msg)



    # For now, choose random fights
    try:
        if lock in ('1', '2'):
            locked_movie = get_object_or_404(Movie, pk=lock_id)
        else:
            locked_movie = Score.randoms.random(filter={'user':request.user.id}, exclude={'starRating':0}).movie
        print 'locked', locked_movie.name
        try:
            rival_movie = locked_movie.not_fought_opponents(request.user)[0]
            
        except IndexError:
            print 'No movie found that %s did not fight before' % locked_movie.name
            rival_movie = locked_movie.fought_opponents(request.user)[0]


        print 'rival', rival_movie.name


        if lock in ('1', '0'):
            movie1 = locked_movie
            movie2 = rival_movie
        else:
            movie1 = rival_movie
            movie2 = locked_movie
            
    except Http404:

        # could not find a movie with the given id value
        err_title = 'No movie with this id'
        err_msg = 'You wanted a movie to fight, but this movie ' +\
                  'is not among the movies you rated here.\n\n' +\
                  'Unless there is something wrong, you should only ' +\
                  'see this if you typed in a specific id in the ' +\
                  'fight url that doesn\'t correspond to any rated ' +\
                  'movie in the database.\n\n' +\
                  'Either there is a typo in the id, or you need to ' +\
                  'rate it first. In the latter case, you can put the ' +\
                  'id in the search bar to see the details of the movie ' +\
                  'and rate it.'
        return error_page(request, err_title, err_msg)

    else:

        # retrieve the previous score of this match-up if there was one
        movie1.note = '&nbsp;'
        movie2.note = '&nbsp;'
        draw_note = '&nbsp;'
        try:
            previous_fights = Fight.objects.filter(user=request.user).filter(contestants=movie1).filter(contestants=movie2)

            # by design we allow a single fight between two anyway, last fight
            # overrides the previous one, so this set should only have a single
            # fight if it's not empty
            last_round = previous_fights[0]

            if last_round.isDraw():
                draw_note = 'Previously drawn'
            else:
                for movie in movie1, movie2:
                    if movie == last_round.winner():
                        movie.note = 'Previous winner'
                
        except IndexError:
            # They did not match up before
            pass
        
        # render                                                                                                                                                                         
        context = {'movie1' : movie1,
                   'movie2' : movie2,
                   'lock'   : lock,
                   'draw_note': draw_note,
               }
        return render(request, 'base/fight.html', context)

@transaction.atomic
def fight_result(request, movie_1_id, movie_2_id, lock):

    if not request.user.is_authenticated():
        args = (movie_1_id, movie_2_id, lock)
        return redirect_to_login('fight_result', args=args)

    # get the movies                                                                                                                                                                 
    movie1 = get_object_or_404(Movie, pk=movie_1_id)
    movie2 = get_object_or_404(Movie, pk=movie_2_id)
    # get the user
    user = request.user
    # get the posted result                                                                                                                                                          
    result = request.POST['result']
    # a result of -1 means "skip", no recording
    # in that case. Only record a valid result
    if int(result) in (0,1,2):
        #                                                                                                                                                                                
        # ~~~~Design choice~~~~~~~~~~~~~                                                                                                                                                 
        # When two movies that were previously compared are compared again,                                                                                                              
        # we will not treat is as another match. Instead of multiple matches,                                                                                                            
        # we will have a single result for any given pair. This is to allow                                                                                                              
        # changes in opinion to have a more immediate effect, to remove                                                                                                                  
        # any confusion as to preferences between any two movies, and to keep                                                                                                            
        # the database compact, simple and straightforward.                                                                                                                              
        #                                                                                                                                                                                
        # Temporarily, score will be changed by a single update (as if                                                                                                               
        # there have been multiple matches), but this will be corrected when                                                                                                             
        # The main way of calculating TrueSkill is going over the entire chain                                                                                                           
        # of Fights from scratch.                                                                                                                                                 
        # ~~~~~~~~~~~~~~~~                                                                                                                                                               
        #                                                                                                                                                                                
        # find the fight if these two movies were compared before                                                                                                                        
        # or create a new fight
        try:
            fight = Fight.objects.filter(
                                       user=user
                                        ).filter(
                                       contestants=movie1
                                       ).filter(
                                       contestants=movie2
                                       ).get()
            # make sure the movies are in the right order                                                                                                                                
            # so that the result integer is accurate                                                                                                                                     
            fight.movie1, fight.movie2 = movie1, movie2
        except Fight.DoesNotExist:
            # match not in database, create a new match                                                                                                                                  
            fight = Fight(user=user,
                          movie1=movie1,
                          movie2=movie2)
        # record the result                                                                                                                                                              
        fight.result = result
        # record the date and time (this is not necessary if a new match                                                                                                                 
        # is created, since this is done by default, but it is necessary                                                                                                                 
        # if an old match is retrieved.                                                                                                                                                  
        fight.timestamp = now()
        # put the match in the database                                                                                                                                                  
        fight.save()
        # --end of recording (end of if)

    # pick new movies to fight and redirect to the fight                                                                                                                                                         
    new_fighters = {}
    if lock == '1':
        new_fighters['movie_1_id'] = movie_1_id
        name = 'fight_a'
    elif lock == '2':
        new_fighters['movie_2_id'] = movie_2_id
        name = 'fight_b'
    else:
        name = 'fight'
    return HttpResponseRedirect(reverse(name, kwargs=new_fighters))



def taste_profile(request):

    if not request.user.is_authenticated():
        return redirect_to_login('taste_profile')

    if not Score.objects.filter(user=request.user.id).exclude(starRating=0):
        err_title = 'No movies rated'
        err_msg = 'You did not rate any movies, so there are ' + \
                  'no movies to build a taste profile from.\n\n ' +\
                  'You can rate some ' + \
                  'at "<a href="/rate">Rate Movies</a>" or ' +\
                  'by using the search bar to find a movie ' + \
                  'and clicking on the stars in its page.'
        return error_page(request, err_title, err_msg)

    return bubbleChart(request, 
                       order_rule='ordered_by_rating')
    # err_title = 'Coming soon'
    # err_msg = 'Taste Profile is under construction, ' +\
    #           'it will be opened soon.\n\n' +\
    #           'Here you will be able to see how much you like ' +\
    #           'each genre, your favorite directors, cyclic wins ' +\
    #           'in your fights (a>b>c>a) and other fun analyses ' +\
    #           'of your taste.'
    # return error_page(request, err_title, err_msg)



def bubbleChart(request, order_rule='ordered_by_rating', num_nodes=None):
    # translate order_rule into django model api                                                                                                                                     
    order_query = {'random': '?',
                  'ordered_by_name': 'movie',
                  'ordered_by_rating': '-mu'
                  }[order_rule]

    # get all the score objects                                                                                                                                                      
    score_list = Score.objects.filter(user=request.user.id).exclude(starRating=0).order_by(order_query)
    print 'score_list', score_list

    # convert num_nodes into a sane integer                                                                                                                                          
    max_num_nodes = len(score_list)
    try:
        num_nodes = int(num_nodes)
        if num_nodes <= 0: num_nodes = max_num_nodes
    except TypeError:
        num_nodes = max_num_nodes

    # slice the first num_nodes movies                                                                                                                                               
    if 0 < num_nodes < len(score_list):
        score_list = score_list[:num_nodes]

    # render                                                                                                                                                                         
    context = {'score_list' : score_list,
               'order_rule' : order_rule,
               'num_nodes': num_nodes,
               'max_num_nodes': max_num_nodes
               }
    #return render(request, 'base/rating_bubble_chart.html', context)
    return render(request, 'base/taste_profile.html', context)
