#!/usr/bin/env python3
"""Sauvegarde les configs d'un lab et les commit dans Git.
Usage : python scripts/backup_configs.py labs/dc-fabric/DCF-03-evpn-multisite --stage final
"""
import argparse
import re
import subprocess
from datetime import date
from getpass import getpass
from pathlib import Path

import yaml
from netmiko import ConnectHandler

# Masque la valeur qui suit password / secret / key-string / pre-shared-key
MASK = re.compile(
    r"((?:password|secret|key-string|pre-shared-key)\s+(?:\d+\s+|ENC\s+)?)\S+",
    re.IGNORECASE,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", type=Path)
    parser.add_argument("--stage", choices=["initial", "final"], default="final")
    args = parser.parse_args()

    devices = yaml.safe_load((args.lab / "inventory.yml").read_text())["devices"]
    out = args.lab / "configs" / args.stage
    out.mkdir(parents=True, exist_ok=True)

    user = input("Utilisateur : ")
    pwd = getpass("Mot de passe : ")

    for dev in devices:
        params = {k: v for k, v in dev.items() if k != "name"}
        with ConnectHandler(**params, username=user, password=pwd) as conn:
            cfg = conn.send_command("show running-config")
        (out / f"{dev['name']}.cfg").write_text(MASK.sub(r"\1<MASQUE>", cfg))
        print(f"OK  {dev['name']}")

    subprocess.run(["git", "add", str(out)], check=True)
    subprocess.run(
        ["git", "commit", "-m", f"{args.lab.name} : configs {args.stage} {date.today()}"],
        check=True,
    )


if __name__ == "__main__":
    main()
