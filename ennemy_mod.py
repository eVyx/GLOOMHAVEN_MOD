import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from database import get_enemy_data, connect_db
from custom_card import CarteEnnemi
import sqlite3
import atexit

# Définition des dimensions
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 800
CARD_SPACING = 20  # Espacement entre les cartes
MAX_COLUMNS = 3  # Nombre max de cartes par ligne avant passage à la suivante

def connect_db():
    """Connexion à la base de données"""
    return sqlite3.connect("ennemy_mod.db")

def clear_table():
    """Vide la table 'ennemis_combat' et réinitialise l'auto-incrémentation."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ennemis_combat;")
        conn.commit()
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ennemis_combat';")
        conn.commit()
        cursor.execute("VACUUM;")
        conn.commit()
        print("✅ Table 'ennemis_combat' vidée et ID réinitialisé à 1.")
    except sqlite3.OperationalError as e:
        print(f"❌ Erreur lors du nettoyage : {e}")
    finally:
        cursor.close()
        conn.close()

atexit.register(clear_table)

class JeuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Ennemis - Gloomhaven")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="#2C2F33")

        self.ennemis_combat = {}
        self.style = Style("darkly")
        self.setup_ui()
        self.charger_liste_ennemis()

    def setup_ui(self):
        """Création de l'interface graphique avec une scrollbar."""
        self.frame_gauche = ttk.Frame(self.root, padding=10)
        self.frame_gauche.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.liste_ennemis = ttk.Combobox(self.frame_gauche, state="readonly")
        self.liste_ennemis.pack(pady=5)

        self.bouton_ajouter = ttk.Button(self.frame_gauche, text="Ajouter l'ennemi", bootstyle="primary", command=self.ajouter_ennemi)
        self.bouton_ajouter.pack(pady=10)

        self.battlefield_frame = ttk.Frame(self.root, padding=10)
        self.battlefield_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(self.battlefield_frame, bg="#2C2F33")
        self.scrollbar = ttk.Scrollbar(self.battlefield_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding=10)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def charger_liste_ennemis(self):
        """Charge la liste des ennemis."""
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nom FROM ennemis ORDER BY nom ASC")
            self.liste_ennemis["values"] = [nom[0] for nom in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def ajouter_ennemi(self):
        """Ajoute un ennemi dans la table `ennemis_combat` et l'affiche sur le champ de bataille."""
        selection = self.liste_ennemis.get()
        if not selection:
            print("❌ Aucun ennemi sélectionné")
            return

        enemy_data = get_enemy_data(selection)
        if not enemy_data:
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ennemis_combat (nom, mouvement, attaque, pv, pv_max, elite, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (selection, enemy_data["mouvement"], enemy_data["attaque"], enemy_data["pv"], enemy_data["pv_max"], enemy_data["elite"], enemy_data["image"]))
            conn.commit()

            enemy_id = cursor.lastrowid  
            print(f"✅ Ennemi ajouté avec ID: {enemy_id}")

            carte = CarteEnnemi(self.scrollable_frame, enemy_id)
            row = len(self.ennemis_combat) // MAX_COLUMNS
            col = len(self.ennemis_combat) % MAX_COLUMNS
            carte.grid(row=row, column=col, padx=10, pady=10)

            self.ennemis_combat[enemy_id] = carte
        finally:
            cursor.close()
            conn.close()

root = tk.Tk()
app = JeuGUI(root)
root.mainloop()
