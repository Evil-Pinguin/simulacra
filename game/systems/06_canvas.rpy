# =============================================================
#  SIMULACRA · 06_canvas.rpy
#  NEURAL CANVAS: игрок раскладывает фрагменты на «холсте
#  памяти» и запускает реконструкцию.
#
#   • собрал верно      → НАСТОЯЩЕЕ ВОСПОМИНАНИЕ
#   • собрал на 60%+    → ЧАСТИЧНО (оба варианта по-своему правы)
#   • собрал криво      → ЛОЖНОЕ ВОСПОМИНАНИЕ (и оно останется
#                          в архиве: игрок будет помнить именно так)
#
#  Использование:  call screen memory_canvas("11-G")
# =============================================================

default canvas_result = None

init python:

    CANVAS_CELLS = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9"]

    # Холст 3×3: координаты клеток (1920×1080)
    CANVAS_ORIGIN = (980, 200)
    CANVAS_CELL_SIZE = (170, 130)
    CANVAS_GAP = 10

    def cell_pos(cid):
        i = CANVAS_CELLS.index(cid)
        col, row = i % 3, i // 3
        return (CANVAS_ORIGIN[0] + col * (CANVAS_CELL_SIZE[0] + CANVAS_GAP),
                CANVAS_ORIGIN[1] + row * (CANVAS_CELL_SIZE[1] + CANVAS_GAP))

    # Фрагменты для раскладки. target=None — «неизвестный объект»,
    # его можно ставить куда угодно (дает пол-очка).
    CANVAS_PIECES = [
        dict(id="p_lamp",    icon="💡", label="красная лампа",       target="c1"),
        dict(id="p_school",  icon="🏫", label="школа",               target="c2"),
        dict(id="p_child",   icon="🧒", label="ребёнок",             target="c4"),
        dict(id="p_door",    icon="🚪", label="дверь",               target="c5"),
        dict(id="p_drawing", icon="📄", label="рисунок",             target="c6"),
        dict(id="p_mike",    icon="👨", label="Майк",                target="c8"),
        dict(id="p_unknown", icon="❓", label="неизвестный объект",  target=None),
    ]
    PIECE_BY_ID = dict((p["id"], p) for p in CANVAS_PIECES)

    TRAY_ORIGIN = (120, 200)

    def tray_pos(pid):
        i = [p["id"] for p in CANVAS_PIECES].index(pid)
        return (TRAY_ORIGIN[0], TRAY_ORIGIN[1] + i * 84)

    def piece_start_pos(pid):
        cid = store.canvas_place.get(pid)
        if cid in CANVAS_CELLS:
            x, y = cell_pos(cid)
            return (x + 10, y + 40)
        return tray_pos(pid)

    def canvas_dragged(drags, drop):
        d = drags[0]
        pid = d.drag_name
        if drop is None:
            store.canvas_place.pop(pid, None)
            x, y = tray_pos(pid)
            d.snap(x, y, 0.2)
            return
        store.canvas_place[pid] = drop.drag_name
        d.snap(drop.x + 10, drop.y + 42, 0.15)

    def reconstruct_memory():
        place = store.canvas_place
        total = len([p for p in CANVAS_PIECES if p["target"]])
        placed_n = len([p for p in CANVAS_PIECES if place.get(p["id"])])
        scored = 0.0
        for p in CANVAS_PIECES:
            cell = place.get(p["id"])
            if not cell:
                continue
            if p["target"] is None:
                scored += 0.5          # неизвестный объект — куда угодно
            elif cell == p["target"]:
                scored += 1.0

        if placed_n < 4:
            store.canvas_result = dict(kind="none",
                head="НЕДОСТАТОЧНО ФРАГМЕНТОВ",
                body="Память не собирается. Нужно хотя бы четыре.")
            return

        if scored >= total:
            store.canvas_result = dict(kind="true",
                head="НАСТОЯЩЕЕ ВОСПОМИНАНИЕ",
                body="Реконструкция совпала с архивной схемой. Фрагмент зафиксирован.")
            find_fragment("f_redlamp")
            add_sync(10)
            unlock("true_memory")
        elif scored >= total * 0.6:
            store.canvas_result = dict(kind="partial",
                head="ЧАСТИЧНО ВЕРНО · %d/%d" % (int(scored), total),
                body="Оба варианта оказались по-своему правы. Разница записана как вариант памяти.")
            add_sync(5)
            unlock("partial_memory")
        else:
            store.canvas_result = dict(kind="false",
                head="ЛОЖНОЕ ВОСПОМИНАНИЕ",
                body="Ты собрал то, чего не было. Теперь оно в архиве — и ты будешь помнить именно так.")
            add_sync(-3)
            unlock("false_memory")

