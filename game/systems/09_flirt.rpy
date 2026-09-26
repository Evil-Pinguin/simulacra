# =============================================================
#  SIMULACRA · 09_flirt.rpy
#  «ИНОГДА ФЛИРТОВАТЬ» — случайные вставки в диалог.
#
#  ЛЮБОВНОЙ ЛИНИИ НЕТ. Ни очков отношений, ни флагов, ни ветвлений:
#  просто краска в разговоре. Ли и Ким — коллеги и друзья по работе.
#
#  Использование — одна строка в любой точке диалога:
#      l "Отбой. Живые — уже победа."
#      $ flirt("li", "kim")
#      kim "..."
#
#  Тумблер в настройках (screens.rpy → screen preferences):
#      textbutton "Флирт в диалогах" action ToggleField(persistent, "flirt_enabled")
# =============================================================

default persistent.flirt_enabled = True  # тумблер в настройках
default flirt_allowed = True             # глушилка на тяжёлые сцены
default flirt_chance = 0.35              # шанс вставки в точке вызова
default flirt_cd = 0                     # откат: сколько точек молчим
default flirt_recent = []                # антиповтор

init python:

    FLIRT_CD = 3              # точек вызова между вставками
    FLIRT_KEEP = 3            # сколько последних реплик не повторять
    FLIRT_REPLY_CHANCE = 0.5  # шанс сухого ответа собеседника

    # Ключ — имя переменной персонажа (строка).
    #   None      — реплика «любому собеседнику»
    #   "kim"     — реплика, адресованная именно Ким
    flirt_lines = {
        "li": {
            None: [
                "Ты сегодня опаснее обычного. Мне нравится.",
                "Смотри, не понравься мне слишком сильно. Я плохо отпускаю.",
                "Красиво работаешь. Жаль, по должности обязан делать вид, что это не комплимент.",
            ],
            "kim": [
                "У тебя вид человека, который не спал двое суток. Красивый вид. Но я всё равно отправлю тебя спать.",
                "Ким, если ты сломаешься, мне будет скучно. Не сломайся.",
                "Я бы сказал «береги себя». Но ты знаешь, что я имел в виду.",
            ],
        },
        "kim": {
            None: [
                "Если выживем — я поставлю. И не провожай меня, я сама.",
                "Ты сегодня в ударе. Осторожнее, я могу привыкнуть.",
                "Не подумай ничего: я просто рада, что ты ещё разговариваешь.",
            ],
            "li": [
                "Ли, это был комплимент? Не морщись, я ничего не записывала.",
                "Ты волнуешься. Это почти мило. Почти.",
                "Если я когда-нибудь перестану спорить — считай, что меня подменили.",
                "Мы коллеги, Ли. Просто в твоей компании я выгляжу лучше.",
            ],
        },
        "_any": {
            None: [
                "Живой и целый — уже неплохо для начала смены.",
                "С тобой хоть поговорить можно. Не то что с остальными.",
            ],
        },
    }

    # Сухие ответы: уводят флирт в работу. Романтики ноль.
    flirt_replies = {
        "kim": [
            "Это комплимент? Тогда запиши его в отчёт, я подпишу.",
            "Ли, мы на работе. Но спасибо. Наверное.",
            "Не начинай. Мне ещё бумажки до утра.",
        ],
        "li": [
            "Я ничего не слышал.",
            "Продолжай. Не отвечу взаимностью — у меня смена.",
            "Записал. Рассмотрю после разбора.",
        ],
    }

    def flirt(who, target=None, chance=None, force=False, reply=True):
        """
        Иногда вставляет лёгкую флирт-реплику от who к target.
        who, target — имена переменных персонажей строками ("li", "kim").
        force=True  — вставить гарантированно (проверка звучания).
        Никаких очков отношений: только реплика в диалоге.
        """
        if not force:
            if not store.persistent.flirt_enabled or not store.flirt_allowed:
                return False
            if store.flirt_cd > 0:
                store.flirt_cd -= 1
                return False
            c = store.flirt_chance if chance is None else chance
            if renpy.random.random() >= c:
                return False

        lines = flirt_lines.get(who) or flirt_lines.get("_any", {})
        pool = list(lines.get(None, []))
        if target:
            pool += list(lines.get(target, []))
        if not pool:
            return False

        fresh = [x for x in pool if x not in store.flirt_recent]
        if fresh:
            line = renpy.random.choice(fresh)
        else:
            line = renpy.random.choice(pool)
            store.flirt_recent = []
        store.flirt_recent = ([line] + list(store.flirt_recent))[:FLIRT_KEEP]

        speaker = getattr(store, who, None)
        if speaker is None:
            return False
        renpy.say(speaker, line)

        if not force:
            store.flirt_cd = FLIRT_CD
            if reply and target and renpy.random.random() < FLIRT_REPLY_CHANCE:
                answers = flirt_replies.get(target) or []
                other = getattr(store, target, None)
                if answers and other is not None:
                    renpy.say(other, renpy.random.choice(answers))
        return True
