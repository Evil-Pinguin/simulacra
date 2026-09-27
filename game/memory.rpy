# Механики памяти «Simulacra»: фрагменты и их достоверность,
# синхронизация Майк ↔ Уилл, архив Майка (связи между фактами),
# шёпот и «повторение с изменениями».
#
# Правило: всё, что начинает взаимодействие (карточка, реплика, пауза),
# вызывается ТОЛЬКО из сценария (label / $), а не из действий экранов.


# СОСТОЯНИЕ ##############################################################

default found_fragments = []       # id найденных фрагментов, в порядке находки
default archive_links = []         # ключи найденных связей "a|b"
default archive_misses = 0         # неудачные попытки связать факты
default sync_level = 0             # синхронизация Майк ↔ Уилл, 0..100
default sync_stage_seen = 0        # последний порог, о котором сообщали
default frag_mod = {}              # поправки стабильности: id -> delta
default belief_050 = None          # чьей версии поверил в конфликте #050
default memory_11g = None          # реконструкция 11-G: "true" / "partial" / "false"
default chapter_tag = "01"         # для истории выборов

# То, что переживает «новый круг» (New Game+) и хранится между сессиями.
default persistent.pass_number = 1
default persistent.choice_log = []
default persistent.mem_fragments = []
default persistent.mem_links = []
default persistent.mem_sync = 0
default persistent.endings_seen = []
default persistent.finished_ch3 = False
default persistent.drawing_seen = False


# ФРАГМЕНТЫ ПАМЯТИ: ДАННЫЕ ###############################################
# stab — стабильность (насколько фрагмент держится), match — совпадение
# с архивом. unknown — источник воспоминания не установлен. conflict —
# фрагмент противоречит другим источникам. Истины нет ни в одном из них.

