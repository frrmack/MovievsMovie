"""urlconf for the base application"""

from django.conf.urls import url, patterns
from base.views import MovieListView, MovieDetailView


urlpatterns = patterns('base.views',
                       # /
                       url(r'^$', 'home', name='home'),
                       # /list                                                                                                                                                  
                       url(r'^list$',
                           MovieListView.as_view(),
                           name = 'movie_list'),
                       # /tt51                                                                                                                                                      
                       url(r'^(?P<pk>tt\d+)$',
                           MovieDetailView.as_view(),
                           name = 'movie_detail'),
                       # /tt51/saverating                                                                                                                                            
                       url(r'^(?P<movie_id>tt\d+)/save_rating$', 'save_movie_rating', name = 'save_rating'),
                       # /search                                                                                                                                                      
                       url(r'^search$', 'search', name='search'),
                       # /comparison/a=tt23&b=tt18                                                                                                                                   
                       url(r'^comparison/a=(?P<movie_1_id>tt\d+)\&b=(?P<movie_2_id>tt\d+)$',
                           'comparison',
                           name = 'comparison'),
                       # /comparison/a=tt23                                                                                                                                        
                       url(r'^comparison/a=(?P<movie_1_id>tt\d+)$', 'comparison', name = 'comparison'),
                       # /comparison/b=tt18                                                                                                                                        
                       url(r'^comparison/b=(?P<movie_2_id>tt\d+)$', 'comparison', name = 'comparison'),
                       # /comparison/                                                                                                                                            
                       url(r'^comparison/$', 'comparison', name = 'comparison'),
                       # /comparison/a=tt23&b=tt18/result                                                                                                                            
                       url(r'^comparison/a=(?P<movie_1_id>tt\d+)\&b=(?P<movie_2_id>tt\d+)/result$',
                           'versusResult',
                           name = 'versus_result'),
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
