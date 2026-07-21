# INDX Filament Profile Converter

Convert PrusaSlicer filament presets made for the Prusa CORE One into presets compatible with Bondtech INDX high-flow toolhead configurations.

The included Polymaker conversion supports:

- Prusa CORE One INDX 4T
- Prusa CORE One INDX 8T
- HF 0.4 mm nozzles

## Ready-to-import files

The `releases/` directory contains:

- `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini` — combined PrusaSlicer bundle
- `polymaker-presets-COREONE-INDX-HF0.4.zip` — individual converted presets

In PrusaSlicer, import the bundle through **File → Import → Import Config Bundle**.

## Run the converter

Python 3.10 or newer is recommended. The script uses only the Python standard library.

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

The input can be a ZIP archive, a directory containing `.ini` files, or one `.ini` file:

```bash
python convert.py path/to/profile.ini
python convert.py path/to/profile-directory
python convert.py path/to/profiles.zip --output output
```

## What is changed

The converter preserves the filament-specific tuning and changes only INDX-related compatibility metadata:

- Converts Core One parent profiles to their `COREONEINDX HF0.4` equivalents
- Adds compatibility for CORE One INDX 4T and 8T printer models
- Requires a 0.4 mm high-flow nozzle
- Renames the filament settings ID to identify it as an INDX HF0.4 preset

The generated compatibility expression is:

```text
printer_model=~/(COREONE_INDX4T|COREONE_INDX8T)/ and nozzle_diameter[0]==0.4 and nozzle_high_flow[0]
```

## Updating the source profiles

Replace the ZIP in `source/` with a newer vendor profile archive, then rerun the converter. A GitHub Actions workflow also builds downloadable artifacts whenever the source profiles or converter are changed.

## Disclaimer

This is a community project and is not affiliated with Bondtech, Prusa Research, or Polymaker. Review slicer settings and validate temperatures, flow, and print quality before relying on a converted profile for production work.

## License

The converter code is licensed under the MIT License. Third-party filament profile data remains subject to the terms of its original publisher.
