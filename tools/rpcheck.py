#!/usr/bin/env python3
"""Проверка синтаксиса .rpy настоящим парсером Ren'Py 8.0.3 без движка.

    bash tools/setup.sh            # один раз: скачает часть исходников Ren'Py
    python3 tools/rpcheck.py game/*.rpy

Что ловит: ошибки разбора Ren'Py-скрипта, ATL и языка экранов, синтаксис Python
внутри блоков. Чего не ловит: ошибки времени выполнения (неверные имена
переменных, свойства стилей, отсутствующие файлы — см. rpxref.py).
"""
import sys, os, types, re, collections

RENPY_SRC = os.environ.get("RENPY_SRC") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "renpy-src")
sys.path.insert(0, RENPY_SRC)


def stub(name, **attrs):
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m


stub("renpy.pydict", DictItems=lambda d: d.items(), find_changes=lambda a, b, c: (set(), set()))


def _letterlike(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9") or c == "_"


def match_logical_word(s, pos):
    start = pos; n = len(s); c = s[pos]
    if c == " ":
        pos += 1
        while pos < n and s[pos] == " ": pos += 1
    elif _letterlike(c):
        pos += 1
        while pos < n and _letterlike(s[pos]): pos += 1
    else:
        pos += 1
    word = s[start:pos]
    magic = (pos - start) >= 3 and word[0] == "_" and word[1] == "_"
    return word, magic, pos


stub("renpy.parsersupport", match_logical_word=match_logical_word)
stub("renpy.compat.dictviews", dictviews=None)

import renpy
import renpy.config
import renpy.object


class _Any(object):
    def __init__(self, *a, **k): pass
    def __call__(self, *a, **k): return _Any()
    def __getattr__(self, k): return _Any()


class _FakeBase(object):
    def __init__(self, *a, **k): pass
    def __call__(self, *a, **k): return _Any()
    def __getattr__(self, k):
        if k.startswith("__"): raise AttributeError(k)
        return _Any()


class _FakeMod(types.ModuleType):
    def __getattr__(self, k):
        if k.startswith("__"): raise AttributeError(k)
        sub = sys.modules.get(self.__name__ + "." + k)
        if sub is not None:
            return sub
        cls = type(k, (_FakeBase,), {})
        setattr(self, k, cls)
        return cls


for name in ["renpy.display", "renpy.display.layout", "renpy.display.behavior", "renpy.display.image",
             "renpy.display.im", "renpy.display.motion", "renpy.display.dragdrop", "renpy.display.viewport",
             "renpy.display.imagemap", "renpy.display.core", "renpy.display.screen", "renpy.display.predict",
             "renpy.text", "renpy.text.text", "renpy.display.transform", "renpy.display.transition"]:
    if name not in sys.modules:
        sys.modules[name] = _FakeMod(name)
renpy.display = sys.modules["renpy.display"]
renpy.text = sys.modules["renpy.text"]


class _Log(object):
    def open(self, *a, **k): return _Any()


renpy.log = _Log()
sys.modules["renpy.log"] = renpy.log
try:
    import renpy.ui
except Exception:
    _ui = _FakeMod("renpy.ui")

    class Addable(object):
        style_prefix = None
    _ui.Addable = Addable
    sys.modules["renpy.ui"] = _ui
    renpy.ui = _ui

import renpy.ast
import renpy.atl
import renpy.parser
import renpy.statements
import renpy.sl2.slparser as slparser

# ATL-свойства из display/transform.py (сам модуль не импортируем — тянет pygame)
src = open(os.path.join(RENPY_SRC, "renpy/display/transform.py"), encoding="utf-8").read()
for mm in re.finditer(r'^add_(?:gl_)?property\("(\w+)"', src, re.M):
    renpy.atl.PROPERTIES[mm.group(1)] = None
m = re.search(r"^ALIASES = \{.*?^\s*\}", src, re.S | re.M)
for mm in re.finditer(r'"(\w+)"\s*:', m.group(0)):
    renpy.atl.PROPERTIES[mm.group(1)] = None
for n in ["pause", "linear", "ease", "easein", "easeout"]:
    renpy.atl.warpers.setdefault(n, lambda x: x)
common = os.path.join(RENPY_SRC, "renpy/common")
for fn in os.listdir(common):
    if fn.endswith(".rpy"):
        t = open(os.path.join(common, fn), encoding="utf-8").read()
        for mm in re.finditer(r"renpy\.atl\.warpers\[\s*['\"](\w+)['\"]\s*\]", t):
            renpy.atl.warpers.setdefault(mm.group(1), lambda x: x)
        for mm in re.finditer(r"@renpy\.atl\.atl_warper\s*\n\s*def (\w+)", t):
            renpy.atl.warpers.setdefault(mm.group(1), lambda x: x)

import renpy.sl2.sldisplayables  # регистрирует операторы языка экранов
try:
    slparser.init()
except Exception:
    pass


class _Ctx(object):
    init_phase = True


class _Args(object):
    command = "lint"


class _Script(object):
    all_pyexpr = []
    all_pycode = []
    def record_pycode(self, *a, **k): pass


_game = types.ModuleType("renpy.game")
_game.exception_info = ""
_game.args = _Args()
_game.context = lambda: _Ctx()
_game.persistent = _Any()
_game.script = _Script()
sys.modules["renpy.game"] = _game
renpy.game = _game

_error_handlers = []
def _push_eh(h): _error_handlers.append(h)
def _pop_eh(): _error_handlers.pop()
def _rp_error(msg):
    if _error_handlers:
        _error_handlers[-1](msg)
    raise Exception(msg)


if not hasattr(renpy, "exports"):
    _ex = _FakeMod("renpy.exports")
    _ex.unelide_filename = lambda fn: fn
    _ex.push_error_handler = _push_eh
    _ex.pop_error_handler = _pop_eh
    _ex.error = _rp_error
    sys.modules["renpy.exports"] = _ex
    renpy.exports = _ex
renpy.error = _rp_error

import renpy.scriptedit
try:
    import renpy.python
    renpy.python.new_compile_flags
except Exception:
    _py = types.ModuleType("renpy.python")
    _py.new_compile_flags = 0
    sys.modules["renpy.python"] = _py
    renpy.python = _py
if not hasattr(renpy, "store"):
    _st = types.ModuleType("store")
    sys.modules["store"] = _st
    renpy.store = _st
_af = types.ModuleType("renpy.add_from")
_af.report_missing = lambda *a, **k: None
sys.modules["renpy.add_from"] = _af
renpy.add_from = _af

# свойства стилей: исполняем часть module/generate_styles.py с данными
_gs = open(os.path.join(RENPY_SRC, "module/generate_styles.py"), encoding="utf-8").read()
_gs_data = _gs[:_gs.index("class CodeGen(object):")]
_gs_data = _gs_data.replace("import setuplib", "").replace('module_gen = "module/" + setuplib.gen', 'module_gen = "module/gen"')
_gns = {"__name__": "generate_styles", "__file__": os.path.join(RENPY_SRC, "module/generate_styles.py"),
        "collections": collections, "os": os}
exec(compile(_gs_data, "generate_styles.py", "exec"), _gns)
_style = types.ModuleType("renpy.style")
_style.prefixed_all_properties = set(p + n for p in _gns["prefixes"] for n in _gns["all_properties"])
_style.all_properties = _gns["all_properties"]
_style.prefix_priority = dict((k, v.priority) for k, v in _gns["prefixes"].items())
sys.modules["renpy.style"] = _style
renpy.style = _style
renpy.config.basedir = os.getcwd()
renpy.config.renpy_base = RENPY_SRC

# операторы, объявленные в renpy/common через python early (play, voice, show screen, ...)
renpy.register_statement = renpy.statements.register
early_ns = {"renpy": renpy, "store": _Any(), "config": renpy.config, "_": lambda s: s, "os": os,
            "_audio_eval": lambda x: x, "voice": lambda *a, **k: None, "voice_sustain": lambda *a, **k: None,
            "_voice": _Any(), "_try_eval": lambda x, *a: x, "basestring": str}
for fn in sorted(os.listdir(common)):
    if not fn.endswith(".rpy"):
        continue
    text = open(os.path.join(common, fn), encoding="utf-8").read()
    if "python early" not in text:
        continue
    lines = text.split("\n"); i = 0
    while i < len(lines):
        if re.match(r"^python early( hide)?( in \w+)?:\s*$", lines[i]):
            j = i + 1; block = []
            while j < len(lines) and (lines[j].startswith("    ") or lines[j].strip() == ""):
                block.append(lines[j][4:]); j += 1
            try:
                exec(compile("\n".join(block), fn, "exec"), early_ns)
            except Exception as e:
                if fn not in ("000atl.rpy", "00icon.rpy", "00iconbutton.rpy", "00layeredimage.rpy"):
                    print("WARN early exec", fn, i, type(e).__name__, e)
            i = j
        else:
            i += 1


def compile_pycode(fn, nodes, errors):
    seen = set()

    def walk(o, depth=0):
        if id(o) in seen or depth > 40: return
        seen.add(id(o))
        if isinstance(o, renpy.ast.PyCode):
            mode = o.mode if o.mode in ("exec", "eval") else "exec"
            try:
                src = o.source
                if isinstance(src, renpy.ast.PyExpr) or isinstance(src, str):
                    compile(str(src), "%s:%s" % (fn, o.location[1] if o.location else "?"), mode)
            except SyntaxError as e:
                errors.append("PYTHON SYNTAX ERROR %s line %s: %s" % (fn, o.location[1] if o.location else "?", e))
            return
        if isinstance(o, (list, tuple)):
            for x in o: walk(x, depth + 1)
        elif isinstance(o, dict):
            for x in o.values(): walk(x, depth + 1)
        elif type(o).__module__.startswith("renpy"):
            names = set()
            for cls in type(o).__mro__:
                names.update(getattr(cls, "__slots__", ()))
            names.update(getattr(o, "__dict__", {}).keys())
            for n in names:
                try:
                    x = getattr(o, n)
                except Exception:
                    continue
                walk(x, depth + 1)
    walk(nodes)


def check(fn):
    renpy.parser.parse_errors = []
    try:
        nodes = renpy.parser.parse(fn)
    except Exception as e:
        import traceback
        print("FAIL", fn, "exception:", type(e).__name__, e)
        traceback.print_exc()
        return False
    if nodes is None or renpy.parser.parse_errors:
        print("FAIL", fn)
        for e in renpy.parser.parse_errors:
            print("   ", e)
        return False
    errors = []
    compile_pycode(fn, nodes, errors)
    if errors:
        print("FAIL", fn)
        for e in errors: print("   ", e)
        return False
    print("PASS %s (%d top-level statements)" % (fn, len(nodes)))
    return True


if __name__ == "__main__":
    ok = True
    for fn in sys.argv[1:]:
        ok = check(fn) and ok
    sys.exit(0 if ok else 1)
