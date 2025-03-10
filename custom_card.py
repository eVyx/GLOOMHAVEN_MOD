import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cairosvg
import os
from database import get_enemy_data, connect_db

# 📌 Définition des chemins de fichiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESSOURCES_DIR = os.path.join(BASE_DIR, "RESSOURCES")
TEXTURES_DIR = os.path.join(RESSOURCES_DIR, "TEXTURES")
ICONS_DIR = os.path.join(RESSOURCES_DIR, "ICONS")
ENNEMIS_DIR = os.path.join(RESSOURCES_DIR, "ENNEMIS")

PAPYRUS_ELITE_TEXTURE_PATH = os.path.join(TEXTURES_DIR, "papyrus_elite.png")
PAPYRUS_NORMAL_TEXTURE_PATH = os.path.join(TEXTURES_DIR, "papyrus_normal.png")
ICON_BOOTS_PATH = os.path.join(ICONS_DIR, "BOOTS.png")
ICON_ATTACK_PATH = os.path.join(ICONS_DIR, "ATTACK.svg")
ICON_HP_PATH = os.path.join(ICONS_DIR, "HP.png")
HP_DOWN_PATH = os.path.join(ICONS_DIR, "HP_DOWN.svg")
HP_UP_PATH = os.path.join(ICONS_DIR, "HP_UP.svg")
SKULL_ICON_PATH = os.path.join(ICONS_DIR, "SKULL.png")

SCALE_FACTOR = 0.8  # Réduction à 80%
CARD_WIDTH, CARD_HEIGHT = int(400 * SCALE_FACTOR), int(560 * SCALE_FACTOR)

