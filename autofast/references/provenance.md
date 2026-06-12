# Provenance

A solid result should be reconstructable without relying on memory.

## Minimum record

- timestamp and host platform;
- OpenFAST executable path, version output, and SHA-256;
- entry file and dependency graph;
- SHA-256 for every available input dependency;
- source model URL/tag/commit when downloaded;
- baseline and declared changes;
- exact command and working directory;
- return code, log, output names and sizes;
- validation status and statistics window;
- analysis script/version;
- failed, skipped, and excluded cases.

## Suggested bundle

```text
provenance/
  manifest.json
  inspection.json
  file_hashes.csv
  command.txt
  environment.json
  logs/
  status/
  analysis/
```

Large binary outputs may remain outside the bundle if their paths, sizes, and
hashes are recorded.

## Source acquisition

For downloaded models record:

- canonical URL;
- repository and commit or release tag;
- acquisition time;
- license;
- local modifications.

Do not describe a moving default branch as a reproducible source.
