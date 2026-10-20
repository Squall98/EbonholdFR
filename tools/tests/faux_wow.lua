--[[ faux_wow.lua — environnement WoW 3.3.5 MINIMAL pour tester EbonholdFR hors du jeu (LuaJIT / lupa).
  Cadres, FontString, infobulles (GameTooltip), événements, OnUpdate, hooksecurefunc, HookScript,
  SavedVariables (simples globales), StaticPopup. Les méthodes inconnues ne font rien (renvoient nil).
  Utilisé par test_ebonholdfr_v4.py.
]]

FAUX = { evenements = {}, temps = 0, cadres = {}, appels = {} }

local function noop() end
-- méthodes inconnues (CamelCase) : ne font rien ; champs inconnus : nil, comme en jeu
local Base = setmetatable({}, { __index = function(_, k)
  if type(k) == "string" and k:match("^%u") then return noop end
end })
local methodes = {}
local function meta(ot)
  local mt = methodes[ot]
  if not mt then
    local m = setmetatable({}, { __index = Base })
    mt = { __index = m, m = m }
    methodes[ot] = mt
  end
  return mt
end

local function creer(ot, nom, parent)
  local o = setmetatable({}, meta(ot))
  o[0] = newproxy and newproxy(false) or {}
  o.__type, o.__nom, o.__shown = ot, nom, true
  o.__children, o.__regions, o.__scripts = {}, {}, {}
  if parent then o.__parent = parent end
  if nom then _G[nom] = o end
  return o
end

function Base.GetObjectType(s) return s.__type end
function Base.IsObjectType(s, t) return s.__type == t end
function Base.GetName(s) return s.__nom end
function Base.GetParent(s) return s.__parent end
function Base.IsProtected(s) return s.__protege and true or false end
function Base.GetChildren(s) return unpack(s.__children) end
function Base.GetNumChildren(s) return #s.__children end
function Base.GetRegions(s) return unpack(s.__regions) end
function Base.GetNumRegions(s) return #s.__regions end
function Base.IsShown(s) return s.__shown end
function Base.IsVisible(s)
  if not s.__shown then return false end
  if s.__parent then return s.__parent:IsVisible() end
  return true
end

local function feuShow(f)
  local sc = f.__scripts.OnShow
  if sc then sc(f) end
  for _, c in ipairs(f.__children) do
    if c.__shown then feuShow(c) end
  end
end
FAUX.feuShow = feuShow

function Base.Show(s)
  local avant = s:IsVisible()
  s.__shown = true
  if not avant and s:IsVisible() then feuShow(s) end
end
function Base.Hide(s)
  local avant = s:IsVisible()
  s.__shown = false
  if avant and s.__scripts.OnHide then s.__scripts.OnHide(s) end
end
function Base.SetScript(s, ev, fn) s.__scripts[ev] = fn end
function Base.GetScript(s, ev) return s.__scripts[ev] end
function Base.HookScript(s, ev, fn)
  local old = s.__scripts[ev]
  if old then s.__scripts[ev] = function(...) old(...); fn(...) end else s.__scripts[ev] = fn end
end
function Base.RegisterEvent(s, ev)
  FAUX.evenements[ev] = FAUX.evenements[ev] or {}
  table.insert(FAUX.evenements[ev], s)
end
function Base.CreateFontString(s, nom)
  local fs = creer("FontString", nom, s)
  table.insert(s.__regions, fs)
  return fs
end
function Base.CreateTexture(s, nom)
  local t = creer("Texture", nom, s)
  table.insert(s.__regions, t)
  return t
end
-- textes : FontString et boutons
function Base.SetText(s, t)
  if s.__fs then s.__fs:SetText(t) else s.__text = t end
end
function Base.GetText(s)
  if s.__fs then return s.__fs:GetText() end
  return s.__text
end
function Base.SetFormattedText(s, fmt, ...) s:SetText(string.format(fmt, ...)) end
function Base.GetFontString(s) return s.__fs end
function Base.SetFontString(s, fs) s.__fs = fs end
function Base.GetFrameLevel() return 1 end
function Base.GetWidth() return 300 end
function Base.GetHeight() return 100 end
function Base.GetCenter() return 0, 0 end
function Base.GetEffectiveScale() return 1 end
function Base.GetChecked(s) return s.__coche end
function Base.SetChecked(s, v) s.__coche = v and true or nil end

function CreateFrame(ot, nom, parent, modele)
  local f = creer(ot, nom, parent)
  if parent then table.insert(parent.__children, f) end
  if ot == "Button" or ot == "CheckButton" then
    f.__fs = creer("FontString", nom and (nom .. "Text") or nil, f)
    table.insert(f.__regions, f.__fs)
  end
  if ot == "GameTooltip" then FAUX.infobulle(f) end
  table.insert(FAUX.cadres, f)
  return f
end

-- ---------------------------------------------------------------------------- infobulles
local M_TT = meta("GameTooltip").m
function M_TT.SetOwner(s, owner) s.__owner = owner; s:ClearLines() end
function M_TT.GetOwner(s) return s.__owner end
function M_TT.ClearLines(s)
  for i = 1, s.__n or 0 do
    _G[s.__nom .. "TextLeft" .. i]:SetText(nil)
    _G[s.__nom .. "TextRight" .. i]:SetText(nil)
    _G[s.__nom .. "TextRight" .. i].__shown = false
  end
  s.__n = 0
  s.__lien, s.__item, s.__sort = nil, nil, nil
