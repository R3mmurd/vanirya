document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#btn-creatures').onclick = () => { loadCreatures(); };
    document.querySelector('#btn-characters').onclick = () => { loadCharacters();  };
    document.querySelector('#btn-spells').onclick = () => { loadSpells(); };
    document.querySelector('#btn-letters').onclick = () => { loadLetters(); };

    updateCharacterInfo();
    loadCreatures();
    setInterval(checkForNewLetters, 1000);
})

function updateBar(barName, currentValue, totalValue) {
    document.querySelector(`#${barName}`).innerHTML = `${currentValue}/${totalValue}`;
    document.querySelector(`#${barName}-bar`).style.width = `${100*currentValue/totalValue}%`;
}

function updateCharacterInfo() {
    fetch(`/game/characters/${window.characterId}/own/`)
    .then(response => response.json())
    .then((character) => {
        if ('error' in character) {
            return;
        }
        updateBar('life', character.current_life, character.life);
        updateBar('mana', character.current_mana, character.mana);
        updateBar('experience', character.experience, character.experience_to_next_level);
        document.querySelector('#money').innerHTML = character.money;
        document.querySelector('#level').innerHTML = character.level;
        document.querySelector('#magic-level').innerHTML = character.magic_level;
        document.querySelector('#attack').innerHTML = character.attack;
        document.querySelector('#defense').innerHTML = character.defense;

    });
}

function createPaginator(numPages, pageNumber) {
    if (numPages <= 1) {
        return '';
    }

    let paginator = '';

    paginator += '<div class="pagination justify-content-center"><nav aria-label="Page navigation"><ul class="pagination">';

    if (pageNumber == 1) {
        paginator += '<li class="page-item disabled">';
    } else {
        paginator += '<li class="page-item">';
    }

    paginator += `<a id="prev" data-page="${pageNumber - 1}" class="page-link btn btn-game" href="javascript:void(0);">Previous</a></li>`
    
    for (i = 1; i <= numPages; ++i) {
        paginator += '<li class="page-item">';
        paginator += `<a id="${i}" data-page="${i}" class="page-link btn btn-game page-number" href="javascript:void(0);">${i}</a></li>`;
    }

    if (pageNumber == numPages) {
        paginator += '<li class="page-item disabled">';
    } else {
        paginator += '<li class="page-item">';
    }
    paginator += `<a id="next" data-page="${pageNumber + 1}" class="page-link btn btn-game" href="javascript:void(0);">Next</a></li>`
    paginator += '</ul></nav></div>'

    return paginator;
}

function buildTable(title, pagination, buildHeader, buildRow) {
    let html = `<h2 class="game-content-panel-title">${title}</h2>`

    html += '<table class="table table-green table-borderless">';
    html += '<thead>';
    html += buildHeader();
    html += '</thead>';
    html += '<tbody>';

    pagination.objects.forEach((item) => {
        html += buildRow(item);
    });
    
    html += '</tbody>';
    html += '</table>';

    html += createPaginator(pagination.num_pages, pagination.page_number);

    document.querySelector('#game-content-panel').innerHTML = html;
}

function loadCreatures(page=1) {
    fetch(`/game/creatures/?page=${page}`)
    .then(response => response.json())
    .then((result) => {
        if ('error' in result) {
            return;
        }
        buildTable('Creatures', result, () => {
            return '<th scope="column">Name</th><th scope="column">Description</th><th scope="column">Life</th><th scope="column">Actions</th>';
        }, (creature) => {
            return `<tr><td>${creature.name}</td><td>${creature.description}</td><td>${creature.current_life}/${creature.life}</td><td><a href="javascript:void(0)" data-creature-id="${creature.id}" class="btn btn-game action-attack-creature">Attack</a></td></tr>`;
        });

        document.querySelectorAll('.action-attack-creature').forEach((link) => {
            link.onclick = () => { attackCreature(link.dataset.creatureId, page); };    
        });

        document.querySelectorAll('.page-link').forEach((link) => {
            link.onclick = () => { loadCreatures(link.dataset.page); };
        });
    });
}

