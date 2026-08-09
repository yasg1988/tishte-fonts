# Tishte

Региональная типографическая система Республики Марий Эл.

## Семейства

- **Tishte Serif** — официальный документный шрифт: свободно распространяемый,
  с засечками, пропорциональный, традиционного начертания, делового стиля и
  метрически совместимый с Times New Roman.
- **Tishte Sans** — экранный шрифт для сайтов, АИС, дашбордов, презентаций и
  мини-приложений. Он визуально родственен Tishte Serif, но не ограничен
  метриками Times New Roman.

## Статус

Собран инженерный прототип Tishte Serif Regular v0.030. В нём начата
собственная визуальная система для кириллицы, марийских букв, латиницы, цифр и
документных знаков. Машинный профиль содержит 212 обязательных символов и
сохраняет их метрики Times New Roman. Прототип пока основан на открытом
метрическом каркасе: полный оригинальный рисунок ещё разрабатывается.
Нормативные и продуктовые требования зафиксированы в каталоге `docs/`.

## Быстрый запуск проверки метрик

```powershell
python scripts/font_metrics_audit.py `
  --reference C:\Windows\Fonts\times.ttf `
  --candidate path\to\TishteSerif-Regular.ttf `
  --charset data\document-charset.txt
```

Для проверки самого инструмента:

```powershell
python scripts/font_metrics_audit.py `
  --reference C:\Windows\Fonts\times.ttf `
  --candidate C:\Windows\Fonts\times.ttf `
  --charset data\document-charset.txt
```

Инструмент сравнивает горизонтальные и вертикальные метрики без копирования
исходного шрифта в репозиторий.

Полная машинная проверка прототипа:

```powershell
python scripts/build_serif_prototype.py
python scripts/font_compliance_audit.py `
  --reference C:\Windows\Fonts\times.ttf `
  --candidate build\TishteSerifPrototype-Regular.ttf `
  --charset data\document-charset.txt
```

Редактируемый источник находится в
`sources/tishte-serif/TishteSerif-Regular.sfd`. Его сборка:

```powershell
python scripts/build_serif_from_sfd.py
```

Для сборки требуется FontForge.

Текущая итерация собирается из
`sources/tishte-serif/iterations/TishteSerif-Regular-v030.sfd` с версией
`0.030`. После сборки выполняется `scripts/font_compliance_audit.py`; релиз не
считается прошедшим проверку при отсутствии обязательных символов или изменении
их документных метрик.

Контрольный лист после сборки:

```powershell
python scripts/render_serif_specimen.py
```