end
local function ligneTT(s, i)
  if not _G[s.__nom .. "TextLeft" .. i] then
    local l = creer("FontString", s.__nom .. "TextLeft" .. i, s); table.insert(s.__regions, l)
    local r = creer("FontString", s.__nom .. "TextRight" .. i, s); table.insert(s.__regions, r)
    r.__shown = false
  end
end
function M_TT.AddLine(s, t)
  s.__n = (s.__n or 0) + 1
  ligneTT(s, s.__n)
  _G[s.__nom .. "TextLeft" .. s.__n]:SetText(t)
end
function M_TT.AddDoubleLine(s, a, b)
  s:AddLine(a)
  local r = _G[s.__nom .. "TextRight" .. s.__n]
  r:SetText(b); r.__shown = true
end
function M_TT.SetText(s, t) s:ClearLines(); s:AddLine(t) end
function M_TT.NumLines(s) return s.__n or 0 end
function M_TT.GetItem(s) if s.__item then return "objet", "|cff1eff00|Hitem:" .. s.__item .. ":0:0:0|h[objet]|h|r" end end
function M_TT.GetSpell(s) if s.__sort then return "sort", "", s.__sort end end
function M_TT.Show(s) s.__shown = true; FAUX.appels.show = (FAUX.appels.show or 0) + 1 end
function M_TT.SetHyperlink(s, lien)
  s:ClearLines()
  local id = tonumber(lien:match("^spell:(%d+)") or "")
  local it = tonumber(lien:match("^item:(%d+)") or "")
  if id and FAUX.SORTS[id] then
    s.__sort = id
    for _, l in ipairs(FAUX.SORTS[id]) do s:AddLine(l) end
    if s.__scripts.OnTooltipSetSpell then s.__scripts.OnTooltipSetSpell(s) end
  elseif it and FAUX.OBJETS[it] then
    s.__item = it
    for _, l in ipairs(FAUX.OBJETS[it]) do s:AddLine(l) end
    if s.__scripts.OnTooltipSetItem then s.__scripts.OnTooltipSetItem(s) end
  end
  s.__shown = true
end
function FAUX.infobulle(f) f.__n = 0 end
FAUX.SORTS, FAUX.OBJETS = {}, {}

-- ---------------------------------------------------------------------------- API globales
function hooksecurefunc(a, b, c)
  local t, nom, fn = a, b, c
  if type(a) == "string" then t, nom, fn = _G, a, b end
  local orig = t[nom]
  t[nom] = function(...)
    local r = { orig(...) }
    fn(...)
    return unpack(r)
  end
end
function GetTime() return FAUX.temps end
function GetAddOnMetadata(a, k) if k == "Version" then return "4.0" end end
function IsAddOnLoaded(n) return FAUX.addons and FAUX.addons[n] or nil end
function GetLocale() return FAUX.locale or "enUS" end
FAUX.NOMS = {}
function GetSpellInfo(id) return FAUX.NOMS[id] end
function UnitName(u) if u == "player" then return "Squall" end end
function InCombatLockdown() return false end
function GetCursorPosition() return 0, 0 end
function ReloadUI() end
function debugprofilestop() return os.clock() * 1000 end
wipe = function(t) for k in pairs(t) do t[k] = nil end return t end
tinsert, tremove = table.insert, table.remove
strsplit = function(sep, s) local out = {} for x in (s .. sep):gmatch("(.-)" .. sep) do out[#out + 1] = x end return unpack(out) end
SlashCmdList = {}
UISpecialFrames = {}
DEFAULT_CHAT_FRAME = { AddMessage = function(_, m) FAUX.dernierMessage = m; table.insert(FAUX.messages, m) end }
FAUX.messages = {}

UIParent = CreateFrame("Frame", "UIParent")
WorldFrame = CreateFrame("Frame", "WorldFrame")
Minimap = CreateFrame("Frame", "Minimap", UIParent)
for _, n in ipairs({ "GameTooltip", "ItemRefTooltip", "ShoppingTooltip1", "ShoppingTooltip2" }) do
  CreateFrame("GameTooltip", n, UIParent, "GameTooltipTemplate")
end
for i = 1, 4 do
  local p = CreateFrame("Frame", "StaticPopup" .. i, UIParent)
  p:CreateFontString("StaticPopup" .. i .. "Text")
  for b = 1, 3 do CreateFrame("Button", "StaticPopup" .. i .. "Button" .. b, p) end
  p.__shown = false
end
function StaticPopup_Resize() FAUX.appels.resize = (FAUX.appels.resize or 0) + 1 end
GossipFrame = CreateFrame("Frame", "GossipFrame", UIParent)
GossipFrameNpcNameText = GossipFrame:CreateFontString("GossipFrameNpcNameText")

-- ---------------------------------------------------------------------------- pilotage
function FAUX.evenement(ev, ...)
  for _, f in ipairs(FAUX.evenements[ev] or {}) do
    local sc = f.__scripts.OnEvent
    if sc then sc(f, ev, ...) end
  end
end
function FAUX.tic(dt)
  dt = dt or 0.1
  FAUX.temps = FAUX.temps + dt
  for _, f in ipairs(FAUX.cadres) do
    local sc = f.__scripts.OnUpdate
    if sc and f:IsVisible() then sc(f, dt) end
  end
end
function FAUX.charger(chemin)
  local fn, err = loadfile(chemin)
  if not fn then error(err) end
  return fn("EbonholdFR", {})
end
