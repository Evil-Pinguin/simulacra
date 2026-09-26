# «Фокус внимания» — механика исследования сцены в «Simulacra».
#
# Игрок водит взглядом (курсором) по деталям сцены. Какая из них —
# триггер, он не знает. Если задержать взгляд на нужной детали,
# экран искажается: МИКРО-ТРИГГЕР, и Майк получает фрагмент памяти.
#
# Экран только возвращает id детали (или "leave"); всё остальное —
# искажение, карточка, реплика — делает сценарий в цикле:
#
#     label ch1_corridor_look:
#         call screen focus_scene(CORRIDOR_HOTSPOTS, corridor_seen)
#         if _return == "leave":
#             jump дальше
#         call focus_examine(_return, corridor_seen, CORRIDOR_NOTES_1, "bg school")
#         jump ch1_corridor_look

default focus_charge = 0.0
default focus_target = None
default corridor_seen = []      # что уже рассмотрели в коридоре (первый визит)
default corridor_seen2 = []     # второй визит

init python:

    FOCUS_TIME = 1.4     # секунд удержания взгляда до срабатывания
    FOCUS_TICK = 0.1     # шаг таймера

    # Координаты для 1920×1080 на фоне "bg school".
    CORRIDOR_HOTSPOTS = [
        dict(id="door101", label="дверь 101", area=(230, 90, 210, 830), trigger=False),
        dict(id="door107", label="дверь 107", area=(1500, 80, 220, 840), trigger=True, fragment="f_paper"),
        dict(id="lockers", label="шкафчики", area=(640, 400, 170, 380), trigger=False),
        dict(id="lockers2", label="шкафчики", area=(1085, 420, 160, 320), trigger=False),
        dict(id="redbox", label="красный ящик", area=(1325, 400, 90, 270), trigger=False),
        dict(id="alarm", label="сигнализация", area=(1350, 170, 100, 100), trigger=True, fragment="f_alarm"),
        dict(id="end", label="конец коридора", area=(840, 400, 240, 250), trigger=False),
        dict(id="lamp", label="лампа", area=(880, 10, 170, 80), trigger=False),
        dict(id="stain", label="пятно на полу", area=(790, 870, 340, 200), trigger=False),
    ]
    HOTSPOT_BY_ID = dict((h["id"], h) for h in CORRIDOR_HOTSPOTS)

    # Первый визит (глава 1, сон на рабочем месте).
    CORRIDOR_NOTES_1 = {
        "door101": "Дверь 101. Матовое стекло, за ним темно. Ручка холодная — я её не трогал, но знаю, что холодная.",
        "door107": "Дверь 107. За ней кто-то очень тихо складывает бумагу. Лист за листом. Аккуратно, уголком внутрь.",
        "lockers": "Шкафчики. Все распахнуты. Пустые — как будто их вытряхнули в спешке.",
        "lockers2": "Такие же шкафчики. На одном — наклейка, детская. Слишком стёрлась, чтобы понять, что на ней было.",
        "redbox": "Красный ящик на стене. Стекло целое. Внутри должен быть шланг. Внутри ничего нет.",
        "alarm": "Красная коробочка под потолком. Сигнализация. Звонок идёт отсюда — и он не кончается.",
        "end": "Конец коридора тонет в темноте. Лампы там не горят. Или горят — но не для меня.",
        "lamp": "Лампа под потолком. Мигает — не в такт звонку. В такт чему-то другому.",
        "stain": "Пятно на линолеуме. Тёмное, вытянутое. Здесь долго кто-то стоял.",
    }

    # Второй визит (глава 2, ночь после отказа от калибровки).
    # То же место — но не то же. Игра этого не комментирует.
    CORRIDOR_NOTES_2 = {
        "door101": "Дверь 101. Стекло разбито. Осколки внутри, не снаружи.",
        "door107": "Дверь 107 приоткрыта. Внутри — парты. На каждой лежит сложенный лист.",
        "lockers": "Шкафчики закрыты. Все. В прошлый раз они были распахнуты — я это помню. Я думал, что помню.",
        "lockers2": "На шкафчике — наклейка. Теперь её видно: солнце с лицом. Детская рука.",
        "redbox": "Красный ящик. Стекло разбито. Шланг размотан по полу — в темноту.",
        "alarm": "Сигнализация молчит. Звонок идёт не отсюда. Звонок идёт из-под пола.",
        "end": "В конце коридора горит красный свет. Его не было. Или я не досмотрел.",
        "lamp": "Лампа не мигает. Горит ровно. Так даже хуже.",
        "stain": "Пятно стало больше. Или я стою ближе.",
    }

    def focus_tick(hotspots):
        """Таймер экрана. Возвращает id детали, когда взгляд удержан достаточно долго."""
        t = store.focus_target
        if t is None:
            store.focus_charge = 0.0
            return None
        store.focus_charge += FOCUS_TICK
        if store.focus_charge >= FOCUS_TIME:
            store.focus_charge = 0.0
            store.focus_target = None
            return t
        return None

    def focus_set_target(hid):
        if store.focus_target != hid:
            store.focus_charge = 0.0
        store.focus_target = hid


