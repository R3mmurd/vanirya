import functools
import json
import random

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from game.helpers import die, level_up
from game.models import (
    Character, CharacterImage, CreatureInstance, Spell, Letter
)


@login_required(login_url='/login/')
def play_game(request, character_pk):
    character = get_object_or_404(
        Character, pk=character_pk, owner=request.user
    )
    return render(request, 'game/game_world.html', {
        'character': character,
        'image': CharacterImage.objects.get(
            gender=character.gender,
            race=character.race,
            vocation=character.vocation
        ).image.url
    })


def exit_game(request):
    return HttpResponseRedirect(reverse('index'))


def json_login_required(f):
    @functools.wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'You are not authenticated.'}, status=401
            )
        return f(request, *args, **kwargs)
    return wrapper


@json_login_required
def get_owned_character(request, pk):
    character = request.user.characters.filter(pk=pk).first()
    if character is None:
        return JsonResponse({'error': 'Character not found.'}, status=404)

    return JsonResponse(character.serialize())


def get_paged_list(request, qs, serializer_function):
    paginator = Paginator(qs, 7)
    page_number = int(request.GET.get('page', 1))
    page_number = max(0, min(page_number, paginator.num_pages))
    page = paginator.get_page(page_number)

    objects = [serializer_function(item) for item in page]

    result = {
        'objects': objects,
        'num_pages': paginator.num_pages,
        'page_number': page_number
    }

    return JsonResponse(result)


@json_login_required
def list_characters(request):
    characters = Character.objects.exclude(owner=request.user)
    return get_paged_list(
        request,
        characters,
        lambda character: {
            'id': character.pk,
            'name': character.name,
            'level': character.level
        }
    )


def list_creatures(request):
    return get_paged_list(
        request,
        CreatureInstance.objects.filter(current_life__gt=0),
        lambda creature: {
            'id': creature.pk,
            'name': creature.creature.name,
            'description': creature.creature.get_description(),
            'life': creature.creature.life,
            'current_life': creature.current_life,
            'image': creature.creature.image.url
        }
    )


def get_creature(request, pk):
    creature = CreatureInstance.objects.filter(pk=pk).first()
    if creature is None:
        return JsonResponse({'error': 'Creature not found.'}, status=404)
    return JsonResponse(creature.serialize())


@csrf_exempt
@json_login_required
def attack_creature(request, pk):
    if request.method != 'PUT':
        return JsonResponse({'error': 'PUT method required.'}, status=405)

    data = json.loads(request.body)

    if 'character_id' not in data:
        return JsonResponse(
            {'error': 'Missing body parameter character_id.'}, status=400
        )

    character = Character.objects.filter(
        pk=int(data['character_id']), owner=request.user
    ).first()

    if character is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    creature_instance = CreatureInstance.objects.filter(
        pk=pk, current_life__gt=0
    ).first()

    if creature_instance is None:
        return JsonResponse({'error': 'Creature not found.'}, status=404)

    result = {
        'damage_done': 0,
        'damage_received': 0,
        'received_experience': 0,
        'level_up': False,
        'character_died': False,
        'creature_died': False,
        'lost': 0,
        'loot': 0,
        'character': None,
        'creature': None
    }

    creature = creature_instance.creature
    mana_power = False
    if character.current_mana >= character.vocation.mana_consume:
        mana_power = character.vocation.mana_consume > 0
        character.current_mana -= character.vocation.mana_consume

    # Character attack and creature defense
    attack_value = round(character.attack_level * random.uniform(0.5, 1.3))

    if mana_power:
        attack_value = round(character.attack_level * random.uniform(1.2, 1.3))

    defense_value = round(creature.defense * random.uniform(0.5, 1.5))
    damage = max(0, attack_value - defense_value)
    creature_instance.current_life -= damage
    creature_instance.save()

    result['creature'] = creature_instance.serialize()
    result['damage_done'] = damage

    if creature_instance.is_dead():
        result['creature_died'] = True
        loot = random.randint(creature.money_low, creature.money_high)
        character.money += loot
        result['loot'] = loot
        result['received_experience'] = creature.experience
        character.experience += creature.experience
        result['level_up'] = level_up(character)
    else:
        # The creature is still alive, counter attack
        attack_value = round(creature.attack * random.uniform(0.5, 1.5))
        defense_value = round(
            character.defense_level * random.uniform(0.5, 1.5)
        )
        if mana_power:
            defense_value = round(
                character.defense_level * random.uniform(1.2, 1.5)
            )
        damage = max(0, attack_value - defense_value)
        character.current_life -= damage

        result['damage_received'] = damage

        # Check whether character is dead
        if character.current_life <= 0:
            result['character_died'] = True
            result['lost'] = die(character)

    character.save()
    result['character'] = character.serialize()

    return JsonResponse(result)