init python:

    FRAG_CATS = [
        ("evidence", "ПОКАЗАНИЯ"),
        ("incidents", "ИНЦИДЕНТЫ"),
        ("people", "ЛЮДИ"),
    ]

    FRAGMENTS = [
        dict(id="f_field", num="#003", title="ПОЛЕ", cat="evidence", src="???",
             stab=58, match=40, unknown=True, conflict=False,
             text="Снег вплотную к лицу, тропинка, дверь без дома. Сны так не выглядят. Так выглядит запись."),
        dict(id="f_visitor", num="#005", title="ПОСЕТИТЕЛЬ", cat="people", src="Ким",
             stab=90, match=0, unknown=False, conflict=False,
             text="Ищет человека без имени и фото. «Я помню, как он смеётся». В базе не значится."),
        dict(id="f_corridor", num="#009", title="ЗЕЛЁНЫЙ КОРИДОР", cat="evidence", src="Майк",
             stab=66, match=91, unknown=False, conflict=True,
             text="Длинный коридор, стены цвета школы. Звонок, который не кончается. Я вижу его каждую ночь."),
        dict(id="f_alarm", num="#012", title="ЗВОНОК", cat="evidence", src="???",
             stab=34, match=77, unknown=True, conflict=False,
             text="Красный сигнал под потолком. В архиве такой звук называется «учебная тревога». Дети выходят во двор по списку."),
        dict(id="f_paper", num="#017", title="ЛИСТ", cat="evidence", src="Уилл",
             stab=64, match=81, unknown=True, conflict=True,
             text="Лист А4, сложенный вчетверо, уголком внутрь. Детская рука. Внутри — то, что я не разворачиваю."),
        dict(id="f_key", num="#021", title="КЛЮЧ", cat="evidence", src="Уилл",
             stab=80, match=70, unknown=False, conflict=False,
             text="Старый ключ на подоконнике. Тёплый — будто его только что держали. Якоря просто так не лежат."),
        dict(id="f_tv", num="#022", title="ПЕРЕДАТЧИК", cat="evidence", src="Майк",
             stab=47, match=12, unknown=False, conflict=True,
             text="Телевизор внутри воспоминания вещает. Записи не вещают — им нечем. Этот — вещал."),
        dict(id="f_badge", num="#027", title="0117-М", cat="incidents", src="Архив",
             stab=95, match=100, unknown=False, conflict=False,
             text="Подписи под санациями за семь лет: оператор 0117-М. Я работаю здесь три года. Мой бейдж: 0117-М."),
        dict(id="f_figure", num="#031", title="НАБЛЮДАТЕЛЬ", cat="people", src="Майк",
             stab=52, match=0, unknown=False, conflict=True,
             text="Человек у забора в чужой памяти. В записи некому смотреть. Он смотрел."),
        dict(id="f_hand", num="#044", title="МАЛЕНЬКАЯ РУКА", cat="evidence", src="???",
             stab=29, match=60, unknown=True, conflict=False,
             text="Маленькая ладонь в моей. Кто-то ведёт меня по коридору. Или я веду. «Не бойся. Это просто учебные сборы»."),
        dict(id="f_will", num="#117", title="УИЛЛ", cat="people", src="Уилл",
             stab=77, match=55, unknown=False, conflict=False,
             text="Пациент №117-У. Заговорил со мной внутри собственной памяти. Записи не называют оператора по имени. Он назвал."),
        dict(id="f_11g", num="11-G", title="ИНЦИДЕНТ 11-G", cat="incidents", src="Архив",
             stab=100, match=100, unknown=False, conflict=False,
             text="Школа №— [[данные изъяты]. 26 детей, преподаватель, персонал. Свидетелей санации: 31."),
        dict(id="f_erasure", num="#050", title="РАПОРТ О САНАЦИИ", cat="incidents", src="Архив",
             stab=88, match=95, unknown=False, conflict=True,
             text="После 11-G оператор 0117-М подал рапорт о стирании собственной памяти. Свидетель процедуры — по его требованию — гражданин У."),
        dict(id="f_redlamp", num="#061", title="КРАСНАЯ ЛАМПА", cat="evidence", src="???",
             stab=22, match=39, unknown=True, conflict=False,
             text="Красный свет в торце коридора. Источник не установлен. Он горел ещё до звонка."),
        dict(id="f_false11g", num="11-G*", title="11-G (РЕКОНСТРУКЦИЯ)", cat="incidents", src="Майк",
             stab=100, match=3, unknown=False, conflict=True,
             text="Собрано вручную. Не совпадает с архивной схемой — и всё равно ощущается как своё. Теперь это тоже воспоминание."),
    ]
    FRAGMENT_BY_ID = dict((f["id"], f) for f in FRAGMENTS)

    # Связи: перетащи один факт на другой. Порядок пары не важен.
    LINKS = [
        dict(a="f_paper", b="f_corridor", sync=6,
             out="Лист — из школы. Сложен так, как складывают дети: вчетверо, уголком внутрь. Он лежал у меня в кармане ещё до того, как я увидел коридор."),
        dict(a="f_badge", b="f_11g", sync=9,
             out="Подпись под санацией 11-G — 0117-М. Мой бейдж. Мой почерк. Система не переиспользует номера."),
        dict(a="f_corridor", b="f_11g", sync=8,
             out="Зелёный коридор — школа из файла 11-G. Я не видел его во сне. Я его помнил."),
        dict(a="f_figure", b="f_will", sync=7,
             out="Наблюдатель у забора — Уилл. Он смотрел на меня из собственной памяти. Он ждал, что я приду снова."),
        dict(a="f_alarm", b="f_11g", sync=6,
             out="Звонок — сигнал учебной тревоги. «Это просто учебные сборы». Дети вышли во двор по списку. Список — на 26 человек."),
        dict(a="f_visitor", b="f_will", sync=5,
             out="Посетитель не знает имени. Уилл знает моё. Оба помнят одного человека — того, кто ещё умел смеяться."),
        dict(a="f_tv", b="f_will", sync=6,
             out="Передатчик в памяти — это он. Уилл вещал мне из записи, пока я думал, что просто слушаю."),
        dict(a="f_hand", b="f_alarm", sync=7,
             out="Маленькая рука. Учебная тревога. Я выводил детей во двор. Я знал, что это не учения."),
        dict(a="f_erasure", b="f_will", sync=10,
             out="Свидетель моего стирания — 117-У. Я сам попросил его смотреть. Чтобы хоть кто-то помнил меня целиком."),
        dict(a="f_field", b="f_erasure", sync=6,
             out="Поле — не сон. Первое, что записалось после стирания: снег, тропинка, дверь. Мой первый слой."),
        dict(a="f_key", b="f_paper", sync=4,
             out="Ключ и лист лежали в одном доме, в одной памяти — и оба оказались у меня. Якоря выбирают сами."),
        dict(a="f_redlamp", b="f_hand", sync=6,
             out="Красный свет горел, когда я вёл ребёнка. Он горел до звонка. Тревогу включили после того, как всё началось."),
    ]

    def link_key(a, b):
        return "|".join(sorted((a, b)))

    LINK_BY_KEY = dict((link_key(l["a"], l["b"]), l) for l in LINKS)

    def frag(fid):
        return FRAGMENT_BY_ID.get(fid)

    def frag_known(fid):
        return fid in store.found_fragments

    def frag_stab(f):
        return max(3, min(100, f["stab"] + store.frag_mod.get(f["id"], 0)))

    def frag_shift(fid, delta):
        """Сдвинуть стабильность фрагмента (калибровка, дрейф между кругами)."""
        store.frag_mod[fid] = store.frag_mod.get(fid, 0) + delta

    def known_fragments():
        return [FRAGMENT_BY_ID[i] for i in store.found_fragments if i in FRAGMENT_BY_ID]

    def find_fragment(fid):
        """Найти фрагмент. Возвращает True, если он новый. Карточку показывает сценарий."""
        if fid not in FRAGMENT_BY_ID or fid in store.found_fragments:
            return False
        store.found_fragments.append(fid)
        if len(store.found_fragments) == 1:
            unlock_ach("ach_fragment")
        add_sync(3)
        return True

    def bar_text(value, width=10):
        """Полоска из блоков: ▮▮▮▮░░░░░░."""
        n = int(round(max(0, min(100, value)) / 100.0 * width))
        return "▮" * n + "░" * (width - n)


