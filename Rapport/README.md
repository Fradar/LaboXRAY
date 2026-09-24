# Rapport de Laboratoire CT - GPH-4102

Ce dossier contient l'ensemble du projet \LaTeX{} du rapport de laboratoire de tomodensitométrie (CT) et contrôle non destructif (CND) pour le cours **GPH-4102**, conformément aux exigences de rédaction scientifique et à la grille d'évaluation de l'Université Laval.

---

## Structure du projet

```
Rapport/
├── main.tex                         # Fichier maître (page de garde, résumé, configuration)
├── references.bib                   # Bibliographie BibTeX (ouvrages et articles majeurs)
├── figures/                         # Figures de qualité publication (300 DPI, échelles)
│   ├── reconstruction_cheval_hd.png
│   ├── comparaison_famille_axes.png
│   ├── optimisation_snr_cor.png
│   ├── analyse_double_paroi_infill.png
│   └── comparatif_materiaux_attenuation.png
└── sections/                        # Sections modulaires
    ├── 01_introduction.tex          # Contexte CND, fabrication additive, objectifs
    ├── 02_theorie.tex               # Beer-Lambert, transformée de Radon, FBP, incertitudes
    ├── 03_methodologie.tex          # Banc Leybold, paramètres X, chaîne numérique
    ├── 04_resultats_cheval.tex      # Famille d'axes, COR sub-pixel, profilométrie FWHM
    ├── 05_metrologie_cubes_preview.tex # Protocole & matrice d'étalonnage pour les cubes
    ├── 06_discussion.tex            # Analyse des incertitudes, beam hardening, pistes
    └── 07_conclusion.tex            # Bilan quantitatif et perspectives
```

---

## Compilation

### Option 1 : Sur Overleaf (Recommandé)
1. Téléversez directement le dossier `Rapport/` (ou un fichier `.zip` contenant son contenu) sur votre compte **Overleaf**.
2. Sélectionnez `main.tex` comme fichier principal.
3. Compilateur recommandé : `pdfLaTeX`.

### Option 2 : En ligne de commande (si TeXLive / MacTeX est installé)
```bash
cd Rapport
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## Intégration des scans de cubes (Séance 2)
Dès que les scans des cubes de calibration contenant les défauts connus seront acquis, il suffira de compléter :
- Les valeurs expérimentales dans le tableau `tab:gabarit_cubes` de `sections/05_metrologie_cubes_preview.tex`.
- Les figures correspondantes dans `figures/`.
