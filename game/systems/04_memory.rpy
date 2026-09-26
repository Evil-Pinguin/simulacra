# =============================================================
#  SIMULACRA · 04_memory.rpy
#  «ДОСТОВЕРНОСТЬ ВОСПОМИНАНИЯ» + «ПОВТОРЕНИЕ С ИЗМЕНЕНИЯМИ»
#
#  Достоверность: у каждого фрагмента есть стабильность и
#  совпадение с архивом. Истины нет ни в одном источнике.
#
#  Повторение: одна и та же сцена на втором круге звучит иначе,
#  игра это не комментирует.
# =============================================================

init python:

    def variant(options):
        """
        Реплика, которая меняется от круга к кругу.
        options[i] — вариант для прохождения i+1.
        Последний вариант используется для всех следующих кругов.

            kim "[variant(['Ты сегодня рано.', 'Ты опять опоздал.'])]"
        """
        i = min(store.pass_number, len(options)) - 1
        return options[max(0, i)]

    def changed_from(text_pass1, text_now):
        """Помощник для подсветки: вернёт True, если реплика изменилась."""
        return text_pass1 != text_now

# ── Карточка фрагмента ─────────────────────────────────────

screen memory_screen():
    tag menu
    add Solid("#07090c", xysize=(1920, 1080))

    text "АРХИВ · ДОСТОВЕРНОСТЬ":
        xalign 0.5
        yalign 0.04
        size 30
        color "#7fe7ff"

    grid 3 2:
        xalign 0.5
        yalign 0.55
        spacing 20

        for f in FRAGMENTS:
            $ known_f = known(f["id"])
            $ stab = f["stab"]
            $ match = f["match"]
            frame:
                xsize 520
                ysize 300
                background Solid("#0d1117")
                if known_f:
                    vbox:
                        spacing 6
                        hbox:
                            text "ВОСПОМИНАНИЕ " + f["num"] size 16 color "#7fe7ff"
                            text f["src"] size 16 color ("#ff6b6b" if f["unknown"] else "#8ef5b0") xalign 1.0
                        text f["title"] size 22 color "#ffffff"
                        text f["text"] size 15 color "#c9d6de" xsize 480
                        hbox:
                            text "Стабильность" size 14 color "#6b7d89" yalign 0.5
                            bar value stab range 100 xsize 200 ysize 6 yalign 0.5
                            text "[stab]%" size 14 color "#ffffff" yalign 0.5
                        hbox:
                            text "Совпадение  " size 14 color "#6b7d89" yalign 0.5
                            bar value match range 100 xsize 200 ysize 6 yalign 0.5
                            text "[match]%" size 14 color "#ffffff" yalign 0.5
                        text ("Источник воспоминания: неизвестен" if f["unknown"] else "Источник воспоминания: подтверждён"):
                            size 13
                            color "#6b7d89"
                        if f["conflict"]:
                            text "⚠ Фрагмент содержит конфликтующие данные.":
                                size 13
                                color "#ffb765"
                        if f["stab"] < 45:
                            text "⚠ Низкая стабильность: деталь может рассыпаться.":
                                size 13
                                color "#ffb765"
                else:
                    vbox:
                        spacing 6
                        text "ВОСПОМИНАНИЕ " + f["num"] size 16 color "#7fe7ff"
                        text "███████████" size 22 color "#33454f"
                        text "Фрагмент не найден. Ищи его через «фокус внимания» или реконструкцию.":
                            size 15
                            color "#6b7d89"
                            xsize 480

    textbutton "ЗАКРЫТЬ":
        xalign 0.98
        yalign 0.96
        action Return()

# ── Конфликт источников (пример: фрагмент #017) ────────────

label memory_conflict_017:
    # Три версии одной правды. Ни одна не главнее.
    "Майк помнит: «В комнате было 4 человека»."
    "Уилл помнит: «В комнате было 3 человека»."
    "Архив говорит: «В комнате было 2 человека»."

    menu:
        "Чьей версии поверить?"
        "Майку (4)":
            $ log_choice("17-й фрагмент: поверил Майку (4 человека)")
            $ add_sync(6)
        "Уиллу (3)":
            $ log_choice("17-й фрагмент: поверил Уиллу (3 человека)")
            $ add_sync(10)
        "Архиву (2)":
            $ log_choice("17-й фрагмент: поверил архиву (2 человека)")
            $ add_sync(-4)
        "Никому":
            $ log_choice("17-й фрагмент: не поверил никому")
    "Истина не хранится нигде. Но выбор уже записан."
    return
