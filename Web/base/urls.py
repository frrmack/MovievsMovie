"""urlconf for the base application"""

from django.conf.urls import url, patterns
from base.views import MovieListView, RateMoviesView, MovieDetailView


urlpatterns = patterns('base.views',
                       # /
                       url(r'^$', 'home', name='home'),


                       # /list                                                                                                                                                  
                       url(r'^list$',
                           MovieListView.as_view(),
                           name = 'movie_list'),


                       # /rate
                       url(r'^rate$',
                           RateMoviesView.as_view(),
                           name = 'rate_movies'),


                       # /tt51                                                                                                                                                      
                       url(r'^(?P<pk>tt\d+)$',
                           MovieDetailView.as_view(),
                           name = 'movie_detail'),
                       # /tt51/saverating                                                                                                                                            
                       url(r'^(?P<movie_id>tt\d+)/save_rating$', 'save_movie_rating', name='save_rating'),


                       # /search                                                                                                                                                      
                       url(r'^search$', 'search', name='search'),


                       # /fight/a=tt23&b=tt18                                                                                                                                   
                       url(r'^fight/a=(?P<movie_1_id>tt\d+)\&b=(?P<movie_2_id>tt\d+)$',
                           'fight',
                           name = 'fight'),
                       # /fight/a=tt23                                                                                                                                        
                       url(r'^fight/a=(?P<movie_1_id>tt\d+)$', 'fight', name='fight_a'),
                       # /fight/b=tt18                                                                                                                                        
                       url(r'^fight/b=(?P<movie_2_id>tt\d+)$', 'fight', name='fight_b'),
                       # /fight/                                                                                                                                            
                       url(r'^fight/$', 'fight', name='fight'),
                       # /fight/a=tt23&b=tt18/result/lock=1           
                       # /fight/a=tt23&b=tt18/result/lock=2         
                       # /fight/a=tt23&b=tt18/result/lock=0
                       url(r'^fight/a=(?P<movie_1_id>tt\d+)\&b=(?P<movie_2_id>tt\d+)/result/lock=(?P<lock>(1|2|0))$',
                           'fight_result',
                           name='fight_result'),


                       # /chart/random/200                                                                                                                                      
                       # /chart/ordered_by_name/                                                                                                                                
                       # /chart/ordered_by_rating/1400                                                                                                                          
                       url(r'^chart/(?P<order_rule>\w+)/(?P<num_nodes>\d+)?$',
                           'bubbleChart',
                           name = 'bubble_chart'),
                       # /chart (default: random order, show all)
                       url(r'^chart/$',
                           'bubbleChart',
                           name = 'bubble_chart')

)
