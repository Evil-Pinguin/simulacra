# Озвучка Ким. Перед каждой репликой k стоит `$ kim_voice("kim_NNN")` —
# файл game/voice/kim_NNN.ogg. Нет файла — реплика идёт без голоса, без ошибки.
# Соответствие номер → текст восстанавливается прямо из сценария
# (строка kim_voice всегда стоит над своей репликой).

init python:

    def kim_voice(name):
        """Голос к следующей реплике (как statement voice, но терпит отсутствие файла)."""
        if not name:
            return
        fn = "voice/" + name + ".ogg"
        if renpy.loadable(fn):
            voice(fn)

    def kim_voice_now(name):
        """Сыграть сразу (для экранов: реплика «Что такое?» при простое)."""
        fn = "voice/" + name + ".ogg"
        if renpy.loadable(fn):
            renpy.sound.play(fn, channel="voice")

    # Приветствие меняется от круга к кругу — файл выбираем по тексту.
    KIM_GREET_VOICE = {
        "Ты сегодня рано.": "kim_greet_1",
        "Ты опять опоздал.": "kim_greet_2",
        "Ты сегодня рано. Опять.": "kim_greet_3",
        "Ты опять опоздал. Опять.": "kim_greet_4",
    }
