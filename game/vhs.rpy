# VHS-эстетика «Simulacra». Эффект плёнки включается только в записях —
# снах и воспоминаниях (vhs_mode). Обычная реальность чистая.
# Плюс атмосферные частицы: снег, пыль и тёмный снег главного меню.

# Плёнка сейчас крутится? Ставится из сценария.
default vhs_mode = False

init python:

    # Снег в два слоя: дальний — мелкий и медленный, ближний — крупнее
    # и быстрее. fast=True — снег уже идёт к моменту появления сцены.
    try:
        _flake_far = Image("snow far.png")
        _flake_near = Image("snow near.png")
        renpy.image("snow_real", Fixed(
            SnowBlossom(_flake_far, count=90, border=40, xspeed=(-30, 30), yspeed=(60, 110), fast=True),
            SnowBlossom(_flake_near, count=18, border=60, xspeed=(-70, 70), yspeed=(150, 240), fast=True),
        ))
    except Exception:
        renpy.image("snow_real", Null())

    # Пыль старого дома: крошечные пылинки, медленно плывущие в свете.
    try:
        _mote = Image("dust mote.png")
        renpy.image("dust_real", Fixed(
            SnowBlossom(_mote, count=26, border=30, xspeed=(-12, 12), yspeed=(7, 20), fast=True),
            SnowBlossom(_mote, count=12, border=30, xspeed=(-20, 20), yspeed=(12, 34), fast=True),
        ))
    except Exception:
        renpy.image("dust_real", Null())

    # Тёмный снег для главного меню.
    try:
        _flake_dark = Image("snow dark.png")
        renpy.image("snow_menu", SnowBlossom(_flake_dark, count=50, border=40, xspeed=(-25, 25), yspeed=(50, 100), fast=True))
    except Exception:
        renpy.image("snow_menu", Null())


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

    if vhs_mode:
        add "vhs scanlines"
        add "vhs static" at vhs_grain


init 999 python:
    _vhs_overlays = list(config.overlay_screens or [])
    for _scr in ("vhs_overlay", "journal_button"):
        if _scr not in _vhs_overlays:
            _vhs_overlays.append(_scr)
    config.overlay_screens = _vhs_overlays
