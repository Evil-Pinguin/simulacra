#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Процедурный саундтрек «Simulacra»: тёмный эмбиент, VHS, несущая 62.8 Гц.

    pip install numpy scipy soundfile
    python3 tools/soundtrack.py            # -> game/music/*.ogg (все треки)
    python3 tools/soundtrack.py menu dive  # только выбранные

Треки:
    menu      — MNEMOSYNE: дрон ре-минор, несущая 62.8 Гц, морзянка сигнала, далёкие удары
    office    — Смена: электропиано-пэд, тиканье часов, гул ламп, редкие щипки
    corridor  — Зелёный коридор: кластер малой секунды, школьный звонок, обратные вздохи
    dive      — Погружение: пульс несущей, арпеджио с детонацией плёнки, дыхание шума
    chase     — Силуэт: 128 BPM, остинато, удары, подъёмы
    ending    — Слияние: тёплый мажорный пэд, щипковая мелодия, несущая

Всё детерминировано (seed), любой трек можно перегенерировать.
"""
import os, sys
import numpy as np
from scipy import signal
import soundfile as sf

SR = 44100
CARRIER = 62.8            # несущая частота №117-У
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game", "music")


# ------------------------------------------------------------ базовые блоки
def tl(dur):
    return np.arange(int(dur * SR)) / SR


def note(n):
    """MIDI -> Гц."""
    return 440.0 * 2 ** ((n - 69) / 12.0)


def env(n, a, d, s, r, hold=None):
    """ADSR по количеству сэмплов n (attack/decay/release в секундах, sustain 0..1)."""
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    hold = n - a - d - r if hold is None else int(hold * SR)
    hold = max(hold, 0)
    e = np.concatenate([
        np.linspace(0, 1, max(a, 1)),
        np.linspace(1, s, max(d, 1)),
        np.full(hold, s),
        np.linspace(s, 0, max(r, 1)),
    ])
    if len(e) < n:
        e = np.concatenate([e, np.zeros(n - len(e))])
    return e[:n]


def osc(kind, f, dur, detune=0.0, wow=(0.0, 0.0), phase=0.0):
    """Осциллятор с медленной детонацией (wow = (глубина, Гц))."""
    t = tl(dur)
    fi = f * (1 + detune) * (1 + wow[0] * np.sin(2 * np.pi * wow[1] * t + phase))
    ph = 2 * np.pi * np.cumsum(fi) / SR
    if kind == "sine":
        return np.sin(ph)
    if kind == "tri":
        return signal.sawtooth(ph, 0.5)
    if kind == "saw":
        return signal.sawtooth(ph)
    if kind == "square":
        return signal.square(ph)
    raise ValueError(kind)


def lowpass(x, fc, order=2):
    sos = signal.butter(order, min(fc, SR / 2 - 100), btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, fc, order=2):
    sos = signal.butter(order, max(fc, 10), btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def bandpass(x, lo, hi, order=2):
    sos = signal.butter(order, [max(lo, 10), min(hi, SR / 2 - 100)], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def sweep_lowpass(x, fc_curve, chunk=2048):
    """Фильтр с плывущей частотой среза: по кускам, с сохранением состояния."""
    y = np.zeros_like(x)
    zi = None
    for i in range(0, len(x), chunk):
        fc = float(np.clip(fc_curve[min(i, len(fc_curve) - 1)], 40, SR / 2 - 200))
        sos = signal.butter(2, fc, btype="low", fs=SR, output="sos")
        if zi is None:
            zi = signal.sosfilt_zi(sos) * x[0]
        y[i:i + chunk], zi = signal.sosfilt(sos, x[i:i + chunk], zi=zi)
    return y


def noise(dur, rng):
    return rng.standard_normal(int(dur * SR))


def pink(dur, rng):
    """Розовый шум (фильтром Paul Kellet)."""
    w = noise(dur, rng)
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w)


def reverb(x, seconds, rng, mix=0.3, predelay=0.02, tone=4000):
    """Свёрточная реверберация с синтетическим импульсом (экспоненциально затухающий шум)."""
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 8, n))
    ir = lowpass(ir, tone)
    ir = np.concatenate([np.zeros(int(predelay * SR)), ir])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    wet = signal.fftconvolve(x, ir)[:len(x)]
    return x * (1 - mix) + wet * mix * 3.0


def delay(x, seconds, feedback=0.4, taps=8, mix=0.35):
    d = int(seconds * SR)
    y = np.zeros(len(x) + d * taps)
    y[:len(x)] += x
    g = 1.0
    for k in range(1, taps + 1):
        g *= feedback
        y[k * d:k * d + len(x)] += x * g
    return (x * (1 - mix) + y[:len(x)] * mix)


def pluck(f, dur, rng, damp=0.996, bright=0.5):
    """Карплус–Стронг: щипок струны."""
    n = int(dur * SR)
    d = int(SR / f)
    exc = rng.standard_normal(d)
    exc = lowpass(exc, 800 + 6000 * bright)
    x = np.zeros(n); x[:d] = exc
    a = np.zeros(d + 2); a[0] = 1; a[d] = -damp * 0.5; a[d + 1] = -damp * 0.5
    y = signal.lfilter([1.0], a, x)
    return y * env(n, 0.002, 0.05, 1.0, 0.3)


def bell(f, dur, ratio=3.47, index=4.0):
    """FM-колокол (школьный звонок, если ratio негармонический)."""
    t = tl(dur)
    idx = index * np.exp(-t * 1.5)
    y = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t))
    return y * np.exp(-t * 0.9) * env(len(t), 0.003, 0.0, 1.0, 0.5)


def kick(dur=0.6, f0=140, f1=42, punch=0.9):
    t = tl(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.tanh(np.sin(ph) * (1 + punch * 2) * np.exp(-t * 6)) * np.exp(-t * 5.5)


def place(buf, x, at, gain=1.0, pan=0.0):
    """Положить моно-сигнал в стерео-буфер в момент at (сек), pan -1..1."""
    i = int(at * SR)
    if i >= buf.shape[0]:
        return
    x = x[:buf.shape[0] - i]
    l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(x), 0] += x * gain * l
    buf[i:i + len(x), 1] += x * gain * r


def stereo_pad(chords, dur_each, kind="saw", voices=3, spread=0.006, wow=(0.002, 0.15), cutoff=1200, rng=None, gain=0.2):
    """Последовательность аккордов (списки MIDI) -> стерео-пэд с кроссфейдами."""
    total = dur_each * len(chords)
    buf = np.zeros((int(total * SR), 2))
    xf = min(2.5, dur_each / 3)
    for ci, ch in enumerate(chords):
        n = int((dur_each + xf) * SR)
        e = env(n, xf, 0.0, 1.0, xf)
        for m in ch:
            for v in range(voices):
                det = spread * (v - (voices - 1) / 2)
                x = osc(kind, note(m), n / SR, detune=det, wow=wow, phase=rng.uniform(0, 6.28))
                x = lowpass(x, cutoff, 2)
                pan = det / (spread * max(voices - 1, 1) / 2 + 1e-9) * 0.7 if voices > 1 else 0
                place(buf, x * e, max(0, ci * dur_each - xf / 2), gain / (len(ch) * voices), pan)
    return buf


# ------------------------------------------------------------ мастеринг
def finish(buf, rms_db=-24.0, peak_db=-1.5, loop_xfade=3.0):
    """Нормализация громкости, мягкий лимитер, бесшовный луп (хвост уходит в начало)."""
    buf = np.nan_to_num(buf)
    buf -= buf.mean(axis=0)
    n = int(loop_xfade * SR)
    if n > 0 and len(buf) > 3 * n:
        head = buf[:n].copy()
        tail = buf[-n:].copy()
        w = np.linspace(0, 1, n)[:, None]
        buf[-n:] = tail * (1 - w) + head * w      # конец плавно переходит в начало...
        buf = buf[n:]                              # ...а само начало отрезаем: луп замыкается без шва
    k = int(0.02 * SR)                             # от щелчка на самом старте
    buf[:k] *= np.linspace(0, 1, k)[:, None]
    rms = np.sqrt(np.mean(buf ** 2)) + 1e-9
    buf *= 10 ** (rms_db / 20) / rms
    buf = np.tanh(buf * 1.2) / 1.2
    peak = np.max(np.abs(buf)) + 1e-9
    lim = 10 ** (peak_db / 20)
    if peak > lim:
        buf *= lim / peak
    return buf.astype(np.float32)


def write(name, buf):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name + ".ogg")
    # пишем кусками: libsndfile на больших буферах Vorbis молча падает
    with sf.SoundFile(p, "w", samplerate=SR, channels=2, format="OGG", subtype="VORBIS") as f:
        for i in range(0, len(buf), 65536):
            f.write(buf[i:i + 65536])
    rms = 20 * np.log10(np.sqrt(np.mean(buf ** 2)) + 1e-9)
    print("%-10s %5.1fs  rms %5.1f dB  peak %5.1f dB  %4d KB" % (name, len(buf) / SR, rms, 20 * np.log10(np.max(np.abs(buf))), os.path.getsize(p) // 1024))


# ------------------------------------------------------------ треки
def track_menu():
    rng = np.random.default_rng(117)
    dur = 96.0
    buf = np.zeros((int(dur * SR), 2))
    t = tl(dur)
    # несущая 62.8 Гц, дышит
    sub = np.sin(2 * np.pi * CARRIER * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t))
    place(buf, sub, 0, 0.08)
    # дрон: D2, A2, D3 + F3 приходит и уходит (плюс октава выше — для «воздуха»)
    pad = stereo_pad([[38, 45, 50, 62], [38, 45, 53, 62], [38, 45, 50, 53, 65], [38, 45, 50, 62]], 24.0, "saw", voices=3,
                     spread=0.008, wow=(0.003, 0.11), cutoff=2200, rng=rng, gain=0.5)
    pad[:, 0] = sweep_lowpass(pad[:, 0], 1100 + 800 * np.sin(2 * np.pi * t / 30.0))
    pad[:, 1] = sweep_lowpass(pad[:, 1], 1100 + 800 * np.sin(2 * np.pi * t / 30.0 + 1.0))
    for c in range(2):
        pad[:, c] = reverb(pad[:, c], 4.0, rng, mix=0.35)
    buf += pad * 0.8
    # плёночный шип + слабый гул сети
    hiss = pink(dur, rng) * 0.02
    place(buf, hiss, 0, 1.0, -0.2); place(buf, pink(dur, rng) * 0.02, 0, 1.0, 0.2)
    place(buf, np.sin(2 * np.pi * 50 * t) * 0.006 + np.sin(2 * np.pi * 100 * t) * 0.003, 0)
    # сигнал: короткие блипы (морзянка «117») раз в ~11 с
    pattern = [0.08, 0.16, 0.08, 0.16, 0.08, 0.16, 0.08, 0.5, 0.08, 0.16, 0.08, 0.16, 0.08, 0.5, 0.25, 0.16, 0.25]
    for start in np.arange(6.0, dur - 6, 11.3):
        pos = start
        seq = np.zeros((int(6 * SR), 2))
        for k, d in enumerate(pattern):
            if k % 2 == 0:
                bl = np.sin(2 * np.pi * 1046.5 * tl(d)) * env(int(d * SR), 0.005, 0.0, 1.0, 0.02)
                place(seq, bl, pos - start, 1.0)
            pos += d
        for c in range(2):
            seq[:, c] = reverb(delay(seq[:, c], 0.37, 0.45, 6, 0.4), 3.0, rng, mix=0.4)
        i = int(start * SR)
        buf[i:i + len(seq)] += seq[:len(buf) - i] * 0.05
    # далёкие удары
    for start in np.arange(3.7, dur, 8.0):
        k = kick(1.6, 90, 38, 0.6)
        k = reverb(k, 2.5, rng, mix=0.5)
        place(buf, k, start, 0.2)
    return finish(buf, -25.0)


def track_office():
    rng = np.random.default_rng(2)
    dur = 96.0
    buf = np.zeros((int(dur * SR), 2))
    t = tl(dur)
    chords = [[50, 57, 60, 64, 67], [46, 53, 57, 60, 65], [41, 48, 53, 57, 60], [45, 52, 55, 60, 64]] * 3
    pad = stereo_pad(chords, 8.0, "tri", voices=2, spread=0.004, wow=(0.0015, 0.2), cutoff=2400, rng=rng, gain=0.5)
    trem = 0.85 + 0.15 * np.sin(2 * np.pi * 4.3 * t)
    pad *= trem[:, None]
    for c in range(2):
        pad[:, c] = reverb(pad[:, c], 2.2, rng, mix=0.25)
    buf += pad
    # гул ламп
    place(buf, (np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t) + 0.25 * np.sin(2 * np.pi * 300 * t)) * 0.004, 0)
    # часы: тик каждую секунду
    tick = highpass(noise(0.03, rng), 2500) * env(int(0.03 * SR), 0.001, 0.0, 1.0, 0.02)
    for s in np.arange(0.5, dur, 1.0):
        place(buf, tick, s, 0.06, 0.55)
    # редкие щипки, ре-минорная пентатоника
    scale = [62, 65, 67, 69, 72, 74, 77]
    s = 2.0
    while s < dur - 4:
        f = note(scale[rng.integers(len(scale))])
        p = pluck(f, 3.5, rng, damp=0.9975, bright=0.3)
        p = reverb(p, 3.0, rng, mix=0.45)
        place(buf, p, s, 0.16, rng.uniform(-0.5, 0.5))
        s += rng.uniform(3.0, 7.0)
    return finish(buf, -26.0)


def track_corridor():
    rng = np.random.default_rng(11)
    dur = 96.0
    buf = np.zeros((int(dur * SR), 2))
    t = tl(dur)
    # кластер: E2 + F2 (малая секунда), плывёт
    for m, det, pan in [(40, 0.0, -0.4), (41, 0.004, 0.4), (52, -0.005, 0.1), (53, 0.002, 0.0), (64, 0.003, -0.2)]:
        x = osc("saw", note(m), dur, detune=det, wow=(0.006, 0.07), phase=rng.uniform(0, 6.28))
        x = lowpass(x, 900, 2)
        x *= 0.55 + 0.45 * np.sin(2 * np.pi * t / 19.0 + pan)
        place(buf, x, 0, 0.06, pan)
    # школьный звонок раз в 13 с, негармонический, с детонацией
    for s in np.arange(5.0, dur - 8, 13.0):
        b = bell(note(76), 6.0, ratio=1.41, index=3.0)
        b = b * (1 + 0.004 * np.sin(2 * np.pi * 0.6 * tl(6.0)))
        b = reverb(b, 5.0, rng, mix=0.6, tone=3000)
        place(buf, b, s, 0.09, rng.uniform(-0.6, 0.6))
    # обратные вздохи: шум с нарастающей огибающей и обрывом
    for s in np.arange(2.0, dur - 4, 7.3):
        n = noise(3.0, rng)
        n = bandpass(n, 300, 1800)
        e = np.exp(np.linspace(-6, 0, len(n)))
        place(buf, n * e, s, 0.05, rng.uniform(-0.7, 0.7))
    # металлические щипки, кластер полутонов
    s = 4.0
    while s < dur - 3:
        f = note(rng.choice([64, 65, 71, 72, 77]))
        p = pluck(f, 2.0, rng, damp=0.992, bright=0.9)
        p = highpass(p, 400)
        p = reverb(p, 4.0, rng, mix=0.5)
        place(buf, p, s, 0.08, rng.uniform(-0.8, 0.8))
        s += rng.uniform(2.5, 9.0)
    # низкий удар каждые 5.3 с
    for s in np.arange(1.0, dur, 5.3):
        place(buf, reverb(kick(1.2, 70, 34, 0.4), 3.0, rng, mix=0.4), s, 0.14)
    # мерцание ламп: высокий треск
    for s in rng.uniform(0, dur, 40):
        z = highpass(noise(0.06, rng), 6000) * env(int(0.06 * SR), 0.001, 0.0, 1.0, 0.04)
        place(buf, z, s, 0.02, rng.uniform(-1, 1))
    return finish(buf, -25.0)


def track_dive():
    rng = np.random.default_rng(628)
    dur = 96.0
    buf = np.zeros((int(dur * SR), 2))
    t = tl(dur)
    # пульс несущей: дыхание 0.5 Гц
    gate = (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t - np.pi / 2)) ** 2
    place(buf, np.sin(2 * np.pi * CARRIER * t) * gate, 0, 0.22)
    # пэд под всем: Bb2 + F3
    pad = stereo_pad([[46, 53], [46, 53, 58], [45, 53], [46, 53]], 24.0, "saw", voices=3, spread=0.007,
                     wow=(0.004, 0.13), cutoff=700, rng=rng, gain=0.35)
    for c in range(2):
        pad[:, c] = reverb(pad[:, c], 3.5, rng, mix=0.3)
    buf += pad
    # арпеджио 80 BPM восьмыми: D3 F3 A3 D4 (плёночная детонация)
    step = 60.0 / 80 / 2
    arp = [50, 53, 57, 62, 57, 53]
    k = 0; s = 0.0
    while s < dur:
        m = arp[k % len(arp)]
        n = int(step * 1.6 * SR)
        x = osc("square", note(m), n / SR, wow=(0.006, 5.7)) * 0.5 + osc("tri", note(m), n / SR, wow=(0.006, 5.7))
        x = lowpass(x, 1400) * env(n, 0.01, 0.15, 0.35, 0.25)
        place(buf, x, s, 0.07, np.sin(k * 0.9) * 0.6)
        k += 1; s += step
    # пинг-понг задержка на арпеджио: копия с задержкой в другой канал
    d = int(step * 1.5 * SR)
    buf[d:, 1] += buf[:-d, 0] * 0.35
    buf[2 * d:, 0] += buf[:-2 * d, 1] * 0.2
    # дыхание шума
    br = bandpass(noise(dur, rng), 200, 2200)
    br = sweep_lowpass(br, 400 + 1800 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 23.0)))
    place(buf, br * gate, 0, 0.035, -0.3)
    # глитч каждые 16 с
    for s in np.arange(15.0, dur - 1, 16.0):
        g = noise(0.35, rng)
        g = np.round(g * 6) / 6                      # битчкраш
        g = bandpass(g, 900, 5000) * env(int(0.35 * SR), 0.001, 0.05, 0.4, 0.1)
        place(buf, g, s, 0.09, rng.uniform(-1, 1))
    return finish(buf, -22.0)


def track_chase():
    rng = np.random.default_rng(7)
    bpm = 128.0
    beat = 60.0 / bpm
    bars = 32
    dur = bars * 4 * beat
    buf = np.zeros((int(dur * SR), 2))
    # ударные
    k = kick(0.5, 150, 45, 1.0)
    hat = highpass(noise(0.05, rng), 7000) * env(int(0.05 * SR), 0.001, 0.0, 1.0, 0.04)
    snare = bandpass(noise(0.18, rng), 900, 4000) * env(int(0.18 * SR), 0.001, 0.02, 0.5, 0.12)
    for b in range(bars * 4):
        s = b * beat
        if b % 4 in (0, 2):
            place(buf, k, s, 0.42)
        if b % 8 == 7:
            place(buf, k, s + beat * 0.5, 0.3)
        if b % 4 in (1, 3):
            place(buf, snare, s, 0.3, 0.1)
        for h in range(2):
            place(buf, hat, s + h * beat / 2, 0.12 if h else 0.18, 0.4 if h else -0.2)
    # бас-остинато шестнадцатыми: D2 D2 D2 F2 D2 D2 G#2 D2
    pat = [38, 38, 38, 41, 38, 38, 44, 38, 38, 38, 41, 38, 46, 38, 44, 43]
    st = beat / 4
    i = 0; s = 0.0
    while s < dur:
        m = pat[i % len(pat)]
        n = int(st * 1.1 * SR)
        x = osc("saw", note(m), n / SR) + osc("square", note(m) / 2, n / SR) * 0.4
        cut = 500 + 3500 * np.exp(-tl(n / SR) * 14)
        x = sweep_lowpass(x, cut, 512) * env(n, 0.002, 0.08, 0.5, 0.05)
        place(buf, x, s, 0.16)
        i += 1; s += st
    # стабы: минорный аккорд на «и» второй доли каждые 2 такта
    for bar in range(0, bars, 2):
        s = bar * 4 * beat + beat * 1.5
        n = int(0.35 * SR)
        x = sum(osc("saw", note(m), n / SR, detune=0.004 * j) for j, m in enumerate([62, 65, 69, 72]))
        x = lowpass(x, 2500) * env(n, 0.003, 0.1, 0.3, 0.2)
        place(buf, reverb(x, 1.5, rng, mix=0.3), s, 0.08, rng.uniform(-0.5, 0.5))
    # подъём каждые 8 тактов
    for bar in range(0, bars, 8):
        s = bar * 4 * beat
        n = noise(8 * 4 * beat, rng)
        n = sweep_lowpass(bandpass(n, 200, 8000), 300 + 5000 * np.linspace(0, 1, len(n)) ** 2)
        place(buf, n * np.linspace(0, 1, len(n)) ** 3, s, 0.03)
    # верхний пэд напряжения: A3 + Bb3
    for m, pan in [(57, -0.5), (58, 0.5)]:
        x = lowpass(osc("saw", note(m), dur, wow=(0.003, 0.2)), 900)
        place(buf, x * (0.5 + 0.5 * np.sin(2 * np.pi * tl(dur) / 16.0)), 0, 0.03, pan)
    return finish(buf, -20.0, loop_xfade=0.05)


def track_ending():
    rng = np.random.default_rng(31)
    dur = 96.0
    buf = np.zeros((int(dur * SR), 2))
    t = tl(dur)
    chords = [[41, 48, 53, 57, 60, 67], [38, 50, 53, 57, 60], [46, 50, 53, 58, 60], [48, 52, 55, 60, 62]] * 2
    pad = stereo_pad(chords, 12.0, "tri", voices=3, spread=0.005, wow=(0.002, 0.17), cutoff=1300, rng=rng, gain=0.55)
    for c in range(2):
        pad[:, c] = reverb(pad[:, c], 3.5, rng, mix=0.35)
    buf += pad
    # несущая — совсем тихо, растворяется к концу
    place(buf, np.sin(2 * np.pi * CARRIER * t) * np.linspace(1, 0.2, len(t)), 0, 0.08)
    # мелодия щипками (фа мажор), медленно
    melody = [(0.5, 72), (3.0, 69), (5.5, 67), (8.5, 65), (12.5, 67), (15.0, 69), (18.5, 72), (23.0, 74),
              (26.0, 72), (29.0, 69), (33.0, 65), (37.0, 67), (40.5, 60), (45.0, 65),
              (49.0, 72), (52.0, 74), (55.0, 76), (59.0, 72), (63.0, 69), (66.5, 67), (70.0, 65),
              (74.0, 67), (78.0, 69), (83.0, 65), (89.0, 60)]
    for s, m in melody:
        p = pluck(note(m), 4.0, rng, damp=0.998, bright=0.35)
        p = reverb(p, 4.5, rng, mix=0.5)
        place(buf, p, s, 0.14, rng.uniform(-0.4, 0.4))
    # шип плёнки
    place(buf, pink(dur, rng) * 0.008, 0, 1.0, -0.3); place(buf, pink(dur, rng) * 0.008, 0, 1.0, 0.3)
    return finish(buf, -25.0)


TRACKS = {
    "menu": track_menu,
    "office": track_office,
    "corridor": track_corridor,
    "dive": track_dive,
    "chase": track_chase,
    "ending": track_ending,
}

if __name__ == "__main__":
    names = sys.argv[1:] or list(TRACKS)
    for n in names:
        write(n, TRACKS[n]())
