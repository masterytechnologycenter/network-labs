# SEC-01 · Conception détaillée

## Adressage

| Réseau | Plage | Usage |
| --- | --- | --- |
| Client Internet | `192.0.2.0/24` | `CLIENT` `.10`, passerelle `ISP-R` `.1` |
| Liaison opérateur | `198.51.100.0/30` | `ISP-R` `.1`, `PA-FW` eth1/1 `.2` |
| IP publique du site | `203.0.113.10/32` | routée par `ISP-R` vers `PA-FW` |
| DMZ | `10.50.0.0/24` | `PA-FW` eth1/2 `.1`, `WEB-DMZ` e0/0 `.10` |
| Trust (transit) | `10.10.0.0/24` | `PA-FW` eth1/3 `.1`, `CORE1` e0/0 `.2` |
| Réseau de sauvegarde | `10.60.0.0/24` | `CORE1` e0/1 `.1`, `WEB-DMZ` e0/1 `.10` |
| Dépôt de sauvegarde | `10.70.0.0/24` | `CORE1` Lo70 `.1` |

Toutes les plages publiques sont des plages de documentation.

## Routage

- `ISP-R` : `203.0.113.0/24` vers `198.51.100.2`.
- `PA-FW` : route par défaut vers `198.51.100.1`.
- `CORE1` : route par défaut vers `10.10.0.1`.
- `WEB-DMZ` : initial, route par défaut vers `10.60.0.1` (panne) ; final, route par défaut vers `10.50.0.1` et `10.70.0.0/24` vers `10.60.0.1`.

## Sécurité sur PA-FW

- Zones : `untrust` (eth1/1), `dmz` (eth1/2), `trust` (eth1/3).
- NAT `DNAT-WEB` : `203.0.113.10` vers `10.50.0.10` (zones avant NAT : untrust vers untrust).
- Règle `WEB-IN` : untrust vers dmz, destination `203.0.113.10` (adresse avant NAT, zone après NAT), services HTTPS et HTTP (le port 80 sert seulement à rediriger vers HTTPS en production).
- Règle `INTERNET-OUT` et NAT `PAT-OUT` : sortie du réseau interne.

## Choix clés

- La règle et le NAT sont corrects dès le départ : la panne vient du routage du serveur, pas de la politique de sécurité.
- Les IOL jouent le client et le serveur (`ip http secure-server` pour HTTPS, `ip http server` pour HTTP) pour garder un lab léger.

## Vérifications

1. Panne : `CLIENT#telnet 203.0.113.10 443` expire ; `PA-FW` montre une session dont l’application est `incomplete` ; route par défaut de `WEB-DMZ` vers `10.60.0.1`.
2. Correction : `CLIENT#telnet 203.0.113.10 443` répond `Open` ; `WEB-DMZ#ping 10.70.0.1` répond.
