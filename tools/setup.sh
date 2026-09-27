#!/bin/bash
# Проверка сценариев без запуска движка: качает нужную часть исходников Ren'Py 8.0.3
# (только .py/.rpy, ~4 МБ) в tools/renpy-src и ставит зависимости.
#   bash tools/setup.sh
#   python3 tools/rpcheck.py game/*.rpy     # синтаксис (настоящий парсер Ren'Py)
#   python3 tools/rpxref.py game            # метки, экраны, картинки, файлы звука
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ ! -f "$HERE/renpy-src/renpy/parser.py" ]; then
  rm -rf /tmp/renpy-full
  git clone -q --depth 1 --branch 8.0.3.22090809 https://github.com/renpy/renpy.git /tmp/renpy-full
  mkdir -p "$HERE/renpy-src/module"
  (cd /tmp/renpy-full && find renpy -type f \( -name "*.py" -o -name "*.rpy" -o -name "*.pyx" \) | tar -cf - -T - | tar -xf - -C "$HERE/renpy-src")
  cp /tmp/renpy-full/module/generate_styles.py "$HERE/renpy-src/module/"
fi
python3 -c "import future, six" 2>/dev/null || pip install -q --break-system-packages future six 2>/dev/null || pip install -q future six
echo "tools ready: $HERE"
