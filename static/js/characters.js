document.addEventListener('DOMContentLoaded', function() {
    selects = document.querySelectorAll('.character_image_selector');
    
    selects.forEach((select) => {
        select.onchange = load_character_image;
    });

    load_character_image();
})

function load_character_image() {
    gender = document.querySelector('#gender').value;
    race = document.querySelector('#race').value;
    vocation = document.querySelector('#vocation').value;
    fetch(`/characters/image/${gender}/${race}/${vocation}/`)
    .then(result => result.json())
    .then((image) => {
        document.querySelector('#character-image').src = image.character_image;
    });
}