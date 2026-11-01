# Importer le lab

Le fichier `.unl` contient la topologie habillée (zones, titres, fiches), les liens et la configuration initiale des nœuds IOL et VPCS.

- **EVE-NG / PnetLab** : compresse le `.unl` en `.zip`, puis Import dans l'interface.
- **Pare-feu Palo Alto** : sa configuration n'est pas chargée automatiquement. Une fois PAN-OS démarré (plusieurs minutes), connecte-toi en console, tape `configure`, colle le contenu de `configs/initial/PA-FW.set.txt`, puis `commit`.
- Images attendues : `paloalto-10.2.9`, IOL L3 `i86bi-linux-l3-adventerprisek9-15.4.2T.bin`, VPCS. Si tes noms diffèrent, corrige `eve-images.yml` puis régénère : `python scripts/make_unl.py labs/securite/SEC-01-paloalto-nat-dmz`.
