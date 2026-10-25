# LLD · INC-01 · Interconnexion siège ↔ Lyon en GRE over IPsec

## 1. Objet

Interconnecter le site de Lyon au siège par un tunnel GRE protégé par IPsec à travers un WAN opérateur, et y faire circuler OSPF (area 0) pour échanger les routes des LAN.

## 2. Plan d'adressage

| Usage | Réseau | SIEGE | LYON | ISP-R |
|---|---|---|---|---|
| Router-ID / Loopback0 | /32 | 1.1.1.1 | 2.2.2.2 | — |
| WAN siège | 203.0.113.0/30 | .1 (e0/0) | — | .2 (e0/0) |
| WAN Lyon | 198.51.100.0/30 | — | .1 (e0/0) | .2 (e0/1) |
| Tunnel0 | 172.16.0.0/30 | .1 | .2 | — |
| LAN siège | 10.10.0.0/24 | .1 (e0/1) | — | — |
| LAN Lyon | 10.20.0.0/24 | — | .1 (e0/1) | — |

## 3. Transport

- Route par défaut de chaque site vers ISP-R ; le WAN n'est jamais annoncé dans OSPF (pas de routage récursif du tunnel).
- Tunnel GRE `Tunnel0`, source `Ethernet0/0`, destination l'adresse WAN du site distant.

## 4. Chiffrement IPsec

| Paramètre | Valeur |
|---|---|
| IKE | IKEv1, PSK, AES-256, SHA-256, DH group 14 |
| Transform-set | ESP AES-256 + SHA-256-HMAC, **mode transport** |
| Rattachement | `tunnel protection ipsec profile GRE-IPSEC` |

## 5. Routage OSPF

- Processus 1, area 0, Router-ID = Loopback0.
- Réseaux annoncés : Loopback0, LAN, Tunnel0. LAN en `passive-interface`.
- Type de réseau du tunnel : point-à-point (pas de DR/BDR).

## 6. Choix MTU / MSS (point clé)

| Paramètre | Valeur standard | Raison |
|---|---|---|
| `ip mtu` sur Tunnel0 | **1400 des deux côtés** | 1500 − en-têtes GRE + ESP + IP externe, avec une marge |
| `ip tcp adjust-mss` | **1360** | 1400 − 40 octets d'en-têtes IP et TCP |

Les deux extrémités d'une adjacence OSPF doivent annoncer le même MTU dans leurs paquets DBD. Toute valeur différente bloque l'adjacence en EXSTART/EXCHANGE. Ne pas utiliser `ip ospf mtu-ignore` comme correctif.

## 7. Vérifications d'exploitation

```
show crypto isakmp sa
show crypto ipsec sa
show ip ospf neighbor
show ip int tu0 | i MTU
show ip route ospf
```
