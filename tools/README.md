# Pipeline de traduction

Scripts Python 3 qui transforment les traductions (`../data/`) en fichier de données de l'addon (`../EbonholdFR/EbonholdFR_Data.lua`).

## Pré-requis
```bash
pip install slpp   # uniquement pour parser un dump in-game
```

## Version 4 (EbonholdFR 4.0) — à utiliser désormais
| Script | Rôle |
|--------|------|
| **`generer_donnees_v4.py`** | Produit `EbonholdFR_Data.lua` (descriptions : empreinte du texte anglais -> gabarit FR, noms anglais) et `EbonholdFR_Interface_Data.lua` (interface du serveur). Entrées : capture anglaise (`/echodump`), `Spell.dbc` et `SpellItemEnchantment.dbc` du serveur, traductions du launcher (`patch_fr.json`), `ui-fr.json` (sinon un petit échantillon intégré), anciennes données `data/` en repli. Bibliothèque standard seulement. `--help` pour les chemins ; `--rapport x.json` pour le détail. |
| **`tests/test_ebonholdfr_v4.py`** | Tests hors jeu (LuaJIT via `lupa`, faux environnement WoW `tests/faux_wow.lua`) : chargement à vide, empreintes Lua = Python, descriptions, infobulles, moteur d'interface, collecte, réglages, coûts. |

```bash
python -I generer_donnees_v4.py            # régénère les deux fichiers de données
python -I tests/test_ebonholdfr_v4.py      # (Python avec lupa installé)
```

Les scripts ci-dessous (v3) restent pour l'historique. ⚠️ Ne plus lancer `gen_fr_data.py` : il réécrirait
`EbonholdFR_Data.lua` dans l'ancien format, que l'addon 4.0 ne lit plus.

## Le script principal (v3)
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
