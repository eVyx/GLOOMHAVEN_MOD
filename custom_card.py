import tkinter as tk
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
            raise ValueError(f"Ennemi ID {enemy_id} introuvable dans `ennemis_combat`.")

        self.width, self.height = CARD_WIDTH, CARD_HEIGHT
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        self.draw_background()
        self.draw_title()
        self.draw_stats()
        self.draw_enemy()
        self.draw_hp_bar()

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

    def draw_hp_bar(self):
        """Ajoute la barre de vie et l'icône PV."""
        bar_x, bar_y = self.width * 0.15, self.height * 0.87  # 🔹 Décalé horizontalement
        bar_width, bar_height = self.width * 0.7, self.height * 0.05

        # Barre de vie verte avec contour noir
        self.canvas.create_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height, outline="black", width=1, fill="#18A86B")

        # **Icône PV déplacée horizontalement** (plus proche de la barre de vie)
        self.icon_hp_tk = ImageTk.PhotoImage(Image.open(ICON_HP_PATH).resize((int(18 * SCALE_FACTOR), int(18 * SCALE_FACTOR)), Image.LANCZOS))
        self.canvas.create_image(bar_x + 60, bar_y + bar_height / 2, anchor="center", image=self.icon_hp_tk)

        # Texte PV bien centré
        self.canvas.create_text(bar_x + bar_width / 2, bar_y + bar_height / 2, anchor="center",
                                text=f"{self.enemy['pv']} / {self.enemy['pv_max']}", font=("Maitree SemiBold", 12), fill="black")



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