# VHS-эстетика «Simulacra»: плёночная картинка — строчная развёртка, живое
# зерно, покачивание ручной камеры и снег. Без служебных надписей.

init python:

    # Падающий снег поверх плёнки. Регистрируется с защитой от ошибок,
    # чтобы сбой эффекта никогда не останавливал запуск игры.
    try:
        _vhs_flake = Image("snowflake.png")
        renpy.image("snow_fall", SnowBlossom(_vhs_flake, count=24, border=80, speed=80))
    except Exception:
        renpy.image("snow_fall", Null())


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


# Живое плёночное зерно — быстрое мерцание.
transform vhs_grain:
    block:
        alpha 0.06
        pause 0.04
        alpha 0.11
        pause 0.03
        alpha 0.07
        pause 0.05
        repeat


screen vhs_overlay():
    zorder 1000

    add "vhs scanlines"
    add "vhs static" at vhs_grain
    add "snow_fall"


init 999 python:
    _vhs_overlays = list(config.overlay_screens or [])
    if "vhs_overlay" not in _vhs_overlays:
        _vhs_overlays.append("vhs_overlay")
    config.overlay_screens = _vhs_overlays
