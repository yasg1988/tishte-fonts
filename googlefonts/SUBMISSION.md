# Google Fonts submission checklist

Tishte Serif and Tishte Sans must be proposed as two separate families. The
technical packages are generated in `build/googlefonts/ofl/`; editable review
exports are generated in `build/googlefonts/upstream/`.

## Completed locally and in CI

- SIL Open Font License 1.1 and retained Tinos/Arimo provenance;
- public GitHub upstream with reproducible open-source build scripts;
- canonical static TTF filenames and Google Fonts naming model;
- GF Latin Core, Cyrillic, extended Cyrillic, Meadow Mari, and Hill Mari;
- `METADATA.pb`, article, specimen image, and canonical OFL package;
- family-wide vertical metrics, `USE_TYPO_METRICS`, meta ScriptLangTags;
- zero FAIL/FATAL/ERROR results in `fontbakery check-googlefonts`;
- a dedicated GitHub Actions readiness gate.

## Before opening the upstream issue

1. Merge the readiness pull request and wait for the dedicated CI job.
2. Download and inspect the `tishte-googlefonts-readiness` artifact.
3. Use the Google Fonts issue form to propose Tishte Serif first, then Tishte
   Sans as a separate family.
4. Link this repository and the successful workflow run; do not attach release
   ZIP files unless a Google Fonts maintainer requests them.
5. Explain the design changes and regional language purpose with concrete
   specimens. Both families are derivatives of fonts already in Google Fonts,
   so inclusion depends on curatorial judgment as well as technical quality.

## Known reviewed warnings

- `MRIE` is the project vendor ID but is not registered in Microsoft's list;
- outline heuristics flag small alignment, collinearity, and segment-angle
  deviations inherited from or intentionally introduced into the design;
- the subset reachability warning includes standalone combining marks required
  by GF Latin Core and decomposed Mari/Latin input;
- Serif math-sign widths intentionally follow its document metric contract.

These warnings are not hidden by configuration. Any new FAIL, FATAL, or ERROR
blocks the readiness workflow.
