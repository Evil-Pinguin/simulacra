# Флешбек «Simulacra»: быстрые кадры перед тем, как Майк входит в старый дом.
# Нарезка ничего не объясняет — она бьёт по памяти игрока, а не по сюжету.
#
# Использование в сценарии:
#     call flashback_house        # первый вход в дом (глава 1)
#     call flashback_return       # возвращение в дом (глава 2)
#     call flashback_school       # перед файлом 11-G (глава 3)

init python:

    # Кадр — (displayable, подпись). Подпись может быть пустой.
    # Существующие фоны берём крупным планом: zoom + смещение.

    def fb_crop(name, zoom=1.35, xa=0.5, ya=0.5):
        return Transform(name, zoom=zoom, xalign=xa, yalign=ya)

    FB_HOUSE = [
        (fb_crop("bg door", 1.5, 0.5, 0.55), "ДВЕРЬ. ПОЛЕ."),
        (fb_crop("bg hall", 1.3, 0.5, 0.5), "ПОЛОВИЦЫ. В ТАКТ."),
        ("fb hand", "МАЛЕНЬКАЯ РУКА"),
        (fb_crop("bg window", 1.9, 0.62, 0.86), "КЛЮЧ. ТЁПЛЫЙ."),
        ("fb paper", "ЛИСТ. Я НЕ РАЗВОРАЧИВАЛ."),
        (fb_crop("bg tv", 1.7, 0.36, 0.42), "ШИПЕНИЕ"),
        (fb_crop("bg school", 1.25, 0.5, 0.45), "ЗВОНОК. НЕ КОНЧАЕТСЯ."),
        ("fb redlamp", "КРАСНЫЙ СВЕТ"),
        (fb_crop("bg snow close", 1.2, 0.5, 0.5), ""),
        ("fb hand", "Я ЗДЕСЬ УЖЕ БЫЛ"),
    ]

    FB_RETURN = [
        (fb_crop("bg room", 1.3, 0.5, 0.5), "ДОМ"),
        (fb_crop("bg hall", 1.6, 0.5, 0.35), "ДВЕРЬ В КОНЦЕ"),
        (fb_crop("bg yard", 1.5, 0.7, 0.55), "ЗАБОР. КТО-ТО СТОИТ."),
        ("fb paper", "ЛИСТ. РАЗВЁРНУТ."),
        (fb_crop("bg tv", 1.7, 0.36, 0.42), ""),
        (fb_crop("bg flat", 1.4, 0.5, 0.6), "ЭТО НЕ ДЕТСТВО"),
    ]

    FB_SCHOOL = [
        (fb_crop("bg school", 1.2, 0.5, 0.5), "ШКОЛА"),
        ("fb redlamp", "КРАСНЫЙ СВЕТ"),
        ("fb hand", "ДВАДЦАТЬ ШЕСТЬ"),
        (fb_crop("bg school", 1.9, 0.72, 0.45), "ТРЕВОГА"),
        ("fb paper", "РИСУНОК"),
        (fb_crop("bg terminal", 1.6, 0.5, 0.4), "0117-М"),
        ("fb hand", "«НЕ БОЙСЯ»"),
    ]

    def play_flashback(frames, per=0.21):
        """
        Быстрая нарезка: кадр мелькает, иногда «выпадает» в чёрное,
        иногда сбивается в помехи, иногда — белая вспышка.
        Вызывать только из сценария.
        """
        rnd = renpy.random
        was_vhs = store.vhs_mode
        store.vhs_mode = True
        renpy.scene()
        renpy.show("fbbase", what=Solid("#000000"))
        renpy.pause(0.15, hard=True)

        for what, caption in frames:
            renpy.show("fbframe", what=what, at_list=[fb_jitter])
            if caption:
                renpy.show_screen("flashback_caption", caption)
            else:
                renpy.hide_screen("flashback_caption")
            renpy.pause(per * (0.75 + rnd.random() * 0.7), hard=True)

            r = rnd.random()
            if r < 0.30:
                # выпадение кадра
                renpy.hide("fbframe")
                renpy.pause(0.05, hard=True)
            elif r < 0.55:
                # помехи
                renpy.show("fbstatic", what="vhs static", zorder=5)
                renpy.pause(0.06, hard=True)
                renpy.hide("fbstatic")
            elif r < 0.75:
                # белая вспышка
                renpy.show("fbflash", what=Solid("#ffffff"), zorder=10)
                renpy.pause(0.04, hard=True)
                renpy.hide("fbflash")

        renpy.hide_screen("flashback_caption")
        renpy.show("fbstatic", what="vhs static", zorder=5)
        renpy.pause(0.12, hard=True)
        renpy.scene()
        renpy.show("fbbase", what=Solid("#000000"))
        renpy.pause(0.35, hard=True)
        store.vhs_mode = was_vhs


# Дёрганье кадра: микро-зум и сдвиг, как у плёнки на лентопротяге.
transform fb_jitter:
    subpixel True
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    block:
        zoom 1.00 xoffset 0
        linear 0.05 zoom 1.04 xoffset -4
        linear 0.06 zoom 1.01 xoffset 3
        linear 0.05 zoom 1.03 xoffset 0
        repeat

transform fb_caption_flicker:
    alpha 1.0
    block:
        pause 0.07
        alpha 0.55
        pause 0.04
        alpha 1.0
        pause 0.05
        alpha 0.8
        pause 0.03
        repeat

screen flashback_caption(caption):
    zorder 150
    text caption:
        xpos 0.04
        ypos 0.88
        size 30
        color "#ffffff"
        font "fonts/game_mono.ttf"
        outlines [(3, "#000000", 0, 0)]
        at fb_caption_flicker
    text "▮ REC":
        xalign 0.96
        ypos 0.10
        size 22
        color "#d95a5a"
        font "fonts/game_mono.ttf"
        at fb_caption_flicker


# СЦЕНАРНЫЕ МЕТКИ ########################################################

# Первый вход в дом: Майк ещё не понимает, откуда он знает эти кадры.
label flashback_house:
    $ play_flashback(FB_HOUSE)
    $ unlock_replay("house")
    return

# Возвращение: короче, злее, с тем, что он уже видел сам.
label flashback_return:
    $ play_flashback(FB_RETURN, per=0.17)
    return

# Перед файлом 11-G: школа собирается из кусков.
label flashback_school:
    $ play_flashback(FB_SCHOOL, per=0.19)
    $ unlock_replay("school")
    return


# Повтор из меню «АРХИВ»: только нарезка, без сюжета.
label replay_flashback_house:
    $ vhs_mode = True
    $ play_flashback(FB_HOUSE)
    scene black
    $ vhs_mode = False
    return

label replay_flashback_school:
    $ vhs_mode = True
    $ play_flashback(FB_SCHOOL, per=0.19)
    scene black
    $ vhs_mode = False
    return
