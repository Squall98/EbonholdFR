# EbonholdFR — Traduction française pour Project Ebonhold

Addon communautaire qui affiche en **français** les descriptions des **Echoes** et des **nœuds du Skill Tree** du serveur privé WoW [Project Ebonhold](https://www.project-ebonhold.com/) (WotLK 3.3.5a, rogue-lite).

> ⚠️ **Projet de fan, non officiel** — non affilié à l'équipe de Project Ebonhold. Le serveur fonctionne en anglais ; cet addon **superpose** une traduction française côté client, sans rien modifier sur le serveur.

## ✨ Ce qui est traduit
- **526 descriptions d'Echoes** (dans l'Echo Browser **et** le panneau d'echoes équipés en jeu).
- **728 descriptions de nœuds du Skill Tree** (Soul Ash Tree).
- Les **noms** (echoes, nœuds, sorts cités dans les descriptions) sont **gardés en anglais**, par choix — seules les phrases de description passent en français.

## 📥 Installation
1. Télécharge ce dépôt (bouton **Code → Download ZIP**), ou un fichier release.
2. Copie le dossier **`EbonholdFR`** dans :
   `World of Warcraft\Interface\AddOns\`
3. Lance le jeu, et à l'écran de sélection des personnages, clique **AddOns** et active **Ebonhold FR** (coche « Load out of date AddOns » si besoin).
4. En jeu, tape **`/reload`**. Un message confirme `Traduction active`.

> L'addon dépend de l'addon serveur **ProjectEbonhold** (installé automatiquement via le launcher du serveur).

## 🔧 Comment ça marche
Le serveur construit les descriptions via des fonctions Lua globales. EbonholdFR les **hooke** et réinjecte la version française, en réutilisant les nombres calculés par le serveur (les valeurs `@token@` restent correctes selon votre niveau / cumuls) :
- `utils.GetSpellDescription` → descriptions d'echoes (Echo Browser).
- `utils.GetStackedSpellDescription` → descriptions d'echoes équipés/cumulés (panneau en jeu).
- Tooltips custom `skillTreeCurrentRankTooltip` / `skillTreeNextRankTooltip` → nœuds du Skill Tree.

Les traductions vivent dans **`data/fr_translations.json`** (clé = texte anglais, valeur = texte français), puis sont compilées en `EbonholdFR/EbonholdFR_Data.lua`.

## 🤝 Contribuer / corriger une traduction
1. Ouvre **`data/fr_translations.json`** et modifie/ajoute la traduction voulue (dans `descs`).
   - ⚠️ Garde les marqueurs `@...@` (ils sont remplacés par des nombres en jeu) et les codes couleur `|cff...|r`.
2. Régénère le fichier de l'addon :
   ```bash
   cd tools
   python gen_data.py
   ```
3. Recharge en jeu (`/reload`) et propose ta correction via une Pull Request.

`tools/build_translations.py` peut aussi auto-traduire les structures simples récurrentes (gains de stats, etc.) — voir `tools/README.md`.

## 🔄 Mettre à jour après un patch du serveur
Quand le serveur ajoute des echoes / nœuds :
1. Installe l'addon **`EbonholdEchoDump`** (fourni ici), connecte-toi, tape `/echodump` puis `/reload`.
2. Régénère les données de référence puis l'addon :
   ```bash
   cd tools
   python parse_dump.py "<...>\WTF\Account\<COMPTE>\SavedVariables\EbonholdEchoDump.lua"
   python build_translations.py   # (optionnel) auto-traduit les nouveaux patterns simples
   python gen_data.py
   ```
3. Traduis les nouveautés restantes dans `data/fr_translations.json`, puis `gen_data.py`.

## 📁 Contenu du dépôt
```
EbonholdFR/         L'addon à installer (Interface/AddOns)
EbonholdEchoDump/   Addon outil : exporte les textes du serveur (echoes + skill tree)
tools/              Pipeline de traduction (Python 3, dépend de slpp)
data/               Textes anglais extraits + fr_translations.json (la traduction)
```

## 🙏 Crédits
- Traduction & outils : la communauté.
- Serveur & contenu original : l'équipe de **Project Ebonhold**.

## 📜 Licence
Code de l'addon et des outils sous licence **MIT** (voir [LICENSE](LICENSE)).
Les textes du jeu appartiennent à leurs auteurs respectifs (équipe Project Ebonhold).
