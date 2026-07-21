# User Guide

This guide explains how to download and import the converted Polymaker profiles into PrusaSlicer.

## Requirements

- PrusaSlicer with a configured Prusa CORE One INDX printer
- A CORE One INDX 4T or 8T configuration
- A 0.4 mm high-flow nozzle profile

## Download the profiles

Open the repository's **Releases** page and select the latest release:

https://github.com/systemdbrew/INDX-Filament-Profile-Converter/releases/latest

Download one of these files:

- `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini` — recommended
- `Polymaker-COREONE-INDX-HF0.4.zip` — individual profile files

The config bundle is the simplest option because it imports all converted Polymaker profiles at once.

## Import the config bundle

1. Open PrusaSlicer.
2. Select **File → Import → Import Config Bundle**.
3. Choose `Polymaker-COREONE-INDX-HF0.4-config-bundle.ini`.
4. Confirm the import.
5. Select your CORE One INDX printer profile.
6. Open the filament preset list and choose the desired Polymaker material.

Imported profiles include `INDX HF0.4` in their names so they are easy to distinguish from standard CORE One profiles.

## Import individual profiles

1. Extract `Polymaker-COREONE-INDX-HF0.4.zip`.
2. In PrusaSlicer, select **File → Import → Import Config**.
3. Select one or more extracted `.ini` files.
4. Confirm the import.

## Verify compatibility

A converted profile should be visible when the selected printer is one of the following:

- Prusa CORE One INDX 4T with HF 0.4 mm nozzle
- Prusa CORE One INDX 8T with HF 0.4 mm nozzle

The profiles intentionally do not appear for standard-flow nozzles or unrelated printer models.

## Updating profiles

When a new release is published:

1. Download the latest config bundle.
2. Import it through **File → Import → Import Config Bundle**.
3. Allow PrusaSlicer to update or replace matching presets when prompted.

Keeping an older release is useful until you have verified the newer profiles on your printer.

## Troubleshooting

### The profiles do not appear

Confirm that the selected printer is a CORE One INDX 4T or 8T profile using an HF 0.4 mm nozzle. The compatibility filter hides the profiles from other printer and nozzle configurations.

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