# ── Экран реконструкции ────────────────────────────────────

screen memory_canvas(mem_id="11-G"):
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))

    text ("ВОСПОМИНАНИЕ " + mem_id):
        xalign 0.03
        yalign 0.05
        size 30
        color "#7fe7ff"

    hbox:
        xalign 0.03
        yalign 0.11
        spacing 12
        $ done = len([p for p in CANVAS_PIECES if store.canvas_place.get(p["id"])])
        text "РЕКОНСТРУКЦИЯ" size 15 color "#6b7d89" yalign 0.5
        bar value done range (len(CANVAS_PIECES) + 3) xsize 240 ysize 6 yalign 0.5

    text "ЛОТОК":
        xalign 0.07
        yalign 0.16
        size 13
        color "#33454f"

    text "ХОЛСТ ПАМЯТИ":
        xalign 0.6
        yalign 0.16
        size 13
        color "#33454f"

    draggroup:
        # клетки холста
        for cid in CANVAS_CELLS:
            $ cx, cy = cell_pos(cid)
            drag:
                drag_name cid
                draggable False
                droppable True
                xpos cx
                ypos cy
                frame:
                    background Solid("#0e1419")
                    xysize CANVAS_CELL_SIZE
                    text cid:
                        size 12
                        color "#2c3b45"
                        xalign 0.06
                        yalign 0.06

        # фрагменты
        for p in CANVAS_PIECES:
            $ px, py = piece_start_pos(p["id"])
            drag:
                drag_name p["id"]
                draggable True
                droppable False
                dragged canvas_dragged
                xpos px
                ypos py
                frame:
                    background Solid("#0f1a21")
                    xysize (150, 60)
                    padding (10, 8)
                    hbox:
                        spacing 8
                        text p["icon"] size 20 yalign 0.5
                        text p["label"] size 14 color "#c9d6de" yalign 0.5

    hbox:
        xalign 0.03
        yalign 0.96
        spacing 12
        textbutton "РЕКОНСТРУИРОВАТЬ":
            action [Function(reconstruct_memory), Show("canvas_verdict")]
        textbutton "ОЧИСТИТЬ":
            action [SetVariable("canvas_place", {}), SetVariable("canvas_result", None)]
        textbutton "ЗАКРЫТЬ":
            action Return()

# ── Вердикт ────────────────────────────────────────────────

screen canvas_verdict():
    zorder 300
    frame:
        xalign 0.5
        yalign 0.5
        xysize (900, 320)
        background Solid("#0d1117")
        if store.canvas_result:
            $ r = store.canvas_result
            $ color = {"true": "#8ef5b0", "partial": "#ffb765",
                       "false": "#ff6b6b", "none": "#6b7d89"}.get(r["kind"], "#ffffff")
            vbox:
                xalign 0.5
                yalign 0.5
                spacing 16
                text r["head"]:
                    xalign 0.5
                    size 34
                    color color
                text r["body"]:
                    xalign 0.5
                    size 18
                    color "#c9d6de"
                    xsize 800
                    text_align 0.5
                textbutton "ПРИНЯТЬ":
                    xalign 0.5
                    action Hide("canvas_verdict")
