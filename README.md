# EbonholdFR — Traduction française pour Project Ebonhold

Addon communautaire qui affiche en **français** les descriptions du serveur privé WoW [Project Ebonhold](https://www.project-ebonhold.com/) (WotLK 3.3.5a, rogue-lite) : **Echoes**, **Skill Tree**, **Affixes** et **Tomes of Echo**.

> ⚠️ **Projet de fan, non officiel** — non affilié à l'équipe de Project Ebonhold. Le serveur fonctionne en anglais ; cet addon **superpose** une traduction française côté client, sans rien modifier sur le serveur.

## ✨ Ce qui est traduit
- **526 Echoes** — Echo Browser, panneau d'echoes équipés, **liens dans le chat**.
- **728 nœuds du Skill Tree** (Soul Ash Tree).
- **165 Affixes** — Enclume Enchantée, **liens chat**, **affixe gravé sur un objet** (ligne violette) et **grimoire**.
- **128 Tomes of Echo** — tooltip d'objet (texte « Use: … » + description courte).
- Les **noms** (echoes, nœuds, sorts/ressources cités) sont **gardés en anglais**, par choix — seules les phrases de description passent en français.
- **Echoes dynamiques par classe** : pour les echoes à variantes (Stonefist Barrage, Ember Spark, Unstable Infusion, Temporal Pressure, Corrosive Breath, Arcane Bombardment), l'addon détecte ta **classe** et affiche **ta** variante — là où le jeu (même en anglais) montre la variante canonique à tout le monde.

## 🎛️ En jeu : bouton minimap & bascule FR/EN
Un **bouton sur la minimap** (icône livre) donne le contrôle complet sans rien désinstaller :
- **Clic droit** : bascule instantanément entre **français** et **texte d'origine en anglais** (l'icône se grise en mode anglais).
- **Clic gauche** : ouvre un **panneau d'options** avec l'interrupteur maître et l'activation **par catégorie** (Echoes / Skill Tree / Affixes / Tomes), plus un bouton *Recharger l'interface*.
- Le bouton se **déplace** autour de la minimap ; position et préférences sont **sauvegardées**.
- Commandes : `/frmenu` (panneau), `/frbouton` (masquer/afficher le bouton).

> Les infobulles changent de langue au survol suivant ; les fenêtres déjà ouvertes se mettent à jour à leur réouverture (ou via *Recharger l'interface*).

## 📥 Installation
1. Télécharge le **`EbonholdFR-vX.Y.zip`** de la dernière [release](../../releases), ou le dépôt (**Code → Download ZIP**).
2. Copie le dossier **`EbonholdFR`** dans :
   `World of Warcraft\Interface\AddOns\`
3. Lance le jeu, à l'écran de sélection des personnages clique **AddOns** et active **Ebonhold FR** (coche « Load out of date AddOns » si besoin).
4. En jeu, tape **`/reload`**. Un message confirme `Traduction active`.

> L'addon dépend de l'addon serveur **ProjectEbonhold** (installé automatiquement via le launcher du serveur).

## 🔧 Comment ça marche
EbonholdFR **hooke** les fonctions/tooltips du serveur et réinjecte la version française, en réutilisant les nombres calculés par le serveur (les valeurs `@token@` restent correctes selon votre niveau / cumuls) :
- `utils.GetSpellDescription` / `utils.GetStackedSpellDescription` → descriptions d'echoes (browser + panneau équipé).
- `SetHyperlink` (GameTooltip / ItemRefTooltip / tooltips du Skill Tree) → nœuds du Skill Tree + liens chat (echoes & affixes).
- `OnTooltipSetItem` → affixes gravés sur les objets + Tomes of Echo.
- `OnTooltipSetSpell` → affixes affichés dans le grimoire.

Les traductions vivent dans **`data/`** (voir ci-dessous), puis sont compilées en `EbonholdFR/EbonholdFR_Data.lua`.

## 🤝 Contribuer / corriger une traduction
- **Echoes & Skill Tree** : `data/fr_translations.json` (clé = texte anglais, valeur = texte français, dans `descs`).
- **Affixes** : `data/affixes_fr.json` (id → FR).
- **Tomes** : `data/tomes_fr.json` (nom d'echo → ligne « Utiliser : … » FR).

⚠️ Garde les marqueurs `@...@` (remplacés par des nombres en jeu) et les codes couleur `|cff...|r`. Les **noms de sorts/ressources/dots restent en anglais**.

Régénère ensuite le fichier de l'addon :
```bash
cd tools
python gen_fr_data.py
```
Recharge en jeu (`/reload`) et propose ta correction via une Pull Request.

## 🔄 Mettre à jour après un patch du serveur
1. Installe l'addon **`EbonholdEchoDump`** (fourni ici), connecte-toi, ouvre l'Enclume / la banque de tomes si besoin, tape `/echodump` puis `/reload`.
2. Le dump est écrit dans `WTF\Account\<COMPTE>\SavedVariables\EbonholdEchoDump.lua` — copie-le dans `data/`.
3. Régénère les données de référence et l'addon avec les scripts de `tools/` (voir `tools/README.md`).

## 📁 Contenu du dépôt
```
EbonholdFR/         L'addon à installer (Interface/AddOns)
EbonholdEchoDump/   Addon outil : exporte les textes du serveur (echoes, skill tree, affixes, tomes)
tools/              Pipeline de traduction (Python 3, dépend de slpp pour le parsing du dump)
data/               Textes anglais extraits + traductions FR (fr_translations.json, affixes_fr.json, tomes_fr.json)
CHANGELOG.md        Historique des versions
```

## 🙏 Crédits
- Traduction & outils : Squall98.
- Serveur & contenu original : l'équipe de **Project Ebonhold**.

## 📜 Licence
Code de l'addon et des outils sous licence **MIT** (voir [LICENSE](LICENSE)).
Les textes du jeu appartiennent à leurs auteurs respectifs (équipe Project Ebonhold).
