# =============================================================
#  SIMULACRA · 08_extras.rpy
#  Мета-меню: Character Gallery / Achievement / Ending List /
#  Scene Replay / Choice History / New Game+
#
#  В главное меню (screens.rpy, screen navigation) добавить:
#      textbutton "ARCHIVE" action ShowMenu("extras_menu")
# =============================================================

default persistent.endings_seen = []
default persistent.choice_log = []
default persistent.gallery_seen = []
default persistent.ng_plus = False
default persistent.memory_fragments = []
default persistent.memory_links = []
default persistent.memory_sync = 0

init python:

    ENDINGS = [
        dict(id="e_true",   name="НАСТОЯЩЕЕ",  hint="Собрал истинное воспоминание 11-G."),
        dict(id="e_false",  name="ЛОЖНОЕ",     hint="Жил чужой версией и не узнал об этом."),
        dict(id="e_merged", name="СЛИЯНИЕ",    hint="Дошёл до 100% синхронизации."),
        dict(id="e_alone",  name="ОДИН",       hint="Разорвал связь до конца."),
    ]

    # Сцены для Scene Replay. label должен быть «безопасным для
    # повтора»: без side-effect'ов, которые ломают состояние.
    REPLAYS = [
        dict(label="flashback_old_house", name="ФЛЕШБЕК · СТАРЫЙ ДОМ"),
        dict(label="memory_conflict_017", name="КОНФЛИКТ · ФРАГМЕНТ #017"),
    ]

    # Галерея персонажей. Файлы: images/gallery/<id>.jpg
    GALLERY = [
        dict(id="mike", name="МАЙК",  role="носитель"),
        dict(id="will", name="УИЛЛ",  role="источник"),
        dict(id="kim",  name="КИМ",   role="напарница"),
        dict(id="lee",  name="ЛИ",    role="азаит"),
        dict(id="masha", name="МАША", role="???", need="f_masha"),
    ]

    def log_choice(text):
        """Пишем выбор в Choice History (внутри menu — после варианта)."""
        entry = "Круг %d · %s" % (store.pass_number, text)
        persistent.choice_log.append(entry)
        if len(persistent.choice_log) > 200:
            persistent.choice_log = persistent.choice_log[-200:]

    def unlock_ending(eid):
        if eid in persistent.endings_seen:
            return
        persistent.endings_seen.append(eid)
        renpy.notify("КОНЦОВКА ОТКРЫТА")

    def start_ng_plus():
        """New Game+: воспоминания остаются, реальность — нет."""
        persistent.ng_plus = True
        persistent.memory_fragments = list(store.found_fragments)
        persistent.memory_links = list(store.archive_links)
        persistent.memory_sync = store.sync_level
        start_new_pass(keep_memory=True)
        renpy.notify("NEW GAME+ · круг %d" % store.pass_number)

    def gallery_open(cid):
        path = "images/gallery/" + cid + ".jpg"
        return renpy.exists(path)

# ── Меню extras ────────────────────────────────────────────

screen extras_menu():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))
    text "SIMULACRA · ARCHIVE":
        xalign 0.5
        yalign 0.08
        size 36
        color "#7fe7ff"

    grid 2 3:
        xalign 0.5
        yalign 0.58
        spacing 26

        textbutton "👥 CHARACTER GALLERY" action ShowMenu("character_gallery") xsize 520 ysize 70
        textbutton "🏆 ACHIEVEMENT"       action ShowMenu("achievements_screen") xsize 520 ysize 70
        textbutton "🎬 ENDING LIST"       action ShowMenu("endings_screen") xsize 520 ysize 70
        textbutton "🔁 SCENE REPLAY"      action ShowMenu("scene_replay_screen") xsize 520 ysize 70
        textbutton "🧾 CHOICE HISTORY"    action ShowMenu("choice_history") xsize 520 ysize 70
        textbutton "✚ NEW GAME+"         action Confirm("Начать новый круг? Воспоминания останутся.",
                                                        [Function(start_ng_plus), Start()]) xsize 520 ysize 70

    textbutton "НАЗАД":
        xalign 0.02
        yalign 0.96
        action Return()

