# Опенинг «Simulacra»: VHS-заставка при запуске (label splashscreen).
# Строки протокола бегут одна за другой, потом — название с расслоением
# на красный и зелёный слой. Голос MNEMOSYNE читает шапку архива.
# Щелчок — пропустить. Повторить можно из раздела АРХИВ → ПОВТОР.

init python:

    OPENING_LINES = [
        "MNEMOSYNE v9.4 // ядро загружено",
        "носитель: 0117-М …… подключён",
        "целостность: 98.1%",
        "архив записей: 3 …… доступ разрешён",
        "свидетелей: 31 …… статус: санированы",
        "аномалий: 1 …… статус: активна",
        "▮ REC",
    ]

    def play_sys_voice(name):
        """Реплика системы голосом. Файла нет — тишина, без ошибки."""
        fn = "voice/" + name + ".ogg"
        if renpy.loadable(fn):
            renpy.sound.play(fn, channel="voice")


style op_line is default:
    font "fonts/game_mono.ttf"
    size 18
    color "#7fd4a8"

style op_title is default:
    font "fonts/game_serif.ttf"
    size 150
    color "#c8ffd8"
    kerning 14

style op_sub is default:
    font "fonts/game_mono.ttf"
    size 20
    color "#9fd8b8"


transform op_line_in(d=0.0):
    alpha 0.0
    pause d
    linear 0.12 alpha 1.0

transform op_title_ghost(d=4.6, dx=6):
    alpha 0.0
    xoffset dx
    pause d
    alpha 0.55
    block:
        xoffset dx
        pause 0.07
        xoffset (-dx)
        pause 0.05
        xoffset (dx * 0.5)
        pause 0.35
        xoffset 0
        pause 0.6
        repeat

transform op_static_burst:
    alpha 0.7
    pause 0.35
    alpha 0.0
    pause 3.9
    alpha 0.5
    pause 0.08
    alpha 0.0


screen opening():

    zorder 100

    add Solid("#04070a")

    add "vhs static" at op_static_burst

    vbox:
        xpos 150
        ypos 130
        spacing 12

        for i, line in enumerate(OPENING_LINES):
            text line style "op_line" at op_line_in(0.6 + i * 0.5)

    fixed:
        xfill True
        yfill True

        text "SIMULACRA" style "op_title" color "#d95a5a" xalign 0.5 yalign 0.47 at op_title_ghost(4.6, -7)
        text "SIMULACRA" style "op_title" color "#7fd4a8" xalign 0.5 yalign 0.47 at op_title_ghost(4.6, 7)
        text "SIMULACRA" style "op_title" xalign 0.5 yalign 0.47 at op_line_in(4.6)

        text "MNEMOSYNE // архив записей" style "op_sub" xalign 0.5 yalign 0.61 at op_line_in(5.6)
        text "записи 01–03 // оператор 0117-М" style "op_sub" color "#517263" xalign 0.5 yalign 0.655 at op_line_in(6.4)

    add "vhs scanlines" alpha 0.55

    text "щёлкни, чтобы пропустить" style "op_line" color "#33473d" size 14 xalign 0.5 yalign 0.95

    button:
        xfill True
        yfill True
        background None
        action Return()

    timer 10.8 action Return()


label splashscreen:

    $ unlock_replay("opening")
    $ play_sys_voice("sys_open")

    scene black

    call screen opening

    $ renpy.sound.stop(channel="voice")

    scene black
    with Dissolve(0.5)

    return


label replay_opening:

    $ play_sys_voice("sys_open")

    scene black

    call screen opening

    $ renpy.sound.stop(channel="voice")

    scene black

    return
