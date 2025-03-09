import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ennemy_mod.db")


def connect_db():
    """Établit une connexion SQLite et crée les tables si elles n'existent pas."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Création des tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ennemis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                mouvement INTEGER NOT NULL,
                attaque INTEGER NOT NULL,
                pv INTEGER NOT NULL,
                pv_max INTEGER NOT NULL,
                elite INTEGER DEFAULT 0,
                image TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ennemis_combat (
                ennemi_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ennemi_source_id INTEGER,
                nom TEXT NOT NULL,
                mouvement INTEGER NOT NULL,
                attaque INTEGER NOT NULL,
                pv INTEGER NOT NULL,
                pv_max INTEGER NOT NULL,
                elite INTEGER DEFAULT 0,
                image TEXT,
                FOREIGN KEY (ennemi_source_id) REFERENCES ennemis(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        return conn

    except Exception as e:
        print(f"❌ Erreur connexion à la base de données : {e}")
        return None


def get_enemy_data(enemy_id):
    """Récupère les données d'un ennemi depuis la table `ennemis`."""
    conn = connect_db()
    if conn is None:
        print("❌ Erreur : Connexion à la base de données échouée.")
        return None

    cursor = conn.cursor()

    try:
        # Vérification si `enemy_id` est bien un ID ou un nom
        query = """
            SELECT id, nom, elite, boss, mouvement, attaque, pv, pv_max, image
            FROM ennemis
            WHERE id = ? OR nom = ?
        """
        cursor.execute(query, (enemy_id, enemy_id))
        result = cursor.fetchone()

        if result:
            return {
                "id": result[0],
                "nom": result[1],
                "elite": bool(result[2]),
                "boss": bool(result[3]),
                "mouvement": result[4],
                "attaque": result[5],
                "pv": result[6],
                "pv_max": result[7],
                "image": result[8]
            }
        else:
            print(f"❌ Aucun ennemi trouvé pour ID/Nom : {enemy_id}")
            return None

    except sqlite3.OperationalError as e:
        print(f"❌ Erreur SQLite : {e}")
        return None

    finally:
        cursor.close()
        conn.close()
