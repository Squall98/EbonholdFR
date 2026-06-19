# -*- coding: utf-8 -*-
import re, json

f = r"../data/EbonholdEchoDump.lua"
src = open(f, encoding="utf-8").read()

# isole le 1er bloc ["tomeItems"] = { ... }
start = src.index('["tomeItems"] = {')
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

# chaque entrée : ["Nom"] = { ... ["title"]="..." ... use line dans tooltip }
tomes = {}
for m in re.finditer(r'\["((?:\\.|[^"\\])*)"\]\s*=\s*\{', block):
    name = m.group(1)
    if name in ("tooltip",):
        continue
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
    title = re.search(r'\["title"\]\s*=\s*"((?:\\.|[^"\\])*)"', body)
    if not title:
        continue
    echo = re.match(r'Tome of Echo: (.+)$', title.group(1).replace('\\"', '"'))
    if not echo:
        continue
    echoName = echo.group(1)
    # ligne "Use: ... when offered new Echoes. <Name>: <blurb>"
    useline = re.search(r'"(Use: Grants[^"]*?when offered new Echoes\. [^"]*)"', body)
    blurb = None
    full = None
    if useline:
        full = useline.group(1)
        mb = re.search(r'when offered new Echoes\. .*?: (.+)$', full)
        if mb:
            blurb = mb.group(1)
    iid = re.search(r'\["itemId"\]\s*=\s*(\d+)', body)
    tomes[echoName] = {"blurb": blurb, "useFull": full,
                       "itemId": int(iid.group(1)) if iid else None}

print("objets tomes parsés:", len(tomes))
nblurb = sum(1 for t in tomes.values() if t["blurb"])
print("avec blurb extrait:", nblurb)
print("--- 6 exemples ---")
for k in list(tomes)[:6]:
    print(" *", k, "->", tomes[k]["blurb"])
json.dump(tomes, open(r"../data\tome_items.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
