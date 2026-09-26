# «АРХИВ» — дополнительные разделы главного меню «Simulacra»:
# люди (галерея), исходы, повтор сцен, история выборов, новый круг (NG+).
# Всё, что здесь показывается, живёт в persistent — переживает игру.

default persistent.replays = []

init python:

    # Люди. Кто открывается — по записям в личном деле (достижениям).
    GALLERY = [
        dict(id="kim", name="КИМ", role="оператор сопровождения",
             image="images/kim smile.png", need="ach_met_kim",
             note="Единственная на этаже, у кого улыбка доходит до глаз."),
        dict(id="lee", name="ЛИ", role="архивариус",
             image="images/lee.png", need="ach_ch2",
             note="Красный пропуск. Во всём корпусе такой один."),
        dict(id="will", name="УИЛЛ", role="пациент №117-У",
             image="images/will close.png", need="ach_contact",
             note="Записи не называют оператора по имени. Он назвал."),
        dict(id="mike", name="МАЙК", role="оператор 0117-М",
             image=None, need=None,
             note="Не попадает в кадр."),
    ]

    # Исходы. Пока их три — по реконструкции 11-G. Остальное — в следующих записях.
    ENDINGS = [
        ("end_true", "11-G: КАК БЫЛО", "Собрать воспоминание целиком — и не добавить лишнего."),
        ("end_partial", "11-G: НЕ ВСЁ", "Собрать картину с пустыми клетками."),
        ("end_false", "11-G: КАК УДОБНО", "Записать ложное воспоминание как правду."),
        ("end_04", None, None),
        ("end_05", None, None),
    ]

    # Повтор сцен.
    REPLAYS = [
        ("house", "ФЛЕШБЕК: ДОМ", "replay_flashback_house", "Кадры перед дверью старого дома."),
        ("school", "ФЛЕШБЕК: ШКОЛА", "replay_flashback_school", "Кадры перед файлом 11-G."),
        ("corridor", "СОН: ЗЕЛЁНЫЙ КОРИДОР", "replay_corridor", "Фокус внимания. Найди триггеры."),
    ]

    def unlock_replay(rid):
        if rid not in persistent.replays:
            persistent.replays.append(rid)

    def unlock_ending(eid):
        if eid not in persistent.endings_seen:
            persistent.endings_seen.append(eid)

    def gallery_open(entry):
        if entry["need"] is None:
            return False
        return bool(getattr(persistent, entry["need"], False))

    def reset_passes():
        """Стереть круги: воспоминания между прохождениями и историю выборов."""
        persistent.pass_number = 1
        persistent.mem_fragments = []
        persistent.mem_links = []
        persistent.mem_sync = 0
        persistent.choice_log = []
        renpy.restart_interaction()


# СТИЛИ ##################################################################

style ex_tab is default:
    background None
    xpadding 0
    activate_sound "audio/click.wav"

style ex_tab_text is text:
    font "fonts/game_mono.ttf"
    size 20
    color "#517263"
    hover_color "#c8ffd8"
    selected_color "#c8ffd8"

style ex_text is default:
    font "fonts/game_mono.ttf"
    size 18
    color "#9fb8ac"

style ex_head is text:
    font "fonts/game_serif.ttf"
    size 26
    color "#c8ffd8"


# ЭКРАН АРХИВА ##########################################################

screen extras():

    tag menu

    default tab = "people"

    add "images/menubg.png"
    add Solid("#04070ad9")
    add "snow_menu"

    vbox:
        xpos 130
        ypos 90
        spacing 24

        text "АРХИВ // ЗАПИСИ ВНЕ СЕССИИ" size 40 color "#c8ffd8" font "fonts/game_serif.ttf"

        hbox:
            spacing 34
            textbutton "ЛЮДИ" style "ex_tab" action SetScreenVariable("tab", "people") selected (tab == "people")
            textbutton "ИСХОДЫ" style "ex_tab" action SetScreenVariable("tab", "endings") selected (tab == "endings")
            textbutton "ПОВТОР" style "ex_tab" action SetScreenVariable("tab", "replay") selected (tab == "replay")
            textbutton "ИСТОРИЯ ВЫБОРОВ" style "ex_tab" action SetScreenVariable("tab", "choices") selected (tab == "choices")
            textbutton ("КРУГ " + str(persistent.pass_number)) style "ex_tab" action SetScreenVariable("tab", "ngplus") selected (tab == "ngplus")

        add Solid("#33473d") xsize 1660 ysize 1

        if tab == "people":
            use ex_people
        elif tab == "endings":
            use ex_endings
        elif tab == "replay":
            use ex_replay
        elif tab == "choices":
            use ex_choices
        else:
            use ex_ngplus

    textbutton "◂ НАЗАД" style "mm_button" xpos 130 yalign 0.95 action Return()


# ЛЮДИ ###################################################################

screen ex_people():

    hbox:
        spacing 40

        for e in GALLERY:

            $ _open = gallery_open(e)

            vbox:
                spacing 10
                xsize 330

                frame:
                    xsize 330
                    ysize 420
                    background Solid("#0a1014")
                    padding (0, 0)

                    if _open:
                        button:
                            xfill True
                            yfill True
                            background None
                            action Show("ex_portrait", None, e)
                            add Transform(e["image"], zoom=0.39) xalign 0.5 yalign 0.0
                    elif e["image"] is None:
                        add "vhs static" xysize (330, 420)
                        text "НЕ ПОПАДАЕТ\nВ КАДР" style "ex_text" color "#c8ffd8" size 22 text_align 0.5 xalign 0.5 yalign 0.5
                    else:
                        add Solid("#04070a") xysize (330, 420)
                        text "▮▮▮▮▮▮" style "ex_text" color "#33473d" size 30 xalign 0.5 yalign 0.5

                if _open or e["image"] is None:
                    text e["name"] style "ex_head"
                    text e["role"] style "ex_text" color "#7fd4a8" size 16
                    text e["note"] style "ex_text" size 16
                else:
                    text "▮▮▮▮" style "ex_head" color "#33473d"
                    text "запись не расшифрована" style "ex_text" color "#33473d" size 16


