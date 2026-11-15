#!/usr/bin/env python3
"""Fabrique le .zip de chaque lab, à côté de son .unl, pour l'import dans EVE-NG.

Usage (depuis la racine de network-labs, avant `zensical build`) :
    python scripts/zip_unl.py

EVE-NG n'importe que des .zip ; PNETLab accepte le .zip ou le .unl.
Pour chaque labs/**/topology/<nom>.unl, écrit labs/**/topology/<nom>.zip (le .unl seul dedans).
Les .zip ne sont jamais commités (*.zip dans .gitignore) : GitHub Actions les refait
à chaque publication (.github/workflows/docs.yml), puis Zensical les copie sur le site.
"""
import zipfile
from pathlib import Path

LABS = Path(__file__).resolve().parent.parent / "labs"


def main():
    n = 0
    for unl in sorted(LABS.glob("**/topology/*.unl")):
        archive = unl.with_suffix(".zip")
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            info = zipfile.ZipInfo(unl.name, date_time=(2026, 1, 1, 0, 0, 0))  # même zip à chaque fois
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, unl.read_bytes())
        n += 1
        print(f"zip : {archive.relative_to(LABS.parent).as_posix()}")
    print(f"{n} zip prêts")


if __name__ == "__main__":
    main()