def load_svg_as_png(svg_path, size=(31, 31)):
    """Charge une icône SVG et la convertit en PNG."""
    png_path = svg_path.replace(".svg", ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])
    img = Image.open(png_path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

class CarteEnnemi(tk.Frame):
    def __init__(self, parent, enemy_id):
        super().__init__(parent)
        self.enemy = self.get_enemy_combat_data(enemy_id)
        if not self.enemy:
            raise ValueError(f"Ennemi ID {enemy_id} introuvable dans ennemis_combat.")

        self.width, self.height = CARD_WIDTH, CARD_HEIGHT

        # **🔹 Création du conteneur principal**
        self.container = tk.Frame(self)
        self.container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # **🎴 Canvas de la carte**
        self.canvas = tk.Canvas(self.container, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        self.icon_skull_tk = ImageTk.PhotoImage(Image.open(SKULL_ICON_PATH).resize((int(18 * SCALE_FACTOR), int(18 * SCALE_FACTOR)), Image.LANCZOS))

        # Chargement de l'icône PV AVANT d'appeler draw_hp_bar()
        self.icon_hp_tk = ImageTk.PhotoImage(Image.open(ICON_HP_PATH).resize((int(18 * SCALE_FACTOR), int(18 * SCALE_FACTOR)), Image.LANCZOS))

        # **🔹 Ajout des composants**
        self.draw_background()
        self.draw_title()
        self.draw_stats()
        self.draw_enemy()
        self.draw_hp_bar()
    
            # 📌 **Ajout de `button_container` dans `CarteEnnemi`**
        self.button_container = tk.Frame(self)
        self.button_container.grid(row=1, column=0, pady=(5, 0))  # 🔹 **Réduction de l’espace sous la carte**

        # 📌 **Taille des boutons améliorée**
        button_size = (150, 150)  # ✅ **Agrandissement uniforme des icônes**

        # 📌 **Chargement des icônes (évite la duplication)**
        self.hp_down_tk = load_svg_as_png(HP_DOWN_PATH, size=button_size)
        self.hp_up_tk = load_svg_as_png(HP_UP_PATH, size=button_size)

        # **➖ Bouton "Moins"**
        self.hp_down = tk.Label(self.button_container, image=self.hp_down_tk, cursor="hand2")
        self.hp_down.grid(row=0, column=0, padx=10, sticky="e")
        self.hp_down.bind("<Button-1>", lambda event: self.modify_hp(-1))  # 🔹 **Décrémentation PV**

        # **➕ Bouton "Plus"**
        self.hp_up = tk.Label(self.button_container, image=self.hp_up_tk, cursor="hand2")
        self.hp_up.grid(row=0, column=1, padx=10, sticky="w")
        self.hp_up.bind("<Button-1>", lambda event: self.modify_hp(+1))  # 🔹 **Incrémentation PV**


    def get_enemy_combat_data(self, ennemi_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ennemis_combat WHERE id = ?", (ennemi_id,))
        enemy_data = cursor.fetchone()
        
        if not enemy_data:
            print(f"❌ Erreur: Ennemi ID {ennemi_id} introuvable dans `ennemis_combat`. Vérifie la table !")
            return None
        
        keys = ["id", "nom", "numero", "mouvement", "attaque", "pv", "pv_max", "elite", "image"]
        enemy_dict = dict(zip(keys, enemy_data))
        
        # Supprimer "ELITE" du titre s'il est présent
        enemy_dict["nom"] = enemy_dict["nom"].replace(" ELITE", "")
        
        conn.close()
        return enemy_dict

    def draw_background(self):
        """Définit le fond de la carte en fonction de l'ennemi (élite ou normal)."""
        bg_image_path = PAPYRUS_ELITE_TEXTURE_PATH if self.enemy["elite"] else PAPYRUS_NORMAL_TEXTURE_PATH
        papyrus_img = Image.open(bg_image_path).resize((int(395 * SCALE_FACTOR), int(550 * SCALE_FACTOR)), Image.LANCZOS)
        self.bg_tk = ImageTk.PhotoImage(papyrus_img)
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.5, anchor="center", image=self.bg_tk)

    def draw_title(self):
        """Affiche le titre centré, avec une taille qui ne dépasse pas la carte et un contour propre."""

        # 🎨 **Définition de la couleur selon élite ou normal**
        title_color = "#FFD700" if self.enemy["elite"] else "white"

        # 📏 **Base dynamique pour la taille du texte**
        max_width = CARD_WIDTH * 0.85  # 85% de la largeur pour éviter de toucher les bords
        font_size = int(CARD_WIDTH * 0.06)  # Taille initiale
        min_font_size = int(CARD_WIDTH * 0.04)  # Taille minimale acceptable

        # 🖌️ **Créer une police Tkinter et tester la largeur du texte**
        while True:
            font = ("Dragon Hunter", font_size)
            text_id = self.canvas.create_text(0, 0, text=self.enemy["nom"], font=font, anchor="nw")
            text_width = self.canvas.bbox(text_id)[2] - self.canvas.bbox(text_id)[0]  # Largeur du texte
            self.canvas.delete(text_id)  # Supprime l’élément temporaire

            if text_width <= max_width or font_size <= min_font_size:
                break
            font_size -= 1  # Réduit la taille jusqu'à ce que ça rentre

        # 📌 **Position et centrage**
        x_center = CARD_WIDTH * 0.5  # Centrage horizontal
        y_position = CARD_HEIGHT * 0.08  # Position verticale ajustée

        # 🖌️ **Contour noir fin sans ombre**
        outline_offset = 1
        for dx, dy in [(-outline_offset, 0), (outline_offset, 0), (0, -outline_offset), (0, outline_offset)]:
            self.canvas.create_text(x_center + dx, y_position + dy, anchor="center",
                                    text=self.enemy["nom"], font=font, fill="black")

        # 🎨 **Texte principal**
        self.canvas.create_text(x_center, y_position, anchor="center",
                                text=self.enemy["nom"], font=font, fill=title_color)

        # 📌 **ID affiché sous le titre**
        self.canvas.create_text(CARD_WIDTH * 0.445, CARD_HEIGHT * 0.107, anchor="nw",
                                text=f"#{self.enemy['id']}", font=("Maitree SemiBold", int(CARD_WIDTH * 0.035)), fill="black")


    def draw_stats(self):
        """Affiche les icônes et valeurs des stats."""
        icon_size = int(CARD_WIDTH * 0.085)
        self.icon_boots_tk = ImageTk.PhotoImage(Image.open(ICON_BOOTS_PATH).resize((icon_size, icon_size), Image.LANCZOS))
        self.icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(icon_size, icon_size))

        self.canvas.create_image(CARD_WIDTH * 0.30, CARD_HEIGHT * 0.198, anchor="nw", image=self.icon_boots_tk)
        self.canvas.create_image(CARD_WIDTH * 0.54, CARD_HEIGHT * 0.198, anchor="nw", image=self.icon_attack_tk)
        
        self.canvas.create_text(CARD_WIDTH * 0.425, CARD_HEIGHT * 0.187, anchor="nw",
                                text=f"{self.enemy['mouvement']}", font=("Maitree SemiBold", int(CARD_WIDTH * 0.05)), fill="black")
        self.canvas.create_text(CARD_WIDTH * 0.652, CARD_HEIGHT * 0.187, anchor="nw",
                                text=f"{self.enemy['attaque']}", font=("Maitree SemiBold", int(CARD_WIDTH * 0.05)), fill="black")

    def draw_enemy(self):
        """Affiche l'image de l'ennemi au centre."""
        enemy_img_path = os.path.join(ENNEMIS_DIR, self.enemy["image"])
        enemy_img = Image.open(enemy_img_path).resize((int(CARD_WIDTH * 0.742), int(CARD_HEIGHT * 0.555)), Image.LANCZOS)
        self.enemy_img_tk = ImageTk.PhotoImage(enemy_img)
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.57, anchor="center", image=self.enemy_img_tk)


    def interpolate_color(self, start_color, end_color, factor):
        """Génère une couleur intermédiaire entre `start_color` et `end_color` en fonction du facteur (0 = start, 1 = end)."""
        start_rgb = tuple(int(start_color[i:i+2], 16) for i in (1, 3, 5))
        end_rgb = tuple(int(end_color[i:i+2], 16) for i in (1, 3, 5))
        
        new_rgb = tuple(int(start + factor * (end - start)) for start, end in zip(start_rgb, end_rgb))
        return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'

    def draw_hp_bar(self):
        """Ajoute la barre de vie dynamique avec couleur variable, disparition à 0 PV et affichage de 'Mort'."""
        
        # 📌 Position et taille fixes de la barre
        bar_x, bar_y = self.width * 0.15, self.height * 0.87
        bar_width, bar_height = self.width * 0.7, self.height * 0.05

        # ✅ Ratio PV restant
        hp_ratio = self.enemy["pv"] / self.enemy["pv_max"]

        # ✅ Déterminer la couleur selon le ratio
        if self.enemy["pv"] > 0:
            bar_color = self.interpolate_color("#18A86B", "#E11E1E", 1 - hp_ratio)  # 🔥 Dégradé dynamique
            icon = self.icon_hp_tk  # Icône cœur normale
            text = f"{self.enemy['pv']} / {self.enemy['pv_max']}"
        else:
            bar_color = None  # ❌ Pas de couleur si PV = 0
            icon = self.icon_skull_tk  # ⚰️ Icône tête de mort
            text = "Mort"

        # ✅ Supprime l'ancienne barre de vie pour éviter les doublons
        self.canvas.delete("hp_bar")

        # 🔹 **Dessiner uniquement la bordure (fixe)**
        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                                    outline="black", width=2, fill="", tags="hp_bar")  # 🔳 **Bordure épaisse 2px**

        # 🔹 **Si l'ennemi a des PV restants, dessiner la barre colorée**
        if self.enemy["pv"] > 0:
            self.canvas.create_rectangle(bar_x, bar_y, bar_x + (bar_width * hp_ratio), bar_y + bar_height,
                                        outline="", width=0, fill=bar_color, tags="hp_bar")

        # 🔹 **Icône PV ou tête de mort**
        self.canvas.create_image(bar_x + 40, bar_y + bar_height / 2, anchor="center",
                                image=icon, tags="hp_bar")

        # 🔹 **Texte PV ou 'Mort'**
        self.canvas.create_text(bar_x + bar_width / 2, bar_y + bar_height / 2, anchor="center",
                                text=text, font=("Maitree SemiBold", 12), fill="black", tags="hp_bar")



    # def create_rounded_rectangle(self, x1, y1, x2, y2, radius=12, **kwargs):
    #     """Dessine un rectangle avec des coins arrondis."""
    #     points = [
    #         x1 + radius, y1, x2 - radius, y1, x2, y1,
    #         x2, y1 + radius, x2, y2 - radius, x2, y2,
    #         x2 - radius, y2, x1 + radius, y2, x1, y2,
    #         x1, y2 - radius, x1, y1 + radius, x1, y1,
    #         x1 + radius, y1
    #     ]
    #     return self.canvas.create_polygon(points, smooth=True, **kwargs)
     
    def add_hp_buttons(self):
        """Ajoute les boutons `-` et `+` sous la carte avec une meilleure taille et alignement."""
        
        button_size = (200, 200)  # ✅ **Agrandir les icônes des boutons**
        
        self.icon_minus = load_svg_as_png(HP_DOWN_PATH, size=button_size)
        self.icon_plus = load_svg_as_png(HP_UP_PATH, size=button_size)

        # 🔘 **Bouton `-`**
        self.btn_minus = tk.Label(self.frame_buttons, image=self.icon_minus, bg="black", cursor="hand2")
        self.btn_minus.grid(row=0, column=0, padx=20)  # ✅ **Alignement en `grid`**

        self.btn_minus.bind("<Button-1>", self.decrement_hp)

        # 🔘 **Bouton `+`**
        self.btn_plus = tk.Label(self.frame_buttons, image=self.icon_plus, bg="black", cursor="hand2")
        self.btn_plus.grid(row=0, column=1, padx=20)  # ✅ **Alignement en `grid`**

        self.btn_plus.bind("<Button-1>", self.increment_hp)

    
    def decrement_hp(self, event):
        """Diminue les PV de l'ennemi"""
        if self.enemy["pv"] > 0:
            self.enemy["pv"] -= 1
            self.modify_hp()

    def increment_hp(self, event):
        """Augmente les PV de l'ennemi"""
        if self.enemy["pv"] < self.enemy["pv_max"]:
            self.enemy["pv"] += 1
            self.modify_hp()

    def modify_hp(self, amount):
        """Modifie les PV de l'ennemi en direct."""
        new_pv = max(0, min(self.enemy["pv"] + amount, self.enemy["pv_max"]))
        self.enemy["pv"] = new_pv  # MAJ des données locales

        # **MAJ dans la BDD**
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE ennemis_combat SET pv = ? WHERE id = ?", (new_pv, self.enemy["id"]))
        conn.commit()
        conn.close()

        # **Redessiner la barre de vie**
        self.draw_hp_bar()
