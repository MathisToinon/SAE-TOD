from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),  # anciennement 'index'
    path('dashboard/', views.dashboard, name='dashboard'),
    path('comparaison/', views.comparaison, name='comparaison'),
    path('secteur/', views.secteur, name='secteur'),
    path('carte/', views.carte, name='carte'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]
