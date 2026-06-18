# Pipeline de traduction

Scripts Python 3 qui transforment la traduction (`../data/fr_translations.json`) en fichier de données de l'addon (`../EbonholdFR/EbonholdFR_Data.lua`).

## Pré-requis
```bash
pip install slpp
```
(slpp n'est nécessaire que pour `parse_dump.py`.)

## Fichiers
| Script | Rôle |
|--------|------|
| `gen_data.py` | **Le plus important.** Lit `data/fr_translations.json` + `data/*-dump.json` → écrit `EbonholdFR/EbonholdFR_Data.lua`. À lancer après toute modif des traductions. |
| `build_translations.py` | Auto-traduit les **structures rigides récurrentes** (gains de stats, résistances, Bane/Slayer, familles de nœuds à rangs, etc.) et les ajoute à `fr_translations.json`. Utile pour dégrossir du nouveau contenu. Ne touche pas aux traductions manuelles existantes. |
| `parse_dump.py` | Régénère `data/echoes-dump.json` + `data/skilltree-dump.json` à partir d'un dump in-game (addon `EbonholdEchoDump`). Pour capturer du nouveau contenu. |

## Données (`../data/`)
- `fr_translations.json` — **la traduction** : `{ "names": {...}, "descs": { "<texte EN>": "<texte FR>" } }`. Seules les `descs` sont utilisées par l'addon (les noms restent en anglais). Le matching ignore les retours à la ligne et le suffixe « Replace … (Rank N) » des nœuds.
- `echoes-dump.json` / `skilltree-dump.json` — textes anglais de référence (spellId → nom + description), extraits du jeu.

## Notes sur les traductions
- **Garder** les `@...@` (remplacés par des nombres en jeu) et les codes couleur `|cff........|r`.
- Pour les echoes à plusieurs rangs (même phrase, nombre différent), une seule traduction par famille suffit : l'addon réinjecte le bon nombre à chaque rang.
