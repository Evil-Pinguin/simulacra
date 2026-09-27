#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор переводов без движка Ren'Py.

Идентификаторы диалогов считаются тем же кодом, что и в движке
(renpy.translation.restructure над настоящим AST), поэтому файлы
game/tl/<lang>/*.rpy совпадают с теми, что сделал бы лаунчер.

    python3 tools/tlgen.py extract            # tools/tl/dialogue_ru.txt, strings_ru.txt (ключ<TAB>текст)
    python3 tools/tlgen.py build english      # tools/tl/english/*.txt -> game/tl/english/*.rpy
    python3 tools/tlgen.py missing english    # что ещё не переведено

Перевод пишется в tools/tl/<lang>/dialogue.txt и strings.txt строками
    <ключ><TAB><перевод>
где ключ — 6 hex md5 исходной строки (см. *_ru.txt). Непереведённое
попадает в tl-файлы как есть, игра не ломается.
"""
import os, re, sys, glob, hashlib, io

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAME = os.path.join(ROOT, "game")
TLDIR = os.path.join(HERE, "tl")
sys.path.insert(0, HERE)

import rpcheck  # noqa: E402  (настраивает парсер)
import renpy  # noqa: E402
import renpy.translation  # noqa: E402

SKIP_FILES = {"gui.rpy", "options.rpy"}      # там переводить нечего
SAY_LIKE = {"text", "textbutton", "label", "voice", "image", "add", "play", "stop", "queue", "scene",
            "show", "hide", "font", "background", "style", "action", "tooltip", "hover_background"}


def key(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:6]


def flatten(nodes, out):
    """Все узлы в порядке текста (через get_children, как assign_names в движке)."""
    for n in nodes:
        n.get_children(out.append)
    return out


_serial = [0]


def assign_names(nodes, rel):
    for n in flatten(nodes, []):
        if getattr(n, "name", None) is None:
            n.name = (rel, 0, _serial[0]); _serial[0] += 1


def game_files():
    fs = [f for f in sorted(glob.glob(os.path.join(GAME, "*.rpy"))) if os.path.basename(f) not in SKIP_FILES]
    return fs


def parse_all():
    """[(filename, translate_nodes, menu_captions, say_lines)] в порядке загрузки движком."""
    translator = renpy.translation.ScriptTranslator()
    renpy.game.script.translator = translator
    result = []
    for fn in game_files():
        rel = os.path.relpath(fn, ROOT)
        os.chdir(ROOT)
        renpy.parser.parse_errors = []
        nodes = renpy.parser.parse(rel)
        if nodes is None:
            raise SystemExit("parse failed: %s %s" % (rel, renpy.parser.parse_errors))
        assign_names(nodes, rel)
        renpy.translation.restructure(nodes)
        flat = flatten(nodes, [])
        translator.take_translates(flat)
        tls = [n for n in flat if n.__class__.__name__ == "Translate" and n.language is None]
        menus = []
        say_lines = set()
        for n in flat:
            cn = n.__class__.__name__
            if cn == "Menu":
                for it in n.items:
                    if it[0]:
                        menus.append(it[0])
            if cn == "Say":
                say_lines.add(n.linenumber)
        result.append((rel, tls, menus, say_lines))
    return result


def scan_strings(rel, say_lines, menus):
    """Строки с кириллицей вне диалогов: подписи экранов, данные, _()-строки, пункты меню."""
    found = []
    src = open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")
    for i, line in enumerate(src, 1):
        t = line.strip()
        if not t or t.startswith("#") or i in say_lines or t.startswith('"""') or "sync_name(" in t:
            continue
        # пункт меню — уже собран из AST
        if re.match(r'^"(?:[^"\\]|\\.)*"\s*(?:if .*)?:\s*$', t):
            continue
        for m in re.finditer(r'"((?:[^"\\]|\\.)*)"', t):
            s = m.group(1)
            if re.search(r"[А-Яа-яЁё]", s):
                found.append((s, i))
    for cap in menus:
        found.append((cap, 0))
    return found


def unescape(s):
    """Строковый литерал Ren'Py/Python -> значение (для ключей строк)."""
    return s.replace('\\"', '"').replace("\\n", "\n")


def load_map(lang, name):
    p = os.path.join(TLDIR, lang, name + ".txt")
    m = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.rstrip("\n")
            if not line or line.startswith("#") or "\t" not in line:
                continue
            k, v = line.split("\t", 1)
            m[k.strip()] = v
    return m


def cmd_extract():
    os.makedirs(TLDIR, exist_ok=True)
    data = parse_all()
    dia = io.StringIO(); seen = set()
    strs = io.StringIO(); seen_s = set()
    n_d = n_s = 0
    for rel, tls, menus, say_lines in data:
        dia.write("## %s\n" % rel)
        for tl in tls:
            for n in tl.block:
                if n.__class__.__name__ == "Say":
                    k = key(n.what)
                    if k in seen:
                        continue
                    seen.add(k); n_d += 1
                    dia.write("%s\t%s\t%s\n" % (k, (n.who or "-"), n.what.replace("\n", "\\n")))
        strs.write("## %s\n" % rel)
        for s, ln in scan_strings(rel, say_lines, menus):
            v = unescape(s)
            k = key(v)
            if k in seen_s:
                continue
            seen_s.add(k); n_s += 1
            strs.write("%s\t%s\n" % (k, v.replace("\n", "\\n")))
    open(os.path.join(TLDIR, "dialogue_ru.txt"), "w", encoding="utf-8").write(dia.getvalue())
    open(os.path.join(TLDIR, "strings_ru.txt"), "w", encoding="utf-8").write(strs.getvalue())
    print("dialogue: %d unique lines, strings: %d unique" % (n_d, n_s))


def rq(s):
    """Строка -> литерал Python в двойных кавычках (old/new в translate strings читаются через eval)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _selftest_rq():
    for t in ['a  b', 'x "y"', 'line\nbreak', 'back\\slash', 'Школа №— [[данные изъяты].']:
        assert eval(rq(t)) == t, t


_selftest_rq()


def cmd_build(lang):
    dmap = load_map(lang, "dialogue")
    smap = load_map(lang, "strings")
    outdir = os.path.join(GAME, "tl", lang)
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "*.rpy")):
        os.remove(f)
    data = parse_all()
    missing_d, missing_s = [], []
    all_strings = []
    for rel, tls, menus, say_lines in data:
        if tls:
            out = io.StringIO()
            out.write("# Перевод диалогов %s (сгенерировано tools/tlgen.py).\n\n" % rel)
            for tl in tls:
                out.write("# %s:%d\ntranslate %s %s:\n\n" % (rel, tl.linenumber, lang, tl.identifier))
                for n in tl.block:
                    if n.__class__.__name__ == "Say":
                        out.write("    # %s\n" % n.get_code())
                    else:
                        out.write("    # %s\n" % n.get_code())
                for n in tl.block:
                    if n.__class__.__name__ == "Say":
                        en = dmap.get(key(n.what))
                        if en is None:
                            missing_d.append((rel, n.linenumber, n.what)); en = n.what
                        en = en.replace("\\n", "\n")
                        out.write("    %s\n" % n.get_code(dialogue_filter=lambda s, en=en: en))
                    else:
                        out.write("    %s\n" % n.get_code())
                out.write("\n")
            name = os.path.splitext(os.path.basename(rel))[0]
            open(os.path.join(outdir, name + ".rpy"), "w", encoding="utf-8").write(out.getvalue())
        for s, ln in scan_strings(rel, say_lines, menus):
            v = unescape(s)
            if v not in [x[1] for x in all_strings]:
                all_strings.append((rel, v, ln))
    out = io.StringIO()
    out.write("# Перевод строк интерфейса и данных (сгенерировано tools/tlgen.py).\n\ntranslate %s strings:\n\n" % lang)
    for rel, v, ln in all_strings:
        en = smap.get(key(v))
        if en is None:
            missing_s.append((rel, ln, v)); continue
        en = en.replace("\\n", "\n")
        out.write("    # %s:%d\n    old %s\n    new %s\n\n" % (rel, ln, rq(v), rq(en)))
    open(os.path.join(outdir, "strings.rpy"), "w", encoding="utf-8").write(out.getvalue())
    print("built %s: dialogue missing %d, strings missing %d" % (lang, len(missing_d), len(missing_s)))
    return missing_d, missing_s


def cmd_missing(lang):
    md, ms = cmd_build(lang)
    for rel, ln, s in md:
        print("D %s:%d\t%s\t%s" % (rel, ln, key(s), s.replace("\n", "\\n")))
    for rel, ln, s in ms:
        print("S %s:%d\t%s\t%s" % (rel, ln, key(s), s.replace("\n", "\\n")))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if cmd == "extract":
        cmd_extract()
    elif cmd == "build":
        cmd_build(sys.argv[2] if len(sys.argv) > 2 else "english")
    elif cmd == "missing":
        cmd_missing(sys.argv[2] if len(sys.argv) > 2 else "english")
