"""urlconf for the base application"""

from django.conf.urls import url, patterns
from base.views import MovieListView, MovieDetailView


urlpatterns = patterns('base.views',
                       url(r'^$', 'home', name='home'),
                       # /base/list                                                                                                                                                  
                       url(r'^list$',
                           MovieListView.as_view(),
                           name = 'movie_list'),
                       # base/5                                                                                                                                                      
                       url(r'^(?P<pk>\d+)$',
                           MovieDetailView.as_view(),
                           name = 'movie_detail'),
                       # base/5/saved                                                                                                                                            
                       url(r'^(?P<pk>\d+)/save_rating$', 'save_movie_rating', name = 'save_rating'),
                       # /base/chart/random/200                                                                                                                                      
                       # /base/chart/ordered_by_name/                                                                                                                                
                       # /base/chart/ordered_by_rating/1400                                                                                                                          
                       url(r'^chart/(?P<order_rule>\w+)/(?P<num_nodes>\d+)?$',
                           'bubbleChart',
                           name = 'bubble_chart'),
                       # base/comparison/a=23&b=18                                                                                                                                   
                       url(r'^comparison/a=(?P<movie_1_id>\d+)\&b=(?P<movie_2_id>\d+)$',
                           'comparison',
                           name = 'comparison'),
                       # base/comparison/a=23                                                                                                                                        
                       url(r'^comparison/a=(?P<movie_1_id>\d+)$', 'comparison', name = 'comparison'),
                       # base/comparison/b=18                                                                                                                                        
                       url(r'^comparison/b=(?P<movie_2_id>\d+)$', 'comparison', name = 'comparison'),
                       # base/comparison/                                                                                                                                            
                       url(r'^comparison/$', 'comparison', name = 'comparison'),
                       # base/comparison/a=23&b=18/result                                                                                                                            
                       url(r'^comparison/a=(?P<movie_1_id>\d+)\&b=(?P<movie_2_id>\d+)/result$',
                           'versusResult',
                           name = 'versus_result'),
                       # /                                                                                                                                                           
                       # /base/                                                                                                                                                      
                       #set /chart to be the default bubble                                                                                                                      
                       #chart: random order, showing all movies                                                                                                                     
                       url(r'^chart/$',
                           'bubbleChart',
                           name = 'bubble_chart')

)
