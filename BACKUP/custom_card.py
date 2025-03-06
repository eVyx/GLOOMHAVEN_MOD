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
ENEMY_IMAGE_PATH = os.path.join(ENNEMIS_DIR, "pillard_vermling.png")
ICON_BOOTS_PATH = os.path.join(ICONS_DIR, "BOOTS.png")
ICON_ATTACK_PATH = os.path.join(ICONS_DIR, "ATTACK.svg")
ICON_HP_PATH = os.path.join(ICONS_DIR, "HP.png")

# 📏 Taille de la carte
CARD_WIDTH, CARD_HEIGHT = 400, 560

# 📌 Définition de l'ennemi
enemy_data = {
    "name": "Pillard Vermling",
    "id": 1,
    "elite": 1,  # Modifier ici pour tester (0 = normal, 1 = élite)
    "mouvement": 2,
    "attaque": 4,
    "hp": 6,
    "max_hp": 6
}

def load_svg_as_png(svg_path, size=(32, 32)):
    """Charge une icône SVG et la convertit en PNG."""
    png_path = svg_path.replace(".svg", ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])
    img = Image.open(png_path).resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


# 🖼️ Création de la fenêtre principale
root = tk.Tk()
root.title("Test Agencement Carte")

canvas = tk.Canvas(root, width=CARD_WIDTH, height=CARD_HEIGHT, bg="black", highlightthickness=0)
canvas.pack()

# 📌 1️⃣ Fond de la carte (Dynamique selon élite ou non)
def draw_background():
    papyrus_texture = PAPYRUS_ELITE_TEXTURE_PATH if enemy_data["elite"] else PAPYRUS_NORMAL_TEXTURE_PATH
    papyrus_img = Image.open(papyrus_texture).resize((395, 550), Image.LANCZOS)
    bg_tk = ImageTk.PhotoImage(papyrus_img)
    canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.5, anchor="center", image=bg_tk)
    return bg_tk

# 📌 2️⃣ Titre et ID de l'ennemi (Avec outline amélioré)
def draw_title():
    x, y = CARD_WIDTH * 0.125, CARD_HEIGHT * 0.053
    font_size = int(CARD_WIDTH * 0.06)
    font = ("Dragon Hunter", font_size)
    text_color = "#FFD700" if enemy_data["elite"] else "#EFA233"  # Or pour élite, orange normal

    # ✅ Contour noir simulé en créant plusieurs copies du texte légèrement décalées
    offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in offsets:
        canvas.create_text(x + dx, y + dy, anchor="nw", text=enemy_data["name"], font=font, fill="black")

    # ✅ Texte principal
    canvas.create_text(x, y, anchor="nw", text=enemy_data["name"], font=font, fill=text_color)

    # ✅ ID de l'ennemi en noir
    canvas.create_text(CARD_WIDTH * 0.445, CARD_HEIGHT * 0.107, anchor="nw",
                       text=f"#{enemy_data['id']}", font=("Maitree SemiBold", int(CARD_WIDTH * 0.05)), fill="black")

# 📌 3️⃣ Icônes et valeurs des stats
def draw_stats():
    icon_boots_tk = ImageTk.PhotoImage(Image.open(ICON_BOOTS_PATH).resize((32, 32), Image.LANCZOS))
    icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(32, 32))

    canvas.create_image(CARD_WIDTH * 0.30, CARD_HEIGHT * 0.198, anchor="nw", image=icon_boots_tk)
    canvas.create_image(CARD_WIDTH * 0.54, CARD_HEIGHT * 0.198, anchor="nw", image=icon_attack_tk)

    canvas.create_text(CARD_WIDTH * 0.425, CARD_HEIGHT * 0.187, anchor="nw",
                       text=str(enemy_data["mouvement"]), font=("Maitree SemiBold", 20), fill="black")
    canvas.create_text(CARD_WIDTH * 0.652, CARD_HEIGHT * 0.187, anchor="nw",
                       text=str(enemy_data["attaque"]), font=("Maitree SemiBold", 20), fill="black")

    return icon_boots_tk, icon_attack_tk

# 📌 4️⃣ Image de l'ennemi
def draw_enemy():
    enemy_img = Image.open(ENEMY_IMAGE_PATH).resize((280, 310), Image.LANCZOS)
    enemy_img_tk = ImageTk.PhotoImage(enemy_img)
    canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.57, anchor="center", image=enemy_img_tk)
    return enemy_img_tk

# 📌 5️⃣ Barre de vie
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    points = [
        x1 + radius, y1, x2 - radius, y1, x2, y1, 
        x2, y1 + radius, x2, y2 - radius, x2, y2, 
        x2 - radius, y2, x1 + radius, y2, x1, y2, 
        x1, y2 - radius, x1, y1 + radius, x1, y1, x1 + radius, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def draw_hp_bar():
    create_rounded_rectangle(canvas, CARD_WIDTH * 0.18, CARD_HEIGHT * 0.88,
                             CARD_WIDTH * 0.82, CARD_HEIGHT * 0.94, radius=10,
                             outline="black", width=2, fill="#18A86B")

    icon_hp_tk = ImageTk.PhotoImage(Image.open(ICON_HP_PATH).resize((24, 22), Image.LANCZOS))
    canvas.create_image(CARD_WIDTH * 0.38, CARD_HEIGHT * 0.890, anchor="nw", image=icon_hp_tk)

    canvas.create_text(CARD_WIDTH * 0.48, CARD_HEIGHT * 0.875, anchor="nw",
                       text=f"{enemy_data['hp']}/{enemy_data['max_hp']}", 
                       font=("Maitree SemiBold", 18), fill="black")

    return icon_hp_tk

# 🏗️ **Appel des fonctions pour construire la carte**
bg_tk = draw_background()
draw_title()
icon_boots_tk, icon_attack_tk = draw_stats()
enemy_img_tk = draw_enemy()
icon_hp_tk = draw_hp_bar()

# 🏁 **Lancer l'affichage**
root.mainloop()
