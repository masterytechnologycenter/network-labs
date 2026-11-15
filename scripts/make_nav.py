#!/usr/bin/env python3
"""Écrit les fichiers .nav.yml du site (menu de gauche) à partir des titres des labs.

Usage (depuis la racine de network-labs) :
    python scripts/make_nav.py

Pourquoi : sans menu écrit à la main, Zensical affiche les noms de dossiers
(« CAS 01 ospf segmentation paloalto », « Debutants »). Ce script donne à chaque
entrée son vrai titre, lu dans le « # Titre » de la page, et ne garde dans le menu
que les parcours qui ont au moins un lab. Il est relancé à chaque publication
par GitHub Actions (.github/workflows/docs.yml) : un nouveau lab apparaît donc
dans le menu sans rien modifier ici.
"""
import re
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs"

# Parcours, dans l'ordre du menu (du plus simple au plus avancé), avec leur titre.
PARCOURS = [
    ("debutants", "Débutants"),
    ("tp-packet-tracer", "TP Packet Tracer"),
    ("incidents", "Incidents en entreprise"),
    ("securite", "Sécurité réseau"),
    ("cas-pratiques", "Cas pratiques"),
    ("campus", "Campus et commutation"),
    ("routage-wan", "Routage et WAN"),
    ("dc-fabric", "Data Center Fabric"),
    ("cloud-hybride", "Cloud hybride"),
    ("automatisation", "Automatisation"),
]

# Titres courts des pages d'un lab, selon leur nom de fichier.
PAGES = {
    "README.md": None,  # page d'accueil du lab : son vrai titre (onglet du navigateur, moteurs de recherche)
    "docs/LLD.md": "Conception détaillée (LLD)",
    "docs/PACKET-TRACER.md": "Construire dans Packet Tracer",
    "topology/LISEZMOI.md": "Importer le lab",
}


def titre(page):
    for ligne in page.read_text(encoding="utf-8").splitlines():
        if ligne.startswith("# "):
            return ligne[2:].strip()
    return page.parent.name


def court(t, limite=64):
    """« INC-02 · Boucle de niveau 2 : tout un étage… » reste entier s'il tient, sinon on coupe proprement."""
    if len(t) <= limite:
        return t
    for sep in (" : ", ", ", " – ", " avec "):
        if sep in t and len(t.split(sep)[0]) >= 12:
            return t.split(sep)[0]
    return t[:limite].rsplit(" ", 1)[0] + "…"


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def labs_du(dossier):
    return sorted(d for d in dossier.iterdir() if d.is_dir() and (d / "README.md").exists())


def ecrire(chemin, lignes):
    texte = "# Généré par scripts/make_nav.py : ne pas modifier à la main.\n" + "\n".join(lignes) + "\n"
    if not chemin.exists() or chemin.read_text(encoding="utf-8") != texte:
        chemin.write_bytes(texte.encode("utf-8"))  # fins de ligne LF, comme le reste du dépôt
        print(f"écrit : {chemin.relative_to(LABS.parent)}")


def main():
    racine = ["nav:", "  - \"Accueil\": index.md"]
    for slug, nom in PARCOURS:
        dossier = LABS / slug
        if not dossier.is_dir():
            continue
        labs = labs_du(dossier)
        if not labs:  # parcours encore vide : hors du menu (sa page reste accessible par lien)
            continue
        racine.append(f"  - {q(nom)}: {slug}")
        menu = ["nav:", "  - index.md"]
        for lab in labs:
            menu.append(f"  - {q(court(titre(lab / 'README.md')))}: {lab.name}")
            pages = ["nav:"]
            for rel, libelle in PAGES.items():
                if (lab / rel).exists():
                    pages.append(f"  - {rel}" if libelle is None else f"  - {q(libelle)}: {rel}")
            autres = sorted(p for p in lab.rglob("*.md") if p.relative_to(lab).as_posix() not in PAGES)
            for p in autres:
                pages.append(f"  - {q(court(titre(p)))}: {p.relative_to(lab).as_posix()}")
            ecrire(lab / ".nav.yml", pages)
        ecrire(dossier / ".nav.yml", menu)
    ecrire(LABS / ".nav.yml", racine)


if __name__ == "__main__":
    main()
