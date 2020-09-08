from django.urls import path

from . import views

urlpatterns = [
    path('', views.main_view, name='index'),
    path('profile/', views.profile, name='profile'),
    path('characters/create/', views.new_character, name='new_character'),
    path('characters/<int:pk>/', views.view_character, name='view_character'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # API URL
    path('characters/image/<int:gender_pk>/<int:race_pk>/<int:vocation_pk>/',
         views.get_character_image,
         name='character_image'),
]
