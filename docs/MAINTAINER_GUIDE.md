# Maintainer and Release Guide

This document covers updating the source Polymaker profiles and publishing a new GitHub Release.

## Automatic upstream checks

The `Check for Polymaker profile updates` workflow runs daily and can also be
started manually. It reads Polymaker's machine-readable preset index, selects
only exact `Prusa` / `Core One` / `PrusaSlicer` entries, and compares both the
reported modification times and downloaded file hashes with
`source/polymaker-manifest.json`.

When profiles change, the workflow downloads a fresh deterministic source ZIP,
runs the tests and converter, and opens or updates an automated pull request.
Review and merge that pull request before publishing a release. A failed
download, unexpected empty result, duplicate filename, or invalid-looking INI
causes the workflow to stop without modifying `main`.

## How releases work

The workflow in `.github/workflows/build.yml` runs when relevant files change on `main`, when a version tag is pushed, or when started manually.

It performs the following steps:

1. Runs the converter tests.
2. Finds the single ZIP archive in `source/`.
3. Converts every Polymaker profile into standard and INDX HF0.4 variants.
4. Builds a combined PrusaSlicer config bundle.
5. Builds a ZIP containing individual profiles.
6. Generates SHA-256 checksums.
7. Uploads a temporary Actions artifact.
8. Creates a permanent GitHub Release when the build was triggered by a version tag.

## Update the Polymaker source archive

The `source/` directory must contain exactly one ZIP archive.

1. Remove the previous archive.
2. Copy the new Polymaker profile archive into `source/`.
3. Give it a clear name, for example:

```text
source/polymaker-presets-38.zip
```

4. Test locally:

```bash
python -m unittest discover -s tests
python convert.py source/polymaker-presets-38.zip
```

5. Inspect the generated files under `output/`.

## Commit the update

```bash
git add source/ convert.py tests/ docs/ README.md
git commit -m "Update Polymaker profiles"
git push origin main
```

Open the repository's **Actions** tab and confirm that **Build and release Polymaker profiles** succeeds.

A normal push creates a temporary workflow artifact that can be downloaded and tested before publishing a release.

## Choose a version number

This project uses semantic-style version tags:

- Patch release, such as `v1.0.1`: corrected conversion or documentation fix
- Minor release, such as `v1.1.0`: new Polymaker profile pack or meaningful feature
- Major release, such as `v2.0.0`: incompatible converter or output-format change

## Publish the release

After the build on `main` succeeds:

```bash
git tag -a v1.1.0 -m "INDX Polymaker profiles v1.1.0"
git push origin v1.1.0
```

The tagged workflow creates a GitHub Release with:

```text
Polymaker-COREONE-INDX-HF0.4-config-bundle.ini
Polymaker-COREONE-INDX-HF0.4.zip
SHA256SUMS.txt
```

GitHub automatically generates release notes from changes since the previous tag.

## Manual workflow run

The build can be started without creating a release:

1. Open **Actions** in GitHub.
2. Select **Build and release Polymaker profiles**.
3. Select **Run workflow**.
4. Choose the `main` branch.

A manual run uploads a temporary artifact but does not create a GitHub Release because it is not associated with a version tag.

## Correcting a failed release

Do not reuse a published version tag for new content. Correct the problem, commit it, and publish a new patch version.

Example:

```bash
git add .
git commit -m "Fix profile conversion"
git push origin main

git tag -a v1.1.1 -m "Fix profile conversion"
git push origin v1.1.1
```

## Generated files

Generated output is ignored by Git and should not normally be committed. Permanent public downloads belong in GitHub Releases.
