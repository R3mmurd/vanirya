from django.contrib import admin
from . import models

admin.site.register(models.Gender)
admin.site.register(models.Race)
admin.site.register(models.Vocation)
admin.site.register(models.CharacterImage)
admin.site.register(models.Character)
admin.site.register(models.Creature)
admin.site.register(models.Spell)
