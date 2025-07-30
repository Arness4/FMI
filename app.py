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
    return """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Évangélisation Madagascar</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow-x: hidden;
            min-height: 100vh;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            min-height: 100vh;
            position: relative;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            animation: float 20s infinite linear;
        }

        @keyframes float {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            position: relative;
            z-index: 2;
        }

        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            position: relative;
            z-index: 2;
        }

        .flag {
            display: inline-block;
            margin-left: 8px;
            font-size: 1.5rem;
        }

        /* Language Toggle */
        .language-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 15px;
            border-radius: 25px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 3;
        }

        .language-toggle:hover {
            background: rgba(255,255,255,0.3);
            transform: scale(1.05);
        }

        /* Main Content Layout */
        .main-content {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
            padding: 20px;
        }

        @media (min-width: 768px) {
            .main-content {
                grid-template-columns: 300px 1fr;
                gap: 30px;
                padding: 30px;
            }
        }

        @media (min-width: 1200px) {
            .main-content {
                grid-template-columns: 350px 1fr 300px;
            }
        }

        /* Sidebar */
        .sidebar {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            height: fit-content;
            position: sticky;
            top: 20px;
        }

        /* Search & Filter Section */
        .search-section {
            margin-bottom: 30px;
        }

        .search-bar {
            position: relative;
            margin-bottom: 20px;
        }

        .search-input {
            width: 100%;
            padding: 15px 50px 15px 20px;
            border: 2px solid #e1e8ed;
            border-radius: 25px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: #ff6b6b;
            box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
        }

        .search-icon {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: #999;
            font-size: 1.2rem;
        }

        .filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 10px 18px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .filter-btn.active {
            background: #ff6b6b;
            color: white;
            border-color: #ff6b6b;
        }

        .filter-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* Stats Cards */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
            border-left: 4px solid #ff6b6b;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            color: #ff6b6b;
            margin-bottom: 8px;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Content Area */
        .content-area {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 25px;
            color: #333;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .section-title::before {
            content: '';
            width: 4px;
            height: 25px;
            background: #ff6b6b;
            margin-right: 15px;
            border-radius: 2px;
        }

        .add-btn {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .add-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
        }

        /* People Grid */
        .people-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }

        @media (max-width: 768px) {
            .people-grid {
                grid-template-columns: 1fr;
            }
        }

        .person-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #ff6b6b;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .person-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #ff6b6b, #ee5a24);
        }

        .person-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .person-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }

        .person-name {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }

        .person-contact {
            font-size: 0.95rem;
            color: #666;
        }

        .person-date {
            font-size: 0.85rem;
            color: #999;
            background: #f8f9fa;
            padding: 5px 10px;
            border-radius: 12px;
        }

        .person-details {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #f0f0f0;
        }

        .detail-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-size: 0.9rem;
        }

        .detail-icon {
            width: 18px;
            margin-right: 10px;
            color: #ff6b6b;
        }

        .detail-text {
            color: #666;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            backdrop-filter: blur(5px);
        }

        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal-content {
            background: white;
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            border-radius: 20px;
            padding: 40px;
            position: relative;
            animation: slideUp 0.3s ease;
            overflow-y: auto;
        }

        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .modal-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .modal-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }

        .modal-subtitle {
            color: #666;
            font-size: 1rem;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group.full-width {
            grid-column: 1 / -1;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
            font-size: 0.95rem;
        }

        .form-input, .form-select {
            width: 100%;
            padding: 15px 18px;
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: #ff6b6b;
            box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1);
        }

        .form-actions {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: flex-end;
        }

        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            min-width: 120px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
        }

        .btn-secondary {
            background: #f8f9fa;
            color: #666;
            border: 1px solid #dee2e6;
        }

        .btn-secondary:hover {
            background: #e9ecef;
        }

        .close-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            background: none;
            border: none;
            font-size: 1.5rem;
            color: #999;
            cursor: pointer;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.3s ease;
        }

        .close-btn:hover {
            background: #f0f0f0;
            transform: rotate(90deg);
        }

        /* Loading and Empty States */
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 60px;
            font-size: 1.1rem;
            color: #666;
        }

        .loading::before {
            content: '⏳';
            margin-right: 10px;
            font-size: 1.5rem;
            animation: spin 2s infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }

        .empty-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.3;
        }

        .empty-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .empty-text {
            font-size: 1rem;
            line-height: 1.5;
        }

        /* Notification */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            z-index: 1001;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification.error {
            background: #dc3545;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
            
            .header .subtitle {
                font-size: 1rem;
            }
            
            .main-content {
                grid-template-columns: 1fr;
                padding: 15px;
            }
            
            .sidebar {
                position: static;
                margin-bottom: 20px;
            }
            
            .modal-content {
                width: 95%;
                padding: 25px;
            }
            
            .form-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <button class="language-toggle" onclick="toggleLanguage()">🇫🇷 FR</button>
            <h1>Évangélisation<span class="flag">🇲🇬</span></h1>
            <p class="subtitle">Fiangonana sy Fitoriana</p>
        </div>

        <!-- Main Content -->
        <div class="main-content">
            <!-- Sidebar -->
            <div class="sidebar">
                <!-- Search & Filter Section -->
                <div class="search-section">
                    <div class="search-bar">
                        <input type="text" class="search-input" placeholder="Rechercher une personne..." id="searchInput">
                        <span class="search-icon">🔍</span>
                    </div>
                    <div class="filters">
                        <button class="filter-btn active" onclick="filterBy('all')">Tous</button>
                        <button class="filter-btn" onclick="filterBy('recent')">Récents</button>
                        <button class="filter-btn" onclick="filterBy('commune')">Par commune</button>
                        <button class="filter-btn" onclick="filterBy('inviteur')">Par inviteur</button>
                    </div>
                </div>

                <!-- Stats -->
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="totalCount">0</div>
                        <div class="stat-label">Personnes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="communeCount">0</div>
                        <div class="stat-label">Communes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="todayCount">0</div>
                        <div class="stat-label">Aujourd'hui</div>
                    </div>
                </div>
            </div>

            <!-- Content Area -->
            <div class="content-area">
                <div class="section-title">
                    📋 Personnes rencontrées
                    <button class="add-btn" onclick="openAddModal()">➕ Ajouter</button>
                </div>
                
                <div id="peopleContainer">
                    <div class="loading">Chargement des données...</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Person Modal -->
    <div class="modal" id="addModal">
        <div class="modal-content">
            <button class="close-btn" onclick="closeAddModal()">✕</button>
            <div class="modal-header">
                <h2 class="modal-title">Nouvelle personne</h2>
                <p class="modal-subtitle">Ajouter une personne rencontrée</p>
            </div>
            
            <form id="addPersonForm">
                <div class="form-grid">
                    <div class="form-group">
                        <label class="form-label">Nom *</label>
                        <input type="text" name="nom" class="form-input" placeholder="Ex: Rakoto" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Prénom *</label>
                        <input type="text" name="prenom" class="form-input" placeholder="Ex: Jean Michel" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Téléphone</label>
                        <input type="tel" name="telephone" class="form-input" placeholder="+261 34 12 345 67">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Commune *</label>
                        <input type="text" name="commune" class="form-input" placeholder="Ex: Antananarivo" required list="communeList">
                        <datalist id="communeList"></datalist>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Fokontany *</label>
                        <input type="text" name="fokontany" class="form-input" placeholder="Ex: Analakely" required list="fokontanyList">
                        <datalist id="fokontanyList"></datalist>
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">Quartier</label>
                        <input type="text" name="quartier" class="form-input" placeholder="Ex: Centre ville" list="quartierList">
                        <datalist id="quartierList"></datalist>
                    </div>
                    
                    <div class="form-group full-width">
                        <label class="form-label">Nom de l'inviteur</label>
                        <input type="text" name="nom_inviteur" class="form-input" placeholder="Personne qui a invité" list="inviteurList">
                        <datalist id="inviteurList"></datalist>
                    </div>
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeAddModal()">Annuler</button>
                    <button type="submit" class="btn btn-primary">Ajouter</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Notification -->
    <div id="notification" class="notification"></div>

    <script>
        let currentLanguage = 'fr';
        let people = [];
        let uniqueValues = {};
        const API_BASE = 'https://fmi-new.render.com';

        // Initialize the app
        document.addEventListener('DOMContentLoaded', function() {
            loadPeople();
            loadUniqueValues();
        });

        // API Functions
        async function loadPeople() {
            try {
                const response = await fetch(`${API_BASE}/convertis`);
                if (!response.ok) throw new Error('Network response was not ok');
                people = await response.json();
                renderPeople(people);
                updateStats();
            } catch (error) {
                console.error('Error loading people:', error);
                showNotification('Erreur lors du chargement des données', 'error');
                renderEmptyState();
            }
        }

        async function loadUniqueValues() {
            try {
                const response = await fetch(`${API_BASE}/convertis/unique-values`);
                if (!response.ok) throw new Error('Network response was not ok');
                uniqueValues = await response.json();
                updateDataLists();
            } catch (error) {
                console.error('Error loading unique values:', error);
            }
        }

        async function addPerson(personData) {
            try {
                const response = await fetch(`${API_BASE}/convertis`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(personData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Erreur lors de l\'ajout');
                }
                
                const result = await response.json();
                showNotification('Personne ajoutée avec succès!');
                loadPeople(); // Reload the list
                loadUniqueValues(); // Update autocomplete lists
                return result;
            } catch (error) {
                console.error('Error adding person:', error);
                showNotification(error.message, 'error');
                throw error;
            }
        }

        // Render Functions
        function renderPeople(peopleToRender) {
            const container = document.getElementById('peopleContainer');
            
            if (peopleToRender.length === 0) {
                renderEmptyState();
                return;
            }
            
            const peopleGrid = document.createElement('div');
            peopleGrid.className = 'people-grid';
            
            peopleToRender.forEach(person => {
                const personCard = createPersonCard(person);
                peopleGrid.appendChild(personCard);
            });
            
            container.innerHTML = '';
            container.appendChild(peopleGrid);
        }

        function createPersonCard(person) {
            const card = document.createElement('div');
            card.className = 'person-card';
            
            const date = person.data_ajout ? new Date(person.data_ajout) : new Date();
            const dateStr = formatDate(date);
            
            card.innerHTML = `
                <div class="person-header">
                    <div>
                        <div class="person-name">${person.prenom} ${person.nom}</div>
                        <div class="person-contact">${person.telephone || 'Pas de téléphone'}</div>
                    </div>
                    <div class="person-date">${dateStr}</div>
                </div>
                <div class="person-details">
                    <div class="detail-item">
                        <span class="detail-icon">📍</span>
                        <span class="detail-text">${person.commune} - ${person.fokontany}</span>
                    </div>
                    ${person.quartier ? `
                    <div class="detail-item">
                        <span class="detail-icon">🏘️</span>
                        <span class="detail-text">${person.quartier}</span>
                    </div>
                    ` : ''}
                    ${person.nom_inviteur ? `
                    <div class="detail-item">
                        <span class="detail-icon">👤</span>
                        <span class="detail-text">Invité par ${person.nom_inviteur}</span>
                    </div>
                    ` : ''}
                </div>
            `;
            
            return card;
        }

        function renderEmptyState() {
            const container = document.getElementById('peopleContainer');
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <div class="empty-title">Aucune personne enregistrée</div>
                    <div class="empty-text">Commencez par ajouter une personne rencontrée lors de vos activités d'évangélisation.</div>
                </div>
            `;
        }

        // Utility Functions
        function formatDate(date) {
            const now = new Date();
            const diff = now - date;
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            
            if (days === 0) return 'Aujourd\'hui';
            if (days === 1) return 'Hier';
            if (days < 7) return `Il y a ${days} jours`;
            
            return date.toLocaleDateString('fr-FR');
        }

        function updateStats() {
            document.getElementById('totalCount').textContent = people.length;
            
            const communes = new Set(people.map(p => p.commune));
            document.getElementById('communeCount').textContent = communes.size;
            
            const today = new Date().toDateString();
            const todayCount = people.filter(p => {
                const personDate = new Date(p.data_ajout || p.date_ajout).toDateString();
                return personDate === today;
            }).length;
            document.getElementById('todayCount').textContent = todayCount;
        }

        function updateDataLists() {
            const lists = {
                'communeList': uniqueValues.communes || [],
                'fokontanyList': uniqueValues.fokontanys || [],
                'quartierList': uniqueValues.quartiers || [],
                'inviteurList': uniqueValues.inviteurs || []
            };
            
            Object.entries(lists).forEach(([listId, values]) => {
                const datalist = document.getElementById(listId);
                if (datalist) {
                    datalist.innerHTML = values.map(value => `<option value="${value}">`).join('');
                }
            });
        }

        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        // Event Handlers
        function toggleLanguage() {
            const toggle = document.querySelector('.language-toggle');
            const title = document.querySelector('.header h1');
            const subtitle = document.querySelector('.subtitle');
            
            if (currentLanguage === 'fr') {
                currentLanguage = 'mg';
                toggle.textContent = '🇲🇬 MG';
                title.innerHTML = 'Fitoriana<span class="flag">🇲🇬</span>';
                subtitle.textContent = 'Évangélisation et Mission';
                
                document.querySelector('.search-input').placeholder = 'Hitady olona...';
                document.querySelector('.modal-title').textContent = 'Olona vaovao';
                document.querySelector('.modal-subtitle').textContent = 'Hanampy olona nihaona';
                
            } else {
                currentLanguage = 'fr';
                toggle.textContent = '🇫🇷 FR';
                title.innerHTML = 'Évangélisation<span class="flag">🇲🇬</span>';
                subtitle.textContent = 'Fiangonana sy Fitoriana';
                
                document.querySelector('.search-input').placeholder = 'Rechercher une personne...';
                document.querySelector('.modal-title').textContent = 'Nouvelle personne';
                document.querySelector('.modal-subtitle').textContent = 'Ajouter une personne rencontrée';
            }
        }

        function filterBy(type) {
            // Remove active class from all filter buttons
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            event.target.classList.add('active');
            
            let filteredPeople = [...people];
            
            switch(type) {
                case 'recent':
                    const sevenDaysAgo = new Date();
                    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
                    filteredPeople = people.filter(p => {
                        const personDate = new Date(p.data_ajout || p.date_ajout);
                        return personDate >= sevenDaysAgo;
                    });
                    break;
                case 'commune':
                    // Group by commune - could implement dropdown for specific commune
                    break;
                case 'inviteur':
                    filteredPeople = people.filter(p => p.nom_inviteur && p.nom_inviteur.trim() !== '');
                    break;
                case 'all':
                default:
                    // Show all people
                    break;
            }
            
            renderPeople(filteredPeople);
        }

        function openAddModal() {
            document.getElementById('addModal').classList.add('active');
            document.body.style.overflow = 'hidden';
        }

        function closeAddModal() {
            document.getElementById('addModal').classList.remove('active');
            document.body.style.overflow = 'auto';
            document.getElementById('addPersonForm').reset();
        }

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const filteredPeople = people.filter(person => {
                const fullName = `${person.prenom} ${person.nom}`.toLowerCase();
                const commune = person.commune.toLowerCase();
                const fokontany = person.fokontany.toLowerCase();
                const quartier = (person.quartier || '').toLowerCase();
                const inviteur = (person.nom_inviteur || '').toLowerCase();
                
                return fullName.includes(searchTerm) || 
                       commune.includes(searchTerm) || 
                       fokontany.includes(searchTerm) ||
                       quartier.includes(searchTerm) ||
                       inviteur.includes(searchTerm);
            });
            
            renderPeople(filteredPeople);
        });

        // Form submission
        document.getElementById('addPersonForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const personData = {
                nom: formData.get('nom'),
                prenom: formData.get('prenom'),
                telephone: formData.get('telephone'),
                commune: formData.get('commune'),
                fokontany: formData.get('fokontany'),
                quartier: formData.get('quartier'),
                nom_inviteur: formData.get('nom_inviteur')
            };
            
            try {
                await addPerson(personData);
                closeAddModal();
            } catch (error) {
                // Error is already handled in addPerson function
            }
        });

        // Close modal when clicking outside
        document.getElementById('addModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeAddModal();
            }
        });

        // Prevent modal close when clicking inside modal content
        document.querySelector('.modal-content').addEventListener('click', function(e) {
            e.stopPropagation();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeAddModal();
            }
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                openAddModal();
            }
        });

        // Auto-refresh data every 30 seconds
        setInterval(() => {
            loadPeople();
        }, 30000);
    </script>
</body>
</html>"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
