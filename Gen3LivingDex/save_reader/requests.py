import requests

def get_pokemon_with_abilities(start, end):
    url = "https://pokeapi.co/api/v2/pokemon/"
    pokemon_data = []
    
    for i in range(start, end + 1):
        response = requests.get(f"{url}{i}")
        if response.status_code == 200:
            data = response.json()
            abilities = [(ability['ability']['name'], ability['slot']) for ability in data['abilities']]
            pokemon_data.append({
                "id": data['id'],
                "name": data['name'],
                "abilities": abilities
            })
    
    return pokemon_data

# Example: Fetch Gen 1-3 Pokémon (ID range for these gens: 1-386)
pokemon_list = get_pokemon_with_abilities(1, 386)

# Print some data
for pokemon in pokemon_list:
    print(pokemon)
