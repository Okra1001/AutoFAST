# Platform Notes

## Windows

- Prefer `cd /d "%~dp0"` in batch runners.
- Keep controller DLL architecture compatible with the OpenFAST executable.
- Quote paths and test non-ASCII or space-containing paths before long runs.
- Capture stdout and stderr into explicit log files.

## Linux and macOS

- Check executable permission and shared-library resolution.
- Preserve case-sensitive filenames.
- Use scripts with `set -e` carefully; still write failure status and logs.

## WSL

- Distinguish Windows and Linux executable paths.
- Avoid mixing Windows controller DLLs with Linux OpenFAST.
- Performance may suffer when repeatedly accessing files through mounted
  Windows drives; document the actual run location.

## Portability

Prefer relative model references. Treat absolute paths, symlinks, external wind
files, controller binaries, and hydrodynamic databases as portability risks
that must appear in inspection and provenance reports.
