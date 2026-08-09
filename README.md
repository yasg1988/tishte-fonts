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

Собрано связанное инженерное семейство Tishte Serif v0.060: Regular, Bold,
Italic и Bold Italic. Каждое начертание содержит 214 обязательных символов,
включая специальные буквы луговомарийского и горномарийского языков, и
сохраняет метрики соответствующего начертания Times New Roman. Собственная
визуальная система Regular развивается с версии v0.040; остальные начертания
пока остаются инженерным OFL-каркасом и требуют оригинализации перед релизом.
Нормативные и продуктовые требования зафиксированы в каталоге `docs/`.

Повторный корпус Microsoft Word v0.060 полностью совпал в пяти парах по числу
страниц и строк. Дополнительно выполнены нативные испытания Microsoft Excel и
PowerPoint с внедрением шрифтов, формулами, таблицами и отдельными образцами
обоих марийских литературных языков. Результаты описаны в
`docs/engineering-family-v060.md`.

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
`sources/tishte-serif/iterations/TishteSerif-Regular-v040.sfd` с версией
`0.040`. После сборки выполняется `scripts/font_compliance_audit.py`; релиз не
считается прошедшим проверку при отсутствии обязательных символов или изменении
их документных метрик.

Контрольный лист после сборки:

```powershell
python scripts/render_serif_specimen.py
```
