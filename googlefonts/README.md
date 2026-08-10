# Google Fonts readiness

This directory contains the review material used to build two independent
Google Fonts family packages: **Tishte Serif** and **Tishte Sans**.

Build both packages from the repository root:

```bash
python scripts/fetch_sans_upstream.py
python scripts/build_googlefonts.py
python scripts/audit_googlefonts_reproducible.py
```

The canonical TTFs and downstream metadata are written to
`build/googlefonts/ofl/tishteserif` and `build/googlefonts/ofl/tishtesans`.
Editable UFO review exports are written to `build/googlefonts/upstream`.
The normal release files are not overwritten.

Run the current official Fontspector profile after installing Fontspector
1.7.3 or newer:

```bash
python scripts/audit_fontspector.py
```

The deterministic CI audit skips network-only checks. Run
`python scripts/audit_fontspector.py --network` for an additional live check;
transient `namecheck.fontdata.com` failures are retried. The audit rejects
every FAIL/FATAL/ERROR and every warning not reviewed in
`data/googlefonts-accepted-warnings.json`; full unfiltered reports are written
to `artifacts/reports/fontspector/`.

The compatibility FontBakery gate remains available as a secondary audit:

```bash
fontbakery check-googlefonts *.ttf METADATA.pb --skip-network
```

FontBakery and gftools currently require incompatible protobuf major
versions. Use separate virtual environments with `requirements-googlefonts.txt`
and `requirements-gftools.txt`.

The families are static-only by design. Google Fonts accepts static-only
families, although final inclusion remains a curatorial decision. Tishte Serif
is derived from Tinos and Tishte Sans from Arimo; the OFL provenance is retained
in font metadata, source documentation, and package licensing.

Reference requirements:

- <https://googlefonts.github.io/gf-guide/onboarding.html>
- <https://googlefonts.github.io/gf-guide/production.html>
- <https://googlefonts.github.io/gf-guide/upstream.html>
- <https://googlefonts.github.io/gf-guide/statics.html>