# СИНХРОНИЗАЦИЯ МАЙК ↔ УИЛЛ ##############################################
# Не шкала отношений. Чем выше — тем меньше понятно, чья это голова.

init python:

    SYNC_STAGES = [
        (0,   "НЕТ СВЯЗИ",    "Я один в своей голове. Пока."),
        (30,  "ШЁПОТ",        "Уилл слышит мысли Майка."),
        (50,  "ЧУЖАЯ ПАМЯТЬ", "Майк видит воспоминания Уилла как свои."),
        (70,  "УНИСОН",       "Они говорят одновременно."),
        (90,  "РАСЩЕПЛЕНИЕ",  "Чьими глазами ты сейчас смотришь?"),
        (100, "СЛИЯНИЕ",      "Две подписи становятся одной."),
    ]

    def sync_stage(value=None):
        v = store.sync_level if value is None else value
        cur = SYNC_STAGES[0]
        for st in SYNC_STAGES:
            if v >= st[0]:
                cur = st
        return cur

    def add_sync(n):
        """Изменить синхронизацию. При переходе порога — тост."""
        store.sync_level = max(0, min(100, store.sync_level + int(n)))
        at, title, desc = sync_stage()
        if at > store.sync_stage_seen:
            store.sync_stage_seen = at
            renpy.show_screen("achievement_toast", "SYNC " + str(at) + " // " + title, desc, "▮ СИНХРОНИЗАЦИЯ")
            play_sys_voice("sync_" + str(at))
            if at >= 50:
                unlock_ach("ach_sync50")
            if at >= 100:
                unlock_ach("ach_sync100")
        elif at < store.sync_stage_seen:
            store.sync_stage_seen = at
        return store.sync_level

    def sync_name(base):
        """Подпись говорящего. После 90 подписи путаются, на 100 — сливаются."""
        s = store.sync_level
        if s >= 100:
            return "// МАЙК+117-У"
        if s >= 90 and renpy.random.random() < 0.5:
            return "// 117-У" if base == "МАЙК" else "// МАЙК"
        return "// " + base

    def sync_say(mike_line, will_line=None):
        """Реплика, которая ведёт себя по-разному в зависимости от синхронизации."""
        will_line = will_line or mike_line
        s = store.sync_level
        if s >= 100:
            renpy.say(store.m, mike_line)
        elif s >= 70:
            renpy.say(store.m, mike_line)
            renpy.say(store.w, will_line)
        elif s >= 50:
            renpy.say(store.w, will_line)
            renpy.say(store.m, "…")
        else:
            renpy.say(store.m, mike_line)

    def whisper(text):
        """Шёпот Уилла в голове Майка. Слышен только с порога 30."""
        if store.sync_level >= 30:
            renpy.say(store.wsp, text)

