# EbonholdFR — Traduction française pour Project Ebonhold

*[English version below](#english)*

Addon communautaire qui affiche en **français** le serveur privé WoW [Project Ebonhold](https://www.project-ebonhold.com/) (WotLK 3.3.5a, rogue-lite) : **l'interface du serveur** (fenêtres, boutons, infobulles) et les descriptions des **Echoes**, du **Soul Tree**, des **Affixes** et des **Tomes of Echo**.

> ⚠️ **Projet de fan, non officiel** — non affilié à l'équipe de Project Ebonhold. Le serveur fonctionne en anglais ; cet addon **superpose** une traduction française côté client, sans rien modifier sur le serveur.

## ✨ Ce qui est traduit (v4.0, données du 20/10/2026)
- **Interface du serveur, en direct** : Echoes / Character Progression, Soul Tree, Prestige, Objectifs (Callboard), Enclume enchantée, Hardcore / Torment, Collections, boîtes de confirmation… et les infobulles qu'elles affichent (~860 textes).
- **546 Echoes** (cartes de choix, journal, panneau de la run, liens dans le chat, recherche en français *et* en anglais).
- **940 sorts du Soul Tree** (infobulles des nœuds, y compris les nœuds « infinis »).
- **189 Affixes** (grimoire, Enclume, liens) et **190 des 194 lignes violettes** gravées sur les objets.
- **149 Tomes of Echo** et les objets « Tome of Echo: … » (123 avec leur résumé traduit, 25 avec le résumé encore en anglais).
- Les **noms** (echoes, nœuds, sorts cités) restent **en anglais**, comme le jeu les affiche.

## 🛡️ Sûr par construction
- L'addon ne traduit **que** si le texte anglais affiché correspond exactement à celui qu'il connaît (« empreinte » : texte sans couleurs, nombres remplacés par `#`). Un texte modifié par une mise à jour du serveur reste en anglais au lieu d'afficher une vieille traduction ; le texte du **patch FR** (déjà en français) n'est jamais écrasé.
- Les nombres sont repris **du texte anglais affiché** (valeurs calculées selon ton niveau, tes stats, tes cumuls).
- Aucun hook global, aucun script posé sur un bouton sécurisé de Blizzard : uniquement les fenêtres de l'addon du serveur et les infobulles.

## ⚙️ Réglages
- Le **launcher Ebonhold FR** (onglet *Français*) écrit `EbonholdFR_Reglages.lua` dans le dossier de l'addon : interface, descriptions des Echoes / du Soul Tree / des affixes, tomes, ligne « EN : nom anglais », patch FR installé. Sans ce fichier, tout est en français.
- **Patch FR installé** : les descriptions sont déjà françaises dans le jeu ; l'addon n'y touche pas et garde seulement l'interface et la ligne grise **« EN : nom anglais »** (utile quand les noms sont traduits).
- **En jeu**, le bouton minimap (icône livre) : **clic droit** = tout en anglais / tout en français, **clic gauche** = panneau d'options. Tes choix sont mémorisés ; si tu changes ensuite les réglages dans le launcher, ceux du launcher reprennent la main.

### Commandes
| Commande | Rôle |
|---|---|
| `/efr` | ouvre / ferme le panneau d'options |
| `/efr bouton` | masque / affiche le bouton minimap |
| `/efr test <id>` | montre l'anglais, le français et l'empreinte d'un echo |
| `/efr stats` | état du moteur d'interface (fenêtres repérées, textes accrochés) |
| `/efr collecte` | active / coupe la **collecte** des textes d'interface encore en anglais |
| `/efr collecte vider` | vide la collecte |
| `/efr fix` | affiche le nom du prochain PNJ de dialogue (diagnostic de la forge / du tableau) |

La collecte (désactivée par défaut) note les textes de l'interface du serveur que l'addon ne connaît pas encore dans `WTF\Account\<COMPTE>\SavedVariables\EbonholdFR.lua` (variable `EbonholdFR_Collecte`), pour compléter la traduction.

## 📥 Installation
Le plus simple : le **launcher Ebonhold FR** installe et met à jour l'addon (onglet *Français*).
À la main : copie le dossier **`EbonholdFR`** dans `World of Warcraft\Interface\AddOns\`, active **Ebonhold FR** dans la liste des AddOns, puis `/reload`. L'addon dépend de **ProjectEbonhold** (l'addon du serveur). Il remplace l'ancien addon séparé **EbonholdFRFix** (forge en français, globales manquantes du client frFR) : supprime-le s'il est encore installé.

## 🔧 Comment ça marche
- **Descriptions** : `utils.GetSpellDescription` / `GetStackedSpellDescription` / `GetSpellSearchText` (addon du serveur) ; infobulles (`SetHyperlink`, `OnTooltipSetSpell`, `OnTooltipSetItem`). Le texte complet est demandé au serveur puis le français est coupé proprement (plus de nombres manquants en fin de carte).
- **Interface** (`EbonholdFR_Interface.lua`) : les fenêtres du serveur sont repérées par leur nom (liste connue + tout nom commençant par `ProjectEbonhold`, `Ebonhold`, `skillTree`…). À leur affichage, l'addon parcourt leurs textes et accroche chaque texte une fois pour suivre ses changements. Textes exacts, phrases à valeurs (« Stacks: 3 ») et phrases faites de morceaux sont reconnus ; un texte inconnu reste en anglais.

## 🔄 Mettre à jour après un patch du serveur
1. Capture en anglais avec l'addon **`EbonholdEchoDump`** (`/echodump` puis `/reload`).
2. Lance `tools/generer_donnees_v4.py` (chemins en options, voir `--help`) : il relit la capture, le `Spell.dbc` du serveur, les traductions du launcher (`patch_fr.json`) et `ui-fr.json`, régénère `EbonholdFR_Data.lua` et `EbonholdFR_Interface_Data.lua` et affiche la couverture.
3. Tests hors jeu : `tools/tests/test_ebonholdfr_v4.py` (Python + `lupa`).

## 📁 Contenu du dépôt
```
EbonholdFR/         L'addon (Interface/AddOns)
EbonholdEchoDump/   Addon outil : exporte les textes du serveur
tools/              Générateur v4 (generer_donnees_v4.py), anciens scripts v3, tests (tools/tests)
data/               Anciennes données v3 (servent de repli pour les tomes et quelques affixes)
CHANGELOG.md        Historique des versions
```

## 🙏 Crédits
- Traduction & outils : Squall98.
- Serveur & contenu original : l'équipe de **Project Ebonhold**.

## 📜 Licence
Code de l'addon et des outils sous licence **MIT** (voir [LICENSE](LICENSE)). Les textes du jeu appartiennent à leurs auteurs respectifs (équipe Project Ebonhold).

---

<a name="english"></a>
# EbonholdFR — French translation for Project Ebonhold (English)

Community addon that shows the WoW private server [Project Ebonhold](https://www.project-ebonhold.com/) (WotLK 3.3.5a) in **French**: the **server's own interface** (windows, buttons, tooltips) and the descriptions of **Echoes**, the **Soul Tree**, **Affixes** and **Tomes of Echo**.

> ⚠️ **Unofficial fan project**, not affiliated with the Project Ebonhold team. Nothing is changed on the server; the translation is overlaid on the client.

## What is translated (v4.0, data of 2026-10-20)
- **Server interface, live**: Echoes / Character Progression, Soul Tree, Prestige, Objectives (Callboard), Enchanted Anvil, Hardcore / Torment, Collections, confirmation dialogs and their tooltips (~860 texts).
- **546 Echoes**, **940 Soul Tree spells**, **189 Affixes** (+ 190 of the 194 engraved item lines), **149 Tomes** and the "Tome of Echo" items.
- Names (echoes, nodes, quoted spells) stay in **English**, as the game shows them.

## Safe by design
- A text is translated **only** if the English text on screen matches the expected one ("fingerprint": text without colours, numbers replaced by `#`). Text changed by a server update stays in English; the French patch's text is never overwritten.
- Numbers are taken **from the English text on screen** (values computed from your level, stats and stacks).
- No global hook, no script set on a secure Blizzard button: only the server addon's windows and the tooltips are touched.

## Settings and commands
- The **Ebonhold FR launcher** (*Français* tab) writes `EbonholdFR_Reglages.lua` in the addon folder; without it everything is in French. With the **French patch** installed, descriptions are left alone (they are already French) and only the interface and the grey **"EN : English name"** line remain.
- In game: minimap button (right-click = all English / all French, left-click = options). In-game choices are remembered until the launcher changes its settings.
- `/efr` (options), `/efr bouton`, `/efr test <id>`, `/efr stats`, `/efr collecte` (collect untranslated interface texts into `EbonholdFR_Collecte`, off by default), `/efr collecte vider`, `/efr fix`.

## Install / update
Use the **Ebonhold FR launcher**, or copy the **`EbonholdFR`** folder into `Interface\AddOns\` and `/reload`. Requires **ProjectEbonhold**. Replaces the old separate **EbonholdFRFix** addon (remove it). After a server patch: capture with `EbonholdEchoDump`, run `tools/generer_donnees_v4.py`, then `tools/tests/test_ebonholdfr_v4.py`.

## Credits and licence
Translation & tools: Squall98. Original server & content: the **Project Ebonhold** team. Code under the **MIT** licence ([LICENSE](LICENSE)); game texts belong to their authors.
