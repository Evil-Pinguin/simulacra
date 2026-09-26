# Оформление интерфейса «Simulacra».

# Меню выбора: мир гаснет в черноте, остаются только варианты.
# Определяется после screens.rpy и заменяет стандартный экран choice.
screen choice(items):

    add Solid("#000000")

    style_prefix "choice"

    vbox:
        xalign 0.5
        yalign 0.5
        spacing gui.choice_spacing

        for i in items:

            textbutton i.caption action i.action


# Механика подбора частот. ###############################################
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
