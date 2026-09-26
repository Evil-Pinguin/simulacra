# VHS-эстетика «Simulacra».
# Всё, что игрок видит, — старая плёнка с воспоминаниями: строчная развёртка,
# зерно, лёгкое дрожание камеры и служебные надписи видеомагнитофона.

default vhs_seconds = 0
default vhs_tape = "MEM-01"

init python:

    def vhs_tick():
        store.vhs_seconds += 1

    def vhs_timecode():
        s = store.vhs_seconds
        return "SP  %d:%02d:%02d" % (s // 3600, (s // 60) % 60, s % 60)


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


# Падающий снег поверх плёнки.
image snow_fall = SnowBlossom("snowflake.png", count=22, border=80, speed=55)


screen vhs_overlay():
    zorder 1000

    add "overlay scanlines"
    add "overlay static" at vhs_grain

    text "PLAY \u25b6" at vhs_blink:
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

    text "[vhs_timecode()]":
        xalign 0.98
        ypos 1000
        size 28
        color "#d8dce2"
        outlines [(2, "#0c0c16", 0, 0)]

    timer 1.0 repeat True action Function(vhs_tick)


init 999 python:
    if "vhs_overlay" not in config.overlay_screens:
        config.overlay_screens = list(config.overlay_screens) + ["vhs_overlay"]
