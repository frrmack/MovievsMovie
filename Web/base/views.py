""" Views for the base application """

from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from django.conf import settings

from django.views.generic import ListView, DetailView

from base.models import Movie, VersusMatch

from datetime import datetime
from django.utils.timezone import utc

import json

import os, sys
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
        title, content, url = movie_search.find(query)
        content = content[:-11] + '...'
        if movie_search.get_imdb_type(url) != "title":
            raise movie_search.NotFoundError
    except movie_search.NotFoundError:
        print 'No movie found with name %s.' % query
        context = {'error_title': 'No title found',
                   'error_message': 'No title matching the query "%s" was found.' % query}
        return render(request, 'base/error_message.html', context)
    else:
        print title
        print url
        # search & parse
        soup = movie_search.connect(url)
        name, year, director = movie_search.parse_name_year_director(soup)
        imdb_id = movie_search.get_imdb_id(url)

        # download the poster temporarily
        poster_url = movie_search.parse_poster_url(soup)
        tmp_poster_file = os.path.join(settings.PROJECT_ROOT, 'base/static/posters/tmp.jpg')
        tmp_poster_url = '%sposters/tmp.jpg' % settings.STATIC_URL
        movie_search.download(poster_url, tmp_poster_file)

        # create model instance
        movie = Movie(id=imdb_id,
                      imdb_id = imdb_id,
                      name=name,
                      year=year,
                      director=director,
                      description=content)
        context = {'movie' : movie,
                   'poster_url': tmp_poster_url}
        return render(request, 'base/movie_detail.html', context)


def comparison(request, movie_1_id=None, movie_2_id=None):
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
            movie2 = Movie.randoms.random()
    except Movie.DoesNotExist:
        # No movies at all in the database                                                                                                                                           
        # ---Temporarily using an empty movie_list view as---                                                                                                                        
        # ---placeholder for a specific page informing this---                                                                                                                       
        return HttpResponseRedirect(reverse('movie_list'))
    # render                                                                                                                                                                         
    context = {'movie1' : movie1,
               'movie2' : movie2
              }
    return render(request, 'base/comparison.html', context)


def save_movie_rating(request, pk=None):

    print 'HEY'
    print pk
    print request.POST['rating']
    movie = get_object_or_404(Movie, pk=pk)
    rating = request.POST['rating']
    movie.starRating = int(rating)
    movie.save()
    return HttpResponse(json.dumps({'rating': rating}),
                        content_type="application/json")



def versusResult(request, movie_1_id, movie_2_id):
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
        # of VersusMatches from scratch.                                                                                                                                                 
        # ~~~~~~~~~~~~~~~~                                                                                                                                                               
        #                                                                                                                                                                                
        # find the match if these two movies were compared before                                                                                                                        
        # or create a new match                                                                                                                                                          
        try:
            match = VersusMatch.objects.filter(
                                       contestants=movie1
                                       ).filter(
                                       contestants=movie2
                                       )[0]
            # make sure the movies are in the right order                                                                                                                                
            # so that the result integer is accurate                                                                                                                                     
            match.movie1, match.movie2 = movie1, movie2
        except IndexError:
            # match not in database, create a new match                                                                                                                                  
            match = VersusMatch(movie1=movie1,
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

    # pick new random movies                                                                                                                                                         
    randID1 = Movie.randoms.random().id
    randID2 = Movie.randoms.random().id
    # give a new comparison view with random movies                                                                                                                                  
    return HttpResponseRedirect(reverse('comparison',
                                        args=(randID1, randID2)))


