from django.urls import path

from . import views

urlpatterns = [
    path('<int:character_pk>/', views.play_game, name='play_game'),
    path('exit/', views.exit_game, name='exit_game'),

    # API URLs

    # Characters
    path('characters/', views.list_characters, name='characters'),
    path('characters/<int:pk>/own/', views.get_owned_character,
         name='get_owned_character'),

    # Creatures
    path('creatures/', views.list_creatures, name='creatures'),
    path('creatures/<int:pk>/', views.get_creature, name='creature_detail'),
    path('creatures/<int:pk>/attack/', views.attack_creature,
         name='attack_creature'),

    # Spells
    path('spells/', views.list_spells, name='spells'),
    path('spells/<int:pk>/', views.get_spell, name='spell_detail'),
    path('spells/<int:pk>/buy/', views.buy_spell, name='buy_spell'),

    # Letters
    path('letters/<int:owner_pk>/', views.list_letters, name='list_letters'),
    path('letters/<int:owner_pk>/count_unread/', views.count_unread_letters,
         name='count_unread_letters'),
    path('letters/<int:owner_pk>/<int:pk>/', views.get_letter,
         name='view_letter'),
    path('letters/<int:owner_pk>/<int:pk>/mark_read/', views.mark_read,
         name='mark_read'),
    path('letters/<int:sender_pk>/send/', views.send_letter,
         name='send_letter'),
]
