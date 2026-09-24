"""
Script de reconstruction tomodensitométrique 3D Haute Résolution et Haut SNR.
Configuration optimisée pour isoler la pièce en PLA et révéler son infill interne :
- Découpage tomographique le long des colonnes X (Axe de rotation physique).
- Plage sélectionnée X=80 à 320 pour isoler le cheval sans la pince métallique de droite.
- Destriping haute fidélité sur les sinogrammes (élimination complète des artéfacts d'anneaux).
- Calage sub-pixel du centre de rotation (COR = -11.6 px) par interpolation spline d'ordre 3.
- Rétroprojection filtrée 2D (FBP avec filtre Shepp-Logan).
- Débruitage léger à Variation Totale (TV) préservant les arêtes (suppression du bruit de photons).
- Masquage précis de la bordure externe du capteur (r <= 220 px).
- Visualiseur interactif 3D Napari (PyQt6).
"""

import os
os.environ['QT_API'] = 'pyqt6'

import glob
import re
import time
import numpy as np
from skimage.io import imread
from skimage.transform import iradon
from skimage.restoration import denoise_tv_chambolle
from joblib import Parallel, delayed
from tqdm import tqdm
import scipy.ndimage as ndi
import matplotlib.pyplot as plt


def get_ordered_projection_files(folder_path, total_angles=360.0, step=0.5):
    """Génère la liste ordonnée exacte de 0° à 360° selon les noms de fichiers."""
    print(f"\n[1/5] Indexation stricte des 720 projections de 0° à {total_angles}°...")
    num_steps = int(round(total_angles / step))
    ordered_files = []
    ordered_angles = []

    for i in range(num_steps):
        deg = i * step
        candidates = [
            f"Projection{int(deg)}.png" if deg.is_integer() else f"Projection{deg}.png",
            f"Projection{deg:.1f}.png",
            f"Projection{int(deg)}.tif" if deg.is_integer() else f"Projection{deg}.tif",
        ]
        filepath = None
        for cand in candidates:
            p = os.path.join(folder_path, cand)
            if os.path.exists(p):
                filepath = p
                break
        if filepath:
            ordered_files.append(filepath)
            ordered_angles.append(deg)

    if len(ordered_files) == 0:
        all_files = sorted(glob.glob(os.path.join(folder_path, '*.png')))
        def get_deg(fp):
            m = re.search(r'(\d+(?:\.\d+)?)\.png$', fp)
            return float(m.group(1)) if m else -1.0
        ordered_files = sorted(all_files, key=get_deg)
        ordered_angles = [get_deg(f) for f in ordered_files]

    print(f" -> {len(ordered_files)} projections prêtes (0.0° à 359.5°).")
    return ordered_files, np.array(ordered_angles, dtype=np.float32)


def load_projections(file_list):
    """Charge les 720 images dans un tableau 3D."""
    print(f"\nChargement des {len(file_list)} images en mémoire...")
    imgs = []
    for f in tqdm(file_list, desc="Lecture des images", unit="img"):
        img = imread(f)
        if img.ndim == 3:
            img = img[:, :, 0]
        imgs.append(img)
    data = np.array(imgs, dtype=np.float32)
    return data


def normalize_and_destripe(proj):
    """
    Normalisation radiométrique de Beer-Lambert et suppression des artéfacts d'anneaux.
    Le destriping corrige les dérives stationnaires de sensibilité des pixels du détecteur.
    """
    print("\n[2/5] Normalisation Beer-Lambert & Suppression des artéfacts d'anneaux...")
    I0 = np.percentile(proj, 99.9)
    print(f" -> Intensité de référence (I0) : {I0:.1f}")
    transmittance = np.clip(proj / I0, 1e-5, 1.0)
    absorbance = -np.log(transmittance)
    
    # Destriping le long de l'axe des angles (axis 0)
    proj_mean = np.mean(absorbance, axis=0)
    proj_median = ndi.median_filter(proj_mean, size=(1, 9))
    stripes = proj_mean - proj_median
    absorbance_clean = absorbance - stripes[None, :, :]
    print(" -> Filtrage des bandes stationnaires appliqué (anneaux éliminés).")
    return absorbance_clean


def _reconstruct_slice_hd(sino_slice, angles_deg, cor_subpixel=-11.6, tv_weight=0.0004):
    """
    Reconstruction d'une coupe avec :
    1. Calage subpixel du centre de rotation (spline ordre 3)
    2. Rétroprojection filtrée (FBP Shepp-Logan)
    3. Débruitage Total Variation (TV) léger pour maximiser le SNR
    4. Masque propre pour exclure le bord du détecteur (r <= 220 px)
    """
    sino_shifted = ndi.shift(sino_slice, (0, cor_subpixel), order=3, mode='nearest')
    rec = iradon(sino_shifted.T, theta=angles_deg, filter_name='shepp-logan', circle=True)
    rec_denoised = denoise_tv_chambolle(rec, weight=tv_weight)
    
    ny, nz = rec_denoised.shape
    Y, Z = np.ogrid[:ny, :nz]
    rec_denoised[(Y - 250)**2 + (Z - 250)**2 > 220**2] = 0.0
    return rec_denoised


