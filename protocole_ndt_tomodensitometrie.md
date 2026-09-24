# Protocole d'Expérience : Tomodensitométrie et Contrôle Non Destructif (NDT)

**Laboratoire de Physique Avancée - Rayons X**

## 1. Préambule

En utilisant une source de rayons X et un capteur de radiographie numérique, cette expérience vise à étudier l'atténuation des rayons X à travers la matière et à utiliser ces informations pour reconstruire une image 3D de la structure interne d'un objet. Ce projet se concentre sur les applications de **Contrôle Non Destructif (NDT - Non-Destructive Testing)** par tomodensitométrie (CT). Le spécimen étudié sera une **petite pièce imprimée en 3D**. L'objectif est d'inspecter l'intégrité structurelle de la pièce (porosités, densité de remplissage, précision dimensionnelle interne) sans l'altérer.

> [!WARNING]
> Les rayons X sont des rayonnements ionisants (capables d'arracher des électrons de la matière). L'appareil doit être utilisé avec toutes les portes vitrées fermées et verrouillées.

---
**Notes Préambule :**
<br><br><br>
---

## 2. Objectifs

*   **Comprendre** les propriétés des rayons X et la loi d'atténuation dans la matière.
*   **Maîtriser** l'utilisation de l'appareil à rayons X et de la caméra CMOS (via connexion Ethernet) disponibles au laboratoire.
*   **Appliquer** les techniques de balayage tomographique pour acquérir des projections d'une pièce imprimée en 3D sous de multiples angles.
*   **Analyser et interpréter** les volumes 3D reconstruits via l'algorithme de rétroprojection filtrée pour identifier les défauts de fabrication (vides, délamination, etc.).

---
**Notes / Hypothèses de départ :**
<br><br><br>
---

## 3. Théorie

### 3.1 Génération et interaction des rayons X
Dans le tube à rayons X, des électrons sont accélérés par une haute tension et percutent une anode. Il en résulte l'émission d'un spectre de rayons X (Bremsstrahlung et rayonnement caractéristique).
Lorsqu'un faisceau de rayons X traverse un matériau d'épaisseur $d$, son intensité $I$ est atténuée selon la loi :
$$I = I_0 \cdot e^{-\mu d}$$
où $I_0$ est l'intensité incidente et $\mu$ le coefficient d'atténuation linéaire du matériau.

### 3.2 Reconstruction Tomographique (Rétroprojection Filtrée)
Le balayage tomographique consiste à acquérir l'atténuation du faisceau pour de multiples angles $\theta$ autour de l'objet.
L'algorithme de **Rétroprojection Filtrée (FBP)** est utilisé par le logiciel *Tomodensitométrie Pro* pour reconstruire le volume : chaque projection subit un filtrage passe-haut puis est "rétro-étalée" le long de son trajet d'origine. L'accumulation de ces projections donne la cartographie 3D des coefficients $\mu(x,y,z)$ de l'objet.

---
**Notes Théoriques :**
<br><br><br>
---

## 4. Appareillage et Matériel (Disponibles au Laboratoire)

*   **Appareil à rayons X** : Appareil de base avec goniomètre et portes vitrées de sécurité.
*   **Tube à rayons X** : Tubes disponibles (Cuivre, Molybdène, Or). **Recommandation :** Utiliser l'anode en **Or (Au)** car elle génère un rayonnement plus énergétique et plus intense que le Cu et le Mo, ce qui est idéal pour traverser une pièce en plastique d'impression 3D en NDT.
*   **Capteur d'imagerie** : Écran à scintillation couplé à un capteur CMOS (connecté via câble ethernet et câble d'alimentation).
*   **Logiciel** : *Tomodensitométrie Pro*.
*   **Échantillon NDT** : Pièce imprimée en 3D (ex: PLA/ABS) d'environ 2 à 4 cm, contenant idéalement des défauts internes ou une structure de remplissage partielle (lattice).

---
**Paramètres d'équipement sélectionnés :**
*Tube choisi :* ........................
*Objet testé :* ........................
*Matériau de l'objet :* ........................
*Dimensions de l'objet :* ........................
<br><br><br>
---

## 5. Méthodologie et Guide Pas à Pas

