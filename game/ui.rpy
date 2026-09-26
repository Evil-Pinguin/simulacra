# Оформление интерфейса и интерактивные механики «Simulacra».

# ШРИФТ И ЗВУК. ##########################################################
# Диалоги — машинописный моноширинный: текст расшифровки записи.
# Обводка — чтобы читалось даже на белом снегу.

style say_dialogue:
    font "fonts/game_mono.ttf"
    size 23
    outlines [(2, "#000000aa", 0, 0)]

style say_label:
    font "fonts/game_mono.ttf"
    outlines [(2, "#000000aa", 0, 0)]

# Мягкий щелчок на любой кнопке.
style button:
    activate_sound "audio/click.wav"


# ДОСТИЖЕНИЯ И ДНЕВНИК: данные. ##########################################

default journal_ids = []

init python:

    ACHIEVEMENTS = [
        ("ach_met_kim", "ЗНАКОМСТВО С КИМ", "Она тебя не видела."),
        ("ach_resonance", "РЕЗОНАНС 62.8", "Первая фиксация несущей."),
        ("ach_anchor", "ЯКОРЬ", "Взять то, что лежало не для тебя."),
        ("ach_not_alone", "НЕ ОДИН", "Оставить помехи говорить."),
        ("ach_first_dive", "ГЛУБОКОЕ ПОГРУЖЕНИЕ", "Вернуться с кровью из носа."),
        ("ach_chase", "ПО СЛЕДУ", "Не упустить того, кого не может быть."),
        ("ach_calib_yes", "ЧИСТКА", "Выбрать покой. Заплатить памятью."),
        ("ach_calib_no", "БОЛЬ ПРАВДЫ", "Оставить швы как есть."),
        ("ach_ch2", "ЦЕПНАЯ РЕАКЦИЯ", "Дочитать запись 02."),
    ]

    JOURNAL = {
        "kim": ("КИМ", "Оператор сопровождения. В отделении дольше всех нас — её перевели сюда давно, ещё до того, как я пришёл. Откуда и за что — не рассказывает, а я не спрашиваю.\n\nХарактер: лёгкая, насмешливая. Единственная на этаже, у кого улыбка доходит до глаз. Под улыбкой — стальная выдержка: страхует так, будто делала это всю жизнь.\n\nЛюбит: нормальный кофе (не из машины), порядок в журнале допуска, побеждать в спорах.\n\nНе любит: формулировку «в базе не значится», героизм после смены и вопросы о прежнем корпусе."),
        "anomaly": ("ЧАСТОТА 62.8", "Под несущей пациента №117-У — вторая волна. Тонкая, как волос в фотоплёнке.\n\nЯ вывел её на динамики. Тошнота, дежавю. Ощущение, что я уже слышал эту частоту. Давно. Изнутри."),
        "visitor": ("ПОСЕТИТЕЛЬ", "Приходит второй день. Ищет человека — без имени, без фото. Говорит одно и то же: «Я помню, как он смеётся».\n\nОхрана вежлива. Здесь все вежливы."),
        "case117": ("ПАЦИЕНТ №117-У", "По документам — попытка самоубийства. Кейс рядовой, значимость низкая.\n\nРанние слои: деревянный дом, детство. В доме никого. Ни голосов, ни шагов.\n\nУ рядовых кейсов не бывает пустых домов."),
        "figure": ("СИЛУЭТ", "В чужой памяти был человек. Далеко, у забора. Стоял и смотрел.\n\nВ воспоминаниях не бывает наблюдателей. Воспоминание — запись, в ней некому смотреть.\n\nОн смотрел."),
        "reports": ("МОИ ОТЧЁТЫ", "Старые записи санаций в архиве подписаны оператором 0117-М. Некоторым — пять лет и больше. Я работаю здесь три года.\n\nМой бейдж: 0117-М.\n\nСистема переиспользует номера. Наверное."),
        "flat": ("СВЕЖИЙ СЛОЙ", "Рывок через десятки слоёв — к самому недавнему. Городская квартира, ночь, телевизор с помехами.\n\nНа столе — лист бумаги, сложенный так же, как мой. Только его — развёрнут.\n\nЯ не успел рассмотреть, что на нём."),
        "dream2": ("ДЕТИ", "Новый сон. Зелёный коридор, звонок — и смех. Детский, много голосов.\n\nВ моей руке — маленькая рука. Кто-то ведёт меня. Или я веду.\n\nЯ проснулся с мокрым лицом. Не помню, чтобы плакал."),
    }

    def unlock_ach(aid):
        if not getattr(persistent, aid, False):
            setattr(persistent, aid, True)
            for a, t, d in ACHIEVEMENTS:
                if a == aid:
                    renpy.show_screen("achievement_toast", t, d, "▮ ЗАПИСЬ В ЛИЧНОЕ ДЕЛО")
                    break

    def journal_add(jid):
        if jid in JOURNAL and jid not in journal_ids:
            journal_ids.append(jid)
            renpy.show_screen("achievement_toast", JOURNAL[jid][0], "новая запись", "▮ ДНЕВНИК ОБНОВЛЁН")

    def journal_remove(jid):
        if jid in journal_ids:
            journal_ids.remove(jid)
            renpy.show_screen("achievement_toast", JOURNAL[jid][0], "фрагмент вычищен", "▮ ЗАПИСЬ УДАЛЕНА")