# Шёпот: без подписи, курсивом, чужим цветом.
define wsp = Character(None, what_italic=True, what_color="#8fb8a8", what_prefix="«", what_suffix="»")


# ИНДИКАТОР СИНХРОНИЗАЦИИ ################################################

screen sync_hud():

    zorder 900

    if sync_level > 0 and not renpy.get_screen("journal_screen"):

        $ _st = sync_stage()

        vbox:
            xanchor 1.0
            xpos 0.985
            ypos 12
            spacing 1

            text ("МАЙК+УИЛЛ" if sync_level >= 100 else "WILL // MIKE"):
                xalign 1.0
                size 12
                color "#51726399"
                font "fonts/game_mono.ttf"

            text ("SYNC " + bar_text(sync_level) + " " + str(sync_level)):
                xalign 1.0
                size 15
                color ("#ffffff" if sync_level >= 100 else "#7fd4a8")
                font "fonts/game_mono.ttf"
                outlines [(2, "#04070a", 0, 0)]

            text _st[1]:
                xalign 1.0
                size 11
                color "#51726377"
                font "fonts/game_mono.ttf"


# КАРТОЧКА ФРАГМЕНТА: ДОСТОВЕРНОСТЬ ######################################
# Показывается сценарием: call screen fragment_card("f_paper")

screen fragment_card(fid, compact=False):

    modal True
    zorder 1600

    $ f = frag(fid)
    $ st = frag_stab(f)

    add Solid("#04070ad0")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 46
        ypadding 36
        background Solid("#0a1014f4")

        vbox:
            spacing 14
            xsize 880

            hbox:
                xfill True
                text ("ВОСПОМИНАНИЕ " + f["num"]) size 26 color "#c8ffd8" font "fonts/game_mono.ttf"
                text ("Источник: " + f["src"]) size 18 color ("#d95a5a" if f["unknown"] else "#7fd4a8") font "fonts/game_mono.ttf" xalign 1.0 yalign 0.5

            text f["title"] size 32 color "#ffffff" font "fonts/game_serif.ttf"

            null height 4

            text ("Стабильность:  " + bar_text(st) + "  " + str(st) + "%") size 18 color "#9fd8b8" font "fonts/game_mono.ttf"
            text ("Совпадение:    " + bar_text(f["match"]) + "  " + str(f["match"]) + "%") size 18 color "#9fd8b8" font "fonts/game_mono.ttf"
            text ("Источник воспоминания: " + ("неизвестен" if f["unknown"] else "подтверждён")) size 16 color "#517263" font "fonts/game_mono.ttf"

            if f["conflict"]:
                text "⚠ ВНИМАНИЕ. Фрагмент содержит конфликтующие данные." size 16 color "#e0b060" font "fonts/game_mono.ttf"
            if st < 40:
                text "⚠ Низкая стабильность: деталь может рассыпаться при следующем обращении." size 16 color "#e0b060" font "fonts/game_mono.ttf"

            null height 6

            text f["text"] size 21 color "#9fb8ac" font "fonts/game_serif.ttf"

            null height 10

            textbutton "ЗАФИКСИРОВАТЬ" style "mm_button" xalign 1.0 action Return(True)

    key "K_ESCAPE" action Return(True)


# Сценарный помощник: найти фрагмент и показать карточку.
label fragment_found(fid):
    if find_fragment(fid):
        call screen fragment_card(fid)
    return


# АРХИВ МАЙКА: СВЯЗИ #####################################################
# Найденные факты лежат по разделам. Игрок перетаскивает факт на факт.
# Совпало — «СВЯЗЬ ОБНАРУЖЕНА»: новая запись и синхронизация.

