# LLD · SEC-01 · Publication d’un serveur web en DMZ derrière un Palo Alto

## 1. Objet

Publier le serveur web 192.168.50.10 (DMZ) sur Internet à l’adresse 203.0.113.10, en HTTP uniquement, sans ouvrir le reste de la DMZ.

## 2. Zones et interfaces

| Interface | Zone | Adresse | Rôle |
|---|---|---|---|
| ethernet1/1 | untrust | 203.0.113.2/24 | Lien opérateur (passerelle 203.0.113.1) |
| ethernet1/2 | dmz | 192.168.50.1/24 | Serveurs publiés |
| ethernet1/3 | trust | 10.10.10.1/24 | LAN interne |

Routeur virtuel `default`, route par défaut vers 203.0.113.1.

## 3. Objets

| Objet | Valeur |
|---|---|
| WEB-PRIVE | 192.168.50.10/32 |
| WEB-PUBLIC | 203.0.113.10/32 |

## 4. NAT

| Règle | De → vers | Destination d’origine | Service | Traduction |
|---|---|---|---|---|
| DNAT-WEB | untrust → untrust | WEB-PUBLIC | service-http | destination → WEB-PRIVE |
| SNAT-LAN | trust → untrust | any | any | source → IP de ethernet1/1 (PAT) |

Pour un NAT de destination, la zone de destination de la règle NAT est celle de l’adresse **publique** (untrust).

## 5. Règles de sécurité

| Règle | De → vers | Destination | Service | Action |
|---|---|---|---|---|
| DMZ-WEB | untrust → dmz | **WEB-PUBLIC (avant NAT)** | service-http | allow |
| LAN-INTERNET | trust → untrust | any | application-default | allow |

**Règle de conception :** une règle de sécurité utilise l’**adresse avant NAT** et la **zone après NAT**. Jamais `any` en destination vers la DMZ.

## 6. Vérifications

```
test security-policy-match from untrust to dmz source 198.51.100.20 destination 203.0.113.10 protocol 6 destination-port 80
show running nat-policy
show running security-policy
show session all filter destination 203.0.113.10
```
