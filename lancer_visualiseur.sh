#!/bin/zsh
# Script de lancement automatique pour la visualisation 3D
cd "$(dirname "$0")"
source .venv/bin/activate
python visualiser_3d.py
