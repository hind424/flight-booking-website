from django.urls import path
from django.conf.urls import url
from . import views
from .views import book

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('search/', views.search, name = 'search'),
    path('book/', views.book, name = 'book'),
    path('user_login/', views.user_login, name = 'user_login'),
    path('payment/', views.payment, name = 'payment'),
    path('trip/<tripId>/<airplane_number_id>', views.trip, name= 'trip')

]