import tkinter as tk
from tkinter import ttk
import os
import cairosvg
from PIL import Image, ImageTk
from database import connect_db, get_ressource_ui

# ================== CONFIGURATION GLOBALE ==================
SCALE_FACTOR = 0.8
CARD_WIDTH, CARD_HEIGHT = int(400 * SCALE_FACTOR), int(560 * SCALE_FACTOR)

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
REDLINE_RIGHT_TEXTURE_PATH = os.path.join(TEXTURES_DIR, "red_line_right.png")
REDLINE_LEFT_TEXTURE_PATH = os.path.join(TEXTURES_DIR, "red_line_left.png")

def load_svg_as_png(svg_path, size=(31, 31)):
    """
    Convertit un fichier SVG en PNG, puis le charge en ImageTk.PhotoImage.
    """
    png_path = svg_path.replace(".svg", ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path,
                     output_width=size[0], output_height=size[1])
    img = Image.open(png_path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

def multi_stop_gradient(ratio):
    """
    Retourne une couleur hexadécimale selon un gradient multi-stop.
    ratio = 1.0 => SGBUS Green
    ratio = 0.75 => Lawn Green
    ratio = 0.50 => Yellow
    ratio = 0.25 => Pumpkin
    ratio = 0.00 => Red
    ratio <= 0   => None (pas de couleur)
    """
    color_stops = [
        (1.00, (37, 224, 0)),    # SGBUS Green
        (0.75, (144, 245, 11)),  # Lawn Green
        (0.50, (242, 255, 0)),   # Yellow
        (0.25, (255, 102, 0)),   # Pumpkin
        (0.00, (224, 0, 0))      # Red
    ]

    if ratio <= 0:
        return None
    if ratio >= 1:
        return "#%02x%02x%02x" % color_stops[0][1]

    for i in range(len(color_stops) - 1):
        r1, c1 = color_stops[i]
        r2, c2 = color_stops[i + 1]
        if ratio <= r1 and ratio > r2:
            seg_length = r1 - r2
            seg_pos = ratio - r2
            factor = seg_pos / seg_length

            r = int(c2[0] + factor * (c1[0] - c2[0]))
            g = int(c2[1] + factor * (c1[1] - c2[1]))
            b = int(c2[2] + factor * (c1[2] - c2[2]))
            return f"#{r:02x}{g:02x}{b:02x}"

    return None

class CarteEnnemi(tk.Frame):
    def __init__(self, parent, enemy_id):
        super().__init__(parent)
        self.enemy = self.get_enemy_combat_data(enemy_id)
        if not self.enemy:
            raise ValueError(f"Ennemi ID {enemy_id} introuvable dans `ennemis_combat`.")

        self.width, self.height = CARD_WIDTH, CARD_HEIGHT

        # Attributs pour gérer le fade to gray
        self.bg_color_img = None
        self.bg_gray_img = None
        self.enemy_img_color = None
        self.enemy_img_gray = None

        # ================== FRAME GLOBAL ==================
        self.frame_global = ttk.Frame(self)
        self.frame_global.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        self.frame_global.columnconfigure(0, weight=1)

        # ================== CANVAS ==================
        self.canvas = tk.Canvas(self.frame_global,
                                width=self.width, height=self.height,
                                bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="n")

        # ================== CONTENEUR BOUTONS PV ==================
        self.button_container = tk.Frame(self.frame_global)
        self.button_container.grid(row=1, column=0, sticky="ew")
        self.button_container.columnconfigure(0, weight=1)
        self.button_container.columnconfigure(1, weight=1)

        # Boutons - / +
        button_size = (100, 100)
        self.hp_down_tk = load_svg_as_png(HP_DOWN_PATH, size=button_size)
        self.hp_up_tk = load_svg_as_png(HP_UP_PATH, size=button_size)

        self.hp_down = tk.Label(self.button_container, image=self.hp_down_tk,
                                cursor="hand2", highlightthickness=0, borderwidth=0)
        self.hp_down.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.hp_down.bind("<Button-1>", self.decrement_hp)

        self.hp_up = tk.Label(self.button_container, image=self.hp_up_tk,
                              cursor="hand2", highlightthickness=0, borderwidth=0)
        self.hp_up.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.hp_up.bind("<Button-1>", self.increment_hp)

        # Icônes PV / crâne
        self.icon_hp_tk = ImageTk.PhotoImage(Image.open(ICON_HP_PATH).resize((18, 18), Image.LANCZOS))
        self.icon_skull_tk = ImageTk.PhotoImage(Image.open(SKULL_ICON_PATH).resize((18, 18), Image.LANCZOS))

        # ================== DESSIN DE LA CARTE ==================
        self.draw_background()
        self.draw_title()
        self.draw_stats()
        self.draw_enemy()
        self.draw_hp_bar()

    # ================== BDD ==================
    def get_enemy_combat_data(self, ennemi_id):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ennemis_combat WHERE id = ?", (ennemi_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            print(f"❌ Erreur: Ennemi ID {ennemi_id} introuvable dans `ennemis_combat`.")
            return None

        keys = ["id", "nom", "numero", "mouvement", "attaque", "pv", "pv_max", "elite", "image"]
        enemy_dict = dict(zip(keys, row))
        # Supprimer " ELITE" du nom si présent
        enemy_dict["nom"] = enemy_dict["nom"].replace(" ELITE", "")
        return enemy_dict

    # ================== FOND ==================
    def draw_background(self):
        """Charge et stocke la version couleur + gris du fond papyrus en RGBA."""
        if self.enemy["elite"]:
            bg_path = PAPYRUS_ELITE_TEXTURE_PATH
        else:
            bg_path = PAPYRUS_NORMAL_TEXTURE_PATH

        papyrus_img_color = Image.open(bg_path).resize(
            (int(395 * SCALE_FACTOR), int(550 * SCALE_FACTOR)),
            Image.LANCZOS
        ).convert("RGBA")

        papyrus_img_gray = papyrus_img_color.convert("L").convert("RGBA")

        self.bg_color_img = papyrus_img_color
        self.bg_gray_img = papyrus_img_gray

        self.bg_tk = ImageTk.PhotoImage(self.bg_color_img)
        self.bg_id = self.canvas.create_image(
            self.width * 0.5, self.height * 0.5,
            anchor="center", image=self.bg_tk
        )

    # ================== TITRE ==================
    def draw_title(self):
        """Affiche le titre centré, avec contour noir et couleur dorée/blanche."""
        title_color = "#FFD700" if self.enemy["elite"] else "white"
        max_width = self.width * 0.85
        font_size = int(self.width * 0.06)
        min_font_size = int(self.width * 0.04)

        while True:
            font = ("Dragon Hunter", font_size)
            text_id = self.canvas.create_text(0, 0, text=self.enemy["nom"], font=font, anchor="nw")
            text_width = self.canvas.bbox(text_id)[2] - self.canvas.bbox(text_id)[0]
            self.canvas.delete(text_id)
            if text_width <= max_width or font_size <= min_font_size:
                break
            font_size -= 1

        x_center = self.width * 0.5
        y_position = self.height * 0.08

        # Contour noir
        outline_offset = 1
        for dx, dy in [(-outline_offset, 0), (outline_offset, 0),
                       (0, -outline_offset), (0, outline_offset)]:
            self.canvas.create_text(
                x_center + dx, y_position + dy,
                text=self.enemy["nom"], font=font,
                fill="black", anchor="center"
            )

        # Titre principal
        self.canvas.create_text(
            x_center, y_position,
            text=self.enemy["nom"], font=font,
            fill=title_color, anchor="center"
        )

        # ID sous le titre (optionnel)
        self.canvas.create_text(
            x_center, self.height * 0.11,
            text=f"#{self.enemy['id']}",
            font=("Maitree SemiBold", int(self.width * 0.035)),
            fill="black", anchor="n"
        )

    # ================== STATS ==================
    def draw_stats(self):
        """Affiche les icônes mouvement/attaque et leurs valeurs."""
        icon_size = int(self.width * 0.1)
        icon_boots = Image.open(ICON_BOOTS_PATH).resize((icon_size, icon_size), Image.LANCZOS)
        self.icon_boots_tk = ImageTk.PhotoImage(icon_boots)

        self.icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(icon_size, icon_size))

        # Icône mouvement
        self.canvas.create_image(self.width * 0.3, self.height * 0.19,
                                 anchor="nw", image=self.icon_boots_tk)
        # Icône attaque
        self.canvas.create_image(self.width * 0.55, self.height * 0.19,
                                 anchor="nw", image=self.icon_attack_tk)

        # Valeurs
        self.canvas.create_text(
            self.width * 0.428, self.height * 0.18,
            anchor="nw",
            text=f"{self.enemy['mouvement']}",
            font=("Maitree SemiBold", int(self.width * 0.06)),
            fill="black"
        )
        self.canvas.create_text(
            self.width * 0.658, self.height * 0.18,
            anchor="nw",
            text=f"{self.enemy['attaque']}",
            font=("Maitree SemiBold", int(self.width * 0.06)),
            fill="black"
        )

    # ================== ENNEMI ==================
    def draw_enemy(self):
        """Charge et stocke la version couleur + gris de l'ennemi en RGBA."""
        enemy_img_path = os.path.join(ENNEMIS_DIR, self.enemy["image"])
        enemy_img_color = Image.open(enemy_img_path).resize(
            (int(CARD_WIDTH * 0.742), int(CARD_HEIGHT * 0.555)),
            Image.LANCZOS
        ).convert("RGBA")

        enemy_img_gray = enemy_img_color.convert("L").convert("RGBA")

        self.enemy_img_color = enemy_img_color
        self.enemy_img_gray = enemy_img_gray

        self.enemy_img_tk = ImageTk.PhotoImage(self.enemy_img_color)
        self.enemy_img_id = self.canvas.create_image(
            self.width * 0.5, self.height * 0.57,
            anchor="center", image=self.enemy_img_tk
        )

    # ================== BARRE DE VIE ==================
    def draw_hp_bar(self):
        """Dessine la barre de vie avec un gradient multi-stop, plus crâne si PV=0."""
        bar_x, bar_y = self.width * 0.15, self.height * 0.87
        bar_width, bar_height = self.width * 0.7, self.height * 0.05

        hp_ratio = self.enemy["pv"] / self.enemy["pv_max"] if self.enemy["pv_max"] else 0
        bar_color = multi_stop_gradient(hp_ratio)

        # Supprime l'ancienne barre
        self.canvas.delete("hp_bar")

        # Remplissage si PV > 0
        if self.enemy["pv"] > 0 and bar_color is not None:
            self.canvas.create_rectangle(
                bar_x, bar_y,
                bar_x + (bar_width * hp_ratio), bar_y + bar_height,
                outline="", width=0, fill=bar_color, tags="hp_bar"
            )

        # Bordure
        self.canvas.create_rectangle(
            bar_x, bar_y,
            bar_x + bar_width, bar_y + bar_height,
            outline="black", width=2, fill="", tags="hp_bar"
        )

        # Icône + texte
        if self.enemy["pv"] > 0:
            icon = self.icon_hp_tk
            text = f"{self.enemy['pv']} / {self.enemy['pv_max']}"
        else:
            icon = self.icon_skull_tk
            text = "Mort"

        self.canvas.create_image(
            bar_x + 40, bar_y + bar_height / 2,
            anchor="center", image=icon, tags="hp_bar"
        )
        self.canvas.create_text(
            bar_x + bar_width / 2, bar_y + bar_height / 2,
            anchor="center", text=text, font=("Maitree SemiBold", 12),
            fill="black", tags="hp_bar"
        )

    # ================== LOGIQUE PV ==================
    def modify_hp(self, amount):
        new_pv = max(0, min(self.enemy["pv"] + amount, self.enemy["pv_max"]))
        self.enemy["pv"] = new_pv

        # Met à jour la BDD
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE ennemis_combat SET pv = ? WHERE id = ?",
                       (new_pv, self.enemy["id"]))
        conn.commit()
        conn.close()

        # Redessine la barre
        self.draw_hp_bar()

        # Si PV = 0 => on lance le fade + l'animation de mort
        if new_pv == 0:
            self.fade_to_gray()
            self.draw_death()

    def increment_hp(self, event):
        """Augmente les PV de l'ennemi."""
        self.modify_hp(+1)

    def decrement_hp(self, event):
        """Diminue les PV de l'ennemi."""
        self.modify_hp(-1)

    # ================== ANIMATION FADE ==================
    def fade_to_gray(self, step=0, steps=10):
        """
        Fait un fondu progressif (fond + ennemi) vers le gris.
        """
        if (not self.bg_color_img or not self.bg_gray_img or
            not self.enemy_img_color or not self.enemy_img_gray):
            return

        ratio = step / float(steps)

        # Blend du fond
        bg_blended = Image.blend(self.bg_color_img, self.bg_gray_img, ratio)
        self.bg_tk = ImageTk.PhotoImage(bg_blended)
        self.canvas.itemconfig(self.bg_id, image=self.bg_tk)

        # Blend de l'ennemi
        enemy_blended = Image.blend(self.enemy_img_color, self.enemy_img_gray, ratio)
        self.enemy_img_tk = ImageTk.PhotoImage(enemy_blended)
        self.canvas.itemconfig(self.enemy_img_id, image=self.enemy_img_tk)

        if step < steps:
            self.after(50, lambda: self.fade_to_gray(step + 1, steps))

    # ================== ANIMATION MORT (CROIX ROUGE) ==================
    def draw_death(self):
        brush1_data = get_ressource_ui("red_line_right")
        brush2_data = get_ressource_ui("red_line_left")

        if not brush1_data or not brush2_data:
            print("❌ Ressources 'red_line_right' ou 'red_line_left' introuvables.")
            return

        brush1_path = os.path.join(RESSOURCES_DIR, brush1_data["image"])
        brush2_path = os.path.join(RESSOURCES_DIR, brush2_data["image"])

        # 1) Ouvrir les images en PIL
        brush1_pil = Image.open(brush1_path).convert("RGBA")
        brush2_pil = Image.open(brush2_path).convert("RGBA")

        # 2) Redimensionner (exemple : multiplier la taille par 1.5)
        #    ou mettre une taille fixe (ex: (300, 300))
        scale_factor = 1.5
        new_size_1 = (int(brush1_pil.width * scale_factor), int(brush1_pil.height * scale_factor))
        new_size_2 = (int(brush2_pil.width * scale_factor), int(brush2_pil.height * scale_factor))

        brush1_pil = brush1_pil.resize(new_size_1, Image.LANCZOS)
        brush2_pil = brush2_pil.resize(new_size_2, Image.LANCZOS)

        # 3) Stocker pour l’animation
        self.death_brush_1 = brush1_pil
        self.death_brush_2 = brush2_pil

        # 4) Lancer l’animation
        self.animate_brush_1()

    def animate_brush_1(self, step=0, max_steps=10):
        """Fait glisser la brosse 1 en diagonale bas-gauche -> haut-droit."""
        if step == 0:
            self.brush1_tk = ImageTk.PhotoImage(self.death_brush_1)
            self.brush1_id = self.canvas.create_image(-9999, -9999,
                                                      image=self.brush1_tk,
                                                      anchor="center")

        # Coordonnées de départ (bas gauche, en dehors du Canvas si tu veux)
        x_start, y_start = -50, self.height + 50

        # Coordonnées d'arrivée = centre de la carte
        x_end, y_end = self.width * 0.5, self.height * 0.5


        frac = step / float(max_steps)
        x = x_start + (x_end - x_start) * frac
        y = y_start + (y_end - y_start) * frac

        self.canvas.coords(self.brush1_id, x, y)

        if step < max_steps:
            self.after(50, lambda: self.animate_brush_1(step + 1, max_steps))
        else:
            self.animate_brush_2()

    def animate_brush_2(self, step=0, max_steps=10):
        """Fait glisser la brosse 2 en diagonale haut-gauche -> bas-droit."""
        if step == 0:
            self.brush2_tk = ImageTk.PhotoImage(self.death_brush_2)
            self.brush2_id = self.canvas.create_image(-9999, -9999,
                                                      image=self.brush2_tk,
                                                      anchor="center")

        x_start, y_start = -50, -50  # par exemple, en dehors en haut gauche
        x_end, y_end = self.width * 0.5, self.height * 0.5


        frac = step / float(max_steps)
        x = x_start + (x_end - x_start) * frac
        y = y_start + (y_end - y_start) * frac

        self.canvas.coords(self.brush2_id, x, y)

        if step < max_steps:
            self.after(50, lambda: self.animate_brush_2(step + 1, max_steps))
        else:
            # Animation terminée
            pass