### Étape 1 : Préparatifs et Montage
1. Installer le tube à rayons X (Or ou Molybdène) dans l'appareil.
2. Pousser le goniomètre vers la droite et le fixer. Positionner le capteur.
3. Fixer la pièce imprimée en 3D sur l'axe du goniomètre. **Important :** L'objet ne doit subir aucun mouvement par rapport à son axe pendant la rotation de 360°.
4. Connecter le capteur (Ethernet et alimentation) et fermer les portes vitrées.

---
**Notes sur le montage expérimental :**
<br><br><br>
---

### Étape 2 : Calibration (Offset et Référence)
> [!TIP]
> La calibration est critique. L'image de référence (champ plat) doit se faire idéalement sans l'objet dans le faisceau pour avoir un champ clair parfait.

1. Lancer le logiciel **Tomodensitométrie Pro**. Aller dans le menu *Caméra*.
2. **Offset (Tube éteint)** :
   - Rayons X éteints.
   - Identifier les pixels défectueux et cliquer sur "Créer image d'offset à partir d'images d'obscurité" (laisser moyenner environ 10-20 images).
3. **Référence (Tube allumé)** :
   - Retirer la pièce du trajet des rayons X.
   - Enclencher les rayons X (Haute Tension $\approx$ 35.0 kV, Courant $\approx$ 1.00 mA). *Note : les deux portes doivent être fermées et verrouillées pour que le tube s'allume.*
   - Cliquer sur "Créer image de référence à partir d'images de champ plat" (laisser moyenner environ 10-20 images).
   - Replacer l'objet et ajuster le temps d'intégration si nécessaire (généralement 825 ms pour Au ou 1750 ms pour Mo).

---
**Paramètres de calibration enregistrés :**
*Tension (kV) :* ........................
*Courant (mA) :* ........................
*Temps d'intégration (ms) :* ........................
*Nb d'images moyennées (Offset/Ref) :* ........................
<br><br><br>
---

### Étape 3 : Ajustement de l'axe de rotation
1. Vérifier que la pièce reste visible sur l'écran lors d'une rotation manuelle/test.
2. L'axe de rotation vertical doit être au centre de l'écran. S'il y a un décalage, cela créera des "images fantômes" (artéfacts de dédoublement) lors de la reconstruction 2D/3D.

---
**Notes d'ajustement de l'axe :**
<br><br><br>
---

### Étape 4 : Balayage Tomographique (Acquisition)
1. Allez dans *Balayage TDM $\rightarrow$ Lancer l'acquisition scanner*.
2. Choisir le nombre d'angles (ex: 360 pour un pas de 1°).
3. Choisir la résolution de reconstruction (le binning). Lancer le balayage. L'appareil tournera la pièce automatiquement.

---
**Paramètres d'acquisition :**
*Nombre de projections :* ........................
*Résolution / Binning choisi :* ........................
*Temps total d'acquisition :* ........................
<br><br><br>
---

### Étape 5 : Reconstruction et Évaluation NDT
1. Laisser le logiciel calculer la rétroprojection filtrée.
2. Si les bords sont flous ou dédoublés en vue 2D, utiliser l'outil de correction de l'axe de rotation du logiciel (corrections souvent à 25% et 75% du bord de l'image) puis recalculer les coupes.
3. **Inspection 2D :** Analyser les plans de coupe (xy, xz, yz). Chercher les variations de $\mu$ (pixels sombres = air/porosité/absence de matière). Mesurer les défauts ou épaisseurs de parois avec l'outil de distance.
4. **Inspection 3D :** Ajuster le *Dégradé* et la *Transparence* pour rendre le plastique externe semi-transparent et révéler la structure de remplissage interne.

---
**Observations et Résultats (Défauts, Porosités, Dimensions) :**
<br><br><br><br><br><br><br><br>
---

## 6. Analyse pour le Rapport
*   Insérer les captures des coupes 2D et 3D montrant la structure interne (ex: remplissage en nid d'abeille, défauts d'extrusion).
*   Discuter de l'influence potentielle du durcissement du spectre (beam hardening) sur l'atténuation au centre de la pièce.
*   Évaluer la résolution spatiale de votre scan : quelle est la taille du plus petit défaut détectable dans votre pièce ?

---
**Brouillon pour l'analyse / Idées :**
<br><br><br><br><br><br>
---

## 7. Références
*   [1] GPH-3000, *Protocole TP rayons X-2*, Université Laval.
*   [2] *Tomodensitométrie - Manuel Utilisateur*, LD DIDACTIC GmbH.
*   [3] I. Bloch, *Reconstruction d'images de tomographie*, LTCI, Télécom Paris.
