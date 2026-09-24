"""
Reconstruction 3D comparative de la Famille 2 (découpe le long des colonnes X) :
- Option 5 : 0-360° (+theta, 720 proj, centre standard)
- Option 6 : 0-360° (-theta, sens de rotation inverse)
- Option 7 : 0-180° (720 proj comprimées sur demi-tour)
- Option 8 : 0-180° (360 proj, demi-scan réel)
- Option 12 : 0-360° (+theta, centre de rotation décalé de -12 px)

Génère une planche comparative complète et prépare les volumes pour Napari.
"""

import os
os.environ['QT_API'] = 'pyqt6'

import time
import numpy as np
from skimage.io import imread
from skimage.transform import iradon
from joblib import Parallel, delayed
import matplotlib.pyplot as plt

folder = 'ChevalHD_2'
print("[1/5] Indexation des projections...")
files = []
for i in range(720):
    deg = i * 0.5
    name = f'Projection{int(deg)}.png' if deg.is_integer() else f'Projection{deg}.png'
    files.append(os.path.join(folder, name))

print("[2/5] Chargement et normalisation Beer-Lambert...")
imgs = [imread(f) for f in files]
data = np.array(imgs, dtype=np.float32)
I0 = np.percentile(data, 99.9)
sinograms = -np.log(np.clip(data / I0, 1e-5, 1.0))

# Définition des plages de coupes (le cheval se situe entre X=80 et X=330)
x_indices = np.arange(80, 330, 1)  # 250 coupes haute résolution
print(f" -> {len(x_indices)} coupes axiales sélectionnées (X={x_indices[0]} à {x_indices[-1]}).")

# Grilles angulaires
th360 = np.linspace(0, 360, 720, endpoint=False)
th180_all = np.linspace(0, 180, 720, endpoint=False)
th180_half = np.linspace(0, 180, 360, endpoint=False)

options_def = [
    ('Option 5', '0-360° (+θ, 720 proj)', lambda s: iradon(s.T, theta=th360, circle=True)),
    ('Option 6', '0-360° (-θ, sens inversé)', lambda s: iradon(s.T, theta=-th360, circle=True)),
    ('Option 7', '0-180° (720 proj)', lambda s: iradon(s.T, theta=th180_all, circle=True)),
    ('Option 8', '0-180° (360 proj)', lambda s: iradon(s[:360].T, theta=th180_half, circle=True)),
    ('Option 12', '0-360° (COR -12px)', lambda s: iradon(np.roll(s, -12, axis=1).T, theta=th360, circle=True)),
]

volumes = {}

print("\n[3/5] Calcul des reconstructions 3D pour chaque option...")
# Masque de bordure circulaire pour éliminer les bords du capteur
ny, nz = 500, 500
Y, Z = np.ogrid[:ny, :nz]
r_mask = np.sqrt((Y - 250)**2 + (Z - 250)**2) > 220

for opt_id, opt_name, recon_fn in options_def:
    t0 = time.time()
    print(f"Reconstruction de {opt_id} ({opt_name})...")
    
    slices = Parallel(n_jobs=-1)(
        delayed(recon_fn)(sinograms[:, :, x]) for x in x_indices
    )
    vol = np.array(slices, dtype=np.float32)
    # Appliquer le masque de bordure
    for i in range(len(vol)):
        vol[i][r_mask] = 0.0
        
    volumes[opt_id] = vol
    print(f" -> Terminé en {time.time() - t0:.1f}s. Shape: {vol.shape}")

print("\n[4/5] Sauvegarde des volumes pour Napari...")
np.savez_compressed('volumes_famille2.npz', **volumes)
print(" -> Fichier 'volumes_famille2.npz' enregistré.")

print("\n[5/5] Génération de la planche comparative visuelle...")
fig, axes = plt.subplots(4, len(options_def), figsize=(20, 16))

for col_idx, (opt_id, opt_name, _) in enumerate(options_def):
    vol = volumes[opt_id]
    
    # 1. Silhouette globale MIP selon X
    mip_x = np.max(vol, axis=0)
    vmin_x, vmax_x = 0.0015, 0.0075
    ax1 = axes[0, col_idx]
    ax1.imshow(mip_x, cmap='magma', vmin=vmin_x, vmax=vmax_x)
    ax1.set_title(f"{opt_id} : {opt_name}\nSilhouette Globale (MIP X)", fontsize=10, fontweight='bold')
    ax1.axis('off')
    
    # 2. Quadrillage d'infill (MIP selon Z)
    mip_z = np.max(vol, axis=2)
    vmin_z, vmax_z = 0.0015, 0.0065
    ax2 = axes[1, col_idx]
    ax2.imshow(mip_z, cmap='magma', vmin=vmin_z, vmax=vmax_z)
    ax2.set_title(f"Quadrillage Infill (MIP Z)", fontsize=10, fontweight='bold')
    ax2.axis('off')
    
    # 3. Coupe longitudinale au centre (Plan Z=250)
    # x_indices démarre à 80, donc X=220 correspond à l'indice 220-80 = 140
    slice_z = vol[:, :, 250].T
    ax3 = axes[2, col_idx]
    ax3.imshow(slice_z, cmap='magma', vmin=0.0012, vmax=0.0065)
    ax3.set_title(f"Coupe Interne (Plan Z=250)", fontsize=10, fontweight='bold')
    ax3.axis('off')
    
    # 4. Coupe transversale (X=220, indice 140)
    slice_trans = vol[140, :, :]
    ax4 = axes[3, col_idx]
    ax4.imshow(slice_trans, cmap='magma', vmin=0.0012, vmax=0.0065)
    ax4.set_title(f"Coupe Transversale (X=220)", fontsize=10, fontweight='bold')
    ax4.axis('off')

plt.suptitle("Comparaison des Reconstructions 3D - Famille 2 (Options 5, 6, 7, 8, 12)", fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('comparaison_famille2_3d.png', dpi=150)
print(" -> Planche haute résolution sauvegardée : 'comparaison_famille2_3d.png'.")
