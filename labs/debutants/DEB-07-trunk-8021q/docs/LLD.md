# DEB-07 · Conception détaillée (LLD)

**Lab** : DEB-07-Trunk-8021Q · **Auteur** : Hilaire TCHOUATEU · **Images** : vIOS L2 (IOS 15.2), VPCS

## 1. Adressage et VLAN

| VLAN | Nom | Sous-réseau | Postes |
|---|---|---|---|
| 10 | COMPTA | 192.168.10.0/24 | COMPTA-1 .11 (ACC-1 Gi0/1) · COMPTA-2 .12 (ACC-2 Gi0/1) |
| 20 | RH | 192.168.20.0/24 | RH-1 .11 (ACC-1 Gi0/2) · RH-2 .12 (ACC-2 Gi0/2) |
| 30 | INVITES | 192.168.30.0/24 | INVITE-1 .11 (ACC-1 Gi0/3) · INVITE-2 .12 (ACC-2 Gi0/3) |
| 99 | NATIF | — | aucun poste : VLAN natif du trunk |

Pas de routeur ni de passerelle : les VLAN restent séparés (hors sujet de ce lab).

## 2. Transport

| Lien | État initial (panne) | État final |
|---|---|---|
| ACC-1 Gi0/0 – ACC-2 Gi0/0 | `switchport mode access` (VLAN 1 seulement) | trunk 802.1Q, natif 99, autorisés 10,20,30,99 |
| Ports Gi0/1 à Gi0/3 | accès, VLAN 10 / 20 / 30, `spanning-tree portfast edge` | inchangé |

## 3. Choix clés

- **Lien explicitement en accès au départ** : on ne dépend pas du mode DTP par défaut de l'image.
- **VLAN natif 99**, sans poste, identique aux deux bouts : choix du lab. Cisco exige le même VLAN natif des deux côtés ; le changer n'est pas présenté comme une règle officielle.
- **Liste des VLAN autorisés** limitée aux VLAN utiles (10, 20, 30) et au natif (99).
- `switchport trunk encapsulation dot1q` : acceptée par vIOS L2 (capture du 30/10). Elle n'existe pas sur les plateformes qui ne gèrent que 802.1Q.

## 4. Vérifications (sorties réelles du 30/10/2026)

| Étape | Commande | Résultat attendu |
|---|---|---|
| Avant | `COMPTA-1> ping 192.168.10.12` | `host (192.168.10.12) not reachable` |
| Avant | `show running-config interface Gi0/0` | `switchport mode access` |
| Après | `show interfaces trunk` | `Gi0/0  on  802.1q  trunking  99` · autorisés `10,20,30,99` |
| Après | pings COMPTA, RH, INVITE vers le poste d'en face | 5 réponses sur 5 |

## 5. Pour aller plus loin

VLAN natif 1 sur ACC-2 seulement : observer les journaux d'ACC-1 (message de non-concordance du VLAN natif, à vérifier en lab).
