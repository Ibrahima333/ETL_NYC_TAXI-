# Data Quality Report — NYC Taxi Analytics

## 1. Informations générales

| Élément | Valeur |
|---|---|
| Source | NYC Taxi & Limousine Commission (TLC) |
| Fichier analysé | `yellow_tripdata_2026-01.parquet` |
| Période | Janvier 2026 |
| Nombre de lignes | 3 724 889 |
| Nombre de colonnes initiales | 20 |
| Outil d'exploration | Python / Pandas |
| Statut | Exploration initiale |

## 2. Valeurs manquantes

Cinq colonnes contiennent des valeurs manquantes :

| Colonne | Nombre de valeurs manquantes |
|---|---:|
| `passenger_count` | 1 088 058 |
| `RatecodeID` | 1 088 058 |
| `store_and_fwd_flag` | 1 088 058 |
| `congestion_surcharge` | 1 088 058 |
| `Airport_fee` | 1 088 058 |

Observation :

- Les cinq colonnes présentent exactement le même nombre de valeurs manquantes.
- Les mêmes 1 088 058 lignes ont simultanément leurs cinq valeurs manquantes.
- Aucune de ces colonnes ne doit être automatiquement remplie par zéro.
- La cause de cette absence reste à investiguer.

## 3. Doublons

Résultat du contrôle :

```python
df.duplicated().sum()
```

Résultat : `0`

Aucun doublon exact sur l'ensemble des colonnes n'a été détecté.

Attention : cela n'exclut pas la présence de plusieurs enregistrements associés à une même course ou opération.

## 4. Anomalies temporelles

Une colonne calculée a été créée :

```python
df["trip_duration"] = (
    df["tpep_dropoff_datetime"]
    - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60
```

Résultats :

| Contrôle | Nombre |
|---|---:|
| Durées négatives | 1 |
| Durées nulles | 45 069 |

Une durée négative signifie que l'heure de dépose est antérieure à l'heure de prise en charge.

Les durées nulles nécessitent une investigation : certaines courses présentent une distance et un montant positifs malgré une durée nulle.

## 5. Anomalies de distance

Résultats :

| Contrôle | Nombre |
|---|---:|
| Distances négatives | 0 |
| Distances nulles | 125 738 |

Les distances nulles représentent environ 3,37 % des enregistrements.

Parmi ces courses :

- 43 905 ont une durée positive et une distance positive est impossible puisque leur distance est nulle.
- 1 164 ont également une durée nulle.
- 92 717 ont simultanément `RatecodeID` manquant et `payment_type = 0`.

Les courses à distance nulle ne doivent pas être automatiquement supprimées.

## 6. Analyse des fournisseurs

Taux de courses à distance nulle par fournisseur :

| VendorID | Total courses | Distance nulle | Taux |
|---:|---:|---:|---:|
| 1 | 710 425 | 9 953 | 1,40 % |
| 2 | 2 965 742 | 114 960 | 3,88 % |
| 6 | 4 017 | 0 | 0 % |
| 7 | 44 705 | 825 | 1,85 % |

Le fournisseur 2 présente le taux le plus élevé.

Cette observation ne permet pas, à elle seule, de conclure à un problème chez ce fournisseur.

## 7. Analyse des types de paiement

Taux de courses à distance nulle par type de paiement :

| Payment type | Signification | Distance nulle |
|---:|---|---:|
| 0 | Flex Fare | 8,52 % |
| 1 | Credit card | 0,81 % |
| 2 | Cash | 2,43 % |
| 3 | No charge | 19,47 % |
| 4 | Dispute | 6,90 % |

Le type de paiement 3 présente le taux le plus élevé.

### Focus sur les courses No charge avec distance nulle

Nombre de courses : 3 240.

| Catégorie de total_amount | Nombre |
|---|---:|
| Positif | 2 562 |
| Négatif | 609 |
| Nul | 69 |

Les courses No charge ne présentent donc pas nécessairement un montant total nul.

### Groupes d'enregistrements similaires

Une recherche a été réalisée sur les colonnes :

- `tpep_pickup_datetime`
- `tpep_dropoff_datetime`
- `PULocationID`
- `DOLocationID`

Résultats :

| Indicateur | Résultat |
|---|---:|
| Lignes appartenant à des groupes similaires | 1 122 |
| Groupes identifiés | 561 |
| Groupes dont la somme de `fare_amount` est nulle | 561 |
| Groupes dont la somme de `total_amount` est nulle | 561 |

Les montants positifs et négatifs s'annulent dans chacun des 561 groupes.

Hypothèse : ces enregistrements pourraient correspondre à des opérations de correction ou d'ajustement financier.

Cette hypothèse doit être confirmée avant toute décision de transformation.

## 8. Règles de qualité envisagées

| Identifiant | Contrôle | Décision actuelle |
|---|---|---|
| DQ01 | `trip_distance >= 0` | Contrôle à automatiser |
| DQ02 | `trip_duration >= 0` | Contrôle à automatiser |
| DQ03 | Vérifier les valeurs manquantes | Documenter et investiguer |
| DQ04 | Vérifier les codes de paiement | Contrôler selon le dictionnaire TLC |
| DQ05 | Vérifier les codes tarifaires | Contrôler selon le dictionnaire TLC |
| DQ06 | Identifier les groupes financiers qui s'annulent | Préserver et investiguer |
| DQ07 | Détecter les doublons exacts | Contrôle à automatiser |

## 9. Décisions de traitement

À ce stade :

- Aucune ligne n'a été supprimée.
- Aucune valeur manquante n'a été remplacée.
- Aucun montant négatif n'a été corrigé.
- Les données originales doivent être conservées dans la couche Bronze.
- Les règles de transformation seront définies avant leur application dans la couche Silver.

## 10. Prochaine étape

Construire le processus d'ingestion des fichiers mensuels NYC TLC vers le Data Lake Bronze.

Les contrôles de qualité documentés ici seront progressivement automatisés avec PySpark dans la couche Silver.