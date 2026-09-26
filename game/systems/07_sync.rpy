# =============================================================
#  SIMULACRA · 07_sync.rpy
#  «СВЯЗЬ МАЙК ↔ УИЛЛ» — не шкала отношений, а СИНХРОНИЗАЦИЯ.
#
#   30%  Уилл слышит мысли Майка
#   50%  Майк видит воспоминания Уилла
#   70%  они говорят одновременно
#   90%  игрок не понимает, чьими глазами смотрит
#  100%  интерфейс объединяется
#
#  Показывать индикатор всегда:  show screen sync_hud
# =============================================================

init python:

    SYNC_STAGES = [
        (0,   "НЕТ СВЯЗИ",          "Майк: «Я один в своей голове. Пока.»"),
        (30,  "ШЁПОТ",              "Уилл слышит мысли Майка. Майк думает, что произнёс их вслух."),
        (50,  "ЧУЖАЯ ПАМЯТЬ",       "Майк начинает видеть воспоминания Уилла как свои."),
        (70,  "УНИСОН",             "Они начинают говорить одновременно. Одинаковые слова."),
        (90,  "РАСЩЕПЛЕНИЕ",        "Игрок уже не понимает, чьими глазами сейчас смотрит."),
        (100, "СЛИЯНИЕ",            "Интерфейс объединяется. Две подписи становятся одной."),
    ]

    def sync_stage(value=None):
        v = store.sync_level if value is None else value
        cur = SYNC_STAGES[0]
        for at, title, text in SYNC_STAGES:
            if v >= at:
                cur = (at, title, text)
        return cur

    def _who(name, display):
        """Лениво создаёт персонажа, если он ещё не объявлен."""
        ch = getattr(store, name, None)
        if ch is None:
            ch = Character(display, color="#7fe7ff")
            setattr(store, name, ch)
        return ch

    def sync_say(mike_line, will_line):
        """
        Реплика, которая ведёт себя по-разному в зависимости от
        уровня синхронизации. Один вызов — вместо обычного say.

            $ sync_say("Дверь была закрыта.", "Дверь была закрыта.")
        """
        s = store.sync_level
        mike = _who("mike", "Майк")
        will = _who("will", "Уилл")

        if s >= 100:
            merged = _who("mike_will", "МАЙК+УИЛЛ")
            renpy.say(merged, mike_line)
        elif s >= 90:
            # непонятно, кто говорит: подпись и текст расходятся
            if renpy.random.random() < 0.5:
                renpy.say(will, mike_line)
            else:
                renpy.say(mike, will_line)
        elif s >= 70:
            renpy.say(mike, mike_line)      # унисон: одни и те же слова
            renpy.say(will, mike_line)
        elif s >= 50:
            renpy.say(will, will_line)
            renpy.say(mike, "…")            # Майк уже не уверен, чьё это
        elif s >= 30:
            renpy.say(will, "Не думай об этом вслух. Я слышу.")
            renpy.say(mike, mike_line)
        else:
            renpy.say(mike, mike_line)

    def sync_check():
        """Показывать уведомление при переходе порога."""
        cur_at = sync_stage()[0]
        if getattr(store, "_sync_last_stage", -1) == cur_at:
            return
        store._sync_last_stage = cur_at
        if cur_at > 0:
            renpy.notify("СИНХРОНИЗАЦИЯ %d%% — %s" % (cur_at, sync_stage()[1]))

# ── Индикатор поверх игры ──────────────────────────────────

default _sync_last_stage = -1

screen sync_hud():
    zorder 120
    $ s = store.sync_level
    $ stage = sync_stage()
    $ merged = s >= 100

    frame:
        xalign 0.99
        yalign 0.02
        xsize 320
        background Solid("#0d1117cc")
        padding (12, 10)
        vbox:
            spacing 4
            hbox:
                if merged:
                    text "МАЙК+УИЛЛ" size 14 color "#ffffff"
                else:
                    text "WILL ↔ MIKE" size 14 color "#6b7d89"
                text ("SYNC " + str(s) + "%"):
                    size 14
                    color ("#ffffff" if merged else "#7fe7ff")
                    xalign 1.0
            bar:
                value s
                range 100
                xsize 296
                ysize 5
            text (stage[1] + " — " + stage[2]):
                size 11
                color "#6b7d89"
                xsize 296

    timer 0.5 repeat True action Function(sync_check)
