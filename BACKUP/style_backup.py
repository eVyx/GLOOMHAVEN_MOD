import ttkbootstrap as ttk
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ttkbootstrap import Style

# 🎨 Palette Dark Fantasy
BG_COLOR = "#151515"   # Fond très sombre
CARD_BG = "#f0e6cb"    # Beige parchemin
TEXT_COLOR = "#2c2c2c" # Noir doux pour le texte
BORDER_COLOR = "#c8442f"  # Rouge foncé pour la bordure
GOLD_COLOR = "#e0d41b"    # Doré pour ELITE

# 📜 Polices personnalisées
TITLE_FONT = ("Garamond", 14, "bold")
TEXT_FONT = ("Garamond", 12)
STAT_FONT = ("Garamond", 14, "bold")
ACTION_FONT = ("Garamond", 12, "italic")

PAPYRUS_TEXTURE_PATH = r"C:\Users\matth\Desktop\GLOOMHAVEN\IMAGES\TEXTURES\papyrus_texture.jpg"

def load_papyrus_texture():
    """Charge la texture Papyrus et la retourne sous forme de PhotoImage"""
    if os.path.exists(PAPYRUS_TEXTURE_PATH):
        try:
            texture_pil = Image.open(PAPYRUS_TEXTURE_PATH)
            texture_pil = texture_pil.resize((250, 362), Image.LANCZOS)
            return texture_pil  # On retourne l'image PIL pour la convertir plus tard
        except Exception as e:
            print(f"❌ Erreur chargement texture: {e}")
    else:
        print(f"❌ Texture non trouvée: {PAPYRUS_TEXTURE_PATH}")
    
    return None


def configure_style():
    """Applique un style cohérent à l'interface"""
    style = Style(theme="darkly")  # Utilisation du thème sombre

    # ✅ Définition des styles
    style.configure("Card.TFrame", background="#f0e6cb", relief="ridge", borderwidth=2)
    style.configure("TLabel", background="#f0e6cb", foreground="black", font=("Garamond", 12))
    style.configure("Title.TLabel", font=("Garamond", 14, "bold"), foreground="black", background="#f0e6cb")
    style.configure("Elite.TLabel", font=("Garamond", 12, "bold"), foreground="#e0d41b", background="#f0e6cb")  # Or pour ELITE

    # ✅ Boutons
    style.configure("TButton", font=("Garamond", 10, "bold"), padding=6)
    
    return style


def create_card_frame(parent, nom, numero, mouvement, attaque, pv, elite, image_path, modifier_pv, supprimer_ennemi, papyrus_texture):
    """Crée une carte d'ennemi avec un style propre"""

    # 📜 **Création du cadre principal**
    card_frame = ttk.Frame(
        parent, width=250, height=362, style="Card.TFrame"
    )
    card_frame.pack_propagate(False)

    # 📜 **Texture Papyrus**
    if papyrus_texture:
        texture_label = tk.Label(card_frame, image=papyrus_texture, bg=CARD_BG)
        texture_label.image = papyrus_texture
        texture_label.place(x=0, y=0, relwidth=1, relheight=1)

    # 📜 **Titre de l'ennemi**
    title_label = ttk.Label(card_frame, text=nom, style="Title.TLabel")
    title_label.pack()

    # 🔢 **Numéro de l'ennemi**
    id_label = ttk.Label(card_frame, text=f"#{numero}", style="TLabel")
    id_label.pack(pady=(0, 5))

    # 🏅 **Affichage "ELITE" en or si applicable**
    if elite == 1:
        elite_label = ttk.Label(card_frame, text="ELITE", style="Elite.TLabel")
        elite_label.pack()

    # 📜 **Bloc Stats**
    stats_frame = ttk.Frame(card_frame, style="Card.TFrame")
    stats_frame.pack(side=tk.BOTTOM, pady=(0, 10))

    label_mvt = ttk.Label(stats_frame, text=f"🏃 {mouvement}", style="TLabel")
    label_mvt.pack(side=tk.LEFT, padx=5)

    label_atk = ttk.Label(stats_frame, text=f"⚔ {attaque}", style="TLabel")
    label_atk.pack(side=tk.LEFT, padx=5)

    # ❤️ **Points de vie**
    hp_label = ttk.Label(stats_frame, text=f"❤️ {pv}", style="TLabel", foreground="red")
    hp_label.pack(side=tk.BOTTOM, pady=(5, 0))

    # 🩸 **Barre de vie**
    health_bar = tk.Canvas(stats_frame, width=100, height=10, bg="gray", highlightthickness=0)
    health_bar.pack(side=tk.BOTTOM, pady=(5, 0))
    update_health_bar(health_bar, pv, pv)

    # 🔘 **Boutons**
    button_frame = ttk.Frame(stats_frame)
    button_frame.pack(side=tk.BOTTOM, pady=(5, 0))

    bouton_moins = ttk.Button(button_frame, text="-1", command=lambda: modifier_pv(hp_label, health_bar, numero, -1, pv), width=3)
    bouton_moins.pack(side=tk.LEFT, padx=3)

    bouton_plus = ttk.Button(button_frame, text="+1", command=lambda: modifier_pv(hp_label, health_bar, numero, 1, pv), width=3)
    bouton_plus.pack(side=tk.LEFT, padx=3)

    bouton_mort = ttk.Button(button_frame, text="💀", command=lambda: supprimer_ennemi(card_frame, numero), width=3)
    bouton_mort.pack(side=tk.LEFT, padx=3)

    return card_frame

# 📜 Fonction pour mettre à jour la barre de vie
def update_health_bar(canvas, pv, max_pv):
    """Met à jour la barre de PV avec un dégradé dynamique."""
    canvas.delete("all")
    
    # Calcul de la couleur (du vert au rouge)
    percentage = max(0, min(1, pv / max_pv))
    red = int((1 - percentage) * 255)
    green = int(percentage * 255)
    color = f"#{red:02X}{green:02X}00"

    # Affichage de la barre de vie
    canvas.create_rectangle(0, 0, int(100 * percentage), 10, fill=color, outline=color)


# 📜 Fonction pour dessiner une carte sur le canvas
def dessiner_carte(canvas, nom, numero, mouvement, attaque, pv, elite):
    """Dessine une carte sur le canvas de preview."""
    canvas.delete("all")

    nom_sans_elite = nom.replace(" ELITE", "")

    # Dessiner la carte
    canvas.create_rectangle(5, 5, 195, 295, outline="white", width=2)

    # Affichage du nom
    canvas.create_text(100, 30, text=nom_sans_elite, font=("Garamond", 14, "bold"), fill="white")
    
     # ✅ Enlève le texte "#PREVIEW#" dans la preview
    if numero == " ":
        text_id = ""
    else:
        text_id = f"#{numero}"

    # Statut ELITE
    if elite == 1:
        canvas.create_text(100, 50, text="ELITE", font=("Garamond", 12, "bold"), fill="gold")

    # ID sous le nom
    canvas.create_text(100, 70, text=f"#{numero}", font=("Garamond", 10), fill="white")

    # Stats
    canvas.create_text(50, 150, text=f"🏃 {mouvement}", font=("Garamond", 12), fill="white")
    canvas.create_text(50, 170, text=f"⚔ {attaque}", font=("Garamond", 12), fill="white")
    canvas.create_text(50, 190, text=f"❤️ {pv}", font=("Garamond", 12, "bold"), fill="red")