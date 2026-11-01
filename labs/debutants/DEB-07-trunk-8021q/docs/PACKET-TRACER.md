# DEB-07 · Construire le lab dans Packet Tracer

**Trunk 802.1Q : plusieurs VLAN, un seul câble** · Packet Tracer 8.x · 5 à 10 minutes. Fiche générée par `scripts/make_pt_kit.py`.

> Lab de dépannage : les configurations ci-dessous **contiennent la panne**. Construis le lab, vérifie que
> le symptôme apparaît, puis enregistre le `.pkt` : c’est ce fichier que reçoivent les apprenants.

## 1. Les équipements

| Nom | Type | Modèle Packet Tracer |
|---|---|---|
| ACC-1 | Switch | **2960-24TT** |
| ACC-2 | Switch | **2960-24TT** |
| COMPTA-1 | PC | **PC-PT** |
| RH-1 | PC | **PC-PT** |
| INVITE-1 | PC | **PC-PT** |
| COMPTA-2 | PC | **PC-PT** |
| RH-2 | PC | **PC-PT** |
| INVITE-2 | PC | **PC-PT** |

Renomme chaque équipement (clic sur le nom sous l'icône) pour retrouver les noms ci-dessus.

## 2. Le câblage

| De | Port | Vers | Port | Câble |
|---|---|---|---|---|
| ACC-1 | GigabitEthernet0/1 | ACC-2 | GigabitEthernet0/1 | Copper Straight-Through |
| COMPTA-1 | FastEthernet0 | ACC-1 | FastEthernet0/1 | Copper Straight-Through |
| RH-1 | FastEthernet0 | ACC-1 | FastEthernet0/2 | Copper Straight-Through |
| INVITE-1 | FastEthernet0 | ACC-1 | FastEthernet0/3 | Copper Straight-Through |
| COMPTA-2 | FastEthernet0 | ACC-2 | FastEthernet0/1 | Copper Straight-Through |
| RH-2 | FastEthernet0 | ACC-2 | FastEthernet0/2 | Copper Straight-Through |
| INVITE-2 | FastEthernet0 | ACC-2 | FastEthernet0/3 | Copper Straight-Through |

### Différences avec le lab PnetLab (vIOS L2)

| Lab PnetLab (vIOS L2) | Packet Tracer (2960-24TT) | Pourquoi |
|---|---|---|
| `Gi0/0` (lien entre les switchs) | `GigabitEthernet0/1` | Le 2960 n'a pas de port Gi0/0 : ses deux ports Gigabit sont Gi0/1 et Gi0/2. |
| `Gi0/1`, `Gi0/2`, `Gi0/3` (postes) | `FastEthernet0/1`, `0/2`, `0/3` | Ports d'accès du 2960. |
| `switchport trunk encapsulation dot1q` | **ligne retirée** | Le 2960 de Packet Tracer refuse cette commande : il ne fait que du 802.1Q. vIOS L2 l'accepte, elle reste dans les configs PnetLab. |
| `spanning-tree portfast edge` | `spanning-tree portfast` | Syntaxe du 2960 de Packet Tracer. |

Le reste (noms, VLAN 10, 20, 30 et 99, adresses, VLAN natif 99, VLAN autorisés) est identique.

## 3. Les PC (Desktop → IP Configuration)

| PC | Adresse IP | Masque | Passerelle | DNS |
|---|---|---|---|---|
| COMPTA-1 | 192.168.10.11 | 255.255.255.0 | — | — |
| RH-1 | 192.168.20.11 | 255.255.255.0 | — | — |
| INVITE-1 | 192.168.30.11 | 255.255.255.0 | — | — |
| COMPTA-2 | 192.168.10.12 | 255.255.255.0 | — | — |
| RH-2 | 192.168.20.12 | 255.255.255.0 | — | — |
| INVITE-2 | 192.168.30.12 | 255.255.255.0 | — | — |

## 4. Les configurations (onglet CLI, copier-coller)

**ACC-1** : `configs/packet-tracer/ACC-1.txt`

```
! ACC-1 · 2960-24TT · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname ACC-1
no ip domain-lookup
!
vlan 10
 name COMPTA
vlan 20
 name RH
vlan 30
 name INVITES
vlan 99
 name NATIF
!
! Gi0/1 ici = Gi0/0 du lab PnetLab (lien vers l'autre switch)
interface GigabitEthernet0/1
 description LIEN-VERS-ACC-2
 switchport mode access
!
interface FastEthernet0/1
 description COMPTA
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface FastEthernet0/2
 description RH
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
!
interface FastEthernet0/3
 description INVITES
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
!
line con 0
 logging synchronous
!
end
write memory
```

**ACC-2** : `configs/packet-tracer/ACC-2.txt`

```
! ACC-2 · 2960-24TT · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname ACC-2
no ip domain-lookup
!
vlan 10
 name COMPTA
vlan 20
 name RH
vlan 30
 name INVITES
vlan 99
 name NATIF
!
! Gi0/1 ici = Gi0/0 du lab PnetLab (lien vers l'autre switch)
interface GigabitEthernet0/1
 description LIEN-VERS-ACC-1
 switchport mode access
!
interface FastEthernet0/1
 description COMPTA
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface FastEthernet0/2
 description RH
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
!
interface FastEthernet0/3
 description INVITES
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
!
line con 0
 logging synchronous
!
end
write memory
```

## 6. Vérifier le symptôme

- [ ] Tous les voyants des câbles sont verts (attendre 30 s que les ports des switchs passent au vert)
- [ ] Depuis COMPTA-1 : ping 192.168.10.12 (COMPTA-2) → échec : c'est le symptôme
- [ ] Sur ACC-1 : show interfaces trunk → aucune ligne (le lien GigabitEthernet0/1 est en mode accès)

## 7. Observer comme dans la vidéo

1. Après la correction, sur ACC-1 : show interfaces trunk → Gig0/1 en trunk 802.1q, VLAN natif 99, VLAN autorisés 10,20,30,99
2. Depuis COMPTA-1 : ping 192.168.10.12 → réussi ; idem RH-1 vers RH-2 (192.168.20.12) et INVITE-1 vers INVITE-2 (192.168.30.12)
3. Mode Simulation, filtre ICMP : clique sur l'enveloppe entre les deux switchs pour voir l'étiquette 802.1Q (VLAN 10)

## 8. Enregistrer

*Fichier → Enregistrer sous* : `topology/DEB-07.pkt`, puis préviens Claude pour l'ajouter au dépôt.

## Solution (formateur, à ne pas distribuer)

Configurations corrigées : `configs/packet-tracer/solution/`. Lignes qui changent :

**ACC-1** · à ajouter

```
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
```

**ACC-2** · à ajouter

```
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99
```