def list_spells(request):
    return get_paged_list(
        request,
        Spell.objects.all(),
        lambda spell: spell.serialize()
    )


def get_spell(request, pk):
    spell = Spell.objects.filter(pk=pk).first()
    if spell is None:
        return JsonResponse({'error': 'Spell not found.'}, status=404)
    return JsonResponse(spell.serialize())


@csrf_exempt
@json_login_required
def buy_spell(request, pk):
    if request.method != 'PUT':
        return JsonResponse({'error': 'PUT method required.'}, status=405)

    data = json.loads(request.body)

    if 'character_id' not in data:
        return JsonResponse(
            {'error': 'Missing body parameter character_id.'}, status=400
        )

    character = Character.objects.filter(
        pk=int(data['character_id']), owner=request.user
    ).first()

    if character is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    spell = Spell.objects.filter(pk=pk).first()
    if spell is None:
        return JsonResponse({'error': 'Spell not found.'}, status=404)

    if character.money < spell.price:
        return JsonResponse(
            {'error': 'Not enough money to buy the spell.'}, status=400
        )

    character.money -= spell.price
    character.current_life = min(
        character.life, character.current_life + spell.life
    )
    character.current_mana = min(
        character.mana, character.current_mana + spell.mana
    )
    character.save()

    result = {
        'added_life': spell.life,
        'added_mana': spell.mana
    }

    return JsonResponse(result)


@json_login_required
def list_letters(request, owner_pk):
    character = Character.objects.filter(
        pk=owner_pk, owner=request.user
    ).first()

    if character is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    return get_paged_list(
        request,
        character.received_letters.all().order_by('-timestamp'),
        lambda letter: letter.serialize()
    )


@json_login_required
def get_letter(request, owner_pk, pk):
    character = Character.objects.filter(
        pk=owner_pk, owner=request.user
    ).first()

    if character is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    letter = character.received_letters.filter(pk=pk).first()
    if letter is None:
        return JsonResponse({'error': 'Letter not found.'}, status=404)

    return JsonResponse(letter.serialize())


@csrf_exempt
@json_login_required
def mark_read(request, owner_pk, pk):
    if request.method != 'PUT':
        return JsonResponse({'error': 'PUT method required.'}, status=405)

    character = Character.objects.filter(
        pk=owner_pk, owner=request.user
    ).first()

    if character is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    letter = character.received_letters.filter(pk=pk).first()
    if letter is None:
        return JsonResponse({'error': 'Letter not found.'}, status=404)

    letter.read = True
    letter.save()

    return JsonResponse({}, status=204)


@json_login_required
def count_unread_letters(request, owner_pk):
    character = Character.objects.filter(
        pk=owner_pk, owner=request.user
    ).first()

    if character is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    return JsonResponse(
        {'count': character.received_letters.filter(read=False).count()}
    )


@csrf_exempt
@json_login_required
def send_letter(request, sender_pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required.'}, status=405)

    sender = Character.objects.filter(
        pk=sender_pk, owner=request.user
    ).first()

    if sender is None:
        return JsonResponse({'error': 'Forbidden.'}, status=403)

    data = json.loads(request.body)

    if 'receiver_id' not in data:
        return JsonResponse(
            {'error': 'Missing body parameter receiver_id.'}, status=400
        )
    if 'title' not in data:
        return JsonResponse(
            {'error': 'Missing body parameter title.'}, status=400
        )
    if 'content' not in data:
        return JsonResponse(
            {'error': 'Missing body parameter content.'}, status=400
        )

    receiver = Character.objects.filter(pk=int(data['receiver_id'])).first()

    if receiver is None:
        return JsonResponse({'error': 'Receiver not found.'}, status=404)

    Letter.objects.create(
        title=data['title'],
        content=data['content'],
        sender=sender,
        receiver=receiver
    )

    return JsonResponse({})
