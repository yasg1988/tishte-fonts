# Tishte

Свободная типографическая система с поддержкой русского, луговомарийского и
горномарийского языков.

## Tishte Serif

Tishte Serif — бесплатный документный шрифт с засечками, метрически совместимый
с Times New Roman. Текущая версия `0.960` включает четыре начертания:

- Regular;
- Bold;
- Italic;
- Bold Italic.

В каждом файле 423 заявленных символа: русская кириллица, специальные буквы
луговомарийского (`Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ҥ ҥ`) и горномарийского
(`Ӓ ӓ, Ӧ ӧ, Ӱ ӱ, Ӹ ӹ`) языков, Latin Extended-A, цифры, валюты,
пунктуация, математические и документные знаки. TTF предназначены для
настольных приложений и мобильной разработки, WOFF2 — для сайтов.

Tishte Serif не является шрифтом Правительства Республики Марий Эл и не
создаёт впечатления такого статуса. Он разработан как свободный кандидат для
документного применения; решение об использовании принимает конкретная
организация.

Tishte Sans — планируемое экранное семейство и в этот выпуск не входит.

## Установка

Скачайте архив последнего выпуска на странице
[Releases](https://github.com/yasg1988/tishte-fonts/releases) и распакуйте его.

### Windows 10 и 11

1. Откройте папку `fonts/ttf`.
2. Выделите четыре TTF-файла.
3. Нажмите правой кнопкой и выберите **Установить** или
   **Установить для всех пользователей**.
4. Перезапустите уже открытые Word, Excel, PowerPoint и другие приложения.

Для установки в профиль текущего пользователя также предназначен скрипт
`tools/Install-TishteSerif.ps1` из архива.

### macOS

1. Откройте четыре TTF-файла из `fonts/ttf`.
2. В приложении «Шрифты» нажмите **Установить шрифт**.
3. Перезапустите приложения, которые были открыты во время установки.

### Linux

Скопируйте TTF в пользовательский каталог шрифтов и обновите кэш:

```bash
mkdir -p ~/.local/share/fonts/Tishte
cp fonts/ttf/*.ttf ~/.local/share/fonts/Tishte/
fc-cache -f
```

### Android

Отдельный «Android-файл» не требуется: Android-приложения используют обычные
TTF. Скопируйте файлы в `app/src/main/res/font/`, используя имена в нижнем
регистре, например `tishte_serif_regular.ttf`.

Jetpack Compose:

```kotlin
val TishteSerif = FontFamily(
    Font(R.font.tishte_serif_regular, FontWeight.Normal),
    Font(R.font.tishte_serif_bold, FontWeight.Bold),
    Font(R.font.tishte_serif_italic, FontWeight.Normal, FontStyle.Italic),
    Font(R.font.tishte_serif_bold_italic, FontWeight.Bold, FontStyle.Italic),
)
```

Системная замена шрифта на всём Android-устройстве стандартным API не
поддерживается: она зависит от производителя, прошивки или root-доступа. Для
сайтов, открываемых на Android, используйте WOFF2 и готовый CSS из `fonts/web`.

### iOS и iPadOS

Разработчик приложения добавляет четыре TTF в проект Xcode, включает их в
`UIAppFonts` файла `Info.plist` и использует семейство `Tishte Serif`.
Системная установка пользователем выполняется только через доверенный профиль
конфигурации или приложение управления шрифтами.

### Веб

Скопируйте содержимое `fonts/web` на сервер, подключите CSS:

```html
<link rel="stylesheet" href="/fonts/tishte-serif-v960.css">
```

```css
body { font-family: "Tishte Serif", serif; }
```

## Сборка и проверка

Требуются Python 3.12+, FontForge и зависимости из `requirements-lock.txt`.

```powershell
python scripts/build_release.py --version 0.960
python scripts/audit_reproducible_build.py --version 0.960
python scripts/audit_metric_contract.py --version 0.960
python scripts/audit_unicode_normalization.py --version 0.960
python scripts/audit_language_corpus.py --version 0.960
python scripts/audit_opentype.py --version 0.960
python scripts/audit_outline_originality.py --version 0.960 --max-identical-ratio 0.01
python scripts/audit_legal_metadata.py --version 0.960
python scripts/run_fontbakery.py --version 0.960
```

Канонические редактируемые исходники находятся в `sources/tishte-serif`.
Сборка проверяется в GitHub Actions на Linux, Windows и macOS.

## Лицензия и происхождение

Tishte распространяется по [SIL Open Font License 1.1](LICENSE.txt). Шрифт
можно бесплатно использовать, встраивать, изучать, изменять и распространять
на условиях OFL. Документы, созданные с его помощью, лицензией шрифта не
ограничиваются.

Tishte Serif является модифицированной версией свободного шрифта Tinos.
Обязательные сведения об исходном проекте и лицензии сохранены в
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) и метаданных файлов.