# ГЛАВНОЕ МЕНЮ в стиле Mnemosyne. ########################################

style mm_button is default
style mm_button:
    background None
    xpadding 0
    activate_sound "audio/click.wav"

style mm_button_text is text:
    font "fonts/game_serif.ttf"
    size 30
    color "#7fd4a8"
    hover_color "#c8ffd8"

screen main_menu():

    tag menu

    add "images/menubg.png"
    add "snow_menu"

    vbox:
        xpos 130
        yalign 0.85
        spacing 12

        text "SIMULACRA" size 74 color "#c8ffd8" font "fonts/game_serif.ttf"
        text "MNEMOSYNE // архив записей" size 20 color "#517263"

        null height 26

        textbutton "НАЧАТЬ ЗАПИСЬ" style "mm_button" action Start()
        textbutton "ПРОДОЛЖИТЬ" style "mm_button" action ShowMenu("load")
        textbutton "ДОСТИЖЕНИЯ" style "mm_button" action ShowMenu("achievements")
        textbutton "НАСТРОЙКИ" style "mm_button" action ShowMenu("preferences")
        textbutton "ВЫХОД" style "mm_button" action Quit(confirm=False)

    text "ЗАПИСЬ 01 // 62.8 ед.":
        xalign 0.97
        yalign 0.96
        size 16
        color "#51726377"


# ЭКРАН ДОСТИЖЕНИЙ. ######################################################

screen achievements():

    tag menu

    add "images/menubg.png"
    add Solid("#04070ad9")
    add "snow_menu"

    vbox:
        xpos 130
        ypos 110
        spacing 30

        text "ЛИЧНОЕ ДЕЛО // ДОСТИЖЕНИЯ" size 40 color "#c8ffd8" font "fonts/game_serif.ttf"

        vbox:
            spacing 22

            for aid, t, d in ACHIEVEMENTS:

                hbox:
                    spacing 18

                    if getattr(persistent, aid, False):
                        add Solid("#7fd4a8") xsize 5 ysize 58
                        vbox:
                            spacing 4
                            text t size 26 color "#c8ffd8"
                            text d size 17 color "#7fd4a8"
                    else:
                        add Solid("#33473d") xsize 5 ysize 58
                        vbox:
                            spacing 4
                            text "▮▮▮▮▮▮▮▮" size 26 color "#33473d"
                            text "запись не расшифрована" size 17 color "#33473d"

        null height 10

        textbutton "◂ НАЗАД" style "mm_button" action Return()


# ДНЕВНИК ОПЕРАТОРА. #####################################################

screen journal_button():
    zorder 900

    textbutton "◈ ДНЕВНИК":
        xpos 16
        ypos 10
        background None
        text_size 17
        text_font "fonts/game_serif.ttf"
        text_color "#51726388"
        text_hover_color "#c8ffd8"
        action Show("journal_screen")

screen journal_screen():

    modal True
    zorder 1500

    add Solid("#04070af0")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 26

        text "ДНЕВНИК ОПЕРАТОРА" size 36 color "#c8ffd8" font "fonts/game_serif.ttf" xalign 0.5

        viewport:
            xsize 1150
            ysize 660
            scrollbars "vertical"
            mousewheel True

            vbox:
                spacing 34

                if not journal_ids:
                    text "Записей пока нет." size 22 color "#517263"

                for jid in journal_ids:
                    vbox:
                        spacing 8
                        text JOURNAL[jid][0] size 27 color "#c8ffd8" font "fonts/game_serif.ttf"
                        text JOURNAL[jid][1] size 20 color "#9fb8ac" font "fonts/game_serif.ttf"

        textbutton "ЗАКРЫТЬ" style "mm_button" action Hide("journal_screen") xalign 0.5


# Меню выбора: мир гаснет, варианты парят слева и справа,
# появляются по очереди и испаряются после нажатия.

