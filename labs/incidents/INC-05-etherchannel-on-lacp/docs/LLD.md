# LLD · INC-05 · Liaison distribution ↔ accès du 2e étage

## 1. Objet

Relier chaque switch d'accès au switch de distribution par deux liens de 1 Gbit/s regroupés en un seul lien logique (EtherChannel), négocié par LACP, pour doubler le débit et survivre à la perte d'un câble.

## 2. Commutation

| Élément | Valeur |
|---|---|
| Mode STP | Rapid PVST+ |
| Root bridge VLAN 10 | DIST-SW, priorité 4096 |
| VLAN utilisateurs | 10 · BUREAUX · 10.5.10.0/24, passerelle 10.5.10.1 (SVI DIST-SW) |
| Uplink | Port-channel1 = Gi0/1 + Gi0/2, trunk 802.1Q, des deux côtés |

## 3. Gabarit des uplinks (standard du site)

| Fonction | Commande | Rôle |
|---|---|---|
| Négociation | `channel-group 1 mode active` (des deux côtés) | Chaque switch envoie des messages LACP : le canal ne se forme qu'avec un voisin qui répond |
| Trunk | `switchport mode trunk` sur Po1 et sur les ports membres | Mêmes réglages sur tous les membres, sinon un port est écarté du canal |
| Protection | `spanning-tree etherchannel guard misconfig` (actif par défaut) | Coupe le canal (err-disabled) si l'autre côté n'est pas regroupé de la même façon |
| Interdit | `channel-group 1 mode on` face à un voisin LACP | Aucune négociation : le canal ne peut pas se former |

| Côté A | Côté B | Canal formé ? |
|---|---|---|
| on | on | Oui, sans négociation |
| active | active | Oui |
| active | passive | Oui |
| passive | passive | **Non** : aucun des deux ne parle en premier |
| on | active ou passive | **Non** |

## 4. Exploitation

- Alerte de supervision sur les messages EtherChannel, en particulier `%EC-5-L3DONTBNDL2` (port suspendu : LACP absent en face), et sur `%PM-4-ERR_DISABLE`.
- Constaté en lab (vIOS L2 15.2, 05/11/2026) : `on` face à `active` ne déclenche **pas** d'err-disabled ; le côté LACP suspend ses ports, le côté `on` se croit en service (`Po1(SU)`).
- Contrôle après toute intervention sur un uplink : `show etherchannel summary` des deux côtés (Po1 en `SU`, membres en `P`) et `show lacp neighbor`.

## 5. Vérifications

```
show etherchannel summary
show lacp neighbor
show running-config | include channel-group
show logging | include EC-
```

Changer de mode : retirer d'abord la ligne exacte (`no channel-group 1 mode on`), puis `channel-group 1 mode active`. IOS refuse le passage direct d'un mode `on` à un mode LACP.

## Sources

- Cisco, *Catalyst 2960-X Switch Layer 2 Configuration Guide*, chapitre « Configuring EtherChannels » : modes `on`, `active`, `passive`, et combinaisons compatibles.
- Cisco, *Catalyst 2960-X Switch Layer 2 Configuration Guide*, chapitre « Configuring Optional Spanning-Tree Features » : EtherChannel guard (`spanning-tree etherchannel guard misconfig`).
- IEEE 802.1AX (Link Aggregation), qui reprend LACP (802.3ad).
