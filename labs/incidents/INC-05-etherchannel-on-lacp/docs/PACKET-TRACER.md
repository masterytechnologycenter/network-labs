# INC-05 · Construire le lab dans Packet Tracer

**EtherChannel qui ne monte pas : mode on contre LACP active** · Packet Tracer 8.x · 5 à 10 minutes. Fiche générée par `scripts/make_pt_kit.py`.

> Lab de dépannage : les configurations ci-dessous **contiennent la panne**. Construis le lab, vérifie que
> le symptôme apparaît, puis enregistre le `.pkt` : c’est ce fichier que reçoivent les apprenants.

## 1. Les équipements

| Nom | Type | Modèle Packet Tracer |
|---|---|---|
| DIST-SW | Switch | **2960-24TT** |
| ACC-1 | Switch | **2960-24TT** |
| SRV-FICHIERS | Serveur | **Server-PT** |
| PC-1 | PC | **PC-PT** |
| PC-2 | PC | **PC-PT** |

Renomme chaque équipement (clic sur le nom sous l'icône) pour retrouver les noms ci-dessus.

## 2. Le câblage

| De | Port | Vers | Port | Câble |
|---|---|---|---|---|
| DIST-SW | GigabitEthernet0/1 | ACC-1 | GigabitEthernet0/1 | Copper Cross-Over |
| DIST-SW | GigabitEthernet0/2 | ACC-1 | GigabitEthernet0/2 | Copper Cross-Over |
| SRV-FICHIERS | FastEthernet0 | DIST-SW | FastEthernet0/1 | Copper Straight-Through |
| PC-1 | FastEthernet0 | ACC-1 | FastEthernet0/1 | Copper Straight-Through |
| PC-2 | FastEthernet0 | ACC-1 | FastEthernet0/2 | Copper Straight-Through |

## 3. Les PC (Desktop → IP Configuration)

| PC | Adresse IP | Masque | Passerelle | DNS |
|---|---|---|---|---|
| SRV-FICHIERS | 10.5.10.10 | 255.255.255.0 | 10.5.10.1 | — |
| PC-1 | 10.5.10.11 | 255.255.255.0 | 10.5.10.1 | — |
| PC-2 | 10.5.10.12 | 255.255.255.0 | 10.5.10.1 | — |

## 4. Les configurations (onglet CLI, copier-coller)

**DIST-SW** : `configs/packet-tracer/DIST-SW.txt`

```
! DIST-SW · 2960-24TT · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname DIST-SW
no ip domain-lookup
!
spanning-tree mode rapid-pvst
spanning-tree vlan 10 priority 4096
!
vlan 10
 name BUREAUX
!
interface range GigabitEthernet0/1 - 2
 description Vers ACC-1
 switchport mode trunk
 channel-group 1 mode active
!
interface Port-channel1
 description Vers ACC-1 (2 x 1 Gbit/s)
 switchport mode trunk
!
! Fa0/1 ici = Gi0/3 du lab PnetLab
interface FastEthernet0/1
 description SRV-FICHIERS
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface Vlan10
 ip address 10.5.10.1 255.255.255.0
 no shutdown
!
line con 0
 logging synchronous
!
end
write memory
```

**ACC-1** : `configs/packet-tracer/ACC-1.txt`

```
! ACC-1 · 2960-24TT · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname ACC-1
no ip domain-lookup
!
spanning-tree mode rapid-pvst
!
vlan 10
 name BUREAUX
!
interface range GigabitEthernet0/1 - 2
 description Vers DIST-SW
 switchport mode trunk
 channel-group 1 mode on
!
interface Port-channel1
 description Vers DIST-SW (2 x 1 Gbit/s)
 switchport mode trunk
!
! Fa0/1 et Fa0/2 ici = Gi0/3 et Gi1/0 du lab PnetLab
interface FastEthernet0/1
 description PC-1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface FastEthernet0/2
 description PC-2
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
!
interface Vlan10
 ip address 10.5.10.2 255.255.255.0
 no shutdown
!
line con 0
 logging synchronous
!
end
write memory
```

## 6. Vérifier le symptôme

- [ ] Attendre 1 minute que les ports des switchs passent au vert (ou à l'orange s'ils sont bloqués)
- [ ] Depuis PC-1 : ping 10.5.10.10 (SRV-FICHIERS) : noter le résultat
- [ ] Sur ACC-1 et sur DIST-SW : show etherchannel summary : noter les lettres entre parenthèses de Po1, Gi0/1 et Gi0/2

## 7. Observer comme dans la vidéo

1. Sur DIST-SW : show lacp neighbor : aucun voisin LACP tant qu'ACC-1 est en mode on
2. Après la correction (ACC-1 en mode active), sur les deux switchs : show etherchannel summary : Po1(SU), Gi0/1(P) et Gi0/2(P)
3. Depuis PC-1 : ping 10.5.10.10 : réussi

## 8. Enregistrer

*Fichier → Enregistrer sous* : `topology/INC-05.pkt`, puis préviens Claude pour l'ajouter au dépôt.

## Solution (formateur, à ne pas distribuer)

Configurations corrigées : `configs/packet-tracer/solution/`. Lignes qui changent :

**ACC-1** · à ajouter

```
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode active
```

**ACC-1** · à retirer (commande précédée de `no`)

```
interface range GigabitEthernet0/1 - 2
 channel-group 1 mode on
```