def reconstruct_3d_volume(sinograms, angles_deg, x_start=80, x_end=321, cor_subpixel=-11.6, n_jobs=-1):
    """Reconstruction tomographique 3D HD de la pièce isolée."""
    x_indices = np.arange(x_start, x_end, 1)
    print(f"\n[3/5] Reconstruction tomographique HD & Haut SNR ({len(x_indices)} coupes axiales)...")
    t0 = time.time()
    
    slices = Parallel(n_jobs=n_jobs)(
        delayed(_reconstruct_slice_hd)(sinograms[:, :, x], angles_deg, cor_subpixel=cor_subpixel)
        for x in tqdm(x_indices, desc="Calcul des coupes HD", unit="coupe")
    )
    volume = np.array(slices, dtype=np.float32)
    print(f" -> Reconstruction terminée en {time.time() - t0:.1f} secondes. Forme : {volume.shape}")
    return volume


def generate_summary_figure(volume):
    """Génère la planche récapitulative haute définition."""
    print("\n[4/5] Génération de la planche haute définition...")
    fig, axes = plt.subplots(2, 2, figsize=(15, 13))
    vmin, vmax = 0.0012, 0.0065

    # 1. Silhouette MIP X
    ax1 = axes[0, 0]
    im1 = ax1.imshow(np.max(volume, axis=0), cmap='magma', vmin=0.0015, vmax=0.0075)
    ax1.set_title('1. Silhouette Globale HD (MIP selon X)', fontsize=12, fontweight='bold')
    ax1.axis('off')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    # 2. Infill MIP Z
    ax2 = axes[0, 1]
    im2 = ax2.imshow(np.max(volume, axis=2), cmap='magma', vmin=0.0015, vmax=0.0065)
    ax2.set_title('2. Treillis d Infill 3D HD (MIP selon Z)', fontsize=12, fontweight='bold')
    ax2.axis('off')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    # 3. Coupe longitudinale interne Z=250
    ax3 = axes[1, 0]
    im3 = ax3.imshow(volume[:, :, 250].T, cmap='magma', vmin=vmin, vmax=vmax)
    ax3.set_title('3. Coupe Longitudinale Interne (Plan Z=250)', fontsize=12, fontweight='bold')
    ax3.axis('off')
    plt.colorbar(im3, ax=ax3, fraction=0.046, pad=0.04)

    # 4. Coupe transversale X=220 (indice 220-80 = 140)
    ax4 = axes[1, 1]
    im4 = ax4.imshow(volume[140, :, :], cmap='magma', vmin=vmin, vmax=vmax)
    ax4.set_title('4. Coupe Transversale (X=220)', fontsize=12, fontweight='bold')
    ax4.axis('off')
    plt.colorbar(im4, ax=ax4, fraction=0.046, pad=0.04)

    plt.suptitle('Cheval PLA Isolé - Qualité Haute Définition, Haut SNR & Haute Résolution', fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig('apercu_cheval_hd_final.png', dpi=150)
    print(" -> Planche haute résolution sauvegardée : 'apercu_cheval_hd_final.png'.")


def view_volume(volume):
    """Lance Napari configuré pour le volume HD."""
    print("\n[5/5] Ouverture du visualiseur 3D interactif...")
    try:
        import napari
    except ImportError:
        print("[ERREUR] Napari n'est pas disponible.")
        return

    c_min = 0.0012
    c_max = 0.0065

    viewer = napari.Viewer(title="Reconstruction CT 3D HD - Cheval PLA (Haut SNR)")
    
    viewer.add_image(
        volume,
        name='Cheval PLA HD (MIP 3D)',
        colormap='magma',
        contrast_limits=[c_min, c_max],
        rendering='mip',
        blending='translucent',
        opacity=1.0,
        visible=True
    )
    
    viewer.dims.ndisplay = 3
    napari.run()


if __name__ == '__main__':
    DOSSIER = 'ChevalHD_2'
    TOTAL_ANGLES = 360.0
    PAS = 0.5
    COR_SUBPIXEL = -11.6

    try:
        fichiers, angles = get_ordered_projection_files(DOSSIER, total_angles=TOTAL_ANGLES, step=PAS)
        projections = load_projections(fichiers)
        sinogrammes_propres = normalize_and_destripe(projections)
        volume = reconstruct_3d_volume(sinogrammes_propres, angles, cor_subpixel=COR_SUBPIXEL, x_start=80, x_end=321)
        
        np.save('volume_reconstruit.npy', volume)
        print(" -> Fichier 'volume_reconstruit.npy' mis à jour.")
        
        generate_summary_figure(volume)
        view_volume(volume)
        
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        import traceback
        traceback.print_exc()