function loadCharacters(page=1) {
    fetch(`/game/characters/?page=${page}`)
    .then(response => response.json())
    .then((result) => {
        if ('error' in result) {
            return;
        }
        buildTable('Characters', result, () => {
            return '<th scope="column">Name</th><th scope="column">Level</th><th scope="column">Actions</th>';
        }, (character) => {
            return `<tr><td>${character.name}</td><td>${character.level}</td><td><a href="javascript:void(0)" data-receiver-id="${character.id}" data-receiver-name="${character.name}" class="btn btn-game action-send-letter">Send letter</a></td></tr>`;
        });

        document.querySelectorAll('.action-send-letter').forEach((link) => {
            link.onclick = () => { sendLetter(link.dataset.receiverId, link.dataset.receiverName) };    
        });

        document.querySelectorAll('.page-link').forEach((link) => {
            link.onclick = () => { loadCharacters(link.dataset.page); };
        });
    });
}

function loadSpells(page=1) {
    fetch(`/game/spells/?page=${page}`)
    .then(response => response.json())
    .then((result) => {
        if ('error' in result) {
            return;
        }
        buildTable('Spells', result, () => {
            return '<th scope="column"></th><th scope="column">Name</th><th scope="column">Description</th><th>Price</th><th scope="column">Actions</th>';
        }, (spell) => {
            return `<tr><td><img src="${spell.image}" width="48" height="48"></td><td>${spell.name}</td><td>${spell.description}</td><td>${spell.price}</td><td><a href="javascript:void(0)" data-spell-id="${spell.id}" class="btn btn-game action-buy-spell">Buy</a></td><tr>`;
        });

        document.querySelectorAll('.action-buy-spell').forEach((link) => {
            link.onclick = () => { buySpell(link.dataset.spellId); };    
        });

        document.querySelectorAll('.page-link').forEach((link) => {
            link.onclick = () => { loadSpells(link.dataset.page); };
        });
    });
}

function loadLetters(page=1) {
    fetch(`/game/letters/${window.characterId}/?page=${page}`)
    .then(response => response.json())
    .then((result) => {
        if ('error' in result) {
            return;
        }
        buildTable('Letters', result, () => {
            return '<th scope="column">Timestamp</th><th scope="column">Sender</th><th scope="column">Title</th><th>Actions</th>';
        }, (letter) => {
            let read = (letter.read) ? 'letter-read' : 'letter-unread';
            return `<tr class="${read}"><td>${letter.timestamp}</td><td>${letter.sender}</td><td>${letter.title}</td><td><a href="javascript:void(0)" data-letter-id="${letter.id}" class="btn btn-game action-view-letter">View</a></td></tr>`;
        });

        document.querySelectorAll('.action-view-letter').forEach((link) => {
            link.onclick = () => { viewLetter(link.dataset.letterId, page); };    
        });

        document.querySelectorAll('.page-link').forEach((link) => {
            link.onclick = () => { loadSpells(link.dataset.page); };
        });
    });
}

function attackCreature(creatureId, page) {
    fetch(`/game/creatures/${creatureId}/attack/`, {
        method: 'PUT',
        body: JSON.stringify({
            character_id: window.characterId
        })
        
    })
    .then(response => response.json())
    .then((result) => {

        if ('error' in result) {
            return;
        }

        let summary = '<h3>Attack Summary</h3>'
        summary += `<p>${result.creature.name} damage: ${result.damage_done}</p>`;
        summary += `<p>Received damage: ${result.damage_received}</p>`;

        if (result.character_died) {
            summary += '<h4>You have died!</h4>';
            summary += `<p>Lost: ${result.lost} gold coins</p>`;
        } else if (result.creature_died) {
            summary += `<h5>The ${result.creature.name} is dead</h5>`;
            summary += `<p>Loot: ${result.loot} gold coins</p>`;
            summary += `<p>You earned ${result.received_experience} points experience</p>`;

            if (result.level_up) {
                summary += `<h4>You have advanced to level ${result.character.level}</h5>`;
            }
        }

        loadCreatures(page);
        updateCharacterInfo();

        document.querySelector('#modal-body').innerHTML = summary;

        const modal = document.querySelector("#modal");
        document.querySelector('#modal-footer').innerHTML = '<buttom class="btn btn-game" id="close-modal-button">Close</button>'
        
        modal.classList.remove("hidden");
        const closeModalButton = document.querySelector("#close-modal-button");
        closeModalButton.onclick = (e) => {
            document.querySelector("#modal").classList.add("hidden");
        };
    });
}