init python:

    ARCHIVE_COLS = {"evidence": 60, "incidents": 470, "people": 880}
    ARCHIVE_TOP = 70
    ARCHIVE_ROW = 78

    def archive_home(fid):
        f = frag(fid)
        cat = f["cat"]
        same = [x["id"] for x in known_fragments() if x["cat"] == cat]
        i = same.index(fid) if fid in same else 0
        return (ARCHIVE_COLS.get(cat, 60), ARCHIVE_TOP + i * ARCHIVE_ROW)

    def try_link(a, b):
        """Попытка связать два факта. Только уведомления — без интеракций."""
        if not a or not b or a == b:
            return False
        key = link_key(a, b)
        if key in store.archive_links:
            renpy.show_screen("achievement_toast", "УЖЕ В АРХИВЕ", "эта связь известна", "▮ АРХИВ")
            return False
        link = LINK_BY_KEY.get(key)
        if link is None:
            store.archive_misses += 1
            renpy.show_screen("achievement_toast", "СВЯЗЬ НЕ ПОДТВЕРЖДЕНА", "пока", "▮ АРХИВ")
            return False
        store.archive_links.append(key)
        add_sync(link["sync"])
        renpy.show_screen("achievement_toast",
                          frag(a)["title"] + " + " + frag(b)["title"],
                          "+" + str(link["sync"]) + " к синхронизации",
                          "▮ СВЯЗЬ ОБНАРУЖЕНА")
        unlock_ach("ach_link")
        if len(store.archive_links) >= 5:
            unlock_ach("ach_detective")
        return True

    def archive_dragged(drags, drop):
        d = drags[0]
        hx, hy = archive_home(d.drag_name)
        d.snap(hx, hy, 0.25)
        if drop is None or drop.drag_name == d.drag_name:
            return
        try_link(d.drag_name, drop.drag_name)
        renpy.restart_interaction()

    def known_links():
        return [LINK_BY_KEY[k] for k in store.archive_links if k in LINK_BY_KEY]

    def links_available():
        """Сколько связей можно найти из уже собранных фрагментов."""
        n = 0
        for l in LINKS:
            if frag_known(l["a"]) and frag_known(l["b"]):
                n += 1
        return n


screen archive_board():

    # Заголовки разделов
    for cat, title in FRAG_CATS:
        text title:
            xpos ARCHIVE_COLS[cat]
            ypos 30
            size 16
            color "#517263"
            font "fonts/game_mono.ttf"

    if not found_fragments:
        text "Фрагментов пока нет. Они находятся во сне, в чужой памяти и в архиве.":
            xpos 60
            ypos 80
            size 19
            color "#33473d"
            font "fonts/game_serif.ttf"

    draggroup:
        xpos 0
        ypos 0
        xsize 1290
        ysize 700

        for f in known_fragments():
            $ hx, hy = archive_home(f["id"])
            drag:
                drag_name f["id"]
                draggable True
                droppable True
                drag_raise True
                dragged archive_dragged
                xpos hx
                ypos hy

                frame:
                    background Solid("#0a1014")
                    xysize (370, 66)
                    padding (14, 8)
                    hbox:
                        spacing 12
                        add Solid("#7fd4a8" if not f["unknown"] else "#d95a5a") xsize 4 ysize 48
                        vbox:
                            spacing 2
                            text f["title"] size 18 color "#c8ffd8" font "fonts/game_mono.ttf"
                            text (f["num"] + " · " + f["src"] + " · " + str(frag_stab(f))) size 13 color "#517263" font "fonts/game_mono.ttf"

    # Выводы
    vbox:
        xpos 1310
        ypos 30
        xsize 560
        spacing 10

        text ("ВЫВОДЫ  " + str(len(archive_links)) + " / " + str(len(LINKS))) size 16 color "#517263" font "fonts/game_mono.ttf"

        if found_fragments:
            text "Перетащи один факт на другой." size 14 color "#33473d" font "fonts/game_mono.ttf"

        viewport:
            xsize 560
            ysize 610
            scrollbars "vertical"
            mousewheel True

            vbox:
                spacing 12

                for l in known_links():
                    frame:
                        background Solid("#0a1014")
                        xsize 530
                        padding (14, 12)
                        vbox:
                            spacing 4
                            text (frag(l["a"])["title"] + "  +  " + frag(l["b"])["title"]) size 13 color "#517263" font "fonts/game_mono.ttf"
                            text l["out"] size 17 color "#c8ffd8" font "fonts/game_serif.ttf"

                if not known_links():
                    text "связей пока нет" size 16 color "#33473d" font "fonts/game_mono.ttf"


