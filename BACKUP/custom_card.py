import tkinter as tk
from PIL import Image, ImageTk
import cairosvg
import os

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

SCALE_FACTOR = 0.8  

# 📏 Taille ajustée de la carte
CARD_WIDTH = int(400 * SCALE_FACTOR)
CARD_HEIGHT = int(560 * SCALE_FACTOR)

def load_svg_as_png(svg_path, size=(32, 32)):
    """Charge une icône SVG et la convertit en PNG."""
    png_path = svg_path.replace(".svg", ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])
    img = Image.open(png_path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

class CarteEnnemi(tk.Frame):
    def __init__(self, parent, enemy_id):
        """Création d'une carte ennemi en récupérant les stats depuis la base de données"""
        super().__init__(parent)

        from ennemy_mod import get_enemy_data  
        self.enemy = get_enemy_data(enemy_id)

        if not self.enemy:
            raise ValueError(f"Ennemi ID {enemy_id} introuvable dans la base de données.")

        self.parent = parent
        self.scale = SCALE_FACTOR

        self.width = int(CARD_WIDTH)
        self.height = int(CARD_HEIGHT)

        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.pack()

        self.draw_background()
        self.draw_title()
        self.draw_stats()
        self.draw_enemy()
        self.draw_hp_bar()

    def draw_background(self):
        """Affiche le fond de la carte en fonction du type (élite ou normal)."""
        bg_image_path = PAPYRUS_ELITE_TEXTURE_PATH if self.enemy["elite"] else PAPYRUS_NORMAL_TEXTURE_PATH
        papyrus_img = Image.open(bg_image_path).resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)

        # 📌 Stocker l’image dans `self` pour éviter sa suppression
        self.bg_tk = ImageTk.PhotoImage(papyrus_img)
        
        # 📌 Utiliser `self.canvas.create_image` avec une référence persistante
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.5, anchor="center", image=self.bg_tk)


    def draw_title(self):
        """Affiche le titre avec une taille ajustée dynamiquement"""
        x = self.width * 0.5  
        y = self.height * 0.07  

        base_font_size = 24  
        max_font_size = 28  
        min_font_size = 14  

        text_length_factor = max(1, len(self.enemy["nom"]) / 12)  
        font_size = max(min_font_size, int(max_font_size / text_length_factor))  

        font = ("Dragon Hunter", font_size)
        text_color = "#FFD700" if self.enemy["elite"] else "white"

        outline_offset = max(int(2 * self.scale), 1)
        for dx, dy in [(-outline_offset, 0), (outline_offset, 0), (0, -outline_offset), (0, outline_offset)]:
            self.canvas.create_text(x + dx, y + dy, anchor="center", text=self.enemy["nom"], font=font, fill="black")

        self.canvas.create_text(x, y, anchor="center", text=self.enemy["nom"], font=font, fill=text_color)

    def draw_stats(self):
        """Affiche les icônes et valeurs des stats."""
        icon_size = int(32 * SCALE_FACTOR)  
        self.icon_boots_tk = ImageTk.PhotoImage(Image.open(ICON_BOOTS_PATH).resize((icon_size, icon_size), Image.LANCZOS))
        self.icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(icon_size, icon_size))

        self.canvas.create_image(CARD_WIDTH * 0.30, CARD_HEIGHT * 0.198, anchor="nw", image=self.icon_boots_tk)
        self.canvas.create_image(CARD_WIDTH * 0.54, CARD_HEIGHT * 0.198, anchor="nw", image=self.icon_attack_tk)

    def draw_enemy(self):
        """Affiche l'image de l'ennemi."""
        enemy_img_path = os.path.join(ENNEMIS_DIR, self.enemy["image"])
        enemy_img = Image.open(enemy_img_path).resize((int(280 * SCALE_FACTOR), int(310 * SCALE_FACTOR)), Image.LANCZOS)
        self.enemy_img_tk = ImageTk.PhotoImage(enemy_img)
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.57, anchor="center", image=self.enemy_img_tk)

    def draw_hp_bar(self):
        """Affiche la barre de vie."""
        bar_width = self.width * 0.64
        bar_height = self.height * 0.06

        bar_x = self.width * 0.18
        bar_y = self.height * 0.875

        self.create_rounded_rectangle(bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                                      radius=max(6, int(8 * self.scale)), outline="black", width=int(2 * self.scale), fill="#18A86B")

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=12, **kwargs):
        """Dessine un rectangle avec des coins arrondis."""
        points = [
            x1 + radius, y1, x2 - radius, y1, x2, y1,
            x2, y1 + radius, x2, y2 - radius, x2, y2,
            x2 - radius, y2, x1 + radius, y2, x1, y2,
            x1, y2 - radius, x1, y1 + radius, x1, y1,
            x1 + radius, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

class CartePreview(CarteEnnemi):
    def __init__(self, parent, enemy_id):
        """Création d'une carte de prévisualisation"""
        super().__init__(parent, enemy_id)
        self.scale = SCALE_FACTOR * 0.65  
        self.width = int(CARD_WIDTH * 0.65)
        self.height = int(CARD_HEIGHT * 0.65)
        
    def draw_background_preview(self):
        """Affiche le fond de la carte en fonction du type (élite ou normal)."""
        bg_image_path = PAPYRUS_ELITE_TEXTURE_PATH if self.enemy["elite"] else PAPYRUS_NORMAL_TEXTURE_PATH
        papyrus_img = Image.open(bg_image_path).resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)

        # 📌 Stocker l’image dans `self` pour éviter sa suppression
        self.bg_tk = ImageTk.PhotoImage(papyrus_img)
        
        # 📌 Utiliser `self.canvas.create_image` avec une référence persistante
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.5, anchor="center", image=self.bg_tk)

    def draw_title_preview(self):
        """Affiche le titre ajusté à la preview"""
        x = self.width * 0.5  
        y = self.height * 0.07  

        font_size = max(int(24 * self.scale), 10)  
        font = ("Dragon Hunter", font_size)
        text_color = "#FFD700" if self.enemy["elite"] else "white"

        outline_offset = max(int(2 * self.scale), 1)
        for dx, dy in [(-outline_offset, 0), (outline_offset, 0), (0, -outline_offset), (0, outline_offset)]:
            self.canvas.create_text(x + dx, y + dy, anchor="center", text=self.enemy["nom"], font=font, fill="black")

        self.canvas.create_text(x, y, anchor="center", text=self.enemy["nom"], font=font, fill=text_color)

    def draw_stats_preview(self):
        """Affiche les stats de la preview"""
        icon_size = int(60 * self.scale)  
        label_size = int(36 * self.scale)  

        self.icon_boots_tk = ImageTk.PhotoImage(Image.open(ICON_BOOTS_PATH).resize((icon_size, icon_size), Image.LANCZOS))
        self.icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(icon_size, icon_size))

        start_x = self.width * 0.2
        spacing_x = self.width * 0.3  
        y_position = self.height * 0.20  

        self.canvas.create_image(start_x, y_position, anchor="center", image=self.icon_boots_tk)
        self.canvas.create_image(start_x + spacing_x, y_position, anchor="center", image=self.icon_attack_tk)
