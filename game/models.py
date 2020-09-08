from django.db import models
from model_utils.models import TimeStampedModel

from people.models import User


class Gender(models.Model):
    """
    Model for genders.
    """
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Race(models.Model):
    """
    Model for races.
    """
    name = models.CharField(max_length=20, unique=True)
    attack_inc = models.SmallIntegerField()
    defense_inc = models.SmallIntegerField()
    magic_inc = models.SmallIntegerField()

    def __str__(self):
        return self.name


class Vocation(models.Model):
    """
    Model for vocations.
    """
    name = models.CharField(max_length=20, unique=True)
    life_inc = models.SmallIntegerField()
    mana_inc = models.SmallIntegerField()
    mana_consume = models.SmallIntegerField()

    def __str__(self):
        return self.name


class CharacterImage(models.Model):
    """
    Model to store an image to each race for each vocation.
    """
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    vocation = models.ForeignKey(Vocation, on_delete=models.CASCADE)
    image = models.FileField(
        upload_to='images/characters/', null=True, verbose_name=''
    )

    def __str__(self):
        return f'{self.gender.name} {self.race.name} {self.vocation}'

    class Meta:
        unique_together = ('gender', 'race', 'vocation')


class Character(TimeStampedModel):
    """
    Model to store characters.
    """
    name = models.CharField(max_length=100, unique=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    vocation = models.ForeignKey(Vocation, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='characters',
        related_query_name='characters'
    )
    money = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    experience_to_next_level = models.IntegerField(default=100)
    life = models.IntegerField(default=100)
    current_life = models.IntegerField(default=100)
    mana = models.IntegerField(default=50)
    current_mana = models.IntegerField(default=50)
    attack_level = models.IntegerField(default=10)
    defense_level = models.IntegerField(default=10)
    magic_level = models.IntegerField(default=1)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender.name,
            'race': self.race.name,
            'vocation': self.vocation.name,
            'level': self.level,
            'experience': self.experience,
            'experience_to_next_level': self.experience_to_next_level,
            'money': self.money,
            'life': self.life,
            'current_life': self.current_life,
            'mana': self.mana,
            'current_mana': self.current_mana,
            'attack': self.attack_level,
            'defense': self.defense_level,
            'magic_level': self.magic_level
        }

    def __str__(self):
        return self.name


class Letter(models.Model):
    """
    Model for messages between characters.
    """
    title = models.CharField(max_length=256)
    content = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    sender = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='sent_letters',
        related_query_name='sent_letters'
    )
    receiver = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='received_letters',
        related_query_name='received_letters'
    )

    def serialize(self):
        return {
            'id': self.pk,
            'sender': self.sender.name,
            'receiver': self.receiver.name,
            'read': self.read,
            'title': self.title,
            'content': self.content,
            'timestamp': self.timestamp.strftime("%b %d %Y, %I:%M %p")
        }


class Creature(models.Model):
    """
    Model for creatures.
    """
    name = models.CharField(max_length=100, unique=True)
    life = models.IntegerField()
    attack = models.IntegerField()
    defense = models.IntegerField()
    experience = models.IntegerField()
    money_low = models.IntegerField()
    money_high = models.IntegerField()
    image = models.FileField(
        upload_to='images/creatures/', null=True, verbose_name=''
    )

    def get_description(self):
        return (f'Atk: {self.attack} - Def: {self.defense} - Drops: '
                f'[{self.money_low}, {self.money_high}] gold coins')

    def serialize(self):
        return {
            'name': self.name,
            'life': self.life,
            'attack': self.attack,
            'defense': self.defense,
            'experience': self.experience,
            'money_low': self.money_low,
            'money_high': self.money_high,
            'image': self.image.url,
        }

    def __str__(self):
        return self.name


class CreatureInstance(models.Model):
    """
    Model for creature instances.
    """
    current_life = models.IntegerField()
    creature = models.ForeignKey(
        Creature,
        on_delete=models.CASCADE,
        related_name='creature_instances',
        related_query_name='creature_instances'
    )

    def is_dead(self):
        return self.current_life <= 0

    def serialize(self):
        result = self.creature.serialize()
        result['current_life'] = self.current_life
        result['id'] = self.pk
        result['is_dead'] = self.is_dead()
        return result

    def __str__(self):
        return str(self.creature)


class Spell(models.Model):
    """
    Model for spells.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=256)
    life = models.IntegerField()
    mana = models.IntegerField()
    price = models.IntegerField()
    image = models.FileField(
        upload_to='images/spells/', null=True, verbose_name=''
    )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.pk,
            'name': self.name,
            'description': self.description,
            'life': self.life,
            'mana': self.mana,
            'price': self.price,
            'image': self.image.url
        }
