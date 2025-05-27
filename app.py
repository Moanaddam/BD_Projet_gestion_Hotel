import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta

def init_database():
    """Initialise la base de données avec toutes les tables nécessaires"""
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    
    # Vérifier si les tables existent déjà
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [table[0] for table in cursor.fetchall()]
    
    if not existing_tables:
        st.info("Création de la base de données...")
        
        # Création des tables (code identique à avant)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Hotel (
            id_hotel INTEGER PRIMARY KEY,
            ville TEXT NOT NULL,R
            pays TEXT NOT NULL,
            code_postal INTEGER
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Client (
            id_client INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            adresse TEXT,
            ville TEXT,
            code_postal INTEGER,
            email TEXT,
            telephone TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS TypeChambre (
            id_type INTEGER PRIMARY KEY,
            libelle TEXT NOT NULL,
            prix_base REAL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chambre (
            id_chambre INTEGER PRIMARY KEY,
            numero INTEGER,
            etage INTEGER,
            vue_mer INTEGER DEFAULT 0,
            id_hotel INTEGER,
            id_type INTEGER,
            FOREIGN KEY (id_hotel) REFERENCES Hotel(id_hotel),
            FOREIGN KEY (id_type) REFERENCES TypeChambre(id_type)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reservation (
            id_reservation INTEGER PRIMARY KEY,
            date_debut TEXT NOT NULL,
            date_fin TEXT NOT NULL,
            id_client INTEGER,
            FOREIGN KEY (id_client) REFERENCES Client(id_client)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ReservationChambre (
            id_reservation INTEGER,
            id_chambre INTEGER,
            PRIMARY KEY (id_reservation, id_chambre),
            FOREIGN KEY (id_reservation) REFERENCES Reservation(id_reservation),
            FOREIGN KEY (id_chambre) REFERENCES Chambre(id_chambre)
        )
        ''')
        
        # Insertion de données de test
        insert_sample_data(cursor)
        
        conn.commit()
        st.success("Base de données créée avec succès!")
    
    conn.close()

def insert_sample_data(cursor):
    """Insère des données d'exemple"""
    try:
        # Hôtels
        cursor.execute("INSERT OR IGNORE INTO Hotel VALUES (1, 'Paris', 'France', 75001)")
        cursor.execute("INSERT OR IGNORE INTO Hotel VALUES (2, 'Lyon', 'France', 69002)")
        
        # Types de chambres
        cursor.execute("INSERT OR IGNORE INTO TypeChambre VALUES (1, 'Simple', 80)")
        cursor.execute("INSERT OR IGNORE INTO TypeChambre VALUES (2, 'Double', 120)")
        
        # Clients
        cursor.execute("INSERT OR IGNORE INTO Client VALUES (1, 'Jean Dupont', '12 Rue de Paris', 'Paris', 75001, 'jean@email.fr', '0612345678')")
        cursor.execute("INSERT OR IGNORE INTO Client VALUES (2, 'Marie Leroy', '5 Avenue Victor Hugo', 'Lyon', 69002, 'marie@email.fr', '0623456789')")
        cursor.execute("INSERT OR IGNORE INTO Client VALUES (3, 'mohamed', '8 Boulevard Saint-Michel', 'Marseille', 13005, 'mohamed@email.fr', '0634567890')")
        
        # Chambres
        cursor.execute("INSERT OR IGNORE INTO Chambre VALUES (1, 201, 2, 0, 1, 1)")
        cursor.execute("INSERT OR IGNORE INTO Chambre VALUES (2, 502, 5, 1, 1, 2)")
        cursor.execute("INSERT OR IGNORE INTO Chambre VALUES (3, 305, 3, 0, 2, 1)")
        cursor.execute("INSERT OR IGNORE INTO Chambre VALUES (4, 410, 4, 0, 2, 2)")
        
        # Réservations
        cursor.execute("INSERT OR IGNORE INTO Reservation VALUES (1, '2025-05-27', '2025-05-28', 3)")
        cursor.execute("INSERT OR IGNORE INTO Reservation VALUES (2, '2025-07-01', '2025-07-05', 2)")
        cursor.execute("INSERT OR IGNORE INTO Reservation VALUES (3, '2025-05-27', '2025-05-28', 3)")
        
        # Liens réservation-chambre
        cursor.execute("INSERT OR IGNORE INTO ReservationChambre VALUES (1, 1)")
        cursor.execute("INSERT OR IGNORE INTO ReservationChambre VALUES (2, 2)")
        cursor.execute("INSERT OR IGNORE INTO ReservationChambre VALUES (3, 1)")
        
    except sqlite3.Error as e:
        st.error(f"Erreur lors de l'insertion des données: {e}")

def get_connection():
    """Retourne une connexion à la base de données"""
    return sqlite3.connect('hotel.db')

def modifier_reservation(reservation_id, nouvelle_date_debut, nouvelle_date_fin, nouvelle_chambre_id):
    """Modifie une réservation existante"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Mise à jour de la réservation
        cursor.execute('''
        UPDATE Reservation 
        SET date_debut = ?, date_fin = ? 
        WHERE id_reservation = ?
        ''', (nouvelle_date_debut, nouvelle_date_fin, reservation_id))
        
        # Mise à jour de la chambre associée
        cursor.execute('''
        UPDATE ReservationChambre 
        SET id_chambre = ? 
        WHERE id_reservation = ?
        ''', (nouvelle_chambre_id, reservation_id))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la modification: {e}")
        return False
    finally:
        conn.close()

def supprimer_reservation(reservation_id):
    """Supprime une réservation"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Supprimer d'abord les liens
        cursor.execute("DELETE FROM ReservationChambre WHERE id_reservation = ?", (reservation_id,))
        # Puis la réservation
        cursor.execute("DELETE FROM Reservation WHERE id_reservation = ?", (reservation_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la suppression: {e}")
        return False
    finally:
        conn.close()

def main():
    st.set_page_config(
        page_title="Gestion d'Hôtel",
        page_icon="🏨",
        layout="wide"
    )
    
    st.title("Gestion Hôtelière Avancée")
    
    # Initialiser la base de données au démarrage
    if 'db_initialized' not in st.session_state:
        init_database()
        st.session_state.db_initialized = True
    
    # Menu de navigation
    menu = st.sidebar.selectbox("Menu", [
        "Tableau de Bord",
        "Gestion des Réservations", 
        "Gestion des Clients",
        "Chambres Disponibles",
        "Nouveau Client",
        "Nouvelle Réservation"
    ])
    
    if menu == "Tableau de Bord":
        st.header("Tableau de Bord")
        
        col1, col2, col3 = st.columns(3)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        with col1:
            cursor.execute("SELECT COUNT(*) FROM Reservation")
            nb_reservations = cursor.fetchone()[0]
            st.metric("Total Réservations", nb_reservations)
        
        with col2:
            cursor.execute("SELECT COUNT(*) FROM Client")
            nb_clients = cursor.fetchone()[0]
            st.metric("Total Clients", nb_clients)
        
        with col3:
            cursor.execute("SELECT COUNT(*) FROM Chambre")
            nb_chambres = cursor.fetchone()[0]
            st.metric("Total Chambres", nb_chambres)
        
        conn.close()
    
    elif menu == "Gestion des Réservations":
        st.header("Gestion des Réservations")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT R.id_reservation, R.date_debut, R.date_fin, 
               C.nom, CH.numero, H.ville
        FROM Reservation R
        JOIN Client C ON R.id_client = C.id_client
        JOIN ReservationChambre RC ON R.id_reservation = RC.id_reservation
        JOIN Chambre CH ON RC.id_chambre = CH.id_chambre
        JOIN Hotel H ON CH.id_hotel = H.id_hotel
        ORDER BY R.date_debut DESC
        ''')
        reservations = cursor.fetchall()
        
        if reservations:
            st.subheader("Liste des Réservations")
            for reservation in reservations:
                with st.expander(f"Réservation #{reservation[0]} - {reservation[3]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Client:** {reservation[3]}")
                        st.write(f"**Dates:** {reservation[1]} au {reservation[2]}")
                    with col2:
                        st.write(f"**Chambre:** {reservation[4]}")
                        st.write(f"**Hôtel:** {reservation[5]}")
                    
                    # Boutons d'action
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button(f"Modifier", key=f"edit_{reservation[0]}"):
                            st.session_state[f'edit_reservation_{reservation[0]}'] = True
                            # Utiliser st.rerun() au lieu de st.experimental_rerun()
                            st.rerun()
                    
                    with col_delete:
                        if st.button(f"Supprimer", key=f"delete_{reservation[0]}"):
                            if supprimer_reservation(reservation[0]):
                                st.success("Réservation supprimée!")
                                # Utiliser st.rerun() au lieu de st.experimental_rerun()
                                st.rerun()
                    
                    # Formulaire de modification (si activé)
                    if st.session_state.get(f'edit_reservation_{reservation[0]}', False):
                        st.subheader("Modifier la Réservation")
                        
                        # Récupérer les chambres disponibles
                        cursor.execute("SELECT id_chambre, numero FROM Chambre")
                        chambres = cursor.fetchall()
                        
                        with st.form(f"edit_form_{reservation[0]}"):
                            nouvelle_date_debut = st.date_input(
                                "Nouvelle date d'arrivée", 
                                value=datetime.strptime(reservation[1], "%Y-%m-%d").date(),
                                key=f"date_debut_{reservation[0]}"
                            )
                            nouvelle_date_fin = st.date_input(
                                "Nouvelle date de départ", 
                                value=datetime.strptime(reservation[2], "%Y-%m-%d").date(),
                                key=f"date_fin_{reservation[0]}"
                            )
                            
                            chambre_options = {f"Chambre {ch[1]}": ch[0] for ch in chambres}
                            current_chambre = f"Chambre {reservation[4]}"
                            default_index = list(chambre_options.keys()).index(current_chambre) if current_chambre in chambre_options else 0
                            
                            nouvelle_chambre_display = st.selectbox(
                                "Nouvelle chambre", 
                                list(chambre_options.keys()),
                                index=default_index,
                                key=f"chambre_{reservation[0]}"
                            )
                            nouvelle_chambre_id = chambre_options[nouvelle_chambre_display]
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("Enregistrer"):
                                    if modifier_reservation(
                                        reservation[0], 
                                        nouvelle_date_debut.strftime("%Y-%m-%d"), 
                                        nouvelle_date_fin.strftime("%Y-%m-%d"), 
                                        nouvelle_chambre_id
                                    ):
                                        st.success("Réservation modifiée avec succès!")
                                        del st.session_state[f'edit_reservation_{reservation[0]}']
                                        st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("Annuler"):
                                    del st.session_state[f'edit_reservation_{reservation[0]}']
                                    st.rerun()
        else:
            st.info("Aucune réservation trouvée")
        
        conn.close()
    
    elif menu == "Gestion des Clients":
        st.header("Gestion des Clients")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM Client ORDER BY nom")
        clients = cursor.fetchall()
        
        if clients:
            st.subheader("Liste des Clients")
            for client in clients:
                with st.expander(f"{client[1]} ({client[5]})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Nom:** {client[1]}")
                        st.write(f"**Adresse:** {client[2]}")
                        st.write(f"**Ville:** {client[3]} ({client[4]})")
                    with col2:
                        st.write(f"**Email:** {client[5]}")
                        st.write(f"**Téléphone:** {client[6]}")
                    
                    # Boutons d'action
                    col_edit, col_delete = st.columns(2)
                    with col_delete:
                        if st.button(f"Supprimer", key=f"delete_client_{client[0]}"):
                            try:
                                cursor.execute("DELETE FROM Client WHERE id_client = ?", (client[0],))
                                conn.commit()
                                st.success("Client supprimé!")
                                st.rerun()  # Changé de st.experimental_rerun() à st.rerun()
                            except sqlite3.IntegrityError:
                                st.error("Impossible de supprimer : client a des réservations associées")
        else:
            st.info("Aucun client trouvé")
        
        conn.close()
    
    elif menu == "Chambres Disponibles":
        st.header("Recherche de Chambres Disponibles")
        
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input("Date d'arrivée", value=date.today())
        with col2:
            date_fin = st.date_input("Date de départ", value=date.today() + timedelta(days=1))
        
        if st.button("Rechercher"):
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT Ch.id_chambre, Ch.numero, Ch.etage, H.ville, TC.libelle, TC.prix_base
            FROM Chambre Ch
            JOIN Hotel H ON Ch.id_hotel = H.id_hotel
            JOIN TypeChambre TC ON Ch.id_type = TC.id_type
            WHERE Ch.id_chambre NOT IN (
                SELECT RC.id_chambre
                FROM ReservationChambre RC
                JOIN Reservation R ON RC.id_reservation = R.id_reservation
                WHERE R.date_debut <= ? AND R.date_fin >= ?
            )
            ''', (date_fin.strftime('%Y-%m-%d'), date_debut.strftime('%Y-%m-%d')))
            
            chambres_dispo = cursor.fetchall()
            
            if chambres_dispo:
                st.success(f"{len(chambres_dispo)} chambre(s) disponible(s)")
                for chambre in chambres_dispo:
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.write(f"**Chambre {chambre[1]}** (Étage {chambre[2]})")
                        st.write(f"{chambre[3]}")
                    with col2:
                        st.write(f"Type: {chambre[4]}")
                        st.write(f"Prix: {chambre[5]}€/nuit")
            else:
                st.error("Aucune chambre disponible pour cette période")
            
            conn.close()
    
    elif menu == "Nouveau Client":
        st.header("Ajouter un Nouveau Client")
        
        with st.form("nouveau_client"):
            nom = st.text_input("Nom complet *", placeholder="Ex: Jean Dupont")
            adresse = st.text_input("Adresse *", placeholder="Ex: 12 Rue de la Paix")
            ville = st.text_input("Ville *", placeholder="Ex: Paris")
            code_postal = st.number_input("Code postal *", min_value=0, step=1, format="%d")
            email = st.text_input("Email *", placeholder="Ex: jean.dupont@email.fr")
            telephone = st.text_input("Téléphone *", placeholder="Ex: 0612345678")
            
            submitted = st.form_submit_button("Enregistrer le Client")
            
            if submitted:
                if nom and adresse and ville and code_postal and email and telephone:
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT MAX(id_client) FROM Client")
                    last_id = cursor.fetchone()[0] or 0
                    new_id = last_id + 1
                    
                    try:
                        cursor.execute(
                            "INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (new_id, nom, adresse, ville, code_postal, email, telephone)
                        )
                        conn.commit()
                        st.success(f"Client {nom} ajouté avec succès!")
                        
                    except sqlite3.IntegrityError:
                        st.error("Erreur: Un client avec cet email existe déjà")
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
                    finally:
                        conn.close()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
    
    elif menu == "Nouvelle Réservation":
        st.header("Nouvelle Réservation")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_client, nom FROM Client ORDER BY nom")
        clients = cursor.fetchall()
        
        if not clients:
            st.warning("Aucun client trouvé. Veuillez d'abord ajouter des clients.")
        else:
            with st.form("nouvelle_reservation"):
                client_options = {f"{client[1]} (ID: {client[0]})": client[0] for client in clients}
                selected_client_display = st.selectbox("Sélectionner un client", list(client_options.keys()))
                client_id = client_options[selected_client_display]
                
                col1, col2 = st.columns(2)
                with col1:
                    date_debut = st.date_input("Date d'arrivée", value=date.today())
                with col2:
                    date_fin = st.date_input("Date de départ", value=date.today() + timedelta(days=1))
                
                if date_debut < date_fin:
                    cursor.execute('''
                    SELECT Ch.id_chambre, Ch.numero, H.ville, TC.libelle, TC.prix_base
                    FROM Chambre Ch
                    JOIN Hotel H ON Ch.id_hotel = H.id_hotel
                    JOIN TypeChambre TC ON Ch.id_type = TC.id_type
                    WHERE Ch.id_chambre NOT IN (
                        SELECT RC.id_chambre
                        FROM ReservationChambre RC
                        JOIN Reservation R ON RC.id_reservation = R.id_reservation
                        WHERE R.date_debut <= ? AND R.date_fin >= ?
                    )
                    ''', (date_fin.strftime('%Y-%m-%d'), date_debut.strftime('%Y-%m-%d')))
                    
                    chambres_dispo = cursor.fetchall()
                    
                    if chambres_dispo:
                        chambre_options = {
                            f"Chambre {ch[1]} - {ch[2]} ({ch[3]}) - {ch[4]}€/nuit": ch[0] 
                            for ch in chambres_dispo
                        }
                        selected_chambre_display = st.selectbox("Sélectionner une chambre", list(chambre_options.keys()))
                        chambre_id = chambre_options[selected_chambre_display]
                        
                        submitted = st.form_submit_button("Confirmer la Réservation")
                        
                        if submitted:
                            cursor.execute("SELECT MAX(id_reservation) FROM Reservation")
                            last_id = cursor.fetchone()[0] or 0
                            new_id = last_id + 1
                            
                            try:
                                cursor.execute(
                                    "INSERT INTO Reservation VALUES (?, ?, ?, ?)",
                                    (new_id, date_debut.strftime('%Y-%m-%d'), date_fin.strftime('%Y-%m-%d'), client_id)
                                )
                                
                                cursor.execute(
                                    "INSERT INTO ReservationChambre VALUES (?, ?)",
                                    (new_id, chambre_id)
                                )
                                
                                conn.commit()
                                st.success(f"Réservation #{new_id} confirmée avec succès!")
                                
                            except Exception as e:
                                st.error(f"Erreur lors de la création de la réservation: {str(e)}")
                    else:
                        st.error("Aucune chambre disponible pour cette période")
                else:
                    st.error("La date de départ doit être postérieure à la date d'arrivée")
        
        conn.close()

if __name__ == "__main__":
    main()