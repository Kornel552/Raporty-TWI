from django.urls import path
from . import views

urlpatterns = [
    path('signup', views.signup_page, name='signup_page'),
    path('login', views.login_page, name='login_page'),
    path('logout', views.logout_page, name='logout_page'),
    path('', views.home, name='home'),
    path('dodaj_szkolenie', views.dodaj_szkolenie, name='dodaj_szkolenie'),
    path('raport_ogolny', views.raport_ogolny, name='raport_ogolny'),
    path('dodaj_ucznia', views.dodaj_ucznia, name='dodaj_ucznia'),
    path('wybierz_ucznia', views.wybierz_ucznia, name='wybierz_ucznia')
]