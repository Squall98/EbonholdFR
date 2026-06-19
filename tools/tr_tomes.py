# -*- coding: utf-8 -*-
import json

ti = json.load(open(r"../data\tome_items.json", encoding="utf-8"))

def norm(s):
    return (s or "").replace("’", "'").replace("‘", "'").strip()

# EN blurb (apostrophes droites) -> FR blurb
BLURB_FR = {
 "Your damage-over-time effects now benefit from Haste.": "Vos effets de dégâts sur la durée bénéficient maintenant de la Hâte.",
 "Each unique Echo increases your damage.": "Chaque Echo unique augmente vos dégâts.",
 "You can dual wield weapons.": "Vous pouvez manier deux armes.",
 "Increases spell damage while making spells cost much more mana.": "Augmente les dégâts des sorts, mais ils coûtent beaucoup plus de mana.",
 "Different offensive casts build stacking bonus damage.": "Des sorts offensifs différents accumulent un bonus de dégâts.",
 "Converts part of your Armor into Spell Power.": "Convertit une partie de votre Armure en puissance des sorts.",
 "Increases mage area damage against large groups.": "Augmente les dégâts de zone du mage contre les grands groupes.",
 "Spells and abilities can make your next key spell instant.": "Vos sorts et capacités peuvent rendre votre prochain sort clé instantané.",
 "Increases Arcane Resistance.": "Augmente la résistance aux Arcanes.",
 "Dealing Fire, Frost, and Arcane grants bonus damage.": "Infliger des dégâts de Feu, de Givre et des Arcanes accorde un bonus de dégâts.",
 "You can equip all armor types.": "Vous pouvez équiper tous les types d'armure.",
 "Critical Strike Rating increases your critical strike damage.": "Le score de critique augmente vos dégâts critiques.",
 "Increases warrior area damage against large groups.": "Augmente les dégâts de zone du guerrier contre les grands groupes.",
 "Increases your spell power when fighting Beasts.": "Augmente votre puissance des sorts contre les Bêtes.",
 "Increases your attack power when fighting Beasts.": "Augmente votre puissance d'attaque contre les Bêtes.",
 "Increases death knight area damage against large groups.": "Augmente les dégâts de zone du chevalier de la mort contre les grands groupes.",
 "Fire damage builds Brittle, increasing crit chance and causing a fiery shatter.": "Les dégâts de Feu accumulent Fragilité, augmentant les chances de critique et provoquant un éclatement enflammé.",
 "Your attacks build Searing Cinders that trigger Deep Breath.": "Vos attaques accumulent des Braises ardentes qui déclenchent Profonde inspiration.",
 "When you take damage while below 50% health, you spray webs, dealing Nature damage to nearby enemies and stunning them.": "Quand vous subissez des dégâts sous 50% de santé, vous projetez des toiles, infligeant des dégâts de Nature aux ennemis proches et les étourdissant.",
 "Killing an enemies summon a Servant of the Lich King fighting for you.": "Tuer un ennemi invoque un Serviteur du Roi-liche qui combat pour vous.",
 "Your healing builds Rally, culminating in a powerful restorative burst.": "Vos soins accumulent Ralliement, aboutissant à une puissante vague de soins.",
 "Dealing repeated Frost damage makes you unleash Frost Breath, dealing Frost damage and making enemies weaker to your Frost damage.": "Infliger des dégâts de Givre répétés vous fait déchaîner un Souffle de givre, infligeant des dégâts de Givre et rendant les ennemis plus vulnérables à vos dégâts de Givre.",
 "Dealing repeated Fire damage makes you summon a Fire Cyclone, dealing Fire damage to nearby enemies.": "Infliger des dégâts de Feu répétés vous fait invoquer un Cyclone de feu, infligeant des dégâts de Feu aux ennemis proches.",
 "Critical strikes call falling stars until a devastating Big Bang erupts.": "Les coups critiques appellent des étoiles filantes jusqu'à ce qu'un Big Bang dévastateur éclate.",
 "Your damage-over-time effects can apply random class damage-over-time effects.": "Vos effets de dégâts sur la durée peuvent appliquer des effets de dégâts sur la durée aléatoires d'autres classes.",
 "Damaging low-health enemies triggers powerful Execute strikes.": "Blesser des ennemis à faible santé déclenche de puissantes frappes d'Exécution.",
 "While in combat, you are enveloped by a Locust Swarm, reducing damage taken and dealing Nature damage to nearby enemies.": "En combat, vous êtes enveloppé d'un Essaim de criquets, réduisant les dégâts subis et infligeant des dégâts de Nature aux ennemis proches.",
 "Dealing repeated Shadow damage afflicts the target with a curse, dealing Shadow damage periodically spreading to a nearby enemy.": "Infliger des dégâts d'Ombre répétés afflige la cible d'une malédiction, infligeant des dégâts d'Ombre périodiquement et se propageant à un ennemi proche.",
 "Increases your spell power when fighting Demons.": "Augmente votre puissance des sorts contre les Démons.",
 "Increases your attack power when fighting Demons.": "Augmente votre puissance d'attaque contre les Démons.",
 "Falling below 35% health briefly transforms you into a Demon.": "Passer sous 35% de santé vous transforme brièvement en Démon.",
 "Increases your attack power when fighting Dragonkin.": "Augmente votre puissance d'attaque contre les Draconiens.",
 "Increases your spell power when fighting Dragonkin.": "Augmente votre puissance des sorts contre les Draconiens.",
 "Your melee attacks have a chance to unleash an Unbalancing Strike, leaving the target Unbalanced, increasing your damage dealt to it.": "Vos attaques de mêlée ont une chance de déchaîner une Frappe déséquilibrante, laissant la cible Déséquilibrée et augmentant les dégâts que vous lui infligez.",
 "Your first hit after entering combat roots the target": "Votre première attaque en entrant en combat immobilise la cible.",
 "Taking damage can hurl spikes back at attackers causing high threat.": "Subir des dégâts peut renvoyer des pointes aux attaquants, générant beaucoup de menace.",
 "Your periodic effects can trigger an additional tick.": "Vos effets périodiques peuvent déclencher un palier supplémentaire.",
 "Your damaging spells and abilities build Edict, invoking Edicts makes you cast Meteor, Void Zone, Unholy Shadow or Holy Wrath.": "Vos sorts et capacités offensifs accumulent Édit ; invoquer les Édits vous fait lancer Météore, Zone du Vide, Ombre impie ou Courroux sacré.",
 "Attacks cycle through Rune of Death, Overload, and Fusion Punch effects.": "Les attaques alternent entre les effets Rune de mort, Surcharge et Coup de fusion.",
 "Increases your spell power when fighting Elementals.": "Augmente votre puissance des sorts contre les Élémentaires.",
 "Increases your attack power when fighting Elementals.": "Augmente votre puissance d'attaque contre les Élémentaires.",
 "Increases Fire Resistance.": "Augmente la résistance au Feu.",
 "Fire damage builds toward a powerful eruption and burn.": "Les dégâts de Feu mènent à une puissante éruption et brûlure.",
 "Dealing Fire and Shadow grants bonus damage.": "Infliger des dégâts de Feu et d'Ombre accorde un bonus de dégâts.",
 "Overhealing is stored and blooms when the target is low.": "Le surplus de soins est stocké et éclôt quand la cible est à faible santé.",
 "Your damage-over-time effects can restore resources to allies.": "Vos effets de dégâts sur la durée peuvent rendre des ressources aux alliés.",
 "Attacks expose the target, increasing damage dealt and dealing area damage.": "Les attaques exposent la cible, augmentant les dégâts infligés et infligeant des dégâts de zone.",
 "Increases warlock area damage against large groups.": "Augmente les dégâts de zone du démoniste contre les grands groupes.",
 "Dodging and parrying unleashes flames, reduces damage taken and grants speed.": "Esquiver et parer déchaîne des flammes, réduit les dégâts subis et accorde de la vitesse.",
 "Greatly reduces damage taken, but heavily lowers damage dealt.": "Réduit fortement les dégâts subis, mais réduit fortement les dégâts infligés.",
 "When struck, you have a chance to freeze the attacker": "Quand vous êtes frappé, vous avez une chance de geler l'attaquant.",
 "Increases Frost Resistance.": "Augmente la résistance au Givre.",
 "Frost damage builds stacks that Fire damage consumes in an icy explosion.": "Les dégâts de Givre accumulent des cumuls que les dégâts de Feu consument en une explosion glacée.",
 "Increases your spell power when fighting Giants.": "Augmente votre puissance des sorts contre les Géants.",
 "Increases your attack power when fighting Giants.": "Augmente votre puissance d'attaque contre les Géants.",
 "Periodically pulls distant enemies to you and increases your damage to them.": "Attire périodiquement les ennemis distants vers vous et augmente vos dégâts contre eux.",
 "Different healing casts build stacking bonus healing.": "Des sorts de soin différents accumulent un bonus de soins.",
 "Greatly increases the damage of long cast-time spells.": "Augmente fortement les dégâts des sorts à long temps d'incantation.",
 "Increases priest area damage against large groups.": "Augmente les dégâts de zone du prêtre contre les grands groupes.",
 "Periodically curses nearby enemies and heals you when they die.": "Maudit périodiquement les ennemis proches et vous soigne quand ils meurent.",
 "Increases hunter area damage against large groups.": "Augmente les dégâts de zone du chasseur contre les grands groupes.",
 "Kills build stacks that summon a Thing from Beyond.": "Les éliminations accumulent des cumuls qui invoquent une Chose d'outre-monde.",
 "Repeated attacks skewer your target and splinter to nearby enemies.": "Les attaques répétées empalent votre cible et se fragmentent vers les ennemis proches.",
 "Your direct healing can grant allies increased attributes.": "Vos soins directs peuvent augmenter les caractéristiques de vos alliés.",
 "Reduces the duration of stun effects on you.": "Réduit la durée des effets d'étourdissement qui vous affectent.",
 "While at low health, your attacks unleash a life-draining swarm.": "À faible santé, vos attaques déchaînent un essaim qui draine la vie.",
 "Builds attack speed and empowers attacks into chain lightning.": "Accumule de la vitesse d'attaque et transforme les attaques en éclair en chaîne.",
 "Your periodic healing can grant allies increased attributes.": "Vos soins périodiques peuvent augmenter les caractéristiques de vos alliés.",
 "Increases your attack power when fighting Mechanical enemies.": "Augmente votre puissance d'attaque contre les ennemis Mécaniques.",
 "Restoring mana also restores health.": "Restaurer du mana restaure aussi de la santé.",
 "Increases your spell power when fighting Mechanical enemies.": "Augmente votre puissance des sorts contre les ennemis Mécaniques.",
 "Killing an enemy summons a Poison Cloud, dealing Nature damage to nearby enemies.": "Tuer un ennemi invoque un Nuage de poison, infligeant des dégâts de Nature aux ennemis proches.",
 "Your attacks can open a Nether Portal that bombards your target.": "Vos attaques peuvent ouvrir un Portail du Néant qui bombarde votre cible.",
 "Your healing is greatly increased, but spells cost much more mana.": "Vos soins sont fortement augmentés, mais les sorts coûtent beaucoup plus de mana.",
 "Your damage-over-time effects spread when affected enemies die.": "Vos effets de dégâts sur la durée se propagent quand les ennemis affectés meurent.",
 "Constantly damages nearby enemies and slows their attack speed.": "Inflige constamment des dégâts aux ennemis proches et ralentit leur vitesse d'attaque.",
 "You alternate between Positive and Negative Charge. Increases crit chance and damage done or reduces damage taken and increases healing and move speed.": "Vous alternez entre Charge positive et Charge négative. Augmente les chances de critique et les dégâts infligés, ou réduit les dégâts subis et augmente les soins et la vitesse de déplacement.",
 "Increases threat generated.": "Augmente la menace générée.",
 "Haste now reduces your global cooldown.": "La Hâte réduit désormais votre temps de recharge global.",
 "Critical strikes build Momentum and unleash a Massive Crash.": "Les coups critiques accumulent Élan et déchaînent un Écrasement massif.",
 "Low Rage boosts generation, high Rage boosts damage.": "Une rage basse améliore la génération, une rage élevée améliore les dégâts.",
 "Delivering a killing blow unleashes Terrifying Roar, dealing damage to nearby enemies and slowing them. Enemies hit take increased damage from you.": "Porter un coup fatal déchaîne un Rugissement terrifiant, infligeant des dégâts aux ennemis proches et les ralentissant. Les ennemis touchés subissent plus de dégâts de votre part.",
 "Dealing damage afflict the target with Reaper's Doom. When it expires, it detonates dealing Shadow damage split between all enemies hit.": "Infliger des dégâts afflige la cible de Sentence du Faucheur. À son expiration, elle détone en infligeant des dégâts d'Ombre répartis entre tous les ennemis touchés.",
 "Fatal damage instead reduces you to 1 health, prevents all damage for 3 sec, and heals you.": "Les dégâts fatals vous réduisent à 1 point de vie, empêchent tous les dégâts pendant 3 sec et vous soignent.",
 "Your damage against low health enemies is increased. When you damage a low health enemy, you deal a additional Shadow damage.": "Vos dégâts contre les ennemis à faible santé sont augmentés. Quand vous blessez un ennemi à faible santé, vous infligez des dégâts d'Ombre supplémentaires.",
 "Low Energy boosts regeneration, high Energy boosts damage.": "Une énergie basse améliore la régénération, une énergie élevée améliore les dégâts.",
 "Multiple different base stat Echoes increase your damage.": "Plusieurs Echoes de caractéristiques de base différentes augmentent vos dégâts.",
 "Attacks can launch rockets, with more rockets from pets and guardians.": "Les attaques peuvent lancer des roquettes, avec davantage de roquettes via vos familiers et gardiens.",
 "Reduces the duration of root effects on you.": "Réduit la durée des effets d'immobilisation qui vous affectent.",
 "Low Runic Power boosts generation, high Runic Power boosts damage.": "Une puissance runique basse améliore la génération, une puissance runique élevée améliore les dégâts.",
 "Increases paladin area damage against large groups.": "Augmente les dégâts de zone du paladin contre les grands groupes.",
 "Summons two permanent guardians that fight and amplify your damage.": "Invoque deux gardiens permanents qui combattent et amplifient vos dégâts.",
 "Your healing is reduced, but incoming damage is heavily reduced.": "Vos soins sont réduits, mais les dégâts subis sont fortement réduits.",
 "Shadow damage-over-time can call down shadow impact blasts.": "Les dégâts d'Ombre sur la durée peuvent faire s'abattre des déflagrations d'ombre.",
 "Increases the area of effect damages of fan of knives against large groups.": "Augmente les dégâts de zone de Pluie de couteaux contre les grands groupes.",
 "Increases Shadow Resistance.": "Augmente la résistance à l'Ombre.",
 "Reduces damage taken from area-of-effect attacks.": "Réduit les dégâts subis par les attaques de zone.",
 "Taking direct damage builds toward a poisonous molt.": "Subir des dégâts directs mène à une mue empoisonnée.",
 "Your next spell or ability also strikes nearby enemies with lightning.": "Votre prochain sort ou capacité frappe aussi les ennemis proches avec de la foudre.",
 "Reduces pushback suffered from damaging attacks while casting.": "Réduit le recul subi par les attaques pendant l'incantation.",
 "Reduces the duration of disarm effects on you.": "Réduit la durée des effets de désarmement qui vous affectent.",
 "While at low health, you go into a Frenzy, increasing Attack Speed and Physical damage dealt.": "À faible santé, vous entrez en Frénésie, augmentant la vitesse d'attaque et les dégâts physiques infligés.",
 "First hits mark enemies, causing them to shatter on death.": "Les premières attaques marquent les ennemis, les faisant éclater à leur mort.",
 "Reduces the duration of movement slowing effects on you.": "Réduit la durée des effets de ralentissement qui vous affectent.",
 "Resources you spend are stored to empower your next ability.": "Les ressources que vous dépensez sont stockées pour renforcer votre prochaine capacité.",
 "Increases shaman area damage against large groups.": "Augmente les dégâts de zone du chaman contre les grands groupes.",
 "Dealing repeated Arcane damage makes you fire a salvo of Magic Missiles into the air, striking up to 3 nearby enemies.": "Infliger des dégâts des Arcanes répétés vous fait tirer une salve de Missiles magiques en l'air, frappant jusqu'à 3 ennemis proches.",
 "Reduces threat generated.": "Réduit la menace générée.",
 "Reduces the duration of fear effects on you.": "Réduit la durée des effets de peur qui vous affectent.",
 "Haste now reduces the cooldown of select class abilities.": "La Hâte réduit désormais le temps de recharge de certaines capacités de classe.",
 "You harvest the souls of nearby enemies, increasing your damage done and regaining health when an enemy dies near you.": "Vous récoltez les âmes des ennemis proches, augmentant vos dégâts et regagnant de la santé quand un ennemi meurt près de vous.",
 "Greatly increases maximum health, but reduces healing received.": "Augmente fortement la santé maximale, mais réduit les soins reçus.",
 "While in combat, you periodically summon Spores increasing the critical strike damage of nearby allies.": "En combat, vous invoquez périodiquement des Spores qui augmentent les dégâts critiques des alliés proches.",
 "Enemies that strike you are afflicted with Decrepit Fever, dealing Shadow damage and reducing the damage they deal to you.": "Les ennemis qui vous frappent sont affligés de Fièvre décrépite, infligeant des dégâts d'Ombre et réduisant les dégâts qu'ils vous infligent.",
 "You can wield two-handed weapons in one hand.": "Vous pouvez manier des armes à deux mains d'une seule main.",
 "Opposing spell schools build charges that unleash Light or Dark bursts.": "Les écoles de sorts opposées accumulent des charges qui déchaînent des explosions de Lumière ou d'Ombre.",
 "Increases your spell power when fighting Undead.": "Augmente votre puissance des sorts contre les Morts-vivants.",
 "Increases your attack power when fighting Undead.": "Augmente votre puissance d'attaque contre les Morts-vivants.",
 "Direct spells can launch arcane missiles at the target.": "Les sorts directs peuvent lancer des missiles des arcanes sur la cible.",
 "Increases Nature Resistance.": "Augmente la résistance à la Nature.",
 "Allows all weapon types to be equipped.": "Permet d'équiper tous les types d'armes.",
 "Dealing repeated Nature damage makes you unleash Poison Bolt Volley, spraying poison at all enemies.": "Infliger des dégâts de Nature répétés vous fait déchaîner une Volée de traits empoisonnés, aspergeant tous les ennemis de poison.",
 "Increases druid area damage against large groups.": "Augmente les dégâts de zone du druide contre les grands groupes.",
}

BLURB_FR_N = {norm(k): v for k, v in BLURB_FR.items()}

out = {}
missing = []
for name, info in ti.items():
    blurb = info.get("blurb")
    if not blurb:
        continue
    fr = BLURB_FR_N.get(norm(blurb))
    if not fr:
        missing.append((name, blurb))
        continue
    # nom de l'echo gardé en ANGLAIS ; enrobage + blurb en FR
    out[name] = ("Utiliser : Permet à ce personnage de découvrir %s parmi les Echoes proposés. %s : %s"
                 % (name, name, fr))

print("tomes traduits:", len(out), "/", len(ti))
if missing:
    print("NON TRADUITS (blurb sans correspondance):", len(missing))
    for m in missing:
        print("  -", m[0], "->", repr(m[1]))
json.dump(out, open(r"../data\tomes_fr.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
