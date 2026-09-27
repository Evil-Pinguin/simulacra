#!/usr/bin/env python3
"""Пакетная озвучка реплик: собрать текст пачками с маркером-разделителем,
а потом разрезать один длинный wav на отдельные реплики по этому маркеру.

Маркер «Стоп. Предупреждение. Стоп.» даёт узнаваемый ритм:
короткий всплеск — длинный — короткий, с паузами вокруг. По нему режем.

    python3 tools/voice_split.py plan kim            # тексты пачек -> tools/voice_batches/kim_N.txt
    python3 tools/voice_split.py split kim_0.wav kim_0.txt game/voice   # нарезать пачку

Реплики берутся из сценария: строка `$ kim_voice("kim_NNN")` над `k "..."`.
"""
import os, re, sys, json

MARKER = "Стоп. Предупреждение. Стоп."
GAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game")
FILES = ["script.rpy", "chapter2.rpy", "chapter3.rpy", "flirt.rpy"]


def spoken(text):
    return re.sub(r"\{[^}]*\}", "", text).replace("%%", "%").replace("[[", "[").replace('\\"', '"')


def collect(prefix):
    """[(id, text)] в порядке сценария: `$ <prefix>_voice("<id>")` над репликой."""
    out = []
    for f in FILES:
        p = os.path.join(GAME, f)
        if not os.path.exists(p):
            continue
        lines = open(p, encoding="utf-8").read().split("\n")
        for i, l in enumerate(lines):
            m = re.match(r'^\s*\$ %s_voice\("(\w+)"\)\s*$' % prefix, l)
            if not m or i + 1 >= len(lines):
                continue
            m2 = re.match(r'^\s*\w+ "((?:[^"\\]|\\.)*)"\s*$', lines[i + 1])
            if m2:
                out.append((m.group(1), spoken(m2.group(1))))
    return out


def batches(items, max_lines=11, max_chars=1300):
    cur, res = [], []
    for it in items:
        if cur and (len(cur) >= max_lines or sum(len(t) + len(MARKER) + 2 for _, t in cur) + len(it[1]) > max_chars):
            res.append(cur); cur = []
        cur.append(it)
    if cur:
        res.append(cur)
    return res


def batch_text(items):
    return ("\n\n" + MARKER + "\n\n").join(t for _, t in items)


# ---------------------------------------------------------------- audio
def bursts_of(data, sr, win=0.01, thr_ratio=0.03, join_gap=0.12):
    import numpy as np
    w = int(sr * win); n = len(data) // w
    rms = np.sqrt(np.mean(data[:n * w].reshape(n, w) ** 2, axis=1))
    thr = max(rms.max() * thr_ratio, 1e-4)
    loud = rms >= thr
    runs = []; i = 0
    while i < n:
        if loud[i]:
            j = i
            while j < n and loud[j]: j += 1
            runs.append([i * win, j * win]); i = j
        else:
            i += 1
    merged = []
    for a, b in runs:
        if merged and a - merged[-1][1] < join_gap:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return merged, thr


def find_markers(bursts):
    """Кандидаты маркера: тройки всплесков короткий(0.15–0.8) — длинный(0.6–2.0) — короткий(0.15–0.8)."""
    cands = []
    for k in range(len(bursts) - 2):
        (a1, b1), (a2, b2), (a3, b3) = bursts[k], bursts[k + 1], bursts[k + 2]
        d1, d2, d3 = b1 - a1, b2 - a2, b3 - a3
        g1, g2 = a2 - b1, a3 - b2
        if 0.15 <= d1 <= 0.8 and 0.6 <= d2 <= 2.0 and 0.15 <= d3 <= 0.8 and 0.08 <= g1 <= 0.9 and 0.08 <= g2 <= 0.9:
            cands.append((a1, b3, k))
    return cands


def split_batch(wav, items, outdir, prefix_ok=True):
    import numpy as np, soundfile as sf
    data, sr = sf.read(wav, dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    total = len(data) / sr
    bursts, thr = bursts_of(data, sr)
    cands = find_markers(bursts)
    n = len(items)
    need = n - 1
    # ожидаемые позиции маркеров по доле символов
    weights = [len(t) + 8 for _, t in items]
    mk = len(MARKER) + 8
    cum, pos = 0.0, []
    tot = sum(weights) + mk * need
    for wgt in weights[:-1]:
        cum += wgt
        pos.append((cum + mk / 2.0) / tot * total)
        cum += mk
    chosen = []
    used = set()
    for p in pos:
        best = None
        for c in cands:
            if c[2] in used:
                continue
            mid = (c[0] + c[1]) / 2
            if best is None or abs(mid - p) < abs((best[0] + best[1]) / 2 - p):
                best = c
        if best is None or abs((best[0] + best[1]) / 2 - p) > max(2.5, 0.15 * total):
            return None, "marker not found near %.1fs (cands=%d)" % (p, len(cands))
        chosen.append(best); used.add(best[2])
    chosen.sort()
    bounds = []
    prev = 0.0
    for a, b, _ in chosen:
        bounds.append((prev, a)); prev = b
    bounds.append((prev, total))
    os.makedirs(outdir, exist_ok=True)
    report = []
    for (vid, text), (a, b) in zip(items, bounds):
        seg = data[int(a * sr): int(b * sr)].copy()
        idx = np.where(np.abs(seg) > thr)[0]
        if len(idx) == 0:
            return None, "empty segment for %s" % vid
        pad = int(sr * 0.08)
        seg = seg[max(0, idx[0] - pad): min(len(seg), idx[-1] + pad)]
        f = int(sr * 0.015)
        seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        dur = len(seg) / sr
        rate = len(text) / dur
        report.append((vid, round(dur, 2), round(rate, 1)))
        sf.write(os.path.join(outdir, vid + ".ogg"), seg, sr, format="OGG", subtype="VORBIS")
    return report, "ok (%d markers of %d candidates)" % (len(chosen), len(cands))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        prefix = sys.argv[2] if len(sys.argv) > 2 else "kim"
        items = collect(prefix)
        extra = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_extra_%s.json" % prefix)
        if os.path.exists(extra):
            items += [tuple(x) for x in json.load(open(extra, encoding="utf-8"))]
        bs = batches(items)
        outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_batches")
        os.makedirs(outdir, exist_ok=True)
        for i, b in enumerate(bs):
            open(os.path.join(outdir, "%s_%d.txt" % (prefix, i)), "w", encoding="utf-8").write(batch_text(b))
            json.dump(b, open(os.path.join(outdir, "%s_%d.json" % (prefix, i)), "w", encoding="utf-8"), ensure_ascii=False)
        print("%d lines, %d batches: %s" % (len(items), len(bs), [len(b) for b in bs]))
    elif cmd == "split":
        wav, meta, outdir = sys.argv[2], sys.argv[3], sys.argv[4]
        items = [tuple(x) for x in json.load(open(meta, encoding="utf-8"))]
        rep, msg = split_batch(wav, items, outdir)
        print(os.path.basename(wav), msg)
        if rep:
            for r in rep:
                print("   ", r)
        sys.exit(0 if rep else 1)
