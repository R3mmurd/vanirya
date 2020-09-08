import random


def level_up(character):
    if character.experience < character.experience_to_next_level:
        return False

    # Increment level
    character.level += 1

    # Increment race values
    character.magic_level += character.race.magic_inc
    character.attack_level += character.race.attack_inc
    character.defense_level += character.race.defense_inc

    # Increment vocation values
    character.life += character.vocation.life_inc
    character.mana += character.vocation.mana_inc

    # Fill up life and mana
    character.current_life = character.life
    character.current_mana = character.mana

    # Compute experience to next level
    character.experience_to_next_level = round(
        character.experience_to_next_level * 2.1
    )

    return True


def die(character):
    character.current_life = character.life
    character.current_mana = character.current_mana
    lost = round(character.money * random.uniform(0.2, 0.3))
    character.money -= lost
    return lost
