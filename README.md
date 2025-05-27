Projet Gestion Hôtelière (Streamlit & SQLite)
Ce projet propose une application web simple pour la gestion d’un hôtel, réalisée avec Streamlit (interface web) et SQLite (base de données).

Fonctionnalités principales
Ajout, modification et suppression de clients et de réservations

Consultation des chambres disponibles sur une période donnée

Affichage des statistiques de base (nombre de clients, réservations, chambres)

Installation et utilisation
Installer les dépendances :


pip install streamlit
Lancer l’application :

streamlit run app.py
L’application crée automatiquement la base SQLite (hotel.db) au premier lancement.

Structure
app.py : code principal de l’interface Streamlit et gestion de la base

hotel.db : base de données SQLite (créée automatiquement)

À propos
Projet pédagogique – gestion de base de données relationnelle et interface web simple.
