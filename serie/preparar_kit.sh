#!/bin/bash
# Monta uma cópia do kit Viral Sem Aparecer com o pacote de ações do Trono Abissal (serie/acoes.py).
# Uso: bash serie/preparar_kit.sh  -> imprime a pasta scripts do kit com ações (use no lugar do kit original).
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
ORIG=$(find / -path '*viral-sem-aparecer/scripts/produzir_historia.py' 2>/dev/null | grep -v kit_trono | head -1)
[ -n "$ORIG" ] || { echo "kit não encontrado" >&2; exit 1; }
SRC=$(dirname "$(dirname "$ORIG")")
DEST=/home/claude/kit_trono
rm -rf "$DEST"; cp -r "$SRC" "$DEST"
printf '\n\n# --- Trono Abissal: pacote de ações\nexec(open(%s, encoding="utf-8").read())\n' "'$REPO/serie/acoes.py'" >> "$DEST/scripts/desenho.py"
echo "$DEST/scripts"
