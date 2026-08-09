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

Собрана дизайн-итерация Tishte Serif v0.930: Regular, Bold,
Italic и Bold Italic. Каждое начертание содержит 422 обязательных символа,
включая специальные буквы луговомарийского и горномарийского языков, и
сохраняет метрики соответствующего начертания Times New Roman. Собственная
визуальная система Regular развивается с версии v0.040; в v0.070 общие признаки
перенесены в остальные начертания, а все четыре файла получили чистую нулевую
маску валидации FontForge. Семейство включает расширенную латиницу, управляемые
пробелы, канонический NFC/NFD-аудит, WOFF2, OTS, FontBakery и GitHub CI.
v0.100–v0.110 расширяют собственную пластику на базовые латинские и
кириллические формы всей семьи. Ограничения RC перечислены в
`docs/release-candidate-v900.md`.
Нормативные и продуктовые требования зафиксированы в каталоге `docs/`.

Повторный корпус Microsoft Word v0.080 полностью совпал в пяти парах по числу
страниц и строк. Дополнительно выполнены нативные испытания Microsoft Excel и
PowerPoint с внедрением шрифтов, формулами, таблицами и отдельными образцами
обоих марийских литературных языков. Результаты описаны в
`docs/engineering-family-v080.md`. Актуальная политика автоматических проверок
описана в `docs/quality-policy-v090.md`.

## Воспроизводимая сборка v0.930

```powershell
python scripts/build_release.py --version 0.930 --source-version 0.130
python scripts/audit_metric_contract.py --version 0.930
python scripts/audit_unicode_normalization_v090.py --version 0.930
python scripts/audit_language_corpus.py --version 0.930
python scripts/audit_opentype_v120.py --version 0.930
python scripts/audit_outline_originality.py --version 0.930 --max-identical-ratio 0.15
python scripts/run_fontbakery.py --version 0.930
```

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
