from django.conf.urls import patterns, include, url

from mizer import views


urlpatterns = patterns('',
    url(r'^mizer/$', views.DashboardView.as_view(), name='mizer_home'),
    url(r'^mizer/year$', views.YearListView.as_view(), name='mizer_year'),
    url(r'^mizer/year/(?P<year>\d+)$', views.YearListView.as_view(), name='mizer_year'),
)
