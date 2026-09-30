import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Captures d'écran réelles prises par l'utilisateur dans le visualiseur 3D Napari (+43.0 px)
paths = [
    '/Users/frankbed/.gemini/antigravity-ide/brain/31fffab9-a99c-4ace-a487-ff5fccd85559/.user_uploaded/media_1790792390266.png', # Niveau 3 : Lettres FBFAL
    '/Users/frankbed/.gemini/antigravity-ide/brain/31fffab9-a99c-4ace-a487-ff5fccd85559/.user_uploaded/media_1790792390296.png', # Niveau 2 : Canaux cylindriques
    '/Users/frankbed/.gemini/antigravity-ide/brain/31fffab9-a99c-4ace-a487-ff5fccd85559/.user_uploaded/media_1790792390303.png', # Niveau 1 : Fentes planes
    '/Users/frankbed/.gemini/antigravity-ide/brain/31fffab9-a99c-4ace-a487-ff5fccd85559/.user_uploaded/media_1790792390321.png'  # Niveau 4 : Vue 3D volumique du peigne
]

# Découpe précise de la zone d'affichage (canvas) dans Napari pour retirer les barres d'outils
crops = []
for p in paths:
    im = Image.open(p).convert('RGB')
    arr = np.array(im)
    # Zone d'affichage Napari : y=24..527, x=125..684
    canvas = arr[24:527, 125:684]
    crops.append(canvas)

# Génération de la planche 2x2 haute résolution pour le rapport
fig, axs = plt.subplots(2, 2, figsize=(11, 10))
titles = [
    "(a) Niveau 3 : Gravure interne « FBFAL »",
    "(b) Niveau 2 : Canaux cylindriques (2 plus petits non résolus)",
    "(c) Niveau 1 : Fentes planes étalonnées",
    "(d) Niveau 4 : Vue volumique 3D du peigne"
]

for i, ax in enumerate(axs.flat):
    ax.imshow(crops[i])
    ax.set_title(titles[i], fontsize=12, fontweight='bold', pad=10)
    ax.axis('off')

plt.tight_layout()
# Sauvegarde en format v2 et standard pour le rapport
plt.savefig('Rapport/figures/scans_cubes_2d_v2.png', dpi=300, bbox_inches='tight')
plt.savefig('Rapport/figures/scans_cubes_2d.png', dpi=300, bbox_inches='tight')
print("Images sauvegardées avec succès dans Rapport/figures/ !")