# ФРАГМЕНТЫ: СПИСОК ДЛЯ ДНЕВНИКА #########################################

screen fragment_list():

    viewport:
        xsize 1800
        ysize 690
        scrollbars "vertical"
        mousewheel True

        vbox:
            spacing 18

            if not found_fragments:
                text "Фрагментов пока нет." size 22 color "#517263" font "fonts/game_serif.ttf"

            for f in known_fragments():
                $ st = frag_stab(f)
                frame:
                    background Solid("#0a1014")
                    xsize 1760
                    padding (20, 16)
                    hbox:
                        spacing 24
                        add Solid("#7fd4a8" if not f["unknown"] else "#d95a5a") xsize 5 ysize 84
                        vbox:
                            spacing 6
                            xsize 1050
                            hbox:
                                spacing 18
                                text ("ВОСПОМИНАНИЕ " + f["num"]) size 16 color "#7fd4a8" font "fonts/game_mono.ttf"
                                text f["title"] size 22 color "#c8ffd8" font "fonts/game_serif.ttf"
                            text f["text"] size 17 color "#9fb8ac" font "fonts/game_serif.ttf"
                        vbox:
                            spacing 4
                            text ("Источник: " + f["src"]) size 14 color ("#d95a5a" if f["unknown"] else "#7fd4a8") font "fonts/game_mono.ttf"
                            text ("Стабильность " + bar_text(st) + " " + str(st) + "%") size 14 color "#9fd8b8" font "fonts/game_mono.ttf"
                            text ("Совпадение   " + bar_text(f["match"]) + " " + str(f["match"]) + "%") size 14 color "#9fd8b8" font "fonts/game_mono.ttf"
                            if f["conflict"]:
                                text "⚠ конфликтующие данные" size 13 color "#e0b060" font "fonts/game_mono.ttf"


# ПОВТОРЕНИЕ С ИЗМЕНЕНИЯМИ ###############################################
# Одна и та же сцена на следующем круге звучит иначе. Игра это не объясняет.

init python:

    def variant(options):
        """Вариант реплики по номеру круга. Последний — для всех следующих кругов."""
        i = min(persistent.pass_number, len(options)) - 1
        return options[max(0, i)]

    def log_choice(caption):
        """История выборов (Choice History)."""
        entry = "КРУГ " + str(persistent.pass_number) + " · ЗАПИСЬ " + str(store.chapter_tag) + " · " + caption
        persistent.choice_log.append(entry)
        if len(persistent.choice_log) > 300:
            persistent.choice_log = persistent.choice_log[-300:]

    def persist_pass_memory():
        """Отложить память между кругами. Вызывается в конце главы."""
        for fid in store.found_fragments:
            if fid not in persistent.mem_fragments:
                persistent.mem_fragments.append(fid)
        for k in store.archive_links:
            if k not in persistent.mem_links:
                persistent.mem_links.append(k)
        persistent.mem_sync = max(persistent.mem_sync, store.sync_level)

    def start_new_pass():
        """New Game+: воспоминания остаются, реальность — нет."""
        persistent.pass_number += 1

    def restore_pass_memory():
        """Вызывается в начале игры на втором и следующих кругах."""
        store.found_fragments = list(persistent.mem_fragments)
        store.archive_links = list(persistent.mem_links)
        store.sync_level = min(60, persistent.mem_sync)
        store.sync_stage_seen = sync_stage()[0]
        # Память портится между кругами: стабильность плывёт.
        for f in FRAGMENTS:
            if f["id"] in store.found_fragments:
                store.frag_mod[f["id"]] = renpy.random.randint(-12, 6)


init 999 python:
    _mem_overlays = list(config.overlay_screens or [])
    if "sync_hud" not in _mem_overlays:
        _mem_overlays.append("sync_hud")
    config.overlay_screens = _mem_overlays
