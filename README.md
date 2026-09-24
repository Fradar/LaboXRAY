# LaboXRAY — Contrôle Non Destructif et Métrologie par Tomodensitométrie à Rayons X

Projet de laboratoire réalisé dans le cadre du cours **Travaux pratiques avancés (GPH-4102)** au Département de physique, de génie physique et d'optique de l'**Université Laval**.

**Auteurs :**
- François Bédard (536 906 601)
- Félix-Antoine Lavoie

**Professeur :**
- Simon Rainville

---

## 📌 Présentation du Projet

Ce projet implémente une chaîne complète d'acquisition, de traitement numérique du signal et de reconstruction tomodensitométrique 3D (micro-CT) appliquée au contrôle non destructif (CND) et à la métrologie dimensionnelle de pièces thermoplastiques (PLA) imprimées en 3D :

1. **Phase 1 (Mise au point et calibration)** :
   - Optimisation des paramètres géométriques et cinématiques sur un spécimen biomimétique complexe (modèle de cheval en PLA, $720$ projections sur $360^\circ$).
   - Élimination des artéfacts d'anneaux (*destriping* haute fidélité).
   - Calibration sub-pixel du centre de rotation ($COR = -11{,}6\text{ px}$).
   - Reconstruction volumique 3D par rétroprojection filtrée (FBP) et régularisation par Variation Totale (TV).

2. **Phase 2 (Métrologie dimensionnelle et détection de défauts)** :
   - Caractérisation métrologique de fantômes cubiques comportant des défauts internes de dimensions certifiées (canaux, encoches).
   - Confrontation des dimensions reconstruites aux modèles CAO nominaux par profilométrie d'atténuation et mesure de largeur à mi-hauteur (FWHM).

---

## 📂 Structure du Répertoire

```text
LaboXRAY/
├── ChevalHD_2/                 # 720 projections radiographiques brutes (0° à 360°, pas de 0.5°)
├── reconstruction_ct.py        # Pipeline de reconstruction tomodensitométrique 3D (FBP + TV)
├── visualiser_3d.py            # Visualiseur 3D interactif multi-vues (Napari) avec boîte à outils de métrologie
├── comparer_famille2_3d.py     # Script d'analyse comparative et d'optimisation cinématique (COR/axe)
├── visualiser_comparaison.py   # Visualisation comparative des reconstructions
├── lancer_visualiseur.sh       # Script shell de démarrage rapide du visualiseur Napari
├── protocole_ndt_tomodensitometrie.md # Protocole expérimental et méthodologique détaillé
├── Rapport/                    # Code source LaTeX et PDF du rapport de laboratoire
│   ├── main.tex                # Document principal LaTeX
│   ├── main.pdf                # Rapport complet compilé (15 pages)
│   ├── sections/               # Sections du rapport (Intro, Théorie, Méthodologie, etc.)
│   ├── figures/                # Figures et illustrations du rapport
│   └── references.bib          # Bibliographie scientifique (BibTeX)
├── Consignes/                  # Consignes et grilles d'évaluation du cours
└── sourcesPDF/                 # Documents de référence théorique (tomo.pdf, etc.)
```

---

## 🚀 Installation et Utilisation

### 1. Environnement Python
Le projet utilise Python 3 avec les dépendances scientifiques suivantes :
```bash
pip install numpy scipy scikit-image joblib tqdm matplotlib napari[all] magicgui PyQt6
```

### 2. Reconstruction 3D
Pour lancer la reconstruction complète du volume à partir des projections brutes :
```bash
python reconstruction_ct.py
```
Le volume reconstruit est sauvegardé au format binaire `volume_reconstruit.npy`.

### 3. Visualisation Interactive et Métrologie 3D
Pour ouvrir l'interface de métrologie 3D :
```bash
python visualiser_3d.py
# ou via le script shell :
./lancer_visualiseur.sh
```

---

## 📄 Rapport de Laboratoire
Le rapport de laboratoire est rédigé en LaTeX avec le moteur TeX / Tectonic :
* Source : `Rapport/main.tex`
* PDF final : `Rapport/main.pdf`
