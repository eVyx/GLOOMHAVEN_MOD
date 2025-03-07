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

SCALE_RATIO = 0.8  # Réduction à 80%
CARD_WIDTH, CARD_HEIGHT = int(400 * SCALE_RATIO), int(560 * SCALE_RATIO)

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

class CarteEnnemi(tk.Frame):
    def __init__(self, parent, enemy_data):
        """Création d'une carte d'ennemi"""
        super().__init__(parent)

        if not enemy_data or "nom" not in enemy_data:
            print("❌ ERREUR: `enemy_data` ne contient pas 'nom' !", enemy_data)
            return

        self.enemy = enemy_data
        self.parent = parent
        
        self.canvas = tk.Canvas(self, width=CARD_WIDTH, height=CARD_HEIGHT, bg="black", highlightthickness=0)
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
        self.bg_tk = ImageTk.PhotoImage(papyrus_img)
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.5, anchor="center", image=self.bg_tk)

    def draw_title(self):
        """Affiche le titre et l'ID de l'ennemi."""
        x, y = CARD_WIDTH * 0.125, CARD_HEIGHT * 0.053
        font_size = int(CARD_WIDTH * 0.06)
        font = ("Dragon Hunter", font_size)
        text_color = "#FFD700" if self.enemy["elite"] else "white"

        # ✅ Contour noir simulé
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in offsets:
            self.canvas.create_text(x + dx, y + dy, anchor="nw", text=self.enemy["nom"], font=font, fill="black")

        self.canvas.create_text(x, y, anchor="nw", text=self.enemy["nom"], font=font, fill=text_color)

        # ✅ ID de l'ennemi en noir
        self.canvas.create_text(CARD_WIDTH * 0.445, CARD_HEIGHT * 0.107, anchor="nw",
                                text=f"#{self.enemy['id']}", font=("Maitree SemiBold", int(CARD_WIDTH * 0.05)), fill="black")

    def draw_stats(self):
        """Affiche les icônes et valeurs des stats."""
        self.icon_boots_tk = ImageTk.PhotoImage(Image.open(ICON_BOOTS_PATH).resize((32, 32), Image.LANCZOS))
        self.icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(32, 32))

        self.canvas.create_image(CARD_WIDTH * 0.30, CARD_HEIGHT * 0.198, anchor="nw", image=self.icon_boots_tk)
        self.canvas.create_image(CARD_WIDTH * 0.54, CARD_HEIGHT * 0.198, anchor="nw", image=self.icon_attack_tk)

        self.canvas.create_text(CARD_WIDTH * 0.425, CARD_HEIGHT * 0.187, anchor="nw",
                                text=str(self.enemy["mouvement"]), font=("Maitree SemiBold", 20), fill="black")
        self.canvas.create_text(CARD_WIDTH * 0.652, CARD_HEIGHT * 0.187, anchor="nw",
                                text=str(self.enemy["attaque"]), font=("Maitree SemiBold", 20), fill="black")

    def draw_enemy(self):
        """Affiche l'image de l'ennemi."""
        enemy_img = Image.open(self.enemy["image"]).resize((280, 310), Image.LANCZOS)
        self.enemy_img_tk = ImageTk.PhotoImage(enemy_img)
        self.canvas.create_image(CARD_WIDTH * 0.5, CARD_HEIGHT * 0.57, anchor="center", image=self.enemy_img_tk)
    
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

    def draw_hp_bar(self):
        """Affiche la barre de vie avec coins arrondis et icône PV bien positionnée."""
        
        # 🎨 Dessiner la barre de vie
        self.create_rounded_rectangle(CARD_WIDTH * 0.18, CARD_HEIGHT * 0.88,
                                    CARD_WIDTH * 0.82, CARD_HEIGHT * 0.94,
                                    radius=10, outline="black", width=2, fill="#18A86B")

        # ❤️ Charger et positionner l’icône HP dans la barre de vie
        self.icon_hp_tk = ImageTk.PhotoImage(Image.open(ICON_HP_PATH).resize((24, 24), Image.LANCZOS))
        self.canvas.create_image(CARD_WIDTH * 0.40, CARD_HEIGHT * 0.89, anchor="nw", image=self.icon_hp_tk)

        # 🔢 Affichage des PV sous forme `actuels/max`
        self.canvas.create_text(CARD_WIDTH * 0.48, CARD_HEIGHT * 0.875, anchor="nw",
                                text=f"{self.enemy['pv']}/{self.enemy['pv_max']}",
                                font=("Maitree SemiBold", 18), fill="black")

   
    
class CartePreview(tk.Frame):
    def __init__(self, parent, enemy_nom, enemy_pv, enemy_elite, mouvement, attaque):
        """Création d'une carte de prévisualisation réduite"""
        super().__init__(parent)
        self.enemy_nom = enemy_nom
        self.enemy_pv = enemy_pv
        self.enemy_elite = enemy_elite
        self.mouvement = mouvement
        self.attaque = attaque

        self.canvas = tk.Canvas(self, width=int(CARD_WIDTH / 1.3), height=int(CARD_HEIGHT / 1.3), bg="black", highlightthickness=0)
        self.canvas.pack()

        self.draw_preview()
    
    def draw_preview(self):
        """Affiche une carte réduite de l'ennemi sans la barre de vie."""
        text_color = "#FFD700" if self.enemy_elite else "white"  

        self.canvas.create_text(80, 30, text=self.enemy_nom.upper(), font=("Dragon Hunter", 12), fill=text_color)

        # Icônes
        self.icon_boots_tk = ImageTk.PhotoImage(Image.open(ICON_BOOTS_PATH).resize((24, 24), Image.LANCZOS))
        self.icon_attack_tk = load_svg_as_png(ICON_ATTACK_PATH, size=(24, 24))
        self.icon_hp_tk = ImageTk.PhotoImage(Image.open(ICON_HP_PATH).resize((20, 20), Image.LANCZOS))

        self.canvas.create_image(60, 80, anchor="nw", image=self.icon_boots_tk)
        self.canvas.create_text(90, 80, text=str(self.mouvement), font=("Maitree SemiBold", 12), fill="black")
        self.canvas.create_image(140, 80, anchor="nw", image=self.icon_attack_tk)
        self.canvas.create_text(170, 80, text=str(self.attaque), font=("Maitree SemiBold", 12), fill="black")
        self.canvas.create_image(220, 80, anchor="nw", image=self.icon_hp_tk)
        self.canvas.create_text(250, 80, text=str(self.enemy_pv), font=("Maitree SemiBold", 12), fill="black")


# 🏁 **Lancement de l'application**
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Agencement Carte")

    enemy_data = {
        "nom": "Pillard Vermling",
        "id": 1,
        "elite": 1,
        "mouvement": 2,
        "attaque": 4,
        "pv": 6,
        "pv_max": 6,
        "image": os.path.join(ENNEMIS_DIR, "pillard_vermling.png")
    }

    app = CarteEnnemi(root, enemy_data)
    app.pack()
    root.mainloop()