# LLD · INC-02 · Protection des ports d'accès du 3e étage

## 1. Objet

Garantir qu'un équipement branché par un utilisateur (switch de bureau, borne, câble en double) ne puisse jamais créer de boucle de niveau 2 sur l'étage.

## 2. Commutation

| Élément | Valeur |
|---|---|
| Mode STP | Rapid PVST+ |
| Root bridge VLAN 10 | DIST-SW, priorité 4096 |
| VLAN utilisateurs | 10 · ETAGE3 · 10.10.10.0/24, passerelle 10.10.10.1 (SVI DIST-SW) |
| Uplink | ACC-1 Gi0/0 ↔ DIST-SW Gi0/1, trunk 802.1Q |

## 3. Gabarit des ports d'accès (standard)

| Fonction | Commande | Rôle |
|---|---|---|
| Accès rapide | `spanning-tree portfast edge` | Pas d'attente de 30 s pour les postes |
| Protection boucle | `spanning-tree bpduguard enable` (et `spanning-tree portfast edge bpduguard default`) | Toute BPDU reçue coupe le port (err-disabled) |
| Filet de sécurité | `storm-control broadcast level 1.00` + `storm-control action shutdown` | Coupe le port si le broadcast dépasse 1 % du débit |
| Interdit | `spanning-tree bpdufilter enable` | Rend STP aveugle sur le port |

## 4. Exploitation

- Alerte de supervision sur les messages `%SPANTREE-2-BLOCK_BPDUGUARD`, `%PM-4-ERR_DISABLE` et `%SW_MATM-4-MACFLAP_NOTIF`.
- Remise en service d'un port err-disabled : après intervention sur site uniquement (pas de recovery automatique sur l'étage).

## 5. Vérifications

```
show spanning-tree interface gi0/1 detail
show interfaces status err-disabled
show storm-control
show logging | include MACFLAP|BPDUGUARD|ERR_DISABLE
```
