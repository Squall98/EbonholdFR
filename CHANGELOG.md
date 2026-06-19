# Changelog

Toutes les versions notables d'EbonholdFR. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/).

## [3.1] — 2026-06-19

### Corrigé / Ajouté
- **Echoes dynamiques affichés selon TA classe.** Pour les 6 echoes à variantes (Stonefist Barrage, Ember Spark, Unstable Infusion, Temporal Pressure, Corrosive Breath, Arcane Bombardment), le serveur affiche la variante **canonique (Guerrier)** à tout le monde dans la carte d'offre — même en anglais. L'addon détecte désormais la **classe du joueur** (`UnitClass`) et affiche **la bonne variante** : un Mage voit « Cone of Cold / Mana », un Voleur « Énergie », un Chevalier de la mort « Runes », etc.
- C'est un comportement que **même la version anglaise du jeu n'a pas** : la traduction FR devient plus juste que l'original sur ces echoes.
- **Affixes « Unique »** : la ligne d'un affixe gravé se terminant par « . Unique. » est maintenant traduite (avant, seul « . Stacks with other ranks. » l'était).
- **Tous les rangs d'affixes traduits** : repli par **motif** — n'importe quel pourcentage/rang d'un effet est traduit, même un rang qui n'avait pas été capturé au dump (ex. « Increases your damage and healing done by 5% »). 44 familles d'effets couvertes automatiquement.
- **Retour à la ligne dans le Skill Tree** : les descriptions longues des nœuds (ex. « Last Resort ») s'affichaient sur une seule ligne illisible ; elles sont désormais **découpées en plusieurs lignes**.

### Notes
- Couverture echoes dynamiques : 10 classes pour 5 de ces echoes ; Unstable Infusion n'existe que pour 8 classes côté serveur (pas de variante Mage/Paladin), géré en conséquence.
- Repères techniques : table `dynFR` (echo → classe → texte) + table `affixEffectSkel` (motif → gabarit), générées par `tools/gen_fr_data.py` ; hooks `dynDesc`, `frAffixPattern`, `wrapText`.

## [3.0] — 2026-06-19

### Ajouté
- **Bouton sur la minimap** (icône livre) : déplaçable autour du cercle, sa position est sauvegardée.
  - **Clic gauche** : ouvre le panneau d'options.
  - **Clic droit** : bascule rapide **FR ⇄ EN** (l'icône se grise en mode anglais).
- **Panneau d'options** :
  - **Interrupteur maître** pour repasser à tout moment au **texte d'origine en anglais**.
  - **Activation par catégorie** : Echoes, Skill Tree, Affixes, Tomes (chacune indépendante).
  - Bouton **Recharger l'interface** pour appliquer le changement aux fenêtres déjà ouvertes.
- **Sauvegarde des préférences** entre les sessions (`SavedVariables`).
- Commandes : `/frmenu` (panneau) et `/frbouton` (masquer/afficher le bouton minimap).

### Corrigé
- **Contenu dynamique par classe (livraison effective)** : la correction annoncée en 2.0 (chaque variante de classe affiche son **bon** sort/ressource/dot — Auto Shot, Lightning Bolt, Crusader Strike, Runes, etc.) n'était en réalité **pas incluse** dans les fichiers de la release 2.0. Elle est désormais **bien présente** dans les données livrées. Si vous voyiez encore « Tir automatique » sur des echoes d'autres classes, c'est corrigé.

### Notes
- Les **infobulles** changent de langue instantanément (au survol suivant). Les **fenêtres déjà ouvertes** (Echoes Browser…) prennent en compte le changement à leur réouverture, ou via le bouton *Recharger l'interface*.

## [2.0] — 2026-06-19

### Ajouté
- **Affixes (165)** traduits **partout** où ils apparaissent :
  - Enclume Enchantée (panneau d'affixes)
  - Liens d'affixes dans le **chat**
  - Affixe **gravé sur un objet** (la ligne violette du tooltip), y compris sur l'objet équipé/dans les sacs
  - **Grimoire** (spellbook)
- **Tomes of Echo (128)** traduits : la phrase « Use: Grants this character… » et la **description courte** de chaque tome (le nom de l'echo reste en anglais).
- **Liens d'echoes dans le chat** : la description s'affiche en français au survol/clic du lien.
- Deux nouveaux systèmes de hook : `OnTooltipSetItem` (affixes gravés + tomes) et `OnTooltipSetSpell` (grimoire).

### Corrigé
- **Contenu dynamique par classe** : 6 echoes (Stonefist Barrage, Ember Spark, Unstable Infusion, Temporal Pressure, Corrosive Breath, Arcane Bombardment) affichaient le texte d'**une seule classe** pour toutes les variantes. Chaque variante de classe a désormais sa **bonne** traduction (sorts/ressources/dots gardés en anglais, structure en français).
- **Troncature** : les descriptions françaises un peu longues n'étaient plus coupées (~200 caractères) ; elles s'affichent en entier (le tooltip passe à la ligne).
- Petites corrections de tournures et de grammaire.

### Notes
- Dans un **lien chat**, les valeurs apparaissent sous forme de formule brute `@sp…@` — c'est identique à l'anglais (le tooltip d'un lien n'est pas résolu hors contexte de classe).
- Le **shift-click** pour partager un echo nécessite d'avoir la barre de chat ouverte (limitation du code serveur sur WoW 3.3.5a, indépendante de cet addon).

## [1.0] — 2026-06-18

### Ajouté
- Première version publique.
- **526 Echoes** traduits (Echo Browser + panneau d'echoes équipés).
- **728 nœuds du Skill Tree** traduits.
- Outil **EbonholdEchoDump** pour exporter les textes du serveur.
- Pipeline de traduction Python (`tools/`) et données sources (`data/`).
- Principe : **noms en anglais, descriptions en français.**
