# Pipeline de traduction

Scripts Python 3 qui transforment les traductions (`../data/`) en fichier de données de l'addon (`../EbonholdFR/EbonholdFR_Data.lua`).

## Pré-requis
```bash
pip install slpp   # uniquement pour parser un dump in-game
```

## Le script principal
| Script | Rôle |
|--------|------|
| **`gen_fr_data.py`** | **Le plus important.** Lit toutes les sources FR (`fr_translations.json`, `affixes_fr.json`, `affix_effect_fr.json`, `tomes_fr.json`) + les dumps EN, et écrit `../EbonholdFR/EbonholdFR_Data.lua`. À lancer après **toute** modif de traduction. |

## Scripts par contenu
| Script | Rôle |
|--------|------|
| `build_fr_translations.py` | Auto-traduit les **structures rigides récurrentes** (gains de stats, résistances, etc.) et les ajoute à `fr_translations.json`. Ne touche pas aux traductions manuelles. |
| `parse_affixes.py` / `tr_affixes.py` | Extrait les affixes d'un dump → `affixes-dump.json`, puis génère `affixes_fr.json` / `affix_effect_fr.json` (3 préfixes + 67 familles d'effets). |
| `parse_tomes.py` / `tr_tomes.py` | Extrait les Tomes of Echo d'un dump → `tome_items.json`, puis génère `tomes_fr.json` (128 blurbs traduits). |
| `fix_dynamic.py` | Corrige les echoes **multi-variantes de classe** : traduit chaque variante séparément (sorts/ressources en anglais). |

## Données (`../data/`)
- `fr_translations.json` — traduction des **echoes + skill tree** : `{ "descs": { "<texte EN>": "<texte FR>" } }`. Le matching ignore les retours à la ligne.
- `affixes_fr.json` / `affix_effect_fr.json` — traductions des affixes (par id, et par effet seul pour les objets gravés).
- `tomes_fr.json` — traduction des tomes (nom d'echo → ligne « Utiliser : … »).
- `*-dump.json` / `*_items.json` — textes anglais de référence extraits du jeu.

## Workflow type
```bash
# après avoir édité une traduction (fr_translations.json / affixes_fr.json / tomes_fr.json) :
python gen_fr_data.py
# puis /reload en jeu
```

## Notes
- **Garder** les `@...@` (remplacés par des nombres en jeu) et les codes couleur `|cff........|r`.
- Les **noms** de sorts/ressources/dots restent en **anglais**.
- Pour capturer du nouveau contenu : addon `EbonholdEchoDump` → `/echodump` → `/reload`, copier le `.lua` SavedVariables dans `../data/`, puis relancer les `parse_*` / `tr_*` concernés.
