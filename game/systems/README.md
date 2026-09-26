# SIMULACRA · системы (game/systems/)

Ren'Py подхватывает `.rpy` рекурсивно — просто скопируй папку в `game/`.
Порядок загрузки важен только для `01_state.rpy` (он первый по номеру).

| Файл | Что делает | Как вызвать |
|---|---|---|
| `01_state.rpy` | Состояние: фрагменты, синхронизация, номер круга, достижения, помощники | — (ядро) |
| `02_flashback.rpy` | Быстрая нарезка кадров перед входом в старый дом | `call flashback_old_house` |
| `03_focus.rpy` | «Фокус внимания»: удержание взгляда → микро-триггер | `call screen focus_scene(CORRIDOR_BG, CORRIDOR_HOTSPOTS)` |
| `04_memory.rpy` | Достоверность воспоминаний + повторение с изменениями | `call screen memory_screen` / `label memory_conflict_017` |
| `05_archive.rpy` | Архив Майка: перетаскивание фактов, поиск связей | `call screen mike_archive` |
| `06_canvas.rpy` | NEURAL CANVAS: реконструкция воспоминания | `call screen memory_canvas("11-G")` |
| `07_sync.rpy` | Синхронизация Майк ↔ Уилл, индикатор, `sync_say` | `show screen sync_hud` |
| `08_extras.rpy` | Character Gallery / Achievements / Endings / Replay / Choice History / NG+ | `ShowMenu("extras_menu")` |

## Быстрый старт

```renpy
# script.rpy, в label start — до первой сцены
label start:
    # New Game+: восстановить память, но не реальность
    if persistent.ng_plus:
        $ found_fragments = list(persistent.memory_fragments)
        $ archive_links = list(persistent.memory_links)
        $ sync_level = persistent.memory_sync

    show screen sync_hud          # индикатор SYNС 0..100
    jump chapter1
```

Файлы, которые нужно положить (без них не упадёт — есть заглушки):

```
game/images/flashback/fb1.jpg … fb4.jpg     # кадры флешбека
game/images/bg/corridor.jpg                 # фон коридора (фокус внимания)
game/images/gallery/*.jpg                   # портреты для галереи
game/audio/glitch.ogg                       # звук микро-триггера
```

Звук подменяется в `03_focus.rpy` последней строкой:
`define audio.simulacra_glitch = "audio/glitch.ogg"`.

## Как это встраивается в главу

```renpy
label chapter3_corridor:
    scene bg corridor

    # 1. Майк подходит к дому — сначала нарезка памяти
    if not seen_flashback:
        call flashback_old_house

    # 2. Исследование: игрок сам ищет, на что смотреть
    "Коридор. Свет включён, а дня нет."
    call screen focus_scene(CORRIDOR_BG, CORRIDOR_HOTSPOTS)

    # 3. Архив доступен в любой момент (например, по кнопке в quick_menu)
    #    call screen mike_archive

    # 4. Реплика, которая меняется от круга к кругу
    kim "[variant(['Ты сегодня рано.', 'Ты опять опоздал.', 'Ты опять опоздал. Или ты уже заходил?'])]"

    # 5. Синхронизация управляет тем, КТО говорит
    $ sync_say("Дверь была закрыта.", "Дверь была закрыта.")
    jump chapter3_class
```

Логирование выборов (для Choice History):

```renpy
menu:
    "Открыть дверь":
        $ log_choice("Открыл дверь 3-Б")
        ...
    "Уйти":
        $ log_choice("Не стал открывать")
        ...
```

## Петля геймплея (чтобы механики не жили порознь)

```
ФОКУС (исследование сцены)
   ↓ фрагмент
АРХИВ (связать факты → +синхронизация)
   ↓ связь
ХОЛСТ ПАМЯТИ (реконструкция → истинное / ложное воспоминание)
   ↓ воспоминание
СИНХРОНИЗАЦИЯ (кто вообще это помнит — Майк или Уилл?)
   ↓ порог
ИЗМЕНЕНИЕ РЕАЛЬНОСТИ (следующий круг — сцена звучит иначе)
   ↓
ФОКУС (но ты уже не уверен, что видел в прошлый раз)
```

Синхронизация **не отдельный экран**, а слой поверх всего: она решает, чья
версия реплики звучит и чьё воспоминание открылось.

## Замечания по версии

- Проверено под Ren'Py 8.0.3 (ветка с `matrixcolor`, `Drag/DragGroup`, `Replay`).
- Если `matrixcolor` в `rgb_split_a/b` ругается — просто удали эти две строки,
  искажение останется за счёт сдвига слоёв.
- `drift_memories()` меняет константы `FRAGMENTS` — они не пишутся в сейв.
  Нужен сохраняемый дрейф — перенеси `stab` в `default`-переменную.
- Все тексты с квадратными скобками (цензура архива) пишутся как `[[данные изъяты]`,
  иначе Ren'Py попытается подставить переменную и упадёт с `KeyError`.
  В `01_state.rpy` это уже сделано правильно.
