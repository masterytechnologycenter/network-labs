#!/usr/bin/env bash
# Usage : ./scripts/new_lab.sh dc-fabric DCF-03 evpn-multisite
set -euo pipefail

TRACK="$1"; ID="$2"; SLUG="$3"
DEST="labs/$TRACK/$ID-$SLUG"

[ -d "labs/$TRACK" ] || { echo "Parcours inconnu : $TRACK"; exit 1; }
[ -e "$DEST" ] && { echo "Existe déjà : $DEST"; exit 1; }

git switch main
git pull
git switch -c "lab/$ID-$SLUG"

cp -r templates/lab "$DEST"
sed -i "s/{{ID}}/$ID/g; s/{{SLUG}}/$SLUG/g" "$DEST/README.md" "$DEST/docs/LLD.md"

echo "Lab créé : $DEST (branche lab/$ID-$SLUG)"
