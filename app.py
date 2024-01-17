from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pokedex.sqlite"

db = SQLAlchemy(app)

class Pokemon(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    order = Column(Integer, nullable=False)
    type = Column(String, nullable=False)

with app.app_context():
    db.create_all()

def get_pokemon_data(pokemon):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon}'
    r = requests.get(url).json()
    return r

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pokemon_name = request.form.get('pokemon_name')
        if pokemon_name:
            return search_pokemon(pokemon_name)
    return render_template('pokemon.html', pokemon=None)

@app.route("/pokemon/<name>")
def search_pokemon(name):
    data = get_pokemon_data(name.lower())
    if 'sprites' not in data or 'other' not in data['sprites']:
        return render_template('pokemon.html', pokemon=None)

    other_sprites = data['sprites']['other']
    
    official_artwork = other_sprites.get('official-artwork', {}).get('front_default')
    dream_artwork = other_sprites.get('dream-artwork', {}).get('front_default')

    if not official_artwork:
        return render_template('pokemon.html', pokemon=None)

   
    pokemon_types = [t['type']['name'] for t in data.get('types', [])]
    if not pokemon_types:
        pokemon_types = ['Desconocido']

    pokemon = {
        'name': data['name'].upper(),
        'height': data['height'],
        'weight': data['weight'],
        'order': data['order'],
        'types': pokemon_types,  
        'hp': data.get('stats')[0].get('base_stat'),
        'attack': data.get('stats')[1].get('base_stat'),
        'defence': data.get('stats')[2].get('base_stat'),
        'speed': data.get('stats')[5].get('base_stat'),
        'photo': official_artwork,
        'photo1': dream_artwork
    }

    return render_template('pokemon.html', pokemon=pokemon)

@app.route("/detalle/<hp>/<attack>/<defence>/<speed>/")
def detalle(hp, attack, defence, speed):
    return render_template('detalle.html', hp=hp, attack=attack, defence=defence, speed=speed)

@app.route("/insert_pokemon/<pokemon_name>")
def insert(pokemon_name):
    data = get_pokemon_data(pokemon_name)
    if data:
        new_pokemon = Pokemon(
            name=data['name'],
            height=data['height'],
            weight=data['weight'],
            order=data['order'],
            type='Estudiante'
        )
        db.session.add(new_pokemon)
        db.session.commit()
        return 'Pokemon Agregado'
    return 'No se pudo obtener información del Pokemon'

@app.route("/select")
def select():
    lista_pokemon = Pokemon.query.all()
    for p in lista_pokemon:
        print(p.name)
    return 'alo'

@app.route("/selectbyname/<name>")
def selectbyname(name):
    poke = Pokemon.query.filter_by(name=name).first()
    return str(poke.id), str(poke.name)

@app.route("/selectbyid/<id>")
def selectbyid(id):
    poke = Pokemon.query.filter_by(id=id).first()
    return str(poke.id) + str(poke.name)

@app.route("/deletetbyid/<id>")
def deletetbyid(id):
    pokemon_a_eliminar = Pokemon.query.filter_by(id=id).first()
    db.session.delete(pokemon_a_eliminar)
    db.session.commit()
    return 'Pokemon Eliminado'

if __name__ == '__main__':
    app.run(debug=True)
