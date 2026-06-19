import json, re

f = r"../data/EbonholdEchoDump.lua"
src = open(f, encoding="utf-8").read()

# locate first ["affixes"] = { and bracket-match to its close
start = src.index('["affixes"] = {')
i = src.index('{', start)
depth = 0
j = i
while j < len(src):
    c = src[j]
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            break
    j += 1
block = src[i:j+1]

# parse entries: [id] = { ... }
affixes = {}
for m in re.finditer(r'\[(\d+)\]\s*=\s*\{', block):
    aid = int(m.group(1))
    # find this entry's body via bracket match
    s = m.end() - 1
    d = 0
    k = s
    while k < len(block):
        if block[k] == '{':
            d += 1
        elif block[k] == '}':
            d -= 1
            if d == 0:
                break
        k += 1
    body = block[s:k+1]
    name = re.search(r'\["name"\]\s*=\s*"((?:\\.|[^"\\])*)"', body)
    desc = re.search(r'\["desc"\]\s*=\s*"((?:\\.|[^"\\])*)"', body)
    wo = re.search(r'\["weaponOnly"\]\s*=\s*(true|false)', body)
    diff = re.search(r'\["difficulty"\]\s*=\s*(\d+)', body)
    def unesc(x):
        return x.replace('\\"', '"').replace('\\\\', '\\') if x else x
    affixes[aid] = {
        "id": aid,
        "name": unesc(name.group(1)) if name else None,
        "desc": unesc(desc.group(1)) if desc else None,
        "weaponOnly": wo.group(1) == "true" if wo else None,
        "difficulty": int(diff.group(1)) if diff else None,
    }

print("affixes parsés:", len(affixes))
json.dump(affixes, open(r"../data\affixes-dump.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# analyse: prefixes uniques + effets
prefixes = {}
effects = []
for a in affixes.values():
    de = a["desc"] or ""
    if ":" in de:
        pre, eff = de.split(":", 1)
        prefixes[pre.strip()] = prefixes.get(pre.strip(), 0) + 1
        effects.append(eff.strip())
    else:
        prefixes["(pas de ':')"] = prefixes.get("(pas de ':')", 0) + 1
        effects.append(de)
print("\n=== PREFIXES uniques ===")
for p, c in sorted(prefixes.items(), key=lambda x: -x[1]):
    print(f"  {c:4} | {p}")
# effets uniques (normalisés en remplaçant les nombres par #)
norm = {}
for e in effects:
    n = re.sub(r'\d+(?:\.\d+)?', '#', e)
    norm.setdefault(n, []).append(e)
print(f"\n=== {len(norm)} familles d'effets (nombre remplacé par #) ===")
for n in sorted(norm):
    print("  *", n, " | ex:", norm[n][0][:80])
