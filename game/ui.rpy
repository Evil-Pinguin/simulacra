# Оформление интерфейса «Simulacra».

# Лучик света вместо системного курсора — кончик луча и есть точка клика.
define config.mouse = {
    "default" : [("images/light cursor.png", 5, 5)],
    "pressed" : [("images/light cursor.png", 5, 5)],
}


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
