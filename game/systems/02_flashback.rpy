# =============================================================
#  SIMULACRA · 02_flashback.rpy
#  Быстрые кадры флешбека ПЕРЕД тем, как Майк заходит в дом.
#
#  Кадры положить в game/images/flashback/ (fb1.jpg … fb4.jpg).
#  Если файла нет — вместо кадра будет чёрный прямоугольник,
#  игра не упадёт.
#
#  Использование в главе:
#      call flashback_old_house
#      scene bg old_house
# =============================================================

init python:

    # (имя файла без расширения, подпись)
    FLASHBACK_FRAMES = [
        ("fb1", "ОБЪЕКТ: СТАРЫЙ ДОМ — ВХОД"),
        ("fb2", "КОРИДОР. СВЕТ ИЗ-ПОД ДВЕРИ"),
        ("fb3", "РИСУНОК. КРАСНЫЙ КРУГ"),
        ("fb4", "КРАСНАЯ ЛАМПА. КТО-ТО БЫЛ ВНУТРИ"),
        ("fb1", "МАЙК: «Я ЗДЕСЬ УЖЕ БЫЛ»"),
    ]

    def fb_displayable(name):
        for ext in (".jpg", ".png", ".webp"):
            path = "images/flashback/" + name + ext
            if renpy.exists(path):
                return path
        return Solid("#0a0a0a", xysize=(1920, 1080))

    def play_flashback(frames=None, per=0.22, jitter=True):
        """
        Быстрая нарезка: кадр мелькает, иногда «выпадает» в белое,
        иногда дёргается зумом. Ничего не объясняет — просто бьёт
        по памяти игрока.
        """
        frames = frames or FLASHBACK_FRAMES
        at = [flashback_jitter] if jitter else []
        renpy.scene(layer="master")
        renpy.show("black", what=Solid("#000000", xysize=(1920, 1080)), layer="master")

        for name, caption in frames:
            renpy.show("fb", what=fb_displayable(name), at_list=at, layer="master")
            renpy.show_screen("flashback_caption", caption)
            renpy.pause(per * (0.7 + renpy.random.random() * 0.7))

            if renpy.random.random() < 0.35:      # выпадение кадра
                renpy.hide("fb", layer="master")
                renpy.pause(0.06)
            if renpy.random.random() < 0.3:       # белая вспышка
                renpy.show("fbflash", what=Solid("#ffffff", xysize=(1920, 1080)),
                           layer="master", zorder=10)
                renpy.pause(0.04)
                renpy.hide("fbflash", layer="master")

        renpy.hide("fb", layer="master")
        renpy.hide("black", layer="master")
        renpy.hide_screen("flashback_caption")
        renpy.scene(layer="master")

label flashback_old_house:
    $ play_flashback()
    $ seen_flashback = True
    return

# ── Оформление нарезки ─────────────────────────────────────

transform flashback_jitter:
    xalign 0.5 yalign 0.5
    block:
        zoom 1.00
        linear 0.05 zoom 1.04
        linear 0.15 zoom 1.00
        xoffset 0
        linear 0.05 xoffset -3
        linear 0.05 xoffset 3
        linear 0.05 xoffset 0
        repeat

transform flashback_flicker:
    alpha 1.0
    block:
        pause 0.06
        alpha 0.7
        pause 0.04
        alpha 1.0
        repeat

screen flashback_caption(text):
    zorder 150
    text text:
        xalign 0.02
        yalign 0.93
        size 26
        color "#ffffff"
        outlines [(2, "#000000", 0, 0)]
        at flashback_flicker
