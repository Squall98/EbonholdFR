-- EbonholdFR_Reglages.lua — réglages écrits par le launcher Ebonhold FR (onglet « Français »).
-- Le launcher remplace ce fichier quand on applique ses réglages ; s'il manque, l'addon prend
-- les valeurs par défaut ci-dessous. Les choix faits en jeu (bouton minimap, /efr) restent
-- possibles et sont mémorisés ; ils sont oubliés si le launcher change ensuite ces réglages.
--   true  = traduit / affiché      false = laissé en anglais / masqué
--   patch = true : le patch FR est installé, les descriptions sont déjà en français dans le jeu :
--           l'addon n'y touche pas et ne garde que l'interface du serveur et la ligne « EN : ».
EbonholdFR_Reglages = {
  version = 1,
  interface = true,       -- interface du serveur (fenêtres, boutons, infobulles)
  echoes_desc = true,     -- descriptions des Echoes
  soultree_desc = true,   -- descriptions du Soul Tree
  affixes_desc = true,    -- affixes (lignes gravées sur les objets, grimoire)
  tomes = true,           -- Tomes of Echo
  nom_anglais = true,     -- ligne grise « EN : nom anglais » quand le nom affiché est traduit
  patch = false,          -- patch FR installé
}
