import sqlite3
import tkinter as tk
import os
from PIL import Image, ImageDraw, ImageTk
import cairosvg
import cairosvg
from PIL import Image, ImageTk


# 📜 Chemins des ressources
DB_PATH = r"C:\Users\matth\Desktop\GLOOMHAVEN\ennemy_mod.db"
PAPYRUS_TEXTURE_PATH = r"C:\Users\matth\Desktop\GLOOMHAVEN\RESSOURCES\TEXTURES\papyrus.png"
DEFAULT_IMAGE_PATH = r"C:\Users\matth\Desktop\GLOOMHAVEN\RESSOURCES\ENNEMIS\default.png"


def load_svg_as_png(svg_path, size=(24, 24)):
    """Convertit une icône SVG en PNG et la charge en tant qu'image Tkinter."""
    png_path = svg_path.replace(".svg", ".png")  # Convertir en chemin PNG temporaire

    # 📌 Conversion du SVG en PNG
    cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])

    # 📌 Charger l'image avec PIL et la convertir en format Tkinter
    img = Image.open(png_path)
    return ImageTk.PhotoImage(img)


def create_rounded_card(width, height, radius=30):
    """Crée une image avec un rectangle arrondi et un fond papyrus."""
    papyrus = Image.open(PAPYRUS_TEXTURE_PATH).resize((width, height), Image.LANCZOS)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((0, 0, width, height), radius, outline="#8B0000", width=10, fill=(255, 255, 255, 50))
    papyrus.paste(overlay, (0, 0), overlay)
    return ImageTk.PhotoImage(papyrus)


