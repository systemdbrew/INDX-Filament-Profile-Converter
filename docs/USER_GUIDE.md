# User Guide

This guide explains how to download and import the converted Polymaker profiles into PrusaSlicer.

## Requirements

- PrusaSlicer with a supported CORE One standard or INDX printer configuration
- A 0.4 mm high-flow nozzle profile

## Download the profiles

Open the repository's **Releases** page and select the latest release:

https://github.com/systemdbrew/INDX-Polymaker-Profile-Converter/releases/latest

Download one of these files:

- `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini` — recommended
- `Polymaker-COREONE-INDX-HF0.4.zip` — individual profile files

The config bundle is the simplest option because it imports all converted Polymaker profiles at once.

## Import the config bundle

1. Open PrusaSlicer.
2. Select **File → Import → Import Config Bundle**.
3. Choose `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini`.
4. Confirm the import.
5. Select your CORE One standard or INDX printer profile.
6. Open the filament preset list and choose the desired Polymaker material.

Each material has two imported presets: `HF0.4` for standard CORE One configurations and `INDX HF0.4` for Bondtech INDX configurations.

## Import individual profiles

1. Extract `Polymaker-COREONE-INDX-HF0.4.zip`.
2. In PrusaSlicer, select **File → Import → Import Config**.
3. Select one or more extracted `.ini` files.
4. Confirm the import.

## Verify compatibility

A converted profile should be visible when the selected printer uses one of these model identifiers:

- Standard: `COREONE`, `COREONEOAK`, `COREONEMMU3`, `COREONEL`, or `COREONELMMU3`
- INDX: `COREONE_INDX4T`, `COREONE_INDX8T`, `COREONEL_INDX4T`, or `COREONEL_INDX8T`

The profiles intentionally do not appear for standard-flow nozzles or unrelated printer models.

## Updating profiles

When a new release is published:

1. Download the latest config bundle.
2. Import it through **File → Import → Import Config Bundle**.
3. Allow PrusaSlicer to update or replace matching presets when prompted.

Keeping an older release is useful until you have verified the newer profiles on your printer.

## Troubleshooting

### The profiles do not appear

Confirm that the selected printer uses one of the supported model identifiers and an HF 0.4 mm nozzle. The compatibility filter hides the profiles from other printer and nozzle configurations.

### Prusa Connect reports a material mismatch

Prusa Connect material matching and PrusaSlicer profile compatibility are separate systems. Confirm the physical spool material assigned in Prusa Connect matches the filament selected in PrusaSlicer.

### A profile imports but produces unexpected results

Treat converted profiles as a starting point. Check the recommended temperature range printed on the spool and perform normal first-layer, temperature, and flow validation before production printing.

### Verify a downloaded file

Linux:

```bash
sha256sum -c SHA256SUMS.txt
```

Windows PowerShell:

```powershell
Get-FileHash .\Polymaker-COREONE-INDX-HF0.4-config-bundle.ini -Algorithm SHA256
```

Compare the displayed hash with the corresponding value in `SHA256SUMS.txt`.
