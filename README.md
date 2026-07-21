# INDX Filament Profile Converter

Converts Polymaker PrusaSlicer filament presets made for the Prusa CORE One into presets compatible with Bondtech INDX high-flow toolhead configurations.

The generated profiles support:

- Prusa CORE One INDX 4T
- Prusa CORE One INDX 8T
- HF 0.4 mm nozzles

> This project currently targets Polymaker's published CORE One profiles. Support for other manufacturers may be considered later, but is not currently a project goal.

## Download profiles

Open the repository's **Releases** page and download either:

- `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini` — recommended combined PrusaSlicer bundle
- `Polymaker-COREONE-INDX-HF0.4.zip` — individual converted presets
- `SHA256SUMS.txt` — checksums for verifying the downloads

In PrusaSlicer, import the bundle through **File → Import → Import Config Bundle**.

## Automated builds and releases

GitHub Actions validates and builds the profiles whenever the converter, tests, workflow, or source profiles change on `main`.

Normal pushes create a temporary downloadable workflow artifact. Version tags additionally create a permanent GitHub Release and attach the generated bundle, ZIP, and SHA-256 checksums.

### Publish a new release

1. Replace the Polymaker ZIP in `source/` with the updated profile archive.
2. Commit and push the change:

```bash
git add source/
git commit -m "Update Polymaker profiles"
git push
```

3. Confirm the **Build and release Polymaker profiles** workflow succeeds.
4. Create and push a version tag:

```bash
git tag -a v1.0.0 -m "INDX Polymaker profiles v1.0.0"
git push origin v1.0.0
```

GitHub Actions will then:

1. Run the automated tests.
2. Convert every source profile.
3. Build the combined config bundle and individual-profile ZIP.
4. Generate SHA-256 checksums.
5. Create the GitHub Release using automatically generated release notes.
6. Attach all three files to the release.

For the next profile update, increment the version, for example `v1.0.1` for a correction or `v1.1.0` for a larger profile update.

## Run the converter locally

Python 3.10 or newer is recommended. The converter uses only the Python standard library.

Place exactly one Polymaker source ZIP in `source/`, then run:

```bash
python convert.py source/polymaker-presets-37.zip
```

Generated files are written to:

```text
output/
├── individual/
├── bundle/INDX-Filament-Profiles-HF0.4-config-bundle.ini
└── release/INDX-Filament-Profiles-HF0.4.zip
```

## What is changed

The converter preserves Polymaker's filament-specific tuning and changes only INDX-related compatibility metadata:

- Converts CORE One parent profiles to their `COREONEINDX HF0.4` equivalents
- Adds compatibility for CORE One INDX 4T and 8T printer models
- Requires a 0.4 mm high-flow nozzle
- Renames the filament settings ID to identify it as an INDX HF0.4 preset

The generated compatibility expression is:

```text
printer_model=~/(COREONE_INDX4T|COREONE_INDX8T)/ and nozzle_diameter[0]==0.4 and nozzle_high_flow[0]
```

## Repository contents

```text
.
├── .github/workflows/build.yml
├── source/
│   └── polymaker-presets-37.zip
├── tests/
├── convert.py
├── LICENSE
└── README.md
```

Generated output is intentionally excluded from Git. GitHub Releases are the public distribution point for converted profiles.

## Disclaimer

This is a community project and is not affiliated with Bondtech, Prusa Research, or Polymaker. Review slicer settings and validate temperatures, flow, and print quality before relying on a converted profile for production work.

## License

The converter code is licensed under the MIT License. Third-party filament profile data remains subject to the terms of its original publisher.
