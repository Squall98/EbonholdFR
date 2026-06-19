# -*- coding: utf-8 -*-
import re, json

aff = json.load(open(r"../data\affixes-dump.json", encoding="utf-8"))

PREFIX = {
    "Allows you to engrave this affix on any equippable item":
        "Permet de graver cet affixe sur n'importe quel objet équipable",
    "Allows you to engrave this affix on any equippable Weapons":
        "Permet de graver cet affixe sur n'importe quelle arme équipable",
    "Allows you to engrave this affix onto any equippable weapon":
        "Permet de graver cet affixe sur n'importe quelle arme équipable",
}

def norm(e):
    return re.sub(r'\d+(?:\.\d+)?', '#', e)

# FR templates dans l'ORDRE TRIÉ (sorted) des effets normalisés (# = nombre)
FR = [
 "Les coups critiques infligent #% de dégâts et de soins supplémentaires",                                                                                                                                                  # 1
 "Les capacités offensives peuvent libérer une Impulsion gelée infligeant # dégâts d'Ombre par seconde pendant # sec, augmentés par votre score de critique",                                                          # 2
 "Infliger des dégâts ralentit le déplacement de votre cible de #% et augmente le délai entre ses attaques de #%.",                                                                                                            # 3
 "Les soins critiques directs restaurent #% de santé supplémentaire, augmentés par votre Intelligence",                                                                                                                          # 4
 "Toutes les # sec, applique un bouclier absorbant # dégâts",                                                                                                                                                                  # 5
 "Augmente les dégâts et soins infligés de #%",                                                                                                                                                                            # 6
 "Augmente la vitesse de course de #%",                                                                                                                                                                                       # 7
 "Augmente l'efficacité des sorts de #%",                                                                                                                                                                                  # 8
 "Augmente votre Armure de #",                                                                                                                                                                                                # 9
 "Augmente votre score de Défense.",                                                                                                                                                                                       # 10
 "Augmente votre régénération de Mana de #%",                                                                                                                                                                            # 11
 "Augmente votre pénétration d'armure de #%",                                                                                                                                                                            # 12
 "Augmente vos chances de coup critique de #%",                                                                                                                                                                               # 13
 "Augmente vos dégâts contre les Morts-vivants.",                                                                                                                                                                        # 14
 "Augmente votre Agilité totale de #%",                                                                                                                                                                                    # 15
 "Augmente votre Intelligence totale de #%",                                                                                                                                                                                  # 16
 "Augmente votre Esprit total de #%",                                                                                                                                                                                         # 17
 "Augmente votre Endurance totale de #%",                                                                                                                                                                                     # 18
 "Augmente votre Force totale de #%",                                                                                                                                                                                         # 19
 "Tuer un ennemi augmente votre score de hâte, cumulable jusqu'à # fois. Un cumul est perdu chaque seconde.",                                                                                                              # 20
 "Soigne périodiquement l'incantateur.",                                                                                                                                                                                   # 21
 "Subir des dégâts peut accorder #% de puissance d'attaque et #% de puissance des sorts pendant # secondes",                                                                                                                # 22
 "Lorsque vous passez sous #% de santé, vous êtes soigné de #% de votre santé maximale et votre Force est augmentée pendant # secondes. Cet effet ne peut pas se produire plus d'une fois toutes les # secondes.",            # 23
 "Tant que vous êtes sous #% de santé, absorbe #% des dégâts subis. Unique",                                                                                                                                            # 24
 "Enveloppe l'incantateur d'un bouclier de feu infligeant des dégâts de Feu chaque seconde aux ennemis proches. Les dégâts augmentent avec la résistance au Feu de l'incantateur.",                                          # 25
 "Vos dégâts de Feu ont une chance de projeter une boule de feu sur la cible, infligeant des dégâts de Feu plus des dégâts supplémentaires toutes les # sec pendant # sec. Les dégâts évoluent avec votre Intelligence.",     # 26
 "Vos dégâts de Givre ont une chance de lancer un trait de givre sur la cible, infligeant des dégâts de Givre et réduisant sa vitesse de déplacement. Les dégâts augmentent avec le nombre d'effets de ralentissement sur la cible.",  # 27
 "Vos soins sur la durée (HoT) infligent # soins supplémentaires par seconde, augmentés par votre Esprit",                                                                                                                  # 28
 "Vos dégâts de Nature ont une chance de couvrir la cible d'Acide corrosif, infligeant des dégâts de Nature toutes les # sec. Tant qu'il est actif, l'Acide corrosif réduit l'armure de la cible, augmenté de #% pour chacun de vos effets de dégâts sur la durée actifs sur la cible.",  # 29
 "Vos dégâts d'Ombre ont une chance d'envoyer un trait d'ombre sur la cible, infligeant des dégâts d'Ombre. Les dégâts augmentent avec vos effets de dégâts d'Ombre sur la durée actifs sur la cible.",                          # 30
 "Vos capacités peuvent déchaîner un Souffle de givre infligeant # dégâts de Givre, augmentés par votre Endurance",                                                                                                          # 31
 "Vos coups critiques ont une chance de corrompre la cible, infligeant des dégâts d'Ombre toutes les # sec. Tant que la Corruption est active, vos coups critiques de sort contre la cible la font flamboyer, infligeant des dégâts supplémentaires basés sur votre Intelligence. Chaque Corruption ne peut flamboyer qu'une fois toutes les # sec au maximum.",  # 32
 "Vos capacités offensives peuvent tirer une Étoile infinie infligeant # dégâts des Arcanes, augmentés par votre caractéristique la plus élevée",                                                                            # 33
 "Vos sorts et capacités offensifs ont une chance d'empoisonner la cible, infligeant des dégâts toutes les # sec pendant # sec. Les cibles empoisonnées subissent #% de dégâts supplémentaires de vos effets de dégâts sur la durée.",  # 34
 "Vos sorts et capacités offensifs ont une chance d'étourdir la cible. La durée de l'étourdissement est augmentée par votre Force.",                                                                                          # 35
 "Vos sorts de soin ont une chance de provoquer Bénédiction des anciens rois pendant # secondes, permettant à vos soins de protéger la cible en absorbant des dégâts égaux à #% du montant soigné.",                             # 36
 "Vos capacités de mêlée et à distance ont une chance d'infliger une Blessure fatale. Les dégâts évoluent avec votre score de pénétration d'armure.",                                                                       # 37
 "Vos attaques de mêlée et à distance ont une chance de Blesser la cible. Cet effet se produit deux fois plus souvent dans le dos de la cible.",                                                                                # 38
 "Vos attaques de mêlée et à distance ont une chance de réduire l'armure de la cible. L'effet est augmenté par votre Agilité.",                                                                                            # 39
 "Vos coups critiques d'attaque de base en mêlée et à distance augmentent votre puissance d'attaque de #, cumulable jusqu'à # fois. Un cumul est perdu chaque seconde.",                                                          # 40
 "Vos attaques et capacités de mêlée ont une chance de frapper une fois supplémentaire pour des dégâts normaux.",                                                                                                          # 41
 "Vos attaques de mêlée ont #% de chances de vous faire frapper tous les ennemis proches, infligeant des dégâts d'arme. Avec une arme à deux mains, vous avez #% de chances de déclencher Tornade d'acier sur votre cible",     # 42
 "Vos soins périodiques peuvent augmenter votre puissance des sorts de soin de # pendant # sec",                                                                                                                          # 43
 "Votre familier attaque #% plus vite",                                                                                                                                                                                      # 44
 "Votre familier inflige #% de dégâts supplémentaires",                                                                                                                                                                    # 45
 "Vos capacités physiques ont une chance de blesser la cible, la faisant saigner et infligeant des dégâts toutes les # sec pendant # sec. Les dégâts évoluent avec la vitesse de votre arme.",                                  # 46
 "Vos capacités à distance ont une chance de frapper votre cible avec des dégâts de Feu. Les dégâts augmentent avec la vitesse de votre arme à distance et votre résistance au Feu.",                                       # 47
 "Vos capacités à distance ont une chance de frapper votre cible avec des dégâts de Givre. Les dégâts augmentent avec la vitesse de votre arme à distance et votre résistance au Givre.",                                    # 48
 "Vos capacités à distance ont une chance de frapper votre cible avec des dégâts de Nature. Les dégâts augmentent avec la vitesse de votre arme à distance et votre résistance à la Nature.",                                 # 49
 "Vos attaques automatiques à distance déclenchent automatiquement un second tir",                                                                                                                                         # 50
 "Vos sorts et capacités ont une chance de foudroyer votre ennemi, infligeant des dégâts de Nature puis rebondissant sur d'autres ennemis proches. Chaque rebond réduit la résistance à la Nature de la victime de #%. Affecte # cibles. Votre cible principale est également happée par un cyclone, ralentissant sa vitesse d'attaque de #% pendant # secondes.",  # 51
 "Vos sorts et capacités ont une chance d'appeler une Étincelle d'Azzinoth pour vous protéger au combat pendant une courte durée.",                                                                                            # 52
 "Vos sorts et capacités ont une chance de frapper un ennemi de dégâts Sacrés. La chance évolue avec votre chance de toucher.",                                                                                              # 53
 "Vos sorts et capacités ont une chance d'invoquer l'esprit infernal de Shahram.",                                                                                                                                          # 54
 "Vos sorts et capacités ont une chance de frapper la cible en infligeant des dégâts de Feu. Les dégâts évoluent avec votre score de critique.",                                                                            # 55
 "Vos sorts et capacités ont une chance de frapper la cible en infligeant des dégâts de Givre. Cet effet a deux fois plus de chances de se produire contre des cibles ralenties.",                                              # 56
 "Vos sorts et capacités ont une chance de frapper la cible en infligeant des dégâts de Nature. Les dégâts évoluent avec votre mana total.",                                                                              # 57
 "Vos sorts et capacités ont une chance d'augmenter les dégâts critiques de vos prochaines capacités lancées dans les # secondes de #%.",                                                                                    # 58
 "Vos sorts et capacités ont une chance de désarmer la cible. La durée du désarmement est augmentée par votre Endurance.",                                                                                                  # 59
 "Vos sorts et capacités ont une chance de projeter une boule de feu infligeant des dégâts de Feu plus des dégâts de feu supplémentaires sur # secondes. Les deux effets évoluent avec les dégâts de Feu sur la durée actifs sur votre cible.",  # 60
 "Vos sorts et capacités ont une chance d'augmenter les dégâts subis par la cible de #% pendant # secondes.",                                                                                                                # 61
 "Vos sorts et capacités ont une chance de vous faire gagner # points d'énergie ou # de rage.",                                                                                                                            # 62
 "Vos sorts et capacités ont une chance de réduire toutes les caractéristiques de la cible. Cet effet est augmenté par votre résistance à la Nature.",                                                                       # 63
 "Vos sorts et capacités ont une chance de voler la vie de la cible. Le montant volé augmente à mesure que votre santé est basse et avec les effets qui augmentent les soins prodigués.",                                          # 64
 "Vos sorts peuvent réduire un temps de recharge aléatoire de # sec",                                                                                                                                                     # 65
 "augmente votre valeur de Blocage de #%",                                                                                                                                                                                    # 66
 "augmente votre Force totale de #%",                                                                                                                                                                                         # 67
]

