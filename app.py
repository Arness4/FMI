from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///convertis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèle de données
class PersonneConvertie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    commune = db.Column(db.String(100), nullable=False)
    fokontany = db.Column(db.String(100), nullable=False)
    quartier = db.Column(db.String(100), nullable=True)
    nom_inviteur = db.Column(db.String(100), nullable=True)  # Changed to nullable=True
    date_ajout = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'telephone': self.telephone,
            'commune': self.commune,
            'fokontany': self.fokontany,
            'quartier': self.quartier,
            'nom_inviteur': self.nom_inviteur,
            'data_ajout': self.date_ajout.strftime('%Y-%m-%d %H:%M:%S') if self.date_ajout else None
        }

# Création de la base
with app.app_context():
    db.create_all()

# ➕ Ajouter une personne convertie
@app.route('/convertis', methods=['POST'])
def ajouter_converti():
    data = request.get_json()
    
    # Add validation for required fields (nom_inviteur removed from required fields)
    required_fields = ['nom', 'prenom', 'commune', 'fokontany']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'Le champ {field} est requis'}), 400
    
    personne = PersonneConvertie(
        nom=data['nom'],
        prenom=data['prenom'],
        telephone=data.get('telephone', ''),
        commune=data['commune'],
        fokontany=data['fokontany'],
        quartier=data.get('quartier', ''),
        nom_inviteur=data.get('nom_inviteur', ''),  # Default to empty string if not provided
        date_ajout=data.get('date_ajout', None)  # Optional field, can be None
    )
    db.session.add(personne)
    db.session.commit()
    return jsonify({'message': 'Personne enregistrée avec succès', 'id': personne.id}), 201

# 📃 Lister tous les convertis
@app.route('/convertis', methods=['GET'])
def lister_convertis():
    personnes = PersonneConvertie.query.all()
    return jsonify([p.to_dict() for p in personnes])

# 🔍 Filtrer par commune
@app.route('/convertis/commune/<commune>', methods=['GET'])
def filtrer_par_commune(commune):
    personnes = PersonneConvertie.query.filter_by(commune=commune).all()
    return jsonify([p.to_dict() for p in personnes])

# 🔍 Filtrer par nom d'inviteur
@app.route('/convertis/inviteur/<nom>', methods=['GET'])
def filtrer_par_inviteur(nom):
    personnes = PersonneConvertie.query.filter_by(nom_inviteur=nom).all()
    return jsonify([p.to_dict() for p in personnes])

# ❌ Supprimer un converti
@app.route('/convertis/<int:id>', methods=['DELETE'])
def supprimer_converti(id):
    personne = PersonneConvertie.query.get_or_404(id)
    db.session.delete(personne)
    db.session.commit()
    return jsonify({'message': 'Personne supprimée'})

# Add a route to get a single converti by ID
@app.route('/convertis/<int:id>', methods=['GET'])
def obtenir_converti(id):
    personne = PersonneConvertie.query.get_or_404(id)
    return jsonify(personne.to_dict())


# 🔍 Get unique values for autocomplete
@app.route('/convertis/unique-values', methods=['GET'])
def get_unique_values():
    communes = db.session.query(PersonneConvertie.commune).distinct().all()
    fokontanys = db.session.query(PersonneConvertie.fokontany).distinct().all()
    quartiers = db.session.query(PersonneConvertie.quartier).distinct().filter(PersonneConvertie.quartier != '').all()
    inviteurs = db.session.query(PersonneConvertie.nom_inviteur).distinct().filter(PersonneConvertie.nom_inviteur != '').all()
    
    return jsonify({
        'communes': [c[0] for c in communes],
        'fokontanys': [f[0] for f in fokontanys],
        'quartiers': [q[0] for q in quartiers],
        'inviteurs': [i[0] for i in inviteurs]
    })

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
