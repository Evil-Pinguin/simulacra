# =============================================================
#  SIMULACRA · 03_focus.rpy
#  МЕХАНИКА «ФОКУС ВНИМАНИЯ»
#
#  Игрок смотрит на объекты. Что именно триггер — не знает.
#  Держит взгляд ~1.2 сек на нужном объекте → МИКРО-ТРИГГЕР:
#  экран едет, звук ломается, игрок получает фрагмент памяти.
#
#  Использование в главе:
#      scene bg corridor
#      call screen focus_scene(CORRIDOR_BG, CORRIDOR_HOTSPOTS)
#      # после Return() игра продолжается
# =============================================================

default focus_debug = False   # True — показывать рамки горячих зон

init python:

    FOCUS_TIME = 1.2          # секунд удержания взгляда
    FOCUS_TICK = 0.1          # шаг таймера в экране

    # Фон коридора (замени на свой файл)
    CORRIDOR_BG = "images/bg/corridor.jpg"

    # Координаты в пикселях для 1920×1080. trigger=True — микро-триггер.
    CORRIDOR_HOTSPOTS = [
        dict(id="door",    label="дверь",    x=883,  y=367, w=230, h=367,
             trigger=False, note="Обычная дверь. Таблица 3-Б. Рука холодная."),
        dict(id="drawing", label="рисунок",  x=1209, y=324, w=192, h=151,
             trigger=True, fragment="f_drawing",
             note="Красный круг вместо головы. Ты уже видел этот почерк."),
        dict(id="lockers", label="шкафчики", x=153,  y=302, w=384, h=496,
             trigger=False, note="Пусто. Все открыты. Как будто их вытряхнули."),
        dict(id="window",  label="окно",     x=1574, y=194, w=268, h=432,
             trigger=False, note="Двор пуст. Свет включён, а дня нет."),
        dict(id="camera",  label="камера",   x=691,  y=86,  w=153, h=108,
             trigger=False, note="Объектив повёрнут в стену. Кто-то не хотел смотреть."),
        dict(id="stain",   label="пятно",    x=1113, y=820, w=268, h=129,
             trigger=True, fragment="f_stain",
             note="Пятно на линолеуме. Формой — как тот круг на рисунке."),
    ]
    HOTSPOT_BY_ID = dict((h["id"], h) for h in CORRIDOR_HOTSPOTS)

    def focus_tick():
        """Вызывается таймером экрана 10 раз в секунду."""
        if store.focus_target is None:
            store.focus_charge = 0.0
            return
        store.focus_charge += FOCUS_TICK
        if store.focus_charge >= FOCUS_TIME:
            trigger_focus(store.focus_target)

    def trigger_focus(hid):
        h = HOTSPOT_BY_ID.get(hid)
        if h is None:
            return
        store.focus_target = None
        store.focus_charge = 0.0

        if h.get("trigger"):
            renpy.play(audio.simulacra_glitch, channel="sound")
            renpy.show_screen("glitch_overlay", h.get("bg", CORRIDOR_BG), "МИКРО-ТРИГГЕР")
            renpy.pause(1.0)
            renpy.hide_screen("glitch_overlay")
            if h.get("fragment"):
                if find_fragment(h["fragment"]):
                    unlock("focus_first")
        else:
            add_sync(1)

        if h.get("note"):
            renpy.say(None, h["note"])

# ── Экран исследования ─────────────────────────────────────

screen focus_scene(bg=CORRIDOR_BG, hotspots=CORRIDOR_HOTSPOTS):
    modal True
    add bg

    # Горячие зоны
    for h in hotspots:
        button:
            area (h["x"], h["y"], h["w"], h["h"])
            background (Solid("#7fe7ff4d") if focus_debug else None)
            hover_background Solid("#7fe7ff22")
            hovered SetVariable("focus_target", h["id"])
            unhovered SetVariable("focus_target", None)
            action NullAction()
            if focus_debug:
                text h["label"]:
                    xalign 0.5 yalign 0.5
                    size 16
                    color "#7fe7ff"
                    outlines [(2, "#000000", 0, 0)]

    # Накопление внимания
    if focus_target:
        $ charge = min(1.0, focus_charge / FOCUS_TIME)
        vbox:
            xalign 0.5
            yalign 0.96
            spacing 4
            text "▮▮▮▮▮▮▮▮▮▮":
                xalign 0.5
                size 18
                color "#33454f"
            bar:
                value charge
                range 1.0
                xsize 320
                ysize 4
                xalign 0.5

    timer FOCUS_TICK repeat True action Function(focus_tick)

    textbutton "ИДТИ ДАЛЬШЕ":
        xalign 0.98
        yalign 0.04
        action [SetVariable("focus_charge", 0.0), SetVariable("focus_target", None), Return()]

    key "K_ESCAPE" action [SetVariable("focus_charge", 0.0), SetVariable("focus_target", None), Return()]

# ── Искажение экрана (МИКРО-ТРИГГЕР) ───────────────────────

screen glitch_overlay(bg=None, caption=""):
    zorder 200
    if bg is not None:
        # два сдвинутых по цвету слоя = RGB-сплит
        add bg at rgb_split_a
        add bg at rgb_split_b
    add Solid("#7fe7ff", xysize=(1920, 1080)) at glitch_flash
    if caption:
        text caption:
            xalign 0.5
            yalign 0.5
            size 72
            color "#ffffff"
            outlines [(3, "#ff5555", 4, 0), (3, "#55ffff", -4, 0)]
            at glitch_text

transform rgb_split_a:
    xalign 0.5 yalign 0.5 alpha 0.35
    matrixcolor SaturationMatrix(3.0) * BrightnessMatrix(0.05)
    block:
        xoffset -7
        pause 0.05
        xoffset 6
        pause 0.05
        repeat

transform rgb_split_b:
    xalign 0.5 yalign 0.5 alpha 0.35
    matrixcolor SaturationMatrix(3.0) * BrightnessMatrix(0.05)
    block:
        xoffset 7
        pause 0.05
        xoffset -6
        pause 0.05
        repeat

transform glitch_flash:
    alpha 0.00
    block:
        alpha 0.10
        pause 0.05
        alpha 0.00
        pause 0.09
        repeat

transform glitch_text:
    block:
        xoffset 0
        pause 0.04
        xoffset 3
        pause 0.04
        xoffset -2
        pause 0.04
        repeat

# Заглушка звука: чтобы не падало без файла. Замени на свой:
#   define audio.simulacra_glitch = "audio/glitch.ogg"
define audio.simulacra_glitch = "<silence 0.3>"
