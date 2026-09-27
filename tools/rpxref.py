#!/usr/bin/env python3
"""Перекрёстная проверка проекта Ren'Py: метки, экраны, картинки, трансформы, файлы звука.

    python3 tools/rpxref.py game
"""
import os, re, sys

game = sys.argv[1] if len(sys.argv) > 1 else "game"
rpy = {}
for root, _, files in os.walk(game):
    for f in files:
        if f.endswith(".rpy"):
            p = os.path.join(root, f)
            rpy[p] = open(p, encoding="utf-8").read()

labels, screens, transforms, images = set(), set(), set(), set()
for p, s in rpy.items():
    labels |= set(re.findall(r"^label (\w+)", s, re.M))
    screens |= set(re.findall(r"^screen (\w+)", s, re.M))
    transforms |= set(re.findall(r"^transform (\w+)", s, re.M))
    images |= set(m.strip() for m in re.findall(r"^image ([\w ]+?)\s*=", s, re.M))
    images |= set(m.strip() for m in re.findall(r"^image ([\w ]+?)\s*:", s, re.M))
    images |= set(m.strip().lower() for m in re.findall(r"""renpy\.image\(\s*["']([\w ]+)["']""", s))
imgdir = os.path.join(game, "images")
for root, _, files in os.walk(imgdir):
    for f in files:
        base, ext = os.path.splitext(f)
        if ext.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            rel = os.path.relpath(root, imgdir)
            name = base if rel == "." else (rel.replace(os.sep, " ") + " " + base)
            images.add(name.lower())
image_tags = set(n.split()[0] for n in images)

transforms |= {"left", "right", "center", "truecenter", "topleft", "topright", "top", "default", "offscreenleft", "offscreenright", "reset"}
images |= {"black", "white"}
screens |= {"say", "choice", "input", "nvl", "main_menu", "game_menu", "save", "load", "preferences", "history", "help",
            "about", "confirm", "skip_indicator", "notify", "quick_menu", "navigation", "file_slots", "extras"}
labels |= {"start", "splashscreen", "quit", "after_load", "main_menu", "before_main_menu"}

missing = []
def need(kind, name, where):
    pool = {"label": labels, "screen": screens, "transform": transforms, "image": images}[kind]
    if name not in pool:
        missing.append("%s: missing %s '%s'" % (where, kind, name))

for p, s in rpy.items():
    for i, line in enumerate(s.split("\n"), 1):
        where = "%s:%d" % (p, i)
        t = line.strip()
        if t.startswith("#"):
            continue
        m = re.match(r"^(?:jump|call) (\w+)\s*(?:\(|$|#| from)", t)
        if m and not t.startswith("call screen") and not t.startswith("jump expression"):
            need("label", m.group(1), where)
        m = re.match(r"^(?:call|show) screen (\w+)", t)
        if m: need("screen", m.group(1), where)
        m = re.match(r"^hide screen (\w+)", t)
        if m: need("screen", m.group(1), where)
        m = re.match(r"^use (\w+)", t)
        if m: need("screen", m.group(1), where)
        for m in re.finditer(r"""renpy\.(?:show_screen|hide_screen|call_screen)\(\s*["'](\w+)["']""", t):
            need("screen", m.group(1), where)
        for m in re.finditer(r"""\b(?:Show|Hide|ShowMenu)\(\s*["'](\w+)["']""", t):
            need("screen", m.group(1), where)
        for m in re.finditer(r"""\b(?:Replay|Jump|Call)\(\s*["'](\w+)["']""", t):
            need("label", m.group(1), where)
        for m in re.finditer(r"""renpy\.(?:jump|call)\(\s*["'](\w+)["']""", t):
            need("label", m.group(1), where)
        m = re.match(r"^(?:scene|show) ([\w][\w ]*?)(?:\s+(?:at|with|onlayer|as|behind|zorder)\b|\s*$)", t)
        if m and not t.startswith("show screen") and not t.startswith("scene expression") and not t.startswith("show expression"):
            name = m.group(1).strip().lower()
            if name not in images and name.split()[0] not in image_tags:
                need("image", name, where)
        m = re.match(r"^hide (\w+)", t)
        if m and not t.startswith("hide screen"):
            if m.group(1).lower() not in image_tags and m.group(1).lower() not in images:
                need("image", m.group(1), where)
        m = re.search(r"\bat ([\w]+)(?:\(|\s*$|,)", t)
        if m and (t.startswith("show ") or t.startswith("scene ") or re.match(r"^(text|add|frame|vbox|hbox|fixed|button|textbutton|imagebutton|image|null|bar|vpgrid|grid|viewport|drag|draggroup)\b", t)):
            need("transform", m.group(1), where)
        for m in re.finditer(r"""["']((?:audio|voice|images)/[^"']+)["']""", t):
            fn = os.path.join(game, m.group(1))
            if not os.path.exists(fn) and "%" not in fn and "[" not in fn and "+" not in t.split(m.group(0))[0][-3:]:
                missing.append("%s: missing file '%s'" % (where, m.group(1)))
        m = re.match(r"^(?:play|queue) \w+ ['\"]([^'\"]+)['\"]", t)
        if m and not os.path.exists(os.path.join(game, m.group(1))):
            missing.append("%s: missing file '%s'" % (where, m.group(1)))
        m = re.match(r"^voice ['\"]([^'\"]+)['\"]", t)
        if m and not os.path.exists(os.path.join(game, m.group(1))):
            missing.append("%s: missing file '%s'" % (where, m.group(1)))

print("labels: %d images: %d screens: %d transforms: %d" % (len(labels), len(images), len(screens), len(transforms)))
if missing:
    for m in sorted(set(missing)):
        print("MISSING", m)
    sys.exit(1)
print("XREF OK")