function buySpell(spellId) {
    fetch(`/game/spells/${spellId}/buy/`, {
        method: 'PUT',
        body: JSON.stringify({
            character_id: window.characterId
        })
        
    })
    .then(response => response.json())
    .then((result) => {

        let summary = '<h3>Spell Purchase Result</h3>'

        if ('error' in result) {
            summary += `<p>${result.error}</p>`;
        } else if (result.added_life > 0) {
            summary += `<p>You have recovered ${result.added_life} life points.</p>`;
        } else {
            summary += `<p>You have recovered ${result.added_mana} mana points.</p>`;
        }

        updateCharacterInfo();

        document.querySelector('#modal-body').innerHTML = summary;

        const modal = document.querySelector("#modal");
        document.querySelector('#modal-footer').innerHTML = '<buttom class="btn btn-game" id="close-modal-button">Close</button>'
        
        modal.classList.remove("hidden");
        const closeModalButton = document.querySelector("#close-modal-button");
        closeModalButton.onclick = (e) => {
            document.querySelector("#modal").classList.add("hidden");
        };
    });
}

function sendLetter(receiverId, characterName) {

    let html = `<h3>Letter to ${characterName}</h3>`;

    html += '<form id="letter-form">';
    html += '<div class="form-group">';
    html += '<input type="text" class="form-control" id="letter-title" placeholder="Title">';
    html += '</div>';
    html += '<div class="form-group">';
    html += '<textarea class="form-control" id="letter-content" placeholder="Content" rows="10"></textarea>';
    html += '</div>';
    html += '<input type="submit" class="btn btn-game" value="Send">'
    html += '</form>';

    document.querySelector('#modal-body').innerHTML = html;

    const modal = document.querySelector("#modal");
    document.querySelector('#modal-footer').innerHTML = '<buttom class="btn btn-game" id="close-modal-button">Close</button>'
    
    modal.classList.remove("hidden");
    const closeModalButton = document.querySelector("#close-modal-button");
    closeModalButton.onclick = (e) => {
        document.querySelector("#modal").classList.add("hidden");
    };

    document.querySelector('#letter-form').onsubmit = () => {
        document.querySelector("#modal").classList.add("hidden");

        fetch(`/game/letters/${window.characterId}/send/`, {
            method: 'POST',
            body: JSON.stringify({
                receiver_id: receiverId,
                title: document.querySelector('#letter-title').value,
                content: document.querySelector('#letter-content').value
            })
            
        })
        .then(response => response.json())
        .then((result) => {
            let summary = '<h3>Letter Sending Result</h3>';

            if ('error' in result) {
                summary += '<p>There was an error sending the letter. Try again later.</p>';
            } else {
                summary += `<p>The letter has been sent to ${characterName}.</p>`
            }

            document.querySelector('#modal-body').innerHTML = summary;
            modal.classList.remove("hidden");
        });

        return false;
    };
}

function viewLetter(letterId, page) {
    fetch(`/game/letters/${window.characterId}/${letterId}/`)
    .then(response => response.json())
    .then((result) => {

        let html = '';

        if ('error' in result) {
            html = '<p>Error retrieving the letter.</p>';
        } else {
            html = `<h3>Letter from ${result.sender}</h3>`;
            html += '<div class="form-group">';
            html += `<input type="text" class="form-control" value="${result.title}" readonly>`;
            html += '</div>';
            html += '<div class="form-group">';
            html += `<textarea class="form-control" rows="10" readonly>${result.content}</textarea>`;
            html += '</div>';
        }


        document.querySelector('#modal-body').innerHTML = html;

        const modal = document.querySelector("#modal");
        document.querySelector('#modal-footer').innerHTML = '<buttom class="btn btn-game" id="close-modal-button">Close</button>'
        
        modal.classList.remove("hidden");
        const closeModalButton = document.querySelector("#close-modal-button");
        closeModalButton.onclick = (e) => {
            document.querySelector("#modal").classList.add("hidden");

            fetch(`/game/letters/${window.characterId}/${letterId}/mark_read/`, {method: 'PUT'});
            loadLetters(page);
        };
    });
}

function checkForNewLetters() {
    fetch(`/game/letters/${window.characterId}/count_unread/`)
    .then(response => response.json())
    .then((result) => { 
        if ('error' in result) {
            return;
        }

        if (result.count > 0) {
            document.querySelector('#unread-letters-counter').innerHTML = `<strong>(${result.count})</strong>`;
        } else {
            document.querySelector('#unread-letters-counter').innerHTML = '';
        }
    });
}