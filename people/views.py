from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from game.models import Gender, Race, Vocation, Character, CharacterImage
from people.models import User


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']

        # Ensure password matches confirmation
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'people/register.html', {
                'error': 'Passwords must match.'
            })
        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username, email, password,
                first_name=first_name, last_name=last_name
            )
            user.save()
        except IntegrityError:
            return render(request, 'people/register.html', {
                'error': 'Username already taken.'
            })
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'people/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'people/login.html', {
                'error': 'Invalid username or password.'
            })
    else:
        return render(request, 'people/login.html')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required(login_url='/login/')
def main_view(request):
    return render(request, 'people/index.html', {
        'characters': request.user.characters.all()
    })


@login_required(login_url='/login/')
def profile(request):
    return render(request, 'people/profile.html')


@login_required(login_url='/login/')
def view_character(request, pk):
    character = get_object_or_404(Character, pk=pk, owner=request.user)
    return render(request, 'people/view_character.html', {
        'character': character
    })


@login_required(login_url='/login/')
def new_character(request):
    num_characters = request.user.characters.count()
    if request.method == 'POST':
        if num_characters == 5:
            return render(request, 'people/create_character.html', {
                'num_characters': num_characters,
                'genders': Gender.objects.all(),
                'races': Race.objects.all(),
                'vocations': Vocation.objects.all(),
                'error':
                    'You have reached the maximum number of allowed characters.'
            })
        name = request.POST['name']
        gender = get_object_or_404(Gender, pk=int(request.POST['gender']))
        race = get_object_or_404(Race, pk=int(request.POST['race']))
        vocation = get_object_or_404(Vocation, pk=int(request.POST['vocation']))

        try:
            Character.objects.create(
                name=name,
                gender=gender,
                race=race,
                vocation=vocation,
                owner=request.user
            )
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, 'people/create_character.html', {
                'num_characters': num_characters,
                'genders': Gender.objects.all(),
                'races': Race.objects.all(),
                'vocations': Vocation.objects.all(),
                'error': 'Character name already taken.'
            })

    return render(request, 'people/create_character.html', {
        'num_characters': num_characters,
        'genders': Gender.objects.all(),
        'races': Race.objects.all(),
        'vocations': Vocation.objects.all()
    })


def get_character_image(request, gender_pk, race_pk, vocation_pk):
    character_image = CharacterImage.objects.filter(
        gender__pk=gender_pk, race__pk=race_pk, vocation__pk=vocation_pk
    ).first()

    if character_image is None:
        return JsonResponse({'error': 'Character image not found'}, status=404)

    return JsonResponse({'character_image': character_image.image.url})
