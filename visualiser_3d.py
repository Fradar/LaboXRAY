"""
Visualiseur 3D interactif multi-vues (Axiale, Sagittale, Coronale, 3D) avec boîte à outils de métrologie.
Résout définitivement le problème de curseur/décalage lors du changement de plan en fournissant
des vues natives orientées avec suivi de règle sans déformation ni bug d'affichage.
"""

import os
# Backend PyQt6 pour un affichage natif et stable sur macOS
os.environ['QT_API'] = 'pyqt6'

import sys
import numpy as np
import scipy.ndimage as ndi
import matplotlib.pyplot as plt

def main():
    volume_path = 'volume_reconstruit.npy'
    if not os.path.exists(volume_path):
        print(f"[ERREUR] Le fichier '{volume_path}' est introuvable. Exécutez d'abord reconstruction_ct.py.")
        sys.exit(1)

    print(f"Chargement de '{volume_path}'...")
    volume_axial = np.load(volume_path)
    print(f"Volume chargé : {volume_axial.shape} voxels.")

    # Pré-calcul des vues orthogonales (instantané par manipulation de strides)
    volume_sagittal = np.moveaxis(volume_axial, 2, 0)  # Profil (Infill complet) : (500, 241, 500)
    volume_coronal = np.moveaxis(volume_axial, 1, 0)   # Face / Dos : (500, 241, 500)

    volumes = {
        'axiale': volume_axial,
        'sagittale': volume_sagittal,
        'coronale': volume_coronal
    }

    import napari
    from magicgui.widgets import Container, PushButton, FloatSpinBox, Label

    viewer = napari.Viewer(title="Laboratoire CT 3D - Métrologie Multi-Plans")

    c_min = 0.0012
    c_max = 0.0065

    # 1. Calque Image principal
    img_layer = viewer.add_image(
        volume_axial,
        name='Cheval PLA HD',
        colormap='magma',
        contrast_limits=[c_min, c_max],
        rendering='mip',
        blending='translucent',
        opacity=1.0
    )

    # 2. Calques Règles dédiés pour chaque plan (évite toute corruption géométrique entre vues)
    ruler_ax = viewer.add_shapes(
        ndim=3,
        name='Règle Axiale',
        shape_type='line',
        edge_color='cyan',
        edge_width=3,
        face_color='transparent'
    )
    ruler_sag = viewer.add_shapes(
        ndim=3,
        name='Règle Sagittale',
        shape_type='line',
        edge_color='yellow',
        edge_width=3,
        face_color='transparent'
    )
    ruler_cor = viewer.add_shapes(
        ndim=3,
        name='Règle Coronale',
        shape_type='line',
        edge_color='lime',
        edge_width=3,
        face_color='transparent'
    )

    rulers = {
        'axiale': ruler_ax,
        'sagittale': ruler_sag,
        'coronale': ruler_cor
    }

    current_view = ['axiale']

    # Widget de contrôle et de métrologie
    lbl_views = Label(value='--- SÉLECTION DU PLAN DE COUPE ---')
    btn_ax = PushButton(text='🔴 Coupe Axiale (Transversale)')
    btn_sag = PushButton(text='🟡 Coupe Sagittale (Vue Profil / Infill)')
    btn_cor = PushButton(text='🟢 Coupe Coronale (Vue Face / Dos)')
    btn_3d = PushButton(text='🧊 Vue 3D Volumique (Perspective)')

    lbl_sep = Label(value='--- OUTILS DE MÉTROLOGIE ---')
    scale_spin = FloatSpinBox(value=0.100, label='Échelle (mm/px) :', step=0.005, min=0.001, max=5.0)
    btn_analyze = PushButton(text='📊 Analyser profil & Épaisseur (FWHM)')
    btn_clear = PushButton(text='🗑️ Effacer les mesures du plan actif')
    lbl_status = Label(value='Prêt : cliquez et glissez sur l\'image pour mesurer.')

    def changer_vue(nom):
        current_view[0] = nom
        if nom == '3d':
            img_layer.data = volume_axial
            viewer.dims.order = (0, 1, 2)
            viewer.dims.ndisplay = 3
            for r in rulers.values():
                r.visible = True
            lbl_status.value = 'Mode 3D actif : rotation à la souris. Cliquez sur un plan 2D pour mesurer.'
            return

        # Vues 2D natives sans aucun bug de transposition
        viewer.dims.ndisplay = 2
        viewer.dims.order = (0, 1, 2)
        v = volumes[nom]
        img_layer.data = v

        # Centrage automatique de la tranche d'observation
        if nom == 'axiale':
            viewer.dims.set_current_step(0, 140)
        else:
            viewer.dims.set_current_step(0, 250)

        # Gestion des calques règles
        for k, r in rulers.items():
            r.visible = (k == nom)

        active_ruler = rulers[nom]
        viewer.layers.selection.active = active_ruler
        active_ruler.mode = 'add_line'

        noms_fr = {
            'axiale': 'Axiale (coupes transversales)',
            'sagittale': 'Sagittale (profil & infill)',
            'coronale': 'Coronale (face/dos)'
        }
        lbl_status.value = f"Vue {noms_fr[nom]} active. Cliquez-glissez pour tracer."

    btn_ax.clicked.connect(lambda: changer_vue('axiale'))
    btn_sag.clicked.connect(lambda: changer_vue('sagittale'))
    btn_cor.clicked.connect(lambda: changer_vue('coronale'))
    btn_3d.clicked.connect(lambda: changer_vue('3d'))

    def effacer_mesures_actives():
        if current_view[0] in rulers:
            rulers[current_view[0]].data = []
            lbl_status.value = f"Mesures effacées pour le plan {current_view[0]}."

    btn_clear.clicked.connect(effacer_mesures_actives)

    def analyser_profil():
        nom = current_view[0]
        if nom not in rulers or len(rulers[nom].data) == 0:
            lbl_status.value = '[!] Aucune mesure tracée sur ce plan. Tracez une ligne d\'abord.'
            return

        active_ruler = rulers[nom]
        active_vol = volumes[nom]
        line = active_ruler.data[-1]  # (2, 3)
        p1, p2 = line[0], line[1]

        scale_mm = float(scale_spin.value)
        dist_px = float(np.linalg.norm(p2 - p1))
        dist_mm = dist_px * scale_mm

        # Échantillonnage du profil d'atténuation sur la vue active
        n_pts = max(int(round(dist_px * 3)), 15)
        t = np.linspace(0, 1, n_pts)
        coords = np.array([p1[d] * (1 - t) + p2[d] * t for d in range(active_vol.ndim)])
        profile = ndi.map_coordinates(active_vol, coords, order=1)

        # Calcul de l'épaisseur à mi-hauteur (FWHM)
        p_min, p_max = float(np.min(profile)), float(np.max(profile))
        half_max = (p_min + p_max) / 2.0
        above = profile >= half_max
        fwhm_px = float(np.sum(above)) / len(profile) * dist_px
        fwhm_mm = fwhm_px * scale_mm

        msg = f"Longueur : {dist_px:.1f} px ({dist_mm:.2f} mm) | Épaisseur FWHM : {fwhm_px:.1f} px ({fwhm_mm:.2f} mm)"
        lbl_status.value = msg
        print(f"\n[MÉTROLOGIE - {nom.upper()}] {msg}")

        # Affichage pop-up non-bloquant du profil
        plt.close('Profil Métrologique CT')
        fig, ax = plt.subplots(num='Profil Métrologique CT', figsize=(7, 3.2))
        dist_axis = np.linspace(0, dist_mm, n_pts)
        ax.plot(dist_axis, profile, color='#ff7f0e', lw=2.5, label='Profil d\'atténuation')
        ax.axhline(half_max, color='#7f7f7f', linestyle='--', label=f'Mi-hauteur ({half_max:.4f})')
        ax.set_xlabel('Distance le long du segment (mm)', fontsize=10)
        ax.set_ylabel('Atténuation μ (1/px)', fontsize=10)
        ax.set_title(f'Plan {nom.capitalize()} — Longueur : {dist_mm:.2f} mm | FWHM : {fwhm_mm:.2f} mm', fontsize=11, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        plt.tight_layout()
        plt.show(block=False)

    btn_analyze.clicked.connect(analyser_profil)

    # Connexion du tracé direct sur chaque règle
    def attacher_evenement(ruler, nom):
        @ruler.events.data.connect
        def on_data_change(event=None):
            if len(ruler.data) > 0 and current_view[0] == nom:
                line = ruler.data[-1]
                dist_px = float(np.linalg.norm(line[1] - line[0]))
                scale_mm = float(scale_spin.value)
                dist_mm = dist_px * scale_mm
                lbl_status.value = f"[{nom.capitalize()}] Dernier tracé : {dist_px:.1f} px = {dist_mm:.2f} mm (cliquez sur Analyser)"

    for k, r in rulers.items():
        attacher_evenement(r, k)

    # Interception des boutons internes de Napari pour empêcher la corruption de coordonnées
    @viewer.dims.events.order.connect
    def on_dims_order_change(event=None):
        if viewer.dims.ndisplay == 2 and tuple(viewer.dims.order) != (0, 1, 2):
            order = tuple(viewer.dims.order)
            if order in [(1, 0, 2), (1, 2, 0)]:
                changer_vue('coronale')
            elif order in [(2, 0, 1), (2, 1, 0)]:
                changer_vue('sagittale')

    container = Container(
        widgets=[
            lbl_views,
            btn_ax,
            btn_sag,
            btn_cor,
            btn_3d,
            lbl_sep,
            scale_spin,
            btn_analyze,
            btn_clear,
            lbl_status
        ],
        labels=True
    )
    viewer.window.add_dock_widget(container, name='Métrologie Multi-Plans', area='right')

    # Démarrage par défaut en coupe axiale avec tracé activé
    changer_vue('axiale')

    print("\n" + "="*75)
    print("      LABORATOIRE CT 3D - NAVIGATION MULTI-PLANS & MÉTROLOGIE")
    print("="*75)
    print("Dans le panneau de droite 'Métrologie Multi-Plans' :")
    print("  🔴 Coupe Axiale       : Coupes transversales perpendiculaires au cylindre.")
    print("  🟡 Coupe Sagittale    : Vue de profil du cheval avec grille d'infill bien à plat.")
    print("  🟢 Coupe Coronale     : Vue de dessus / face du cheval.")
    print("  🧊 Vue 3D Volumique   : Rendu 3D avec rotation libre à la souris.")
    print("\nPour chaque plan 2D, l'outil Ligne est automatiquement activé sous votre curseur,")
    print("sans aucun décalage ni bug d'affichage !")
    print("="*75 + "\n")

    napari.run()

if __name__ == '__main__':
    main()
