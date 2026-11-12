# DEB-01 · Construire le lab dans Packet Tracer

**Switch ou routeur : qui fait quoi ?** · Packet Tracer 8.x · 5 à 10 minutes. Fiche générée par `scripts/make_pt_kit.py`.

## 1. Les équipements

| Nom | Type | Modèle Packet Tracer |
|---|---|---|
| R1 | Routeur | **2911** |
| SW1 | Switch | **2960-24TT** |
| SW2 | Switch | **2960-24TT** |
| PC1 | PC | **PC-PT** |
| PC3 | PC | **PC-PT** |
| PC2 | PC | **PC-PT** |

Renomme chaque équipement (clic sur le nom sous l'icône) pour retrouver les noms ci-dessus.

## 2. Le câblage

| De | Port | Vers | Port | Câble |
|---|---|---|---|---|
| PC1 | FastEthernet0 | SW1 | FastEthernet0/1 | Copper Straight-Through |
| PC3 | FastEthernet0 | SW1 | FastEthernet0/3 | Copper Straight-Through |
| SW1 | GigabitEthernet0/1 | R1 | GigabitEthernet0/0 | Copper Straight-Through |
| R1 | GigabitEthernet0/1 | SW2 | GigabitEthernet0/1 | Copper Straight-Through |
| PC2 | FastEthernet0 | SW2 | FastEthernet0/1 | Copper Straight-Through |

## 3. Les PC (Desktop → IP Configuration)

| PC | Adresse IP | Masque | Passerelle |
|---|---|---|---|
| PC1 | 192.168.10.10 | 255.255.255.0 | 192.168.10.1 |
| PC3 | 192.168.10.30 | 255.255.255.0 | 192.168.10.1 |
| PC2 | 192.168.20.20 | 255.255.255.0 | 192.168.20.1 |

## 4. Les configurations (onglet CLI, copier-coller)

**R1** : `configs/packet-tracer/R1.txt`

```
! R1 · 2911 · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname R1
interface GigabitEthernet0/0
 description LAN 192.168.10.0/24 vers SW1
 ip address 192.168.10.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/1
 description LAN 192.168.20.0/24 vers SW2
 ip address 192.168.20.1 255.255.255.0
 no shutdown
end
write memory
```

**SW1** : `configs/packet-tracer/SW1.txt`

```
! SW1 · 2960-24TT · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname SW1
end
write memory
```

**SW2** : `configs/packet-tracer/SW2.txt`

```
! SW2 · 2960-24TT · à coller tel quel dans l'onglet CLI
no
enable
configure terminal
hostname SW2
end
write memory
```

## 6. Vérifier

- [ ] Tous les voyants des câbles sont verts (attendre 30 s que les ports des switchs passent en vert)
- [ ] Depuis PC1 : ping 192.168.10.30 (PC3, même réseau) → réussi
- [ ] Depuis PC1 : ping 192.168.20.20 (PC2, autre réseau) → réussi (le premier essai peut échouer, le temps de l'ARP)
- [ ] Sur R1 : show ip route → deux réseaux connectés (C) 192.168.10.0/24 et 192.168.20.0/24

## 7. Observer comme dans la vidéo

1. Passe en mode Simulation (en bas à droite), filtre sur ICMP et ARP.
2. Depuis PC1, ping 192.168.10.30 : la requête ARP part sur tous les ports de SW1 (l'inondation), puis la réponse revient directement.
3. Sur SW1 : show mac-address-table → PC1 et PC3 y sont, avec leur port.
4. Depuis PC1, ping 192.168.20.20 : clique sur l'enveloppe à chaque saut. Entre PC1 et R1, la MAC de destination est celle de R1 G0/0 ; entre R1 et PC2, c'est celle de PC2. L'IP de destination reste 192.168.20.20 du début à la fin.

## 8. Enregistrer

*Fichier → Enregistrer sous* : `topology/DEB-01.pkt`, puis préviens Claude pour l'ajouter au dépôt.
