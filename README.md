<div align="center">

# INDX Filament Profile Converter

**Polymaker filament profiles for Prusa CORE One printers equipped with Bondtech INDX high-flow toolheads.**

[![Build profiles](https://github.com/systemdbrew/INDX-Filament-Profile-Converter/actions/workflows/build.yml/badge.svg)](https://github.com/systemdbrew/INDX-Filament-Profile-Converter/actions/workflows/build.yml)
[![Latest release](https://img.shields.io/github/v/release/systemdbrew/INDX-Filament-Profile-Converter?display_name=tag&sort=semver)](https://github.com/systemdbrew/INDX-Filament-Profile-Converter/releases/latest)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE)

[**Download the latest profiles**](https://github.com/systemdbrew/INDX-Filament-Profile-Converter/releases/latest) · [Installation guide](docs/USER_GUIDE.md) · [Release guide](docs/MAINTAINER_GUIDE.md)

</div>

---

## About

Polymaker publishes tuned PrusaSlicer profiles for the standard Prusa CORE One. This project converts those profiles for Bondtech INDX high-flow configurations while preserving Polymaker's filament-specific tuning.

### Supported configurations

| Printer | Tool configuration | Nozzle |
|---|---:|---:|
| Prusa CORE One INDX | 4T | HF 0.4 mm |
| Prusa CORE One INDX | 8T | HF 0.4 mm |

> CORE One L is not included because an INDX configuration for that printer does not currently exist.

## Download

The easiest way to use this project is to download the newest files from the [**GitHub Releases page**](https://github.com/systemdbrew/INDX-Filament-Profile-Converter/releases/latest).

| File | Purpose |
|---|---|
| `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini` | Recommended combined PrusaSlicer import bundle |
| `Polymaker-COREONE-INDX-HF0.4.zip` | Individual converted filament presets |
| `SHA256SUMS.txt` | Download integrity checksums |

For import instructions and troubleshooting, see the [user guide](docs/USER_GUIDE.md).

## What the converter changes

The converter preserves Polymaker's temperatures, cooling, extrusion, and filament-specific tuning. It changes only the metadata needed for INDX compatibility:

- Replaces CORE One parent profiles with their `COREONEINDX HF0.4` equivalents
- Adds compatibility for `COREONE_INDX4T` and `COREONE_INDX8T`
- Requires a 0.4 mm high-flow nozzle
- Renames each filament settings ID to clearly identify the INDX profile

Generated compatibility condition:

```text
printer_model=~/(COREONE_INDX4T|COREONE_INDX8T)/ and nozzle_diameter[0]==0.4 and nozzle_high_flow[0]
```

## Automated builds and releases

GitHub Actions checks Polymaker's public preset catalog every day for exact
`Prusa` / `Core One` / `PrusaSlicer` matches. It compares each profile's
reported modification time and SHA-256 content hash with the tracked manifest.

When upstream profiles change, the automation downloads a fresh source archive,
runs the converter tests, validates all generated profiles, and opens a pull
request for maintainer review. Unexpected empty results, duplicate filenames,
invalid profile files, or conversion failures stop the update without changing
`main`.

The build workflow generates fresh profile downloads whenever the source
Polymaker archive or converter changes.

A version tag such as `v1.1.0` automatically creates a GitHub Release containing the generated bundle, individual profiles, and checksums.

Project maintainers can follow the [release and update guide](docs/MAINTAINER_GUIDE.md).

## Repository layout

```text
.
├── .github/workflows/
│   ├── build.yml
│   └── update-polymaker.yml
├── docs/
│   ├── MAINTAINER_GUIDE.md
│   └── USER_GUIDE.md
├── scripts/
│   └── sync_polymaker.py
├── source/
│   ├── polymaker-manifest.json
│   └── polymaker-presets-core-one.zip
├── tests/
├── convert.py
├── LICENSE
└── README.md
```

Generated profiles are intentionally excluded from Git. GitHub Releases are the public distribution point.

## Project scope

This project currently focuses only on Polymaker because Polymaker provides comprehensive PrusaSlicer profile packs and these are the profiles used by the maintainer. Other filament brands may be considered later, but are not currently a project goal.

## Disclaimer

This is a community project and is not affiliated with Bondtech, Prusa Research, or Polymaker. Review slicer settings and validate temperatures, flow, and print quality before relying on a converted profile for production work.

## License

The converter code is licensed under the [MIT License](LICENSE). Third-party filament profile data remains subject to the terms of its original publisher.
