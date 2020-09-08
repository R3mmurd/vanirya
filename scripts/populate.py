import random

from django.db import IntegrityError

from game.models import (
    Creature, CreatureInstance, Gender, Race, Vocation, Character
)

from faker import Faker

from people.models import User

fake = Faker()

character_names = [
    'Butterfly',
    'Boomer',
    'Cobra',
    'Marvel',
    'Twitch',
    'Hammer',
    'Daring',
    'Chuck',
    'Silence',
    'Punch',
    'Scruffy',
    'Dusty',
    'Chuck',
    'Thunder',
    'Beau',
    'Tigress',
    'Ace',
    'King',
    'Sparky',
    'Dog',
    'Blondie',
    'Wiz',
    'Magician',
    'Gilly',
    'Twinkle',
    'Whopper',
    'Bull',
    'Knight',
    'Peanut',
    'Lock',
    'Smiley',
    'Chappie',
    'Bull',
    'Fury',
    'Dragon',
    'Skin',
    'Worm',
    'Double Trouble',
    'Cookie',
    'Honey'
]

genders = list(Gender.objects.all())
races = list(Race.objects.all())
vocations = list(Vocation.objects.all())


def create_random_characters(user):
    n = random.randint(2, 5)

    while n > 0:
        data = dict(
            name=random.choice(character_names),
            gender=random.choice(genders),
            race=random.choice(races),
            vocation=random.choice(vocations),
            level=random.randint(1, 6),
            experience=0,
            experience_to_next_level=100,
            owner=user
        )

        data['money'] = random.randint(50, 100) * data['level']

        for _ in range(data['level'] - 1):
            data['experience'] += data['experience_to_next_level']
            data['experience_to_next_level'] = round(
                data['experience_to_next_level'] * 2.1
            )

        diff = data['experience_to_next_level'] - data['experience']
        data['experience'] += random.randint(10, diff - 10)

        data['life'] = 100 + (data['level'] - 1) * data['vocation'].life_inc
        data['mana'] = 50 + (data['level'] - 1) * data['vocation'].mana_inc
        data['current_life'] = data['life']
        data['current_mana'] = data['mana']

        data['attack_level'] = (
                10 + (data['level'] - 1) * data['race'].attack_inc
        )
        data['defense_level'] = (
                10 + (data['level'] - 1) * data['race'].defense_inc
        )
        data['magic_level'] = 1 + (data['level'] - 1) * data['race'].magic_inc

        try:
            Character.objects.create(**data)
            n -= 1
        except IntegrityError:
            pass


def create_random_users():
    User.objects.exclude(is_superuser=True).delete()

    n = random.randint(5, 10)

    for i in range(n):
        user = None

        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f'{first_name.lower()}.{last_name.lower()}@example.com'
        username = f'{first_name.lower()}_{last_name.lower()}'
        while user is None:
            try:
                user = User.objects.create_user(
                    username, email, '12345',
                    first_name=first_name, last_name=last_name
                )
                user.save()
            except IntegrityError:
                user = None
                username = f'{username}{i + 1}'
        create_random_characters(user)


def spawn_creatures():
    creatures = Creature.objects.all()
    CreatureInstance.objects.all().delete()

    for creature in creatures:
        n = random.randint(15, 30)
        spawn = []

        for _ in range(n):
            spawn.append(CreatureInstance(
                creature=creature,
                current_life=creature.life
            ))
        CreatureInstance.objects.bulk_create(spawn)


def run():
    create_random_users()
    spawn_creatures()
