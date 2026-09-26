# VHS-эстетика «Simulacra»: плёночная картинка — строчная развёртка, живое
# зерно и покачивание ручной камеры. Плюс атмосферные частицы:
# реалистичный снег для зимних сцен и пыль для старого дома.

init python:

    # Снег в два слоя: дальний — мелкий и медленный, ближний — крупный
    # и быстрый. Показывается только в заснеженных сценах.
    try:
        _flake_far = Image("snow far.png")
        _flake_near = Image("snow near.png")
        renpy.image("snow_real", Fixed(
            SnowBlossom(_flake_far, count=70, border=60, xspeed=(-40, 40), yspeed=(70, 130)),
            SnowBlossom(_flake_near, count=16, border=130, xspeed=(-90, 90), yspeed=(200, 320)),
        ))
    except Exception:
        renpy.image("snow_real", Null())

    # Пыль старого дома: медленно плывущие пылинки в тёплом свете.
    try:
        _mote = Image("dust mote.png")
        renpy.image("dust_real", Fixed(
            SnowBlossom(_mote, count=30, border=40, xspeed=(-14, 14), yspeed=(8, 24)),
            SnowBlossom(_mote, count=14, border=40, xspeed=(-24, 24), yspeed=(16, 42)),
        ))
    except Exception:
        renpy.image("dust_real", Null())


# Дыхание «плеча» — покачивание ручной камеры. Слегка с запасом кадра,
# чтобы по краям никогда не проглядывала темная полоска.
transform handheld:
    subpixel True
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    zoom 1.04
    block:
        linear 0.8 xoffset -7 yoffset 5
        linear 0.7 xoffset 6 yoffset -6
        linear 0.9 xoffset -3 yoffset 4
        linear 0.7 xoffset 5 yoffset -3
        linear 0.8 xoffset 0 yoffset 0
        repeat


# Живое плёночное зерно — телевизионное мерцание, быстрое.
transform vhs_grain:
    block:
        alpha 0.06
        pause 0.025
        alpha 0.12
        pause 0.02
        alpha 0.08
        pause 0.03
        alpha 0.11
        pause 0.02
        repeat


screen vhs_overlay():
    zorder 1000

    add "vhs scanlines"
    add "vhs static" at vhs_grain


init 999 python:
    _vhs_overlays = list(config.overlay_screens or [])
    if "vhs_overlay" not in _vhs_overlays:
        _vhs_overlays.append("vhs_overlay")
    config.overlay_screens = _vhs_overlays
