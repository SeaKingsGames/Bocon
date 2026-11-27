#!/bin/sh
# Cómo se armaron las frutas de «Marionetas listas» (correr desde la raíz del repo).
set -e
F=recursos-fuentes/marionetas/frutas
sep(){ python3 herramientas/marionetas/separar.py "$F/$1.png" "/tmp/$1-piezas"; }
arm(){ python3 herramientas/marionetas/armar.py "$1" "/tmp/$2-piezas" "$2" --guardar; }
# el plátano tapa su brazo derecho: se hace en espejo del otro, y su pie derecho se ve solo un poco
FORCE=3:armA,6:footA MIRROR=A sep platano; arm Plátano platano
for k in fresa pina sandia naranja mango; do sep $k; done
arm Fresa fresa; arm Piña pina; arm Sandía sandia; arm Naranja naranja; arm Mango mango
sep aguacate; AJUSTE='{"ey":-0.6,"my":-0.33,"er":0.15,"ex":0.3,"bw":0.45}' arm Aguacate aguacate
sep uvas; AJUSTE='{"ey":-0.85,"my":-0.45,"er":0.24,"ex":0.42,"bw":0.7,"ojos":"caricatura"}' arm Uvas uvas
sep coco; AJUSTE='{"ojos":"caricatura"}' arm Coco coco
