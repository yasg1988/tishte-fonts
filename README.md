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

Собран инженерный прототип Tishte Serif Regular v0.001. Он подтверждает
метрическую, лицензионную и упаковочную схему, но пока использует открытые
контуры метрического каркаса: собственный визуальный дизайн ещё разрабатывается.
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
