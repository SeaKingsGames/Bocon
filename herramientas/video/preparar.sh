#!/usr/bin/env bash
# Kit de video de Bocón: deja todo listo una vez por máquina (se guarda en ~/.cache/bocon-video).
# Se puede correr las veces que sea: lo que ya está no se vuelve a bajar.
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
C="${BOCON_CACHE:-$HOME/.cache/bocon-video}"
mkdir -p "$C"

# 1. Python: transcripción y navegador sin ventana
python3 -c "import faster_whisper" 2>/dev/null || pip install -q --break-system-packages faster-whisper
python3 -c "import playwright" 2>/dev/null || pip install -q --break-system-packages playwright
python3 -c "import numpy, scipy" 2>/dev/null || pip install -q --break-system-packages numpy scipy

# 2. Whisper small (CT2). Hugging Face suele estar bloqueado: viene partido en 4 paquetes de npm.
W="$C/whisper"
if [ ! -s "$W/model.bin" ]; then
  echo "Bajando Whisper small (~250 MB)…"
  T="$(mktemp -d)"; mkdir -p "$W"
  ( cd "$T" && for i in 0 1 2 3; do
      npm pack -q "@skillninja/shortmovie-telop-model-p$i" >/dev/null
      mkdir -p "p$i" && tar -xzf skillninja-shortmovie-telop-model-p$i-*.tgz -C "p$i"; done )
  cat "$T"/p0/package/model.bin.part0 "$T"/p1/package/model.bin.part1 \
      "$T"/p2/package/model.bin.part2 "$T"/p3/package/model.bin.part3 > "$W/model.bin.tmp"
  for f in config.json tokenizer.json vocabulary.json preprocessor_config.json; do cp "$T/p0/package/$f" "$W/"; done
  if [ -f "$T/p0/package/model.sha256" ]; then
    ( cd "$W" && echo "$(awk '{print $1}' "$T/p0/package/model.sha256")  model.bin.tmp" | sha256sum -c --quiet - ) \
      || { echo "El modelo no coincide con su sha256"; exit 1; }
  fi
  mv "$W/model.bin.tmp" "$W/model.bin"; rm -rf "$T"
fi

# 3. Fuentes de Bocón (Google Fonts suele estar bloqueado): se sacan de @fontsource.
python3 "$AQUI/fuentes.py" "$C"

echo "Kit listo en $C"
