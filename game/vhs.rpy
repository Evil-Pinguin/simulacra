# VHS-эстетика «Simulacra».
# Всё, что игрок видит, — старая плёнка с воспоминаниями: строчная развёртка,
# зерно, лёгкое дрожание камеры и служебные надписи видеомагнитофона.

default vhs_seconds = 0
default vhs_clock = "0:00:00"
default vhs_tape = "MEM-01"

init python:

    def vhs_tick():
        store.vhs_seconds += 1
        s = store.vhs_seconds
        store.vhs_clock = "%d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60)

    # Падающий снег поверх плёнки. Регистрируется с защитой от ошибок,
    # чтобы сбой эффекта никогда не останавливал запуск игры.
    try:
        _vhs_flake = Image("snowflake.png")
        renpy.image("snow_fall", SnowBlossom(_vhs_flake, count=22, border=80, speed=55))
    except Exception:
        renpy.image("snow_fall", Null())


# Дыхание «плеча» — покачивание ручной камеры.
transform handheld:
    subpixel True
    block:
        linear 1.5 xoffset -7 yoffset 5
        linear 1.3 xoffset 6 yoffset -6
        linear 1.7 xoffset -3 yoffset 4
        linear 1.4 xoffset 5 yoffset -3
        linear 1.6 xoffset 0 yoffset 0
        repeat


# Мигание надписи PLAY.
transform vhs_blink:
    block:
        alpha 1.0
        pause 0.55
        alpha 0.15
        pause 0.35
        repeat


# Живое плёночное зерно.
transform vhs_grain:
    block:
        alpha 0.05
        pause 0.07
        alpha 0.09
        pause 0.05
        alpha 0.06
        pause 0.08
        repeat


screen vhs_overlay():
    zorder 1000

    add "vhs scanlines"
    add "vhs static" at vhs_grain
    add "snow_fall"

    text "PLAY ▶" at vhs_blink:
        xpos 70
        ypos 45
        size 34
        color "#eef0f4"
        outlines [(2, "#0c0c16", 0, 0)]

    text "[vhs_tape]":
        xpos 70
        ypos 1000
        size 28
        color "#d8dce2"
        outlines [(2, "#0c0c16", 0, 0)]

    text "SP  [vhs_clock]":
        xalign 0.98
        ypos 1000
        size 28
        color "#d8dce2"
        outlines [(2, "#0c0c16", 0, 0)]

    timer 1.0 repeat True action Function(vhs_tick)


init 999 python:
    _vhs_overlays = list(config.overlay_screens or [])
    if "vhs_overlay" not in _vhs_overlays:
        _vhs_overlays.append("vhs_overlay")
    config.overlay_screens = _vhs_overlays
