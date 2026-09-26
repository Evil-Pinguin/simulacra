# =============================================================
#  SIMULACRA · 05_archive.rpy
#  «АРХИВ МАЙКА»: игрок сам перетаскивает факты друг к другу.
#  Совпадение → СВЯЗЬ ОБНАРУЖЕНА → новая запись + синхронизация.
#
#  Использование:  call screen mike_archive
# =============================================================

init python:

    # Пары фактов, которые что-то значат.
    COMBOS = [
        dict(a="f_drawing", b="f_11g",   sync=7,
             out="РИСУНОК найден на месте 11-G. Это не совпадение, это почерк."),
        dict(a="f_drawing", b="f_masha", sync=9,
             out="МАША рисовала. Круги — её почерк. Значит, она была там."),
        dict(a="f_11g",     b="f_masha", sync=6,
             out="МАША не числится в 11-G, но помнит коридор. Список врёт."),
        dict(a="f_stain",   b="f_drawing", sync=8,
             out="ПЯТНО повторяет форму круга. Кто-то стоял там долго."),
        dict(a="f_lee",     b="f_11g",   sync=5,
             out="ЛИ составил отчёт до инцидента. Он знал, что войдёт внутрь."),
        dict(a="f_redlamp", b="f_stain", sync=4,
             out="Красная лампа освещала пятно. Цвет — не кровь. Краска."),
    ]
    COMBO_BY_ID = dict((c["a"] + "|" + c["b"], c) for c in COMBOS)

    def combo_key(a, b):
        if a > b:
            a, b = b, a
        for k in COMBO_BY_ID:
            x, y = k.split("|")
            if (x, y) == (a, b) or (x, y) == (b, a):
                return k
        return None

    def try_link(a, b):
        """Попытка связать два факта. Возвращает True при успехе."""
        if not a or not b or a == b:
            return False
        key = combo_key(a, b)
        if key is None:
            add_sync(1)                       # даже ошибка что-то шевелит
            renpy.notify("Связь не подтверждена. Пока.")
            return False
        if key in store.archive_links:
            renpy.notify("Эта связь уже в архиве.")
            return False
        store.archive_links.append(key)
        add_sync(COMBO_BY_ID[key]["sync"])
        renpy.notify("СВЯЗЬ ОБНАРУЖЕНА")
        unlock("first_link")
        if len(store.archive_links) >= 4:
            unlock("detective")
        renpy.restart_interaction()
        return True

    def archive_items():
        """Только найденные фрагменты — остальных в архиве нет."""
        return [f for f in FRAGMENTS if known(f["id"])]

    def archive_home(fid):
        items = archive_items()
        if fid not in [f["id"] for f in items]:
            return (80, 200)
        i = [f["id"] for f in items].index(fid)
        return (80 + (i % 2) * 400, 220 + (i // 2) * 96)

    def archive_dragged(drags, drop):
        d = drags[0]
        d.snap(archive_home(d.drag_name)[0], archive_home(d.drag_name)[1], 0.2)
        if drop is None or drop.drag_name == d.drag_name:
            return
        try_link(d.drag_name, drop.drag_name)

# ── Экран архива ───────────────────────────────────────────

screen mike_archive():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))

    text "АРХИВ МАЙКА":
        xalign 0.03
        yalign 0.05
        size 30
        color "#7fe7ff"

    text "Перетащи один факт на другой":
        xalign 0.03
        yalign 0.11
        size 15
        color "#6b7d89"

    # ── факты ──
    draggroup:
        for f in archive_items():
            $ hx, hy = archive_home(f["id"])
            drag:
                drag_name f["id"]
                draggable True
                droppable True
                dragged archive_dragged
                xpos hx
                ypos hy
                frame:
                    background Solid("#0f1a21")
                    xysize (360, 72)
                    padding (14, 10)
                    vbox:
                        text f["title"] size 17 color "#7fe7ff"
                        text (f["num"] + " · " + f["src"]) size 13 color "#6b7d89"

    # ── выводы ──
    vbox:
        xalign 0.97
        yalign 0.14
        xsize 720
        spacing 12
        text "ВЫВОДЫ" size 16 color "#6b7d89"
        if not store.archive_links:
            text "связей пока нет" size 15 color "#33454f"
        for key in store.archive_links:
            if key in COMBO_BY_ID:
                $ c = COMBO_BY_ID[key]
                frame:
                    background Solid("#0d1117")
                    xsize 720
                    padding (14, 12)
                    vbox:
                        spacing 4
                        text (FRAGMENT_BY_ID[c["a"]]["title"] + "  +  " + FRAGMENT_BY_ID[c["b"]]["title"]):
                            size 14
                            color "#6b7d89"
                        text ("СВЯЗЬ ОБНАРУЖЕНА: " + c["out"]):
                            size 16
                            color "#ffffff"
                            xsize 690
                        text ("+" + str(c["sync"]) + "% СИНХРОНИЗАЦИИ"):
                            size 12
                            color "#8ef5b0"

    textbutton "ЗАКРЫТЬ":
        xalign 0.98
        yalign 0.96
        action Return()
