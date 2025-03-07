import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import sqlite3
import os
from custom_card import CarteEnnemi, CartePreview

# 📌 Définition des dimensions
WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 800
CARD_SPACING = 20  # Espacement entre les cartes

# 📌 Connexion à la base de données
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ennemy_mod.db")

def connect_db():
    """Établit une connexion SQLite"""
    conn = sqlite3.connect(DB_PATH)
    return conn

def get_enemy_data(enemy_name):
    """Récupère les données d'un ennemi depuis la base de données"""
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nom, elite, pv, pv_max, mouvement, attaque, image FROM ennemis WHERE nom = ?", (enemy_name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nom": row[1].replace(" ELITE", ""),
            "elite": row[2],
            "pv": row[3],
            "pv_max": row[4],
            "mouvement": row[5],
            "attaque": row[6],
            "image": row[7] if row[7] else "default.png"
        }
    return None

class JeuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Ennemis - Gloomhaven")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg="#2C2F33")

        self.conn = connect_db()
        self.ennemis_combat = {}

        self.style = Style("darkly")

        self.setup_ui()
        self.charger_liste_ennemis()

    def setup_ui(self):
        """Création de l'interface graphique avec une scrollbar"""
        self.frame_gauche = ttk.Frame(self.root, padding=10)
        self.frame_gauche.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # 📜 Sélection de l'ennemi
        self.liste_ennemis = ttk.Combobox(self.frame_gauche, state="readonly")
        self.liste_ennemis.pack(pady=5)
        self.liste_ennemis.bind("<<ComboboxSelected>>", self.afficher_details_avant_ajout)

        self.bouton_ajouter = ttk.Button(self.frame_gauche, text="Ajouter l'ennemi", bootstyle="primary",
                                         command=self.ajouter_ennemi)
        self.bouton_ajouter.pack(pady=10)

        self.preview_container = ttk.Frame(self.frame_gauche, padding=10)
        self.preview_container.pack()

        # 🔽 **Ajout d'un conteneur scrollable pour le battlefield**
        self.battlefield_frame = ttk.Frame(self.root, padding=10)
        self.battlefield_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(self.battlefield_frame, bg="#2C2F33")
        self.scrollbar = ttk.Scrollbar(self.battlefield_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding=10)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def charger_liste_ennemis(self):
        """Charge la liste des ennemis et met en jaune les élites dans le menu déroulant."""
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nom, elite FROM ennemis ORDER BY nom ASC")
            ennemis = cursor.fetchall()

            self.liste_ennemis["values"] = [nom for nom, _ in ennemis]
        finally:
            cursor.close()
            conn.close()

    def afficher_details_avant_ajout(self, event):
        """Affiche une prévisualisation de l'ennemi avant son ajout."""
        selection = self.liste_ennemis.get()
        if not selection:
            return

        enemy_data = get_enemy_data(selection)
        if not enemy_data:
            return

        for widget in self.preview_container.winfo_children():
            widget.destroy()

        preview_card = CartePreview(self.preview_container, enemy_data["nom"], enemy_data["pv"], 
                                    enemy_data["elite"], enemy_data["mouvement"], enemy_data["attaque"])
        preview_card.pack()

    def ajouter_ennemi(self):
        """Ajoute un ennemi sur le champ de bataille en respectant l'affichage horizontal."""
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
            cursor.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM ennemis_combat")
            prochain_numero = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO ennemis_combat (ennemi_id, nom, numero, mouvement, attaque, pv, elite)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (enemy_data["id"], selection, prochain_numero, enemy_data["mouvement"],
                  enemy_data["attaque"], enemy_data["pv"], enemy_data["elite"]))
            conn.commit()

            # 📌 Placement des cartes en mode horizontal avec retour à la ligne
            nb_ennemis = len(self.ennemis_combat)
            max_per_row = WINDOW_WIDTH // (400 + CARD_SPACING)  # 400 = largeur d'une carte

            row = nb_ennemis // max_per_row
            col = nb_ennemis % max_per_row

            carte = CarteEnnemi(self.scrollable_frame, enemy_data)
            carte.grid(row=row, column=col, padx=10, pady=10)

            self.ennemis_combat[f"{prochain_numero}"] = carte

        finally:
            cursor.close()
            conn.close()

    def mettre_a_jour_pv(self, numero, delta):
        """Met à jour les PV dans la base et rafraîchit l'UI"""
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT pv FROM ennemis_combat WHERE numero = ?", (numero,))
            result = cursor.fetchone()
            if not result:
                return

            nouveaux_pv = max(0, result[0] + delta)
            cursor.execute("UPDATE ennemis_combat SET pv = ? WHERE numero = ?", (nouveaux_pv, numero))
            conn.commit()

            if f"{numero}" in self.ennemis_combat:
                ennemi = self.ennemis_combat[f"{numero}"]
                ennemi.set_pv(nouveaux_pv)

        finally:
            cursor.close()
            conn.close()

    def fermer_connexion(self):
        """Ferme proprement la connexion SQLite"""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ennemis_combat")
        conn.commit()
        conn.close()
        self.root.destroy()


# 🚀 Lancer l'application
root = tk.Tk()
app = JeuGUI(root)
root.mainloop()
