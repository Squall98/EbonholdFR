--[[ EbonholdFR_Fix.lua — ex-addon EbonholdFRFix (EbonholdFRFix.lua), intégré à EbonholdFR 4.0.

  Sur un client en français, les PNJ / objets du serveur (forge « Enchanted Anvil », tableau des
  objectifs « Objectives Board ») s'affichent avec un nom traduit. ProjectEbonhold compare ce nom
  à la chaîne ANGLAISE exacte pour ouvrir sa fenêtre : en français la comparaison échoue et on
  tombe sur le dialogue par défaut. On ouvre alors nous-mêmes la bonne fenêtre quand on reconnaît
  le nom FRANÇAIS. Ne se déclenche jamais sur un nom anglais (le serveur s'en occupe déjà).
  Diagnostic : /efr fix (ou /frfix) affiche le nom du prochain PNJ de dialogue.
]]

local E = EbonholdFR or {}

-- noms français exacts (UTF-8 : é = \195\169)
local FORGE = {
  ["Enclume enchant\195\169e"] = true,
}
local TABLEAU = {
  -- à confirmer en jeu avec /efr fix (nom envoyé par le serveur aux clients français)
  ["Tableau des objectifs"] = true,
  ["Panneau des objectifs"] = true,
  ["Tableau d'objectifs"] = true,
}
E.NomsForge, E.NomsTableau = FORGE, TABLEAU

local diag = false
local actif = nil   -- "forge" | "tableau" | nil

local function cacherGossip()
  if GossipFrame then
    GossipFrame:SetAlpha(0)
    GossipFrame:EnableMouse(false)
    GossipFrame:ClearAllPoints()
    GossipFrame:SetPoint("TOPLEFT", UIParent, "BOTTOMRIGHT", 1000, -1000)
  end
end

local function rendreGossip()
  if GossipFrame then
    GossipFrame:SetAlpha(1)
    GossipFrame:EnableMouse(true)
    GossipFrame:ClearAllPoints()
    GossipFrame:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 16, -116)
  end
end

local function ouvrirForge()
  if EbonholdExtractionFrame then
    actif = "forge"
    cacherGossip()
    EbonholdExtractionFrame:Show()
    return true
  end
  return false
end

local function ouvrirTableau()
  local PE = ProjectEbonhold
  if PE and PE.ObjectivesUI and PE.ObjectivesUI.DisplayObjectives and PE.ObjectivesService then
    actif = "tableau"
    cacherGossip()
    local objectifs = PE.ObjectivesService.GetCurrentObjectives and PE.ObjectivesService.GetCurrentObjectives()
    if objectifs and #objectifs > 0 then
      PE.ObjectivesUI.DisplayObjectives(objectifs)
    elseif PE.ObjectivesService.RequestObjectives then
      PE.ObjectivesService.RequestObjectives()   -- le service affiche les objectifs à leur arrivée
    end
    return true
  end
  return false
end

local f = CreateFrame("Frame")
f:RegisterEvent("GOSSIP_SHOW")
f:RegisterEvent("GOSSIP_CLOSED")
f:SetScript("OnEvent", function(self, event)
  if event == "GOSSIP_SHOW" then
    if not GossipFrame or not GossipFrame:IsShown() then return end
    local nom = GossipFrameNpcNameText and GossipFrameNpcNameText:GetText()
    if diag and E.msg then E.msg("dialogue PNJ = [" .. tostring(nom) .. "]") end
    if nom then
      if FORGE[nom] then ouvrirForge()
      elseif TABLEAU[nom] then ouvrirTableau() end
    end
  elseif event == "GOSSIP_CLOSED" then
    if actif then
      local etait = actif
      actif = nil
      rendreGossip()
      -- comme le serveur le fait pour le nom anglais : fermer la fenêtre avec le dialogue
      if etait == "forge" and EbonholdExtractionFrame and EbonholdExtractionFrame:IsShown() then
        EbonholdExtractionFrame:Hide()
      elseif etait == "tableau" and ObjectivesMainFrame and ObjectivesMainFrame:IsShown() then
        ObjectivesMainFrame:Hide()
      end
    end
  end
end)

local function basculerDiag()
  diag = not diag
  if E.msg then
    E.msg(diag and "diagnostic ON : parle \195\160 un PNJ, son nom s'affiche. Refais /efr fix pour couper."
      or "diagnostic OFF.")
  end
end

E.Commandes = E.Commandes or {}
E.Commandes.fix = basculerDiag
SLASH_FRFIX1 = "/frfix"
SlashCmdList["FRFIX"] = basculerDiag