# construit l'ensemble trié des effets normalisés, depuis les données
effs = set()
for a in aff.values():
    de = a["desc"] or ""
    eff = de.split(":", 1)[1].strip() if ":" in de else de.strip()
    effs.add(norm(eff))
norm_sorted = sorted(effs)

assert len(norm_sorted) == len(FR), ("compte familles", len(norm_sorted), "FR", len(FR))
eff_map = dict(zip(norm_sorted, FR))

# vérif d'alignement : imprime EN-normalisé -> FR
print("=== ALIGNEMENT (vérifie quelques lignes) ===")
for i, n in enumerate(norm_sorted):
    print(f"[{i+1}] EN: {n[:60]}")
    print(f"     FR: {eff_map[n][:60]}")

out = {}
problems = []
for a in aff.values():
    de = a["desc"] or ""
    if ":" in de:
        pre, eff = de.split(":", 1)
        pre = pre.strip(); eff = eff.strip()
    else:
        pre = None; eff = de.strip()
    nums = re.findall(r'\d+(?:\.\d+)?', eff)
    tmpl = eff_map[norm(eff)]
    if tmpl.count('#') != len(nums):
        problems.append((a["id"], a["name"], tmpl.count('#'), len(nums), eff))
        continue
    it = iter(nums)
    fr_eff = re.sub('#', lambda m: next(it), tmpl)
    fr_pre = PREFIX.get(pre, pre) if pre else None
    out[str(a["id"])] = (fr_pre + " : " + fr_eff) if fr_pre else fr_eff

print("\n=== RÉSULTAT ===")
print("affixes traduits:", len(out), "/", len(aff))
if problems:
    print("PROBLEMES (# mismatch):")
    for p in problems:
        print("  ", p)
else:
    print("aucun mismatch de nombres.")

json.dump(out, open(r"../data\affixes_fr.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# Map EFFET seul (EN -> FR) pour traduire les affixes gravés sur les objets
eff_out = {}
for a in aff.values():
    de = a["desc"] or ""
    if ":" not in de:
        continue
    pre, eff = de.split(":", 1)
    en_eff = eff.strip()
    nums = re.findall(r'\d+(?:\.\d+)?', en_eff)
    tmpl = eff_map[norm(en_eff)]
    if tmpl.count('#') != len(nums):
        continue
    it = iter(nums)
    fr_eff = re.sub('#', lambda m: next(it), tmpl)
    eff_out[en_eff] = fr_eff
print("effets d'affixes (map objet):", len(eff_out))
json.dump(eff_out, open(r"../data\affix_effect_fr.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