transform choice_bgfade:
    on show:
        alpha 0.0
        linear 0.35 alpha 1.0
    on hide:
        linear 0.5 alpha 0.0

transform choice_float(d=0.0):
    on show:
        alpha 0.0 yoffset 26
        pause d
        easein 0.5 alpha 1.0 yoffset 0
        block:
            ease 1.6 yoffset 7
            ease 1.6 yoffset -7
            repeat
    on hide:
        easeout 0.55 alpha 0.0 yoffset -46

screen choice(items):

    add Solid("#000000") at choice_bgfade

    vbox:
        xfill True
        yalign 0.5
        spacing 64

        for idx, i in enumerate(items):

            textbutton i.caption:
                xalign (0.25 if idx % 2 == 0 else 0.75)
                background None
                text_font "fonts/game_mono.ttf"
                text_size 30
                text_color "#c8ffd8"
                text_hover_color "#ffffff"
                text_outlines [(2, "#04070a", 0, 0)]
                at choice_float(idx * 0.18)
                action i.action


# Позиция Ким на сцене.
transform kim_right:
    xalign 0.82
    yalign 1.0

# Выравнивание масштаба эмоций: лицо всегда одного размера,
# лишнее уходит под текстбокс.
image kim smile = "images/kim smile.png"
image kim laugh = "images/kim laugh.png"
image kim serious = Transform("images/kim serious.png", zoom=1.18, yoffset=191)
image kim smirk = Transform("images/kim smirk.png", zoom=1.08, yoffset=85)
image kim surprised = Transform("images/kim surprised.png", zoom=0.97, yoffset=-32)
image kim sad = "images/kim sad.png"
image kim wink = Transform("images/kim wink.png", zoom=0.97, yoffset=-32)


# ОЖИВЛЯЖ: если игрок молчит ~12 секунд, Ким переспрашивает. ############

transform bubble_in:
    on show:
        alpha 0.0 yoffset 12
        easein 0.3 alpha 1.0 yoffset 0
    on hide:
        easeout 0.3 alpha 0.0

screen kim_idle():

    zorder 950

    default poke = 0

    if poke == 0:
        timer 12.0 action SetScreenVariable("poke", 1)
    elif poke == 1:
        frame at bubble_in:
            xalign 0.80
            ypos 120
            background Solid("#0a1014e0")
            padding (22, 12)
            text "Ким: — Что такое?" size 20 color "#ffb3c8" font "fonts/game_mono.ttf"
        timer 3.0 action SetScreenVariable("poke", 2)
    else:
        frame at bubble_in:
            xalign 0.80
            ypos 120
            background Solid("#0a1014e0")
            padding (22, 12)
            text "Майк: — А… Ничего." size 20 color "#aad4ff" font "fonts/game_mono.ttf"
        timer 2.6 action SetScreenVariable("poke", 0)


# ДИАЛОГОВОЕ ОКНО в стиле проекта. ######################################

style namebox:
    background "#0a1014cc"
    padding (20, 6)


# ТОСТ ДОСТИЖЕНИЙ / ДНЕВНИКА — в духе Minecraft, но в нашем стиле:
# плашка с иконкой съезжает сверху справа, повисает и уезжает обратно.

transform ach_slide:
    xanchor 1.0
    xpos 0.99
    ypos -180
    alpha 0.0
    easein 0.5 ypos 36 alpha 1.0
    pause 3.8
    easeout 0.5 ypos -180 alpha 0.0

screen achievement_toast(title, desc="", header="▮ ЗАПИСЬ В ЛИЧНОЕ ДЕЛО"):

    zorder 2000

    frame at ach_slide:
        background Solid("#0a1014f2")
        xpadding 14
        ypadding 14

        hbox:
            spacing 20

            frame:
                background Solid("#7fd4a8")
                xpadding 2
                ypadding 2

                frame:
                    background Solid("#122e22")
                    xsize 82
                    ysize 82

                    text "◈" size 46 color "#c8ffd8" xalign 0.5 yalign 0.5

            vbox:
                spacing 4
                yalign 0.5
                text header size 15 color "#517263" font "fonts/game_mono.ttf"
                text title size 24 color "#c8ffd8" font "fonts/game_mono.ttf"
                if desc:
                    text desc size 16 color "#7fd4a8" font "fonts/game_mono.ttf"

    timer 4.9 action Hide("achievement_toast")


# МЕХАНИКА 1: подбор частот. #############################################

default freq_value = 18.0