# ЭКРАН ИССЛЕДОВАНИЯ ######################################################

screen focus_scene(hotspots, seen, leave_text="ИДТИ ДАЛЬШЕ"):

    modal True

    # Горячие зоны поверх сцены (сам фон уже показан оператором scene).
    for h in hotspots:
        button:
            area h["area"]
            background None
            hover_background Solid("#c8ffd80e")
            hovered Function(focus_set_target, h["id"])
            unhovered Function(focus_set_target, None)
            action NullAction()

            if h["id"] in seen:
                text "◦":
                    xalign 0.5
                    yalign 0.5
                    size 22
                    color "#c8ffd855"
                    font "fonts/game_mono.ttf"

    # Что под взглядом, и сколько ещё держать.
    if focus_target:

        $ _cur = [x for x in hotspots if x["id"] == focus_target]
        $ _label = _cur[0]["label"] if _cur else ""
        $ _n = int(min(1.0, focus_charge / FOCUS_TIME) * 10)

        vbox:
            xalign 0.5
            ypos 0.90
            spacing 4

            text ("◈ " + _label):
                xalign 0.5
                size 22
                color "#c8ffd8"
                font "fonts/game_mono.ttf"
                outlines [(2, "#04070a", 0, 0)]

            text ("▮" * _n + "░" * (10 - _n)):
                xalign 0.5
                size 16
                color "#7fd4a8"
                font "fonts/game_mono.ttf"
                outlines [(2, "#04070a", 0, 0)]

    else:

        text "смотри":
            xalign 0.5
            ypos 0.92
            size 18
            color "#51726399"
            font "fonts/game_mono.ttf"
            outlines [(2, "#04070a", 0, 0)]

    timer FOCUS_TICK repeat True action Function(focus_tick, hotspots)

    textbutton (leave_text + " ▸"):
        xalign 0.97
        ypos 0.09
        background None
        text_font "fonts/game_mono.ttf"
        text_size 22
        text_color "#c8ffd8"
        text_hover_color "#ffffff"
        text_outlines [(2, "#04070a", 0, 0)]
        action [SetVariable("focus_charge", 0.0), SetVariable("focus_target", None), Return("leave")]


# МИКРО-ТРИГГЕР: ИСКАЖЕНИЕ ЭКРАНА ########################################

transform glitch_red:
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    alpha 0.45
    matrixcolor TintMatrix("#ff5050")
    block:
        xoffset -12
        pause 0.05
        xoffset 9
        pause 0.04
        xoffset -5
        pause 0.06
        repeat

transform glitch_cyan:
    anchor (0.5, 0.5)
    pos (0.5, 0.5)
    alpha 0.45
    matrixcolor TintMatrix("#50ffff")
    block:
        xoffset 12
        pause 0.05
        xoffset -9
        pause 0.04
        xoffset 5
        pause 0.06
        repeat

transform glitch_static:
    alpha 0.35
    block:
        alpha 0.55
        pause 0.03
        alpha 0.25
        pause 0.04
        alpha 0.6
        pause 0.02
        repeat

transform glitch_band:
    xpos 0
    ypos -60
    linear 0.9 ypos 1080

transform glitch_caption:
    block:
        xoffset 0
        pause 0.04
        xoffset 4
        pause 0.04
        xoffset -3
        pause 0.04
        repeat

screen glitch_overlay(bg):

    zorder 1400

    add bg at glitch_red
    add bg at glitch_cyan
    add "vhs static" at glitch_static
    add "vhs scanlines"
    add Solid("#ffffff22", xysize=(1920, 46)) at glitch_band

    text "МИКРО-ТРИГГЕР":
        xalign 0.5
        yalign 0.5
        size 64
        color "#ffffff"
        font "fonts/game_mono.ttf"
        outlines [(3, "#ff5050", 5, 0), (3, "#50ffff", -5, 0)]
        at glitch_caption


# СЦЕНАРНЫЕ ПОМОЩНИКИ ####################################################

# Искажение экрана + звук. Вызывать из сценария.
label focus_trigger(bg="bg school"):
    play sound "audio/glitch.wav"
    show screen glitch_overlay(bg)
    with vpunch
    pause 0.95
    hide screen glitch_overlay
    return

# Рассмотреть деталь: отметить, при триггере — исказить и выдать фрагмент, сказать реплику.
label focus_examine(hid, seen, notes, bg="bg school"):

    $ _h = HOTSPOT_BY_ID.get(hid)

    if _h is None:
        return

    if hid not in seen:
        $ seen.append(hid)

    if _h.get("trigger") and not frag_known(_h["fragment"]):
        call focus_trigger(bg)
        if not _in_replay:
            call fragment_found(_h["fragment"])
            $ unlock_ach("ach_focus")

    $ renpy.say(None, notes.get(hid, "…"))

    return
