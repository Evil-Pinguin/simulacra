# =============================================================
#  SIMULACRA · 01_state.rpy
#  Состояние игры + общие помощники. Остальные системы
#  опираются на этот файл — подключайте его первым.
#  Папка game/systems/ подхватывается Ren'Py автоматически.
# =============================================================

# ── Переменные (участвуют в сохранениях и откате) ───────────
default sync_level = 0        # СИНХРОНИЗАЦИЯ Майк ↔ Уилл, 0..100
default pass_number = 1       # номер круга: «повторение с изменениями»
default found_fragments = []  # id найденных фрагментов
default archive_links = []    # id найденных связей в архиве
default achievements = []     # id достижений
default canvas_place = {}     # piece_id -> cell_id (NEURAL CANVAS)
default focus_charge = 0.0    # «фокус внимания»: накопление взгляда
default focus_target = None   # id горячей точки под взглядом
default seen_flashback = False

init python:

    # ── Константы ───────────────────────────────────────────

    # Фрагменты памяти. stab — стабильность, match — совпадение с
    # архивом. unknown=True — источник неизвестен (печатается «???»).
    FRAGMENTS = [
        dict(id="f_drawing", num="#017", title="РИСУНОК", src="Уилл", stab=64, match=81,
             text="Лист А4, карандаш. Человек и красный круг вместо головы.",
             unknown=True, conflict=True),
        dict(id="f_stain", num="#019", title="ПЯТНО НА ПОЛУ", src="Майк", stab=41, match=58,
             text="Пятно у выхода. Майк помнит его круглым. Схема — вытянутое.",
             unknown=False, conflict=False),
        dict(id="f_11g", num="11-G", title="ИНЦИДЕНТ 11-G", src="Архив", stab=88, match=95,
             text="Школа №— [[данные изъяты]. Класс: 26 детей, преподаватель, персонал.",
             unknown=False, conflict=False),
        dict(id="f_masha", num="#023", title="МАША", src="Уилл", stab=72, match=66,
             text="Девочка из 11-G. Ни в одном списке эвакуации её нет.",
             unknown=False, conflict=False),
        dict(id="f_lee", num="#031", title="ЛИ", src="Майк", stab=55, match=74,
             text="Азаит. Пришёл первым, ушёл последним. Отчёт написал раньше, чем случилось.",
             unknown=False, conflict=False),
        dict(id="f_redlamp", num="#044", title="КРАСНАЯ ЛАМПА", src="???", stab=22, match=39,
             text="Красный свет в торце коридора. Источник не установлен.",
             unknown=True, conflict=False),
    ]
    FRAGMENT_BY_ID = dict((f["id"], f) for f in FRAGMENTS)

    ACHIEVEMENTS = {
        "first_fragment": "первый фрагмент",
        "focus_first":    "первый микро-триггер",
        "first_link":     "первая связь в архиве",
        "detective":      "собрать 4 связи",
        "true_memory":    "истинное воспоминание",
        "partial_memory": "частично верная реконструкция",
        "false_memory":   "ложное воспоминание",
        "sync100":        "100% синхронизации",
    }

    # ── Помощники ───────────────────────────────────────────

    def unlock(aid):
        """Выдать достижение (один раз)."""
        if aid in store.achievements:
            return False
        store.achievements.append(aid)
        name = ACHIEVEMENTS.get(aid, aid)
        renpy.notify("ДОСТИЖЕНИЕ: " + name)
        return True

    def add_sync(n):
        """Изменить синхронизацию Майк ↔ Уилл."""
        store.sync_level = max(0, min(100, store.sync_level + int(n)))
        if store.sync_level >= 100:
            unlock("sync100")
        return store.sync_level

    def find_fragment(fid):
        """Найти фрагмент памяти. Возвращает True, если он новый."""
        if fid in store.found_fragments:
            return False
        store.found_fragments.append(fid)
        f = FRAGMENT_BY_ID.get(fid)
        renpy.notify("ФРАГМЕНТ ПОЛУЧЕН: " + (f["title"] if f else fid))
        add_sync(4)
        unlock("first_fragment")
        return True

    def known(fid):
        return fid in store.found_fragments

    def drift_memories(amount=8):
        """
        Память портится между кругами: стабильность плавает.
        ВАЖНО: меняет константы FRAGMENTS — они не сохраняются в сейв,
        поэтому при загрузке значения вернутся к базовым. Если нужно
        сохранение дрейфа — перенеси stab в default-переменную.
        """
        for f in FRAGMENTS:
            f["stab"] = max(5, min(100, f["stab"] + renpy.random.randint(-amount, amount)))

    def start_new_pass(keep_memory=True):
        """Новый круг: реальность сбрасывается, воспоминания — нет."""
        store.pass_number += 1
        if not keep_memory:
            store.found_fragments = []
            store.archive_links = []
        store.canvas_place = {}
        store.focus_charge = 0.0
        store.focus_target = None
        drift_memories()
        renpy.notify("КРУГ %d. Воспоминания остались, реальность — нет." % store.pass_number)
