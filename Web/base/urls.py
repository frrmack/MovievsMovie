"""urlconf for the base application"""

from django.conf.urls import url, patterns

from django.views.generic import DetailView, ListView

from base import views
from base.models import Movie

from random import shuffle


urlpatterns = patterns('base.views',
                       url(r'^$', 'home', name='home'),
                       # /main/list                                                                                                                                                  
                       url(r'^list$',
                           ListView.as_view ( queryset = Movie.objects.order_by('-starSeededTrueSkillMu') ),
                           name = 'movie_list'),
                       # main/5                                                                                                                                                      
                       url(r'^(?P<pk>\d+)$',
                           DetailView.as_view( model = Movie ),
                           name = 'movie_detail'),
                       # /main/chart/random/200                                                                                                                                      
                       # /main/chart/ordered_by_name/                                                                                                                                
                       # /main/chart/ordered_by_rating/1400                                                                                                                          
                       url(r'^chart/(?P<order_rule>\w+)/(?P<num_nodes>\d+)?$',
                           views.bubbleChart,
                           name = 'bubble_chart'),
                       # main/comparison/a=23&b=18                                                                                                                                   
                       url(r'^comparison/a=(?P<movie_1_id>\d+)\&b=(?P<movie_2_id>\d+)$',
                           views.comparison,
                           name = 'comparison'),
                       # main/comparison/a=23                                                                                                                                        
                       url(r'^comparison/a=(?P<movie_1_id>\d+)$', views.comparison, name = 'comparison'),
                       # main/comparison/b=18                                                                                                                                        
                       url(r'^comparison/b=(?P<movie_2_id>\d+)$', views.comparison, name = 'comparison'),
                       # main/comparison/                                                                                                                                            
                       url(r'^comparison/$', views.comparison, name = 'comparison'),
                       # main/comparison/a=23&b=18/result                                                                                                                            
                       url(r'^comparison/a=(?P<movie_1_id>\d+)\&b=(?P<movie_2_id>\d+)/result$',
                           views.versusResult,
                           name = 'versus_result'),
                       # /                                                                                                                                                           
                       # /main/                                                                                                                                                      
                       # set home page to be the default bubble                                                                                                                      
                       # chart: random order, showing all movies                                                                                                                     
                       # url(r'^$',
                       #     views.bubbleChart,
                       #     name = 'bubble_chart')



)
