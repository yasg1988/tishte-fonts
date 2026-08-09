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

Собран кандидат независимой приёмки Tishte Serif v0.950: Regular, Bold,
Italic и Bold Italic. Каждое начертание содержит 422 обязательных символа,
включая специальные буквы луговомарийского и горномарийского языков, и
сохраняет метрики соответствующего начертания Times New Roman. В v0.950
нормализованы лицензионные и идентификационные метаданные производных файлов,
добавлен отдельный правовой аудит и подготовлены четыре независимых протокола:
типографический, луговомарийский, горномарийский и юридический. Пустые формы и
автоматические отчёты не означают одобрения экспертов и не придают шрифту
официального статуса. Программа приёмки описана в
`docs/expert-review-v950.md`, правовые границы — в `docs/legal-review-v950.md`.

Нативный корпус Microsoft Word v0.950 совпадает с Times New Roman во всех пяти
парах по числу страниц и строк. Корпусы Excel и PowerPoint проходят без ошибок
формул, переполнения и расхождений высоты текста. Это доказательство метрической
совместимости, но не замена печатной, языковой или юридической приёмки.

## Воспроизводимая сборка v0.950

```powershell
python scripts/build_release.py --version 0.950 --source-version 0.140
python scripts/audit_reproducible_build.py --version 0.950 --source-version 0.140
python scripts/audit_metric_contract.py --version 0.950
python scripts/audit_unicode_normalization_v090.py --version 0.950
python scripts/audit_language_corpus.py --version 0.950
python scripts/audit_opentype_v120.py --version 0.950
python scripts/audit_outline_originality.py --version 0.950 --max-identical-ratio 0.01
python scripts/audit_legal_metadata.py --version 0.950
python scripts/run_fontbakery.py --version 0.950
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
