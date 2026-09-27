# Флирт. Со всеми, кроме охраны. Взаимности пока нет ни у кого:
# Ким показывает средний палец, Ли фиксирует, Уилл переводит на «потом».
# Счётчик за прохождение — flirt_count, за все круги — persistent.flirt_total.

default flirt_count = {}
default persistent.flirt_total = {}

image kim finger = "images/kim finger.png"

init python:

    FLIRT_NAMES = {"kim": "КИМ", "lee": "ЛИ", "will": "УИЛЛ"}

    def flirt_n(who):
        """Сколько раз за это прохождение."""
        return store.flirt_count.get(who, 0)

    def flirt_total(who):
        """Сколько раз за все круги."""
        return (persistent.flirt_total or {}).get(who, 0)

    def flirt_register(who):
        store.flirt_count[who] = flirt_n(who) + 1
        t = dict(persistent.flirt_total or {})
        t[who] = t.get(who, 0) + 1
        persistent.flirt_total = t
        log_choice("♥ флирт: " + FLIRT_NAMES[who])
        if all(k in store.flirt_count for k in FLIRT_NAMES):
            unlock_ach("ach_flirt_all")

    def flirt_summary():
        """Строка для Архива."""
        parts = []
        for k in ("kim", "lee", "will"):
            parts.append(FLIRT_NAMES[k] + " " + str(flirt_total(k)))
        return "флирт: " + " · ".join(parts) + " · взаимность: 0 · охрана: вне протокола"


# КИМ ####################################################################

label flirt_kim:

    $ flirt_register("kim")

    if flirt_n("kim") == 1:

        show kim finger
        with dissolve

        "Ким не отрывается от монитора. Поднимает руку."
        "Средний палец. Ровно, без выражения — как показания прибора."

        $ kim_voice("kim_094")
        k "Регламент, Майк. Пункт семь: служебные романы — после конца света."

        $ unlock_ach("ach_flirt_kim")

    elif flirt_n("kim") == 2:

        show kim finger
        with dissolve

        $ kim_voice("kim_095")
        k "Второй раз за неделю."

        "Палец. Тот же. Она даже руку не меняет."

        $ kim_voice("kim_096")
        k "Записываю в журнал допуска. Графа «настойчивость»."

    else:

        show kim finger
        with dissolve

        "Она не поворачивается. Палец находит меня сам, как стрелка компаса."

        $ kim_voice("kim_097")
        k "Я уже даже не смотрю."

        m "Заметил."

    show kim smirk
    with dissolve

    return


# ЛИ #####################################################################

label flirt_lee:

    $ flirt_register("lee")

    if flirt_n("lee") == 1:

        "Ли смотрит на меня так, как смотрят на опечатку в протоколе."

        li "…"

        li "Зафиксировано."

        "Он действительно что-то записывает."

    else:

        li "Оператор. Вы переутомлены."

        "Он говорит это, не оборачиваясь. В спину."

    return


# УИЛЛ ###################################################################

label flirt_will:

    $ flirt_register("will")

    if flirt_total("will") == 1:

        "Он улыбается. Тепло, по-настоящему — так, что на секунду забываешь, где мы."

        w "Ты и тогда так говорил."

        m "Когда — тогда?"

        w "Не сейчас, Майк. Сначала вспомни. Потом — всё остальное."

        "Это не «нет». Но и не «да». Это «после»."

    else:

        w "Знаешь, сколько раз я это слышал?"

        w "Столько же, сколько раз ты забывал."

        "Он не отводит взгляд. Он никогда не отводит."

    return
