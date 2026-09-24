"""
Visualiseur interactif 3D comparatif dans Napari pour la Famille 2.
Permet d'activer/désactiver et comparer en 3D :
- Option 5 (0-360° +theta)
- Option 6 (0-360° -theta)
- Option 7 (0-180° 720 proj)
- Option 8 (0-180° 360 proj)
- Option 12 (0-360° COR -12px)
"""

import os
os.environ['QT_API'] = 'pyqt6'

import sys
import numpy as np

def main():
    npz_path = 'volumes_famille2.npz'
    if not os.path.exists(npz_path):
        print(f"[ERREUR] '{npz_path}' introuvable. Exécutez d'abord comparer_famille2_3d.py.")
        sys.exit(1)

    print(f"Chargement des volumes comparatifs depuis '{npz_path}'...")
    data = np.load(npz_path)

    import napari

    viewer = napari.Viewer(title="Comparaison 3D - Famille 2 (Options 5, 6, 7, 8, 12)")

    c_min = 0.0012
    c_max = 0.0065

    colormaps = {
        'Option 5': 'magma',
        'Option 6': 'viridis',
        'Option 7': 'turbo',
        'Option 8': 'plasma',
        'Option 12': 'inferno',
    }

    descriptions = {
        'Option 5': 'Option 5 : 0-360° (+θ, 720 proj) - Référence',
        'Option 6': 'Option 6 : 0-360° (-θ, sens inversé)',
        'Option 7': 'Option 7 : 0-180° (720 proj)',
        'Option 8': 'Option 8 : 0-180° (360 proj, demi-tour)',
        'Option 12': 'Option 12 : 0-360° (COR -12px)',
    }

    for key in ['Option 5', 'Option 6', 'Option 7', 'Option 8', 'Option 12']:
        if key in data:
            vol = data[key]
            # Seule l'Option 5 est active au départ, les autres sont prêtes à être cochées
            is_visible = (key == 'Option 5')
            viewer.add_image(
                vol,
                name=descriptions.get(key, key),
                colormap=colormaps.get(key, 'magma'),
                contrast_limits=[c_min, c_max],
                rendering='mip',
                blending='translucent',
                opacity=1.0,
                visible=is_visible
            )

    print("\n" + "="*70)
    print("        VISUALISEUR COMPARATIF 3D MULTI-OPTIONS (NAPARI)")
    print("="*70)
    print("Utilisez la liste des calques à gauche pour cocher / décocher")
    print("et comparer directement les différentes options en 3D.")
    print("="*70 + "\n")

    viewer.dims.ndisplay = 3
    napari.run()

if __name__ == '__main__':
    main()