screen freq_tuner(target=62.8, tol=3.0):

    modal True

    add Solid("#04070a")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 60
        ypadding 45
        background Solid("#0a1014")

        vbox:
            spacing 26
            xsize 960

            text "MNEMOSYNE // ЧАСТОТНЫЙ АНАЛИЗ — ПАЦИЕНТ №117-У" color "#7fd4a8" size 26
            text "Ведите несущую. Чем ближе частота — тем ровнее отклик." color "#517263" size 18

            bar value VariableValue("freq_value", 100.0) xsize 960

            text "НЕСУЩАЯ: [freq_value:.1f] ед." color "#9fd8b8" size 22

            if abs(freq_value - target) <= tol:
                text "ОТКЛИК: РЕЗОНАНС. Сигнал держится ровно." color "#c8ffd8" size 22
            elif abs(freq_value - target) <= 10:
                text "ОТКЛИК: сильный. Почти в фазе." color "#7fd4a8" size 22
            elif abs(freq_value - target) <= 25:
                text "ОТКЛИК: слабый. Что-то есть." color "#517263" size 22
            else:
                text "ОТКЛИК: шум." color "#33473d" size 22

            textbutton "ЗАФИКСИРОВАТЬ ЧАСТОТУ":
                xalign 0.5
                action Return(abs(freq_value - target) <= tol)

            textbutton "ПРОПУСТИТЬ ▸":
                xalign 1.0
                action Return("skip")


# МЕХАНИКА 2: кабинет-хаб. ###############################################

default office_done = set()

screen office_hub():

    modal True

    if "coffee" not in office_done:
        textbutton "▸ Кофемашина":
            xalign 0.88
            yalign 0.42
            action Return("coffee")

    if "papers" not in office_done:
        textbutton "▸ Бумаги на столе":
            xalign 0.32
            yalign 0.78
            action Return("papers")

    if "window" not in office_done:
        textbutton "▸ Окно":
            xalign 0.07
            yalign 0.30
            action Return("window")

    if "chair" not in office_done:
        textbutton "▸ Кресло":
            xalign 0.63
            yalign 0.62
            action Return("chair")

    if "coffee" in office_done:
        textbutton "Сесть работать":
            xalign 0.5
            yalign 0.96
            action Return("work")


# МЕХАНИКА 3: калибровка нейрокортекса. ##################################

default cal_amp = 20.0
default cal_phase = 85.0
default cal_gain = 10.0

screen neuro_calib(ta=34.0, tp=71.5, tg=52.0, tol=4.0):

    modal True

    add "bg terminal"
    add Solid("#04070aa8")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 60
        ypadding 40
        background Solid("#0a1014d9")

        vbox:
            spacing 18
            xsize 960

            text "MNEMOSYNE // КАЛИБРОВКА НЕЙРОКОРТЕКСА" color "#7fd4a8" size 26
            text "Сведите три контура с эталоном. Допуск — узкий." color "#517263" size 18

            text "АМПЛИТУДА: [cal_amp:.1f]" color "#9fd8b8" size 20
            bar value VariableValue("cal_amp", 100.0) xsize 960
            if abs(cal_amp - ta) <= tol:
                text "— контур сведён" color "#c8ffd8" size 17
            else:
                text "— рассогласование" color "#33473d" size 17

            text "ФАЗА: [cal_phase:.1f]" color "#9fd8b8" size 20
            bar value VariableValue("cal_phase", 100.0) xsize 960
            if abs(cal_phase - tp) <= tol:
                text "— контур сведён" color "#c8ffd8" size 17
            else:
                text "— рассогласование" color "#33473d" size 17

            text "УСИЛЕНИЕ: [cal_gain:.1f]" color "#9fd8b8" size 20
            bar value VariableValue("cal_gain", 100.0) xsize 960
            if abs(cal_gain - tg) <= tol:
                text "— контур сведён" color "#c8ffd8" size 17
            else:
                text "— рассогласование" color "#33473d" size 17

            hbox:
                xalign 0.5
                spacing 60

                textbutton "ЗАПУСТИТЬ ТЕСТ":
                    action Return(abs(cal_amp - ta) <= tol and abs(cal_phase - tp) <= tol and abs(cal_gain - tg) <= tol)

                textbutton "ПРОПУСТИТЬ ▸":
                    action Return("skip")


