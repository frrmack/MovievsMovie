""" Views for the base application """

from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse

from django.conf import settings

from django.views.generic import ListView, DetailView

from base.models import Movie, Fight

from datetime import datetime
from django.utils.timezone import utc

import json

import os, sys, shutil
# absolute path to this script
SCRIPTPOS = os.path.abspath(__file__).rsplit('/',1)[0] + '/'
sys.path.append(SCRIPTPOS+"../../code/")
import movie_search

def now():
    return datetime.utcnow().replace(tzinfo=utc)


def home(request):
    """ Default view for the root """
    return render(request, 'base/home.html')


class MovieListView(ListView):

    context_object_name = "movie_list"
    queryset = Movie.objects.order_by('-starSeededTrueSkillMu')
    template_name = "base/movie_list.html"

    def dispatch(self, request, *args, **kwargs):
        # check if there is some video onsite
        if not self.get_queryset():
            
            err_title = 'No movies rated'
            err_msg = 'You did not rate any movies, so there are ' + \
                      'no movies to list.\n\n You can rate a movie by ' + \
                      'using the search bar to find it\'s detail page ' + \
                      'and clicking on the relevant amount ' +\
                      'of stars in the rating field.'
            return error_page(request, err_title, err_msg)

        else:
            return super(MovieListView, self).dispatch(request, *args, **kwargs)



class MovieDetailView(DetailView):

    model = Movie
    template_name = "base/movie_detail.html"

    def get_context_data(self, **kwargs):
        movie = kwargs['object']
        # Call the base implementation first to get a context
        context = super(MovieDetailView, self).get_context_data(**kwargs)
        # Add in a poster url
        context['poster_url'] = "%sposters/%s" % (settings.STATIC_URL,
                                                  movie.poster_name) 
        return context


def error_page(request, title, message):

    message = message.replace('\n','<br>')
    context = {'error_title': title,
               'error_message': message}
    return render(request, 'base/error_message.html', context)


def bubbleChart(request, order_rule='random', num_nodes=None):
    # translate order_rule into django model api                                                                                                                                     
    order_query = {'random': '?',
                  'ordered_by_name': 'name',
                  'ordered_by_rating': '-starRating'
                  }[order_rule]

    # get all the movie objects                                                                                                                                                      
    movie_list = Movie.objects.order_by(order_query)

    # convert num_nodes into a sane integer                                                                                                                                          
    max_num_nodes = len(movie_list)
    try:
        num_nodes = int(num_nodes)
        if num_nodes <= 0: num_nodes = max_num_nodes
    except TypeError:
        num_nodes = max_num_nodes

    # slice the first num_nodes movies                                                                                                                                               
    if 0 < num_nodes < len(movie_list):
        movie_list = movie_list[:num_nodes]

    # render                                                                                                                                                                         
    context = {'movie_list' : movie_list,
               'order_rule' : order_rule,
               'num_nodes': num_nodes,
               'max_num_nodes': max_num_nodes
               }
    return render(request, 'base/rating_bubble_chart.html', context)




def search(request):

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
            poster_to_show = movie.poster_name

        except Movie.DoesNotExist:

            # B) not in the db, parse the imdb page
            soup = movie_search.connect(url)
            name, year, director = movie_search.parse_name_year_director(soup)
            content = content[:-11] + '...'
            description = content.replace('\n', ' ')

            #    download the poster temporarily (if there is a poster)
            try:
                imdb_poster_url = movie_search.parse_poster_url(soup)
            except movie_search.NotFoundError:
                poster_name_in_db = '_empty_poster.jpg'
                poster_to_show = '_empty_poster.jpg'
            else:
                tmp_poster_file = os.path.join(settings.PROJECT_ROOT, 'base/static/posters/tmp.jpg')
                poster_name_in_db = '%s.jpg' % imdb_id
                movie_search.download(imdb_poster_url, tmp_poster_file)
                poster_to_show = "tmp.jpg"

            #    create model instance
            movie = Movie(imdb_id = imdb_id,
                          name=name,
                          year=year,
                          director=director,
                          description=description,
                          poster_name=poster_name_in_db)

        finally:
            # put together the url for the poster
            poster_url = '%sposters/%s' % (settings.STATIC_URL,
                                           poster_to_show)


        # now we have a movie (and a poster), either retrieved from our db
        # or parsed from imdb. Show its details. Render, baby, render.
        #
        # [If the rating is changed in this view, the movie will be saved.
        #  If it was already in our db, only the rating will change. If it
        #  wasn't in there, it will get in at this point. This is handled by
        #  the save_movie_rating view.]
            
        context = {'movie' : movie,
                   'poster_url': poster_url}

        return render(request, 'base/movie_detail.html', context)



