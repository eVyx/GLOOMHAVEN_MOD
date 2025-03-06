import sqlite3
import tkinter as tk
import os
from tkinter import ttk
from ttkbootstrap import Style
import importlib

import card
import importlib
importlib.reload(card)  # ✅ Recharge correctement le module
from card import CarteEnnemi, CartePreview  # ✅ Importe les classes après rechargement


# 📜 Connexion à la base de données SQLite
DB_PATH = r"C:\Users\matth\Desktop\GLOOMHAVEN\ennemy_mod.db"


def connect_db():
    """Établit une connexion SQLite avec gestion des verrous."""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")  # ✅ Active WAL pour éviter les locks
    cursor.execute("PRAGMA busy_timeout = 5000;")  # ✅ SQLite attend 5 sec si la base est verrouillée
    return conn


class JeuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Ennemis - Gloomhaven")
        self.root.geometry("1400x700")
        self.root.configure(bg="#2C2F33")

        self.conn = connect_db()
        self.cursor = self.conn.cursor()
        self.ennemis_combat = {}  # ✅ Dictionnaire pour stocker les ennemis en combat

        self.root.protocol("WM_DELETE_WINDOW", self.fermer_connexion)

        # Chargement du style
        self.style = Style("darkly")

        self.setup_ui()
        self.charger_liste_ennemis()

    def setup_ui(self):
        """Création de l'interface graphique"""
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

        self.battlefield_container = ttk.Frame(self.root, padding=10)
        self.battlefield_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(self.battlefield_container, bg="#2C2F33")
        self.scrollable_frame = ttk.Frame(self.canvas, padding=10)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def charger_liste_ennemis(self):
        """Charge la liste des ennemis dans le menu déroulant"""
        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nom FROM ennemis ORDER BY nom ASC")
            self.liste_ennemis["values"] = [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()
            
    def afficher_details_avant_ajout(self, event):
        """Affiche une prévisualisation de l'ennemi avant son ajout."""
        selection = self.liste_ennemis.get()
        if not selection:
            return

        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT mouvement, attaque, pv, elite FROM ennemis WHERE nom = ?", (selection,))
            result = cursor.fetchone()

            if not result:
                print(f"❌ Erreur : Aucun ennemi trouvé pour {selection}")
                return

            mouvement, attaque, pv, elite = result

            # Supprime la preview actuelle
            for widget in self.preview_container.winfo_children():
                widget.destroy()

            # Création de la carte preview
            preview_card = CartePreview(self.preview_container, selection, pv, elite, mouvement, attaque)
            preview_card.pack()

        finally:
            cursor.close()
            conn.close()  # ✅ Assure la fermeture de la connexion après usage


    def ajouter_ennemi(self):
        """Ajoute un ennemi sur le champ de bataille et en base de données"""
        selection = self.liste_ennemis.get()
        if not selection:
            print("❌ Aucun ennemi sélectionné")
            return

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, mouvement, attaque, pv, elite FROM ennemis WHERE nom = ?", (selection,))
            result = cursor.fetchone()
            if not result:
                print(f"❌ Erreur : Aucun ennemi trouvé pour {selection}")
                return

            ennemi_id, mouvement, attaque, pv, elite = result

            cursor.execute("SELECT COALESCE(MAX(numero), 0) + 1 FROM ennemis_combat")
            prochain_numero = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO ennemis_combat (ennemi_id, nom, numero, mouvement, attaque, pv, elite)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ennemi_id, selection, prochain_numero, mouvement, attaque, pv, elite))
            conn.commit()

            carte = CarteEnnemi(self.scrollable_frame, selection, self.mettre_a_jour_pv, pv, elite, mouvement, attaque, numero=prochain_numero, jeu=self)
            carte.grid(row=len(self.ennemis_combat) // 3, column=len(self.ennemis_combat) % 3, padx=10, pady=10)

            self.ennemis_combat[f"{prochain_numero}"] = carte
        finally:
            cursor.close()
            conn.close()

    def mettre_a_jour_pv(self, numero, delta):
        """Met à jour les PV dans la base et rafraîchit l'UI"""
        conn = sqlite3.connect(DB_PATH)
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
                ennemi.set_pv(nouveaux_pv)  # ✅ Rafraîchissement UI
                ennemi.update_health_bar()  # ✅ Mise à jour de la barre de vie
        finally:
            cursor.close()
            conn.close()

    def supprimer_ennemi(self, numero):
        """Supprime un ennemi de la base et de l'affichage"""
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ennemis_combat WHERE numero = ?", (numero,))
        conn.commit()
        conn.close()

        if f"{numero}" in self.ennemis_combat:
            self.ennemis_combat[f"{numero}"].destroy()
            del self.ennemis_combat[f"{numero}"]

    def fermer_connexion(self):
        """Ferme proprement la connexion à la base"""
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ennemis_combat")
            conn.commit()
            conn.close()
        finally:
            self.root.destroy()


# 🚀 Lancer l'application
root = tk.Tk()
app = JeuGUI(root)
root.mainloop()