# МЕХАНИКА 4: сканер слоя памяти. ########################################screen mem_scanner():

    modal True

    add Solid("#000000c8")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 50
        ypadding 40
        background Solid("#0a1014")

        vbox:
            spacing 24

            text "СКАНИРОВАНИЕ СЛОЯ // выберите сектор" color "#7fd4a8" size 24 xalign 0.5

            grid 3 3:
                spacing 14
                xalign 0.5

                textbutton "А1" xsize 150 ysize 90 action Return(0)
                textbutton "А2" xsize 150 ysize 90 action Return(1)
                textbutton "А3" xsize 150 ysize 90 action Return(2)
                textbutton "Б1" xsize 150 ysize 90 action Return(3)
                textbutton "Б2" xsize 150 ysize 90 action Return(4)
                textbutton "Б3" xsize 150 ysize 90 action Return(5)
                textbutton "В1" xsize 150 ysize 90 action Return(6)
                textbutton "В2" xsize 150 ysize 90 action Return(7)
                textbutton "В3" xsize 150 ysize 90 action Return(8)

            textbutton "ПРОПУСТИТЬ ▸":
                xalign 1.0
                action Return("skip")


# ГЛАВА 2: призрак вдалеке. ##############################################
# Мерцающий силуэт в чужой памяти.

transform ghost_far(x=0.62, y=0.60, z=0.30):
    xalign x
    yalign y
    zoom z
    block:
        linear 0.14 alpha 0.75
        linear 0.11 alpha 0.20
        linear 0.16 alpha 0.60
        linear 0.12 alpha 0.05
        linear 0.18 alpha 0.65
        repeat


# МЕХАНИКА 5: слежение за силуэтом. ######################################
# Кнопки направлений поверх сцены — фон не гасим, силуэт видно.

screen chase_dir():

    modal True

    text "НЕ УПУСТИТЬ СИЛУЭТ":
        xalign 0.5
        ypos 46
        size 22
        color "#c8ffd8"
        font "fonts/game_mono.ttf"
        outlines [(2, "#04070a", 0, 0)]

    hbox:
        xalign 0.5
        yalign 0.90
        spacing 130

        textbutton "◀ ВЛЕВО":
            background None
            text_font "fonts/game_mono.ttf"
            text_size 28
            text_color "#c8ffd8"
            text_hover_color "#ffffff"
            text_outlines [(2, "#04070a", 0, 0)]
            action Return("l")

        textbutton "▲ ПРЯМО":
            background None
            text_font "fonts/game_mono.ttf"
            text_size 28
            text_color "#c8ffd8"
            text_hover_color "#ffffff"
            text_outlines [(2, "#04070a", 0, 0)]
            action Return("c")

        textbutton "ВПРАВО ▶":
            background None
            text_font "fonts/game_mono.ttf"
            text_size 28
            text_color "#c8ffd8"
            text_hover_color "#ffffff"
            text_outlines [(2, "#04070a", 0, 0)]
            action Return("r")


# МЕХАНИКА 6: архив «Мои отчёты». ########################################

screen my_reports(viewed):

    modal True

    add "bg terminal"
    add Solid("#04070ab8")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 55
        ypadding 40
        background Solid("#0a1014d9")

        vbox:
            spacing 20
            xsize 1100

            text "MNEMOSYNE // АРХИВ САНАЦИЙ — ВЫДАЧА ПО ЗАПРОСУ" color "#7fd4a8" size 24 font "fonts/game_mono.ttf"
            text "Записи доступны оператору для служебного ознакомления." color "#517263" size 16 font "fonts/game_mono.ttf"

            null height 8

            textbutton "ИНЦИДЕНТ 7-Б   // санация // оператор 0117-М":
                background None
                text_font "fonts/game_mono.ttf"
                text_size 21
                text_color ("#33473d" if 0 in viewed else "#9fd8b8")
                text_hover_color "#ffffff"
                action Return(0)

            textbutton "ИНЦИДЕНТ 9-В   // санация // оператор 0117-М":
                background None
                text_font "fonts/game_mono.ttf"
                text_size 21
                text_color ("#33473d" if 1 in viewed else "#9fd8b8")
                text_hover_color "#ffffff"
                action Return(1)

            textbutton "ИНЦИДЕНТ 11-G  // файл повреждён":
                background None
                text_font "fonts/game_mono.ttf"
                text_size 21
                text_color ("#33473d" if 2 in viewed else "#9fd8b8")
                text_hover_color "#ffffff"
                action Return(2)

            textbutton "ИНЦИДЕНТ 12-Н  // санация // оператор 0117-М":
                background None
                text_font "fonts/game_mono.ttf"
                text_size 21
                text_color ("#33473d" if 3 in viewed else "#9fd8b8")
                text_hover_color "#ffffff"
                action Return(3)

            null height 14

            textbutton "ЗАКРЫТЬ АРХИВ":
                xalign 0.5
                text_font "fonts/game_mono.ttf"
                action Return("close")
