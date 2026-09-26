# Оформление интерфейса и интерактивные механики «Simulacra».

# ГЛАВНОЕ МЕНЮ в стиле Mnemosyne. ########################################

style mm_button is default
style mm_button:
    background None
    xpadding 0

style mm_button_text is text:
    size 30
    color "#7fd4a8"
    hover_color "#c8ffd8"

screen main_menu():

    tag menu

    add "images/menubg.png"

    vbox:
        xpos 130
        yalign 0.82
        spacing 12

        text "SIMULACRA" size 74 color "#c8ffd8"
        text "MNEMOSYNE // архив записей" size 20 color "#517263"

        null height 30

        textbutton "НАЧАТЬ ЗАПИСЬ" style "mm_button" action Start()
        textbutton "ПРОДОЛЖИТЬ" style "mm_button" action ShowMenu("load")
        textbutton "НАСТРОЙКИ" style "mm_button" action ShowMenu("preferences")
        textbutton "ВЫХОД" style "mm_button" action Quit(confirm=False)

    text "ЗАПИСЬ 01 // 62.8 ед.":
        xalign 0.97
        yalign 0.96
        size 16
        color "#51726377"


# Меню выбора: мир гаснет в черноте, остаются только варианты.
screen choice(items):

    add Solid("#000000")

    style_prefix "choice"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing gui.choice_spacing

        for i in items:

            textbutton i.caption action i.action


# Позиция Ким на сцене.
transform kim_right:
    xalign 0.82
    yalign 1.0


# ДОСТИЖЕНИЯ. ############################################################
# Тост в стиле Mnemosyne: выезжает справа сверху, висит и гаснет сам.

transform ach_slide:
    xanchor 1.0
    xpos 0.99
    ypos 40
    alpha 0.0
    xoffset 320
    easein 0.45 alpha 1.0 xoffset 0
    pause 3.6
    easeout 0.6 alpha 0.0 xoffset 60

screen achievement_toast(title, desc=""):

    zorder 2000

    frame at ach_slide:
        background Solid("#0a1014ee")
        xpadding 0
        ypadding 0

        hbox:
            add Solid("#7fd4a8") xsize 6 ysize 110

            frame:
                background None
                xpadding 26
                ypadding 16

                vbox:
                    spacing 5
                    text "▮ ЗАПИСЬ В ЛИЧНОЕ ДЕЛО" size 15 color "#517263"
                    text title size 25 color "#c8ffd8"
                    if desc:
                        text desc size 17 color "#7fd4a8"

    timer 4.8 action Hide("achievement_toast")


# МЕХАНИКА 1: подбор частот. #############################################
# Игрок ведёт ползунок несущей частоты; чем ближе к цели — тем ровнее
# отклик. Фиксация проходит только в зоне резонанса.

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


# МЕХАНИКА 2: кабинет-хаб. ###############################################
# Спокойная зона: игрок сам решает, что осмотреть. Работать можно сесть
# только после кофе — сцена с пятном обязательна для сюжета.

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
# Три контура — амплитуда, фаза, усиление. Тест проходит, только когда
# все три сведены с эталоном.

default cal_amp = 20.0
default cal_phase = 85.0
default cal_gain = 10.0

screen neuro_calib(ta=34.0, tp=71.5, tg=52.0, tol=4.0):

    modal True

    add Solid("#04070a")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 60
        ypadding 40
        background Solid("#0a1014")

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

            textbutton "ЗАПУСТИТЬ ТЕСТ":
                xalign 0.5
                action Return(abs(cal_amp - ta) <= tol and abs(cal_phase - tp) <= tol and abs(cal_gain - tg) <= tol)


# МЕХАНИКА 4: сканер слоя памяти. ########################################
# Сетка секторов 3×3. Игрок ищет точку перехода по отклику «теплее —
# холоднее».

screen mem_scanner():

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
