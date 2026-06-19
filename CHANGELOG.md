# Changelog

Toutes les versions notables d'EbonholdFR. Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/).

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
