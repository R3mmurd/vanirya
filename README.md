# Vanirya

This is a web game inspired by the 2010 academic project with the name "[Misterios de Munrrael](http://demiangutierrez.me/2011/04/20/misterios-de-munrrael/)."

In this version of the game, you can create an account. When you log in, You will be in a panel where you can see
any characters that you have created (empty when you get there for the first time). You have the option of creating until five characters
by typing its name and selecting a gender, a race, and a vocation. In the character list, you have options to view the character details
and play the game with it.

When you select to play with any of your characters, you will be redirected to a screen with a navigation bar to view the spawned creatures,
the other characters in the game (not the characters you own), the list of available spells to buy, and the list of letters that your character
has received from other characters. By default, you enter on the screen with the spawned creatures. There is also a right panel with the information
of your character such as life bar, mana bar, experience bar, amount of gold coins, level, magic level, attack level, defense level, and the image
if the character (there is a default image for each triplet of gender, race, and vocation).

On the screen of creatures, you are able to attack any of them by clicking the button "Attack." Any time that you attack any creature, it will counter attack automatically, then a summary of the attack is shown on a modal. The effectiveness of the attack depends on the character's attack level and the creature's defense level. The effectiveness of the defense depends on the character's defense level and the creature's attack level. The attack or the defense could be powered up by using mana for vocations than has a non-zero positive value on the field `mana_consume`. When a creature dies, it will give you a loot of gold coins and some amount of experience. If your character dies, it will lose a number of gold coins between 20% and 30% of the amount that it has. When the character levels up, the total amount of life and mana are increased according the values defined by its vocation. Similarly, the attack, defense, and magic levels are increased according the values defined by its race.

On the screen of characters, you are able to send letters to any other character by clicking the button "Send letter." On the screen of spells, you can buy any of them by clicking the button "Buy." Finally, on the screen of Letters, you can see the character's received letters; by clicking the button "View", you can read the content of any of them.

## Getting started

In order to install and run this project, you should follow the next steps:

1. Create a virtual environment, for example: `python3 -m venv vanirya_venv`.
2. Activate the virtual environment, for example: `source vanirya_venv/bin/activate`.
3. Go to the project directory: `cd path/to/vanirya`.
4. Install the requirements: `pip install -r requirements.txt`.
5. Generate migrations: `python manage.py makemigrations`.

In this package, it is provided a little database with some values. If you want to use it, go to step 9. Otherwise,
remove the file db.sqlite3 and continue step 5.

6. Migrate models: `python manage.py migrate`.
7. Create a superuser: `python manage.py createsuperuser`.
8. Log in in the admin system (`/admin/`) and create definitions for: genders, races, vocations, character images for each triplet
   (gender, race, vocation), and creatures.
9. Populate the database. There is a script that populates the database with some random users and characters. It also generates a random
    spawn of creatures. Run the script: `python manage.py runscript populate`.
10. Run the server: `python manage.py runserver`.
11. Enjoy the game.

## The database

In this project, there is a small database (`db.sqlite3`) with some basic definitions:

- Genders: Male and Female.
- Races: Human, Elf, and Dwarf.
- Vocations: Knight and Wizard.
- Character images: Some downloaded pictures to represent each triplet of gender, race, and vocation.
- Users: An admin with username "vaniryaadm" and password "vaniryaadm". It also contains some randomly generated users.
  You can see their values in the admin system. All of them have "12345" as password.
- Characters: Contains some randomly generated characters. You can see their values in the admin system.
- Creatures: Goblin, Wolf, And Minotaur.
- Creature instances: Contains a randomly generated spawn of creatures.
- Spells: Potions for recovering life and mana. For each of them, there are three versions: weak, medium, and strong.

## Technical details

### Backend

The backend of this project was developed with Python and Django. There are 2 applications: `people` and `game`.

The application `people` contains the model `User`. It also contains urls and views for: register, log in, log out, view profile,
list characters, view character details, create new character, and an API view to get the image url associated to a
triplet (gender, race, vocation).

The application `game` contains urls and API view for the following models: `Gender`, `Race`, `Vocation`, `CharacterImage`, `Character`, `Letter`,
`Creature` (definition), `CreatureInstance` (for spawn), and `Spell`. It also contains views and a set of API views ant their urls.
They are to perform the following operations:

- Play game: Enters the game screen with the selected character.
- Exit game: Exits from the game screen and go back to the screen of character selection.
- List characters: Retrieves a paged list of all characters in the game except the characters that you own.
- Get owned character: Retrieves the details of a character that you own.
- List creatures: Retrieves a paged list of the spawned creatures.
- Attack creature: Performs an attack between the character and the selected creature.
- List Spells: Retrieves a paged list of the available spells.
- Buy spell: Performs a spell purchase. It will discount money from your character and increase life and mana according to the values
  on it.
- List letters: Retrieves a paged list of the letters that the character has received ordered from the newest to the oldest.
- Get letter: Retrieves the detail of a letter than the character has received.
- Count unread letters: Returns the number of unread letters.
- Mark read: Mark a letter as read.
- Sends letter: Send a letter to another character.

### Frontend

The frontend of this project was developed with HTML5 and CSS by using some features of [Bootstrap](https://getbootstrap.com/). The game screen
was developed with a single page building all the UI with Javascript by using asynchronous calls to the API of the game.