def save_movie_rating(request, movie_id):

    rating = request.POST['rating']
    name = request.POST['name']

    # Check if the movie is already in the db
    try:
        # A) Already in the db, just change the rating
        movie = Movie.objects.get(pk=movie_id)
        print 'retrieved %s from database' % name

    except Movie.DoesNotExist:
        # B) Not in the db, saving it for the first time
        movie = Movie(imdb_id = request.POST['imdb_id'],
                      name= request.POST['name'],
                      year= request.POST['year'],
                      director= request.POST['director'],
                      description= request.POST['description'],
                      poster_name = request.POST['poster_name'])
        tmp_poster = os.path.join(settings.PROJECT_ROOT,
                                  'base/static/posters/tmp.jpg')
        permanent_poster = os.path.join(settings.PROJECT_ROOT,
                                        'base/static/posters/%s' \
                                        % request.POST['poster_name'])
        shutil.copy(tmp_poster, permanent_poster)
        print 'initialized new model for %s' % name


    # set the rating and save
    movie.starRating = int(rating)
    movie.save()
    print 'saved %s in the db with the new rating %s' % (name, rating)

    # done
    return HttpResponse(json.dumps({'rating': rating}),
                        content_type="application/json")




def fight(request, movie_1_id=None, movie_2_id=None):

    # Choose movie 2 randomly if both movies for the
    # fight have the same actual id. Can't fight yourself!
    if movie_1_id == movie_2_id != None:
        movie_2_id = None

    try:
        # get the first movie                                                                                                                                                        
        if movie_1_id is not None:
            movie1 = get_object_or_404(Movie, pk=movie_1_id)
        else:
            # if no id given, pick a random one                                                                                                                                      
            movie1 = Movie.randoms.random()
        # get the second movie                                                                                                                                                       
        if movie_2_id is not None:
            movie2 = get_object_or_404(Movie, pk=movie_2_id)
        else:
            # if no id given, pick a random one                                                                                                                                      
            # that movie1 did not fight before
            # also make sure you don't get movie1
            movie2 = Movie.randoms.random(exclude=movie1)
            max_tries = Movie.objects.count()
            counter = 0
            while movie1.did_already_fight(movie2):
                movie2 = Movie.randoms.random(exclude=movie1)
                # don't search for too long
                counter += 1
                if counter == max_tries:
                    print 'GAVE UP'
                    break
            print 'After %i tries: %s VS %s' % (counter, movie1.name, movie2.name)

            
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

    except Movie.DoesNotExist:

        # could not find any movie (Movie.randoms.random() failed)
        err_title = 'No movies to fight'
        err_msg = 'You did not rate any movies, so there are ' + \
                  'no movies to fight against each other.\n\n' + \
                  'A fight is only meaningful between movies ' + \
                  'you have seen. Without rated movies, it is ' + \
                  'impossible to know which ones you did see. ' + \
                  'Also, the first step for finding how a movie ' + \
                  'ranks for you among others is to give it a ' + \
                  'star rating.\n\n' + \
                  'You can rate a movie by ' + \
                  'using the search bar to find it\'s detail page ' + \
                  'and clicking on the relevant amount ' +\
                  'of stars in the rating field.'
        return error_page(request, err_title, err_msg)

    else:
        # render                                                                                                                                                                         
        context = {'movie1' : movie1,
                   'movie2' : movie2
               }
        return render(request, 'base/fight.html', context)




def fight_result(request, movie_1_id, movie_2_id):
    # get the movies                                                                                                                                                                 
    movie1 = get_object_or_404(Movie, pk=movie_1_id)
    movie2 = get_object_or_404(Movie, pk=movie_2_id)
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
        # Temporarily, TrueSkill will be changed by a single update (as if                                                                                                               
        # there have been multiple matches), but this will be corrected when                                                                                                             
        # The main way of calculating TrueSkill is going over the entire chain                                                                                                           
        # of Fights from scratch.                                                                                                                                                 
        # ~~~~~~~~~~~~~~~~                                                                                                                                                               
        #                                                                                                                                                                                
        # find the match if these two movies were compared before                                                                                                                        
        # or create a new match                                                                                                                                                          
        try:
            match = Fight.objects.filter(
                                       contestants=movie1
                                       ).filter(
                                       contestants=movie2
                                       )[0]
            # make sure the movies are in the right order                                                                                                                                
            # so that the result integer is accurate                                                                                                                                     
            match.movie1, match.movie2 = movie1, movie2
        except IndexError:
            # match not in database, create a new match                                                                                                                                  
            match = Fight(movie1=movie1,
                          movie2=movie2)
        # record the result                                                                                                                                                              
        match.result = result
        # record the date and time (this is not necessary if a new match                                                                                                                 
        # is created, since this is done by default, but it is necessary                                                                                                                 
        # if an old match is retrieved.                                                                                                                                                  
        match.timestamp = now()
        # put the match in the database                                                                                                                                                  
        match.save()
        # --end of recording (end of if)

    # # pick new random movies                                                                                                                                                         
    # randID1 = Movie.randoms.random().imdb_id
    # randID2 = Movie.randoms.random().imdb_id
    # # give a new fight view with random movies                                                                                                                                  
    # return HttpResponseRedirect(reverse('fight',
    #                                     args=(randID1, randID2)))
    # THIS ABOVE HELPS US SHOW THE IDS IN THE URL
    return HttpResponseRedirect(reverse('fight'))


