import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# 1. Charger la capture CAO 3D réelle fournie par l'utilisateur
cad_path = '/Users/frankbed/.gemini/antigravity-ide/brain/31fffab9-a99c-4ace-a487-ff5fccd85559/.user_uploaded/media_1790793734371.png'
im_cad = Image.open(cad_path).convert('RGB')
arr_cad = np.array(im_cad)

# Découpe ajustée avec marge légère
bg = arr_cad[0, 0].astype(int)
diff = np.abs(arr_cad.astype(int) - bg).max(axis=2)
mask = diff > 8
rows = np.where(mask.any(axis=1))[0]
cols = np.where(mask.any(axis=0))[0]
pad = 15
ymin = max(0, rows[0] - pad)
ymax = min(arr_cad.shape[0], rows[-1] + pad)
xmin = max(0, cols[0] - pad)
xmax = min(arr_cad.shape[1], cols[-1] + pad)
tight_cad = im_cad.crop((xmin, ymin, xmax, ymax))

# 2. Charger la capture CT 3D réelle de l'utilisateur (+43.0 px)
ct_path = '/Users/frankbed/.gemini/antigravity-ide/brain/31fffab9-a99c-4ace-a487-ff5fccd85559/.user_uploaded/media_1790792390321.png'
im_ct = Image.open(ct_path).convert('RGB')
canvas_ct = im_ct.crop((125, 24, 684, 527))

arr_ct = np.array(canvas_ct)
mask_ct = (arr_ct > 15).any(axis=2)
rows_ct = np.where(mask_ct.any(axis=1))[0]
cols_ct = np.where(mask_ct.any(axis=0))[0]
pad = 12
ymin_ct = max(0, rows_ct[0] - pad)
ymax_ct = min(arr_ct.shape[0], rows_ct[-1] + pad)
xmin_ct = max(0, cols_ct[0] - pad)
xmax_ct = min(arr_ct.shape[1], cols_ct[-1] + pad)
tight_ct = canvas_ct.crop((xmin_ct, ymin_ct, xmax_ct, ymax_ct))

# 3. Sauvegarder les fichiers individuels propres
tight_cad.save('Rapport/figures/cube2_cad_reference.png')
tight_ct.save('Rapport/figures/cube2_ct_3d_reference.png')

# 4. Assembler la figure composite 4
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6), dpi=300)

ax1.imshow(tight_cad)
ax1.set_title('(a) Modèle numérique CAO nominal (STL) - Cube 2\n[Architecture interne : fentes, canaux, lettres FBFAL et peigne]', fontsize=11, fontweight='bold', pad=12)
ax1.axis('off')

ax2.imshow(tight_ct)
ax2.set_title('(b) Reconstruction 3D tomodensitométrique (Scan micro-CT)\n[Rendu volumique optimisé - COR = +43,0 px]', fontsize=11, fontweight='bold', pad=12)
ax2.axis('off')

plt.tight_layout()
plt.savefig('Rapport/figures/comparaison_stl_ct_cube2.png', dpi=300, bbox_inches='tight')
print("Figure 4 régénérée au complet avec succès dans Rapport/figures/comparaison_stl_ct_cube2.png !")