screen ex_portrait(e):

    modal True
    zorder 1700

    add Solid("#04070af0")

    button:
        xfill True
        yfill True
        background None
        action Hide("ex_portrait")

    add e["image"]:
        xalign 0.5
        yalign 1.0

    vbox:
        xpos 130
        yalign 0.5
        spacing 10
        text e["name"] size 54 color "#c8ffd8" font "fonts/game_serif.ttf"
        text e["role"] style "ex_text" color "#7fd4a8"
        text e["note"] style "ex_text" xsize 500

    text "щёлкни, чтобы закрыть" style "ex_text" color "#33473d" size 15 xalign 0.5 yalign 0.96


# ИСХОДЫ ################################################################

screen ex_endings():

    vbox:
        spacing 22

        for eid, t, d in ENDINGS:

            hbox:
                spacing 18

                if t is not None and eid in persistent.endings_seen:
                    add Solid("#7fd4a8") xsize 5 ysize 58
                    vbox:
                        spacing 4
                        text t size 26 color "#c8ffd8"
                        text d size 17 color "#7fd4a8"
                elif t is not None:
                    add Solid("#e0b060") xsize 5 ysize 58
                    vbox:
                        spacing 4
                        text "▮▮▮▮▮▮▮▮" size 26 color "#33473d"
                        text "исход не достигнут" size 17 color "#33473d"
                else:
                    add Solid("#33473d") xsize 5 ysize 58
                    vbox:
                        spacing 4
                        text "▮▮▮▮▮▮▮▮" size 26 color "#33473d"
                        text "запись не расшифрована — следующая глава" size 17 color "#33473d"

        null height 6
        text ("Достигнуто: " + str(len([e for e in persistent.endings_seen if e in [x[0] for x in ENDINGS]])) + " из " + str(len([x for x in ENDINGS if x[1] is not None]))) style "ex_text" color "#517263" size 16


# ПОВТОР ################################################################

screen ex_replay():

    vbox:
        spacing 22

        for rid, t, lbl, d in REPLAYS:

            hbox:
                spacing 18

                if rid in persistent.replays:
                    add Solid("#7fd4a8") xsize 5 ysize 58
                    vbox:
                        spacing 4
                        textbutton t style "mm_button" text_size 26 action Replay(lbl, locked=False)
                        text d size 17 color "#7fd4a8"
                else:
                    add Solid("#33473d") xsize 5 ysize 58
                    vbox:
                        spacing 4
                        text "▮▮▮▮▮▮▮▮" size 26 color "#33473d"
                        text "сцена ещё не записана" size 17 color "#33473d"

        null height 6
        text "Повтор — только плёнка. Выборы и прогресс он не трогает." style "ex_text" color "#517263" size 16


# ИСТОРИЯ ВЫБОРОВ #######################################################

screen ex_choices():

    vbox:
        spacing 16

        if not persistent.choice_log:
            text "Выборов пока не было. Или их уже стёрли." style "ex_text" color "#517263"
        else:
            viewport:
                xsize 1200
                ysize 560
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 8
                    for entry in reversed(persistent.choice_log):
                        text entry style "ex_text" size 17

            textbutton "ОЧИСТИТЬ ИСТОРИЮ" style "ex_tab" action Confirm("Стереть историю выборов?", SetField(persistent, "choice_log", []))


# НОВЫЙ КРУГ ############################################################

screen ex_ngplus():

    vbox:
        spacing 18
        xsize 1100

        text ("КРУГ " + str(persistent.pass_number)) style "ex_head"

        text "Новый круг — это не «новая игра». Реальность обнуляется: Ким снова тебя не знает, файл 11-G снова закрыт. Память — нет." style "ex_text"
        text "Фрагменты и связи Архива переходят на следующий круг. Стабильность при этом плывёт: что-то станет чётче, что-то рассыплется. Синхронизация переносится частично." style "ex_text"
        text "Некоторые реплики на новом круге звучат иначе. Игра этого не объясняет." style "ex_text" color "#7fd4a8"

        null height 6

        text ("Перенесётся: фрагментов " + str(len(persistent.mem_fragments)) + ", связей " + str(len(persistent.mem_links)) + ", синхронизация " + str(min(60, persistent.mem_sync))) style "ex_text" color "#c8ffd8"

        null height 6

        if persistent.finished_ch3:
            textbutton ("НАЧАТЬ КРУГ " + str(persistent.pass_number + 1) + " ▸") style "mm_button" action [Function(start_new_pass), Start()]
        else:
            text "Новый круг откроется после записи 03." style "ex_text" color "#517263"

        if persistent.pass_number > 1 or persistent.mem_fragments:
            textbutton "СТЕРЕТЬ КРУГИ" style "ex_tab" action Confirm("Стереть память между кругами? Фрагменты, связи и история выборов будут потеряны.", Function(reset_passes))


# ПОВТОР КОРИДОРА: только механика, без сюжета.
label replay_corridor:

    $ vhs_mode = True
    $ corridor_seen = []

    scene bg school at handheld
    with fade

    "Зелёный коридор. Звонок. Смотри внимательно."

label replay_corridor_loop:

    call screen focus_scene(CORRIDOR_HOTSPOTS, corridor_seen)

    if _return == "leave":
        scene black
        with fade
        $ vhs_mode = False
        return

    call focus_examine(_return, corridor_seen, CORRIDOR_NOTES_1)

    jump replay_corridor_loop
