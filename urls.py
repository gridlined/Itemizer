from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^year/(?P<year>\d+)', views.YearListView.as_view(), name='mizer_year'),
    url(r'^year', views.YearListView.as_view(), name='mizer_year'),
    url(r'^', views.DashboardView.as_view(), name='mizer_home'),
]