# ── Галерея персонажей ─────────────────────────────────────

screen character_gallery():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))
    text "CHARACTER GALLERY":
        xalign 0.5 yalign 0.06 size 30 color "#7fe7ff"

    grid 3 2:
        xalign 0.5
        yalign 0.55
        spacing 24
        for c in GALLERY:
            $ opened = (c.get("need") is None) or known(c["need"])
            $ has_img = gallery_open(c["id"])
            frame:
                xysize (520, 330)
                background Solid("#0d1117")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 10
                    if opened and has_img:
                        add ("images/gallery/" + c["id"] + ".jpg"):
                            xalign 0.5
                            xsize 200
                    else:
                        add Solid("#131b21", xysize=(200, 200)):
                            xalign 0.5
                    text (c["name"] if opened else "???"):
                        xalign 0.5 size 24 color ("#ffffff" if opened else "#33454f")
                    text (c["role"] if opened else "—"):
                        xalign 0.5 size 14 color "#6b7d89"

    textbutton "НАЗАД" action Return() xalign 0.02 yalign 0.96

# ── Достижения ─────────────────────────────────────────────

screen achievements_screen():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))
    text ("ACHIEVEMENT  " + str(len(store.achievements)) + " / " + str(len(ACHIEVEMENTS))):
        xalign 0.5 yalign 0.06 size 30 color "#7fe7ff"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 14
        for aid, name in ACHIEVEMENTS.items():
            $ got = aid in store.achievements
            hbox:
                spacing 16
                text ("🏆" if got else "▢"):
                    size 22
                    color ("#ffb765" if got else "#33454f")
                text (name if got else "███████████"):
                    size 20
                    color ("#ffffff" if got else "#33454f")

    textbutton "НАЗАД" action Return() xalign 0.02 yalign 0.96

# ── Концовки ───────────────────────────────────────────────

screen endings_screen():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))
    text "ENDING LIST":
        xalign 0.5 yalign 0.06 size 30 color "#7fe7ff"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 18
        for e in ENDINGS:
            $ got = e["id"] in persistent.endings_seen
            frame:
                xsize 900
                background Solid("#0d1117")
                padding (16, 14)
                vbox:
                    spacing 4
                    text (e["name"] if got else "████████"):
                        size 24
                        color ("#ffffff" if got else "#33454f")
                    text (e["hint"] if got else "Условие неизвестно."):
                        size 14
                        color "#6b7d89"

    textbutton "НАЗАД" action Return() xalign 0.02 yalign 0.96

# ── Повтор сцен ────────────────────────────────────────────

screen scene_replay_screen():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))
    text "SCENE REPLAY":
        xalign 0.5 yalign 0.06 size 30 color "#7fe7ff"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 16
        for r in REPLAYS:
            textbutton r["name"]:
                xsize 620
                action Replay(r["label"], locked=False)
        text "Добавь свои метки в REPLAYS (см. 08_extras.rpy).":
            size 13
            color "#33454f"

    textbutton "НАЗАД" action Return() xalign 0.02 yalign 0.96

# ── История выборов ────────────────────────────────────────

screen choice_history():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))
    text "CHOICE HISTORY":
        xalign 0.5 yalign 0.06 size 30 color "#7fe7ff"
    text "Что ты выбрал — и что помнишь, что выбрал.":
        xalign 0.5 yalign 0.12 size 14 color "#6b7d89"

    viewport:
        xalign 0.5
        yalign 0.55
        xsize 1000
        ysize 620
        scrollbars "vertical"
        mousewheel True
        vbox:
            spacing 6
            if not persistent.choice_log:
                text "выборов пока нет" size 16 color "#33454f"
            for entry in persistent.choice_log:
                text entry size 15 color "#c9d6de"

    textbutton "НАЗАД" action Return() xalign 0.02 yalign 0.96