class CarteEnnemi(tk.Frame):
    def __init__(self, parent, nom, action_callback, pv, elite, mouvement, attaque, numero, jeu):
        """Carte d'ennemi en combat avec fond personnalisé et icônes."""
        super().__init__(parent, borderwidth=2, relief="solid")

        self.nom = nom.replace(" ELITE", "")
        self.pv = pv
        self.elite = elite
        self.mouvement = mouvement
        self.attaque = attaque
        self.numero = numero
        self.action_callback = action_callback
        self.jeu = jeu  

        # ✅ Correction du fond
        bg_color = parent["bg"] if "bg" in parent.keys() else "white"
        self.configure(bg=bg_color)

        self.width, self.height = 300, 400
        self.config(width=self.width, height=self.height)
        self.grid_propagate(False)

        # 🎨 Appliquer l'image de fond
        self.bg_tk = create_rounded_card(self.width, self.height)
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, highlightthickness=0, bg=bg_color)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk)

        # 📌 Charger les icônes AVANT de les utiliser
        self.icon_movement = ImageTk.PhotoImage(Image.open(r"C:\Users\matth\Desktop\GLOOMHAVEN\RESSOURCES\ICONS\BOOTS.png"))
        self.icon_attack = load_svg_as_png(r"C:\Users\matth\Desktop\GLOOMHAVEN\RESSOURCES\ICONS\ATTACK.svg")

        # 📜 **Image de l'ennemi**
        self.image_path = self.get_image_path_from_db()
        self.display_enemy_image(self.image_path)

        # 📌 Définition des positions avant affichage
        x_mouvement = self.width * 0.25
        x_attaque = self.width * 0.65
        y_position = self.height * 0.18

        # ✅ Affichage des icônes Mouvement et Attaque
        self.canvas.create_image(x_mouvement, y_position, image=self.icon_movement, anchor="center")
        self.canvas.create_text(x_mouvement + 25, y_position, text=self.mouvement, font=("DRAGON HUNTER", 14), fill="black", anchor="w")
        self.canvas.create_image(x_attaque, y_position, image=self.icon_attack, anchor="center")
        self.canvas.create_text(x_attaque + 25, y_position, text=self.attaque, font=("DRAGON HUNTER", 14), fill="black", anchor="w")

        # 🏷️ **Nom de l'ennemi**
        self.canvas.create_text(self.width // 2, int(self.height * 0.08), text=self.nom.upper(),
                                font=("DRAGON HUNTER", 16), fill="black")

        # 🎖️ **Affichage "ELITE"**
        if self.elite == 1:
            self.canvas.create_text(self.width // 2, int(self.height * 0.13), text="ELITE",
                                    font=("DRAGON HUNTER", 12), fill="#8B0000")
        
        # ❤️ **Healthbar**
        self.health_bar = tk.Canvas(self, width=int(self.width * 0.8), height=10, bg="gray", highlightthickness=0)
        self.health_bar.place(x=int(self.width * 0.1), y=int(self.height * 0.85))

        # 🔢 **Affichage des stats**
        self.afficher_boutons_stats()

        # ✅ Initialisation correcte des PV
        self.set_pv(self.pv)

        # 🔥 Fixe les images en mémoire
        self.canvas.image = [self.bg_tk, self.enemy_img_tk, self.icon_movement, self.icon_attack]
                
    def load_svg_as_png(svg_path, size=(24, 24)):
        """Convertit une icône SVG en image PNG et la charge en tant qu'image Tkinter."""
        png_path = svg_path.replace(".svg", ".png")  # Convertir en chemin PNG temporaire

        # 📌 Conversion du SVG en PNG
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=size[0], output_height=size[1])

        # 📌 Charger l'image avec PIL et la convertir en format Tkinter
        img = Image.open(png_path)
        return ImageTk.PhotoImage(img)
    
    def display_enemy_image(self, image_path):
        """Charge et affiche l'image de l'ennemi avec correction d'alignement et transparence."""
        img = Image.open(image_path)
        img = img.resize((int(self.width * 0.6), int(self.height * 0.35)), Image.LANCZOS)
        self.enemy_img_tk = ImageTk.PhotoImage(img)

        x_center = self.width // 2
        y_position = int(self.height * 0.25)

        self.canvas.create_image(x_center, y_position, anchor="n", image=self.enemy_img_tk)
        self.canvas.image.append(self.enemy_img_tk)  # 🔥 Fixe l’image en mémoire

    def afficher_boutons_stats(self):
        """Ajoute les boutons de gestion des PV."""
        button_y = int(self.height * 0.92)

        self.bouton_moins = tk.Button(self, text="-1", command=lambda: self.action_callback(self.numero, -1), width=2)
        self.bouton_moins.place(x=self.width * 0.2, y=button_y)

        self.bouton_plus = tk.Button(self, text="+1", command=lambda: self.action_callback(self.numero, 1), width=2)
        self.bouton_plus.place(x=self.width * 0.5, y=button_y)

        self.bouton_mort = tk.Button(self, text="💀", command=self.destroy, width=2)
        self.bouton_mort.place(x=self.width * 0.8, y=button_y)

    def set_pv(self, nouveaux_pv):
        """Met à jour les PV de l'ennemi et rafraîchit l'affichage."""
        self.pv = nouveaux_pv
        print(f"🔄 Mise à jour PV UI : {self.nom} - {self.pv}")
        self.update_health_bar()

    def update_health_bar(self):
        """Met à jour la barre de vie avec affichage des PV restants."""
        self.health_bar.delete("all")
        max_pv = self.get_max_pv_from_db()
        percentage = max(0, min(1, self.pv / max_pv))

        color = "#18A86B" if percentage > 0.75 else "#E5C100" if percentage > 0.5 else "#F07818" if percentage > 0.25 else "#AF374B"
        self.health_bar.create_rectangle(0, 0, int((self.width * 0.8) * percentage), 10, fill=color, outline=color)
        self.health_bar.create_text(int(self.width * 0.4), -5, text=f"❤️ {self.pv} / {max_pv}",
                                    font=("DRAGON HUNTER", 10, "bold"), fill="white")
        self.health_bar.update_idletasks()

    def get_max_pv_from_db(self):
        """Récupère les PV max de l'ennemi depuis la BDD."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT pv FROM ennemis WHERE nom = ?", (self.nom,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else 10

    def get_image_path_from_db(self):
        """Récupère le chemin de l'image de l'ennemi depuis la BDD."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT image FROM ennemis WHERE nom = ?", (self.nom,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and os.path.exists(result[0]) else DEFAULT_IMAGE_PATH


class CartePreview(tk.Frame):
    def __init__(self, parent, nom, pv, elite, mouvement, attaque):
        """Affiche une prévisualisation de la carte ennemi avec un ratio réduit."""
        super().__init__(parent, borderwidth=0, relief="ridge")  # ✅ Bordure plus fine
        
        self.nom = nom.replace(" ELITE", "")
        self.pv = pv
        self.elite = elite
        self.mouvement = mouvement
        self.attaque = attaque

        # ✅ Ajustement des dimensions pour la preview (60% de la taille normale)
        self.width, self.height = int(300 * 0.6), int(400 * 0.6)
        self.config(width=self.width, height=self.height)
        self.grid_propagate(False)

        # 🎨 Appliquer l'image de fond
        self.bg_tk = create_rounded_card(self.width, self.height)
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, highlightthickness=0)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_tk)
        self.canvas.pack()

        # 🏷️ **Nom de l'ennemi**
        self.canvas.create_text(self.width // 2, int(self.height * 0.08), text=self.nom.upper(),
                                font=("DRAGON HUNTER", 12), fill="black")

        # 🎖️ **Affichage "ELITE"**
        if self.elite:
            self.canvas.create_text(self.width // 2, int(self.height * 0.13), text="ELITE",
                                    font=("DRAGON HUNTER", 10), fill="#8B0000")

        # 🔢 **Affichage des statistiques**
        self.afficher_statistiques_preview()


    def afficher_statistiques_preview(self):
        """Affiche les statistiques (mouvement | attaque | PV) avec icônes et ratio réduit."""
        stat_font = ("DRAGON HUNTER", 8)
        icon_font = ("Font Awesome 6 Free Solid", 8)

        stat_y = int(self.height * 0.85)  # ✅ Meilleur placement
        positions = [0.15, 0.5, 0.85]
        stats = [("🚶", self.mouvement), ("✊", self.attaque), ("❤️", self.pv)]

        for i, (icon, value) in enumerate(stats):
            self.canvas.create_text(self.width * positions[i], stat_y, text=icon, font=icon_font, fill="black")
            self.canvas.create_text(self.width * (positions[i] + 0.1), stat_y, text=value, font=stat_font, fill="black")
