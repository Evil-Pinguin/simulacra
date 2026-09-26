# «Рисование воспоминания» — реконструкция инцидента 11-G в «Simulacra».
#
# Майк собирает воспоминание на холсте 3×3 из семи фрагментов-фишек:
# ребёнок, школа, рисунок, Майк, дверь, красная лампа, неизвестный объект.
# Правильных мест — шесть. Один объект в это воспоминание не входит.
#
# Результат: "true" (всё на месте, лишнего нет) / "partial" / "false".
# Подсказки складываются из найденных фрагментов — Архив → фрагменты → реконструкция.
#
#     call screen memory_canvas
#     $ memory_11g = canvas_result()

default canvas_placed = {}          # id фишки -> индекс клетки 0..8 или отсутствует

init python:

    CANVAS_PIECES = [
        dict(id="child",   label="ребёнок",       glyph="☺", color="#c8ffd8"),
        dict(id="school",  label="школа",         glyph="⌂", color="#9fd8b8"),
        dict(id="drawing", label="рисунок",       glyph="✎", color="#e0b060"),
        dict(id="mike",    label="Майк",          glyph="◉", color="#aad4ff"),
        dict(id="door",    label="дверь",         glyph="▯", color="#9fb8ac"),
        dict(id="redlamp", label="красная лампа", glyph="●", color="#d95a5a"),
        dict(id="unknown", label="неизвестный объект", glyph="◌", color="#7fd4a8"),
    ]
    CANVAS_PIECE_BY_ID = dict((p["id"], p) for p in CANVAS_PIECES)

    # Где что было на самом деле. Клетки: 0 1 2 / 3 4 5 / 6 7 8.
    CANVAS_TRUTH = {
        "redlamp": 2,
        "door": 4,
        "child": 5,
        "mike": 6,
        "drawing": 7,
        "school": 8,
    }

    # Геометрия (1920×1080).
    CV_GX, CV_GY, CV_CELL, CV_GAP = 1040, 150, 220, 12
    CV_PIECE = 200
    CV_TRAY = [(140, 170), (390, 170), (640, 170),
               (140, 410), (390, 410), (640, 410),
               (140, 650), (390, 650), (640, 650)]

    def cv_cell_pos(i):
        return (CV_GX + (i % 3) * (CV_CELL + CV_GAP),
                CV_GY + (i // 3) * (CV_CELL + CV_GAP))

    def cv_cell_rect(i):
        x, y = cv_cell_pos(i)
        return (x, y, CV_CELL, CV_CELL)

    def cv_piece_home(pid):
        idx = [p["id"] for p in CANVAS_PIECES].index(pid)
        return CV_TRAY[idx]

    def cv_piece_pos(pid):
        """Где фишка должна стоять сейчас: в клетке или дома в лотке."""
        cell = store.canvas_placed.get(pid)
        if cell is None:
            return cv_piece_home(pid)
        x, y = cv_cell_pos(cell)
        return (x + (CV_CELL - CV_PIECE) // 2, y + (CV_CELL - CV_PIECE) // 2)

    def cv_piece_in_cell(cell):
        for pid, c in store.canvas_placed.items():
            if c == cell:
                return pid
        return None

    def canvas_dragged(drags, drop):
        """Фишку отпустили. drop — клетка или None."""
        piece = drags[0]
        pid = piece.drag_name

        if drop is None or not drop.drag_name.startswith("cell"):
            store.canvas_placed.pop(pid, None)
        else:
            cell = int(drop.drag_name[4:])
            other = cv_piece_in_cell(cell)
            if other is not None and other != pid:
                # занято — прежняя фишка уезжает домой
                store.canvas_placed.pop(other, None)
                d = piece.drag_group.get_child_by_name(other)
                if d is not None:
                    hx, hy = cv_piece_home(other)
                    d.snap(hx, hy, 0.25)
            store.canvas_placed[pid] = cell

        x, y = cv_piece_pos(pid)
        piece.snap(x, y, 0.15)
        renpy.restart_interaction()

    def canvas_score():
        correct = 0
        for pid, cell in CANVAS_TRUTH.items():
            if store.canvas_placed.get(pid) == cell:
                correct += 1
        return correct

    def canvas_result():
        """"true" / "partial" / "false"."""
        correct = canvas_score()
        alien = "unknown" in store.canvas_placed
        if correct == len(CANVAS_TRUTH) and not alien:
            return "true"
        if correct >= 4:
            return "partial"
        return "false"

    def canvas_hints():
        """Подсказки из найденных фрагментов. Чем полнее Архив, тем легче собрать правду."""
        hints = []
        if frag_known("f_alarm") or frag_known("f_redlamp"):
            hints.append("Красный свет — вверху справа. Я смотрел на него снизу.")
        if frag_known("f_hand"):
            hints.append("Ребёнок стоял справа от двери. Дверь была в самой середине.")
        if frag_known("f_paper") or frag_known("f_visitor"):
            hints.append("Рисунок лежал внизу, посередине — между мной и школой.")
        if frag_known("f_erasure"):
            hints.append("Меня стёрли из нижнего левого угла. Значит, я там был.")
        if frag_known("f_field") or frag_known("f_corridor"):
            hints.append("Школа — там, где кончается поле. Внизу справа.")
        if frag_known("f_11g"):
            hints.append("В файле 11-G семь объектов. Один из них — не отсюда.")
        if not hints:
            hints.append("Я ничего не помню. Придётся рисовать наугад.")
        return hints


# ЭКРАН ХОЛСТА ###########################################################

style cv_text is default:
    font "fonts/game_mono.ttf"
    color "#9fb8ac"
    size 18

style cv_piece_frame is default:
    background Solid("#0a1014e6")
    padding (8, 8)

screen memory_canvas():

    modal True
    zorder 1200

    add Solid("#04070a")
    add "vhs scanlines"

    # Заголовок
    vbox:
        xpos 140
        ypos 50
        spacing 4
        text "ВОСПОМИНАНИЕ 11-G // РЕКОНСТРУКЦИЯ" style "cv_text" color "#c8ffd8" size 26
        text "Расставь объекты так, как это было. Не так, как удобно." style "cv_text" color "#517263" size 17

    # Сетка холста
    for i in range(9):
        frame:
            area cv_cell_rect(i)
            background Solid("#0a1014")
            padding (0, 0)
            text ("[[" + str(i) + "]"):
                xpos 6
                ypos 4
                style "cv_text"
                size 13
                color "#33473d"

    # Рамка холста
    add Frame(Solid("#33473d"), 0, 0) xpos (CV_GX - 8) ypos (CV_GY - 8) xysize (3 * CV_CELL + 2 * CV_GAP + 16, 4)
    add Frame(Solid("#33473d"), 0, 0) xpos (CV_GX - 8) ypos (CV_GY + 3 * CV_CELL + 2 * CV_GAP + 4) xysize (3 * CV_CELL + 2 * CV_GAP + 16, 4)
    add Frame(Solid("#33473d"), 0, 0) xpos (CV_GX - 8) ypos (CV_GY - 8) xysize (4, 3 * CV_CELL + 2 * CV_GAP + 16)
    add Frame(Solid("#33473d"), 0, 0) xpos (CV_GX + 3 * CV_CELL + 2 * CV_GAP + 4) ypos (CV_GY - 8) xysize (4, 3 * CV_CELL + 2 * CV_GAP + 16)

    # Перетаскивание: клетки — приёмники, фишки — фигуры.
    draggroup:

        for i in range(9):
            drag:
                drag_name ("cell" + str(i))
                draggable False
                droppable True
                pos cv_cell_pos(i)
                null width CV_CELL height CV_CELL

        for p in CANVAS_PIECES:
            drag:
                drag_name p["id"]
                draggable True
                droppable False
                drag_raise True
                dragged canvas_dragged
                pos cv_piece_pos(p["id"])

                frame:
                    style "cv_piece_frame"
                    xysize (CV_PIECE, CV_PIECE)
                    vbox:
                        xalign 0.5
                        yalign 0.5
                        spacing 6
                        text p["glyph"]:
                            xalign 0.5
                            style "cv_text"
                            size 72
                            color p["color"]
                        text p["label"]:
                            xalign 0.5
                            style "cv_text"
                            size 16
                            color p["color"]
                            text_align 0.5

    # Подсказки из Архива
    frame:
        xpos CV_GX
        ypos 880
        xsize (3 * CV_CELL + 2 * CV_GAP)
        ysize 160
        background Solid("#0a1014")
        padding (16, 12)
        vbox:
            spacing 4
            text "ИЗ ФРАГМЕНТОВ:" style "cv_text" color "#7fd4a8" size 15
            for h in canvas_hints()[:5]:
                text ("· " + h) style "cv_text" size 15

    # Состояние и завершение
    vbox:
        xpos 140
        ypos 900
        spacing 10

        text ("Размещено: " + str(len(canvas_placed)) + " из 7") style "cv_text" size 17

        textbutton "ЗАФИКСИРОВАТЬ ВОСПОМИНАНИЕ ▸":
            background None
            text_font "fonts/game_mono.ttf"
            text_size 22
            text_color "#c8ffd8"
            text_hover_color "#ffffff"
            text_insensitive_color "#33473d"
            sensitive (len(canvas_placed) >= 4)
            action Return("done")

        text "нельзя зафиксировать меньше четырёх объектов" style "cv_text" size 14 color "#33473d"


# ПОКАЗ РЕЗУЛЬТАТА ########################################################

transform cv_result_in:
    alpha 0.0
    linear 0.5 alpha 1.0

screen canvas_verdict(result):

    modal True
    zorder 1300

    add Solid("#04070a")
    add "vhs scanlines"

    $ _title = {"true": "ВОСПОМИНАНИЕ ПОДТВЕРЖДЕНО", "partial": "ЧАСТИЧНОЕ СОВПАДЕНИЕ", "false": "ЛОЖНОЕ ВОСПОМИНАНИЕ"}[result]
    $ _color = {"true": "#c8ffd8", "partial": "#e0b060", "false": "#d95a5a"}[result]
    $ _pct = {"true": "100", "partial": str(int(canvas_score() * 100 / 6)), "false": str(int(canvas_score() * 100 / 6))}[result]

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14
        at cv_result_in

        text _title style "cv_text" size 40 color _color xalign 0.5
        text ("Совпадение с файлом 11-G: " + _pct + "%") style "cv_text" size 20 xalign 0.5

        if result == "true":
            text "Архив изменён. Файл 11-G теперь совпадает с показаниями свидетеля 0117-М." style "cv_text" size 17 color "#7fd4a8" xalign 0.5
        elif result == "partial":
            text "Картина складывается — но не вся. Пустые клетки заполнит кто-то другой." style "cv_text" size 17 color "#7fd4a8" xalign 0.5
        else:
            text "Записано. Теперь это тоже правда — для кого-то." style "cv_text" size 17 color "#7fd4a8" xalign 0.5

        null height 30

        textbutton "ДАЛЬШЕ ▸":
            xalign 0.5
            background None
            text_font "fonts/game_mono.ttf"
            text_size 22
            text_color "#c8ffd8"
            text_hover_color "#ffffff"
            action Return("ok")


# СЦЕНАРНАЯ МЕТКА: холст + вердикт + последствия.
label memory_canvas_scene:

    $ canvas_placed = {}
    $ vhs_mode = False

    call screen memory_canvas

    $ memory_11g = canvas_result()

    call screen canvas_verdict(memory_11g)

    if memory_11g == "true":
        $ unlock_ach("ach_true_memory")
        $ add_sync(10)
        call fragment_found("f_redlamp")
    elif memory_11g == "partial":
        $ add_sync(5)
    else:
        $ unlock_ach("ach_false_memory")
        $ add_sync(-3)
        call fragment_found("f_false11g")

    return
