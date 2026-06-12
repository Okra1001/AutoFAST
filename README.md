# AutoFAST v1.0

[![中文说明](https://img.shields.io/badge/文档-中文说明-red)](README.zh-CN.md)
[![OpenFAST](https://img.shields.io/badge/OpenFAST-Official_Repository-blue)](https://github.com/OpenFAST/openfast)

AutoFAST is a universal Codex/agent skill for taking OpenFAST work from an
executable or model directory to traceable, validated simulation results.

It is turbine-agnostic and supports beginner bootstrap, dependency inspection,
safe scalar edits, single runs, resumable sweeps, error diagnosis, text and
binary output analysis, controlled comparisons, and provenance bundles.

AutoFAST does not replace OpenFAST. It provides an agent-oriented workflow
around the official [OpenFAST](https://github.com/OpenFAST/openfast) solver and
its input models.

## What AutoFAST provides

- Bootstrap guidance when the user has only an OpenFAST executable.
- Conservative discovery of entry files, modules, and dependencies.
- Exact scalar-field editing with dry runs, backups, and visible diffs.
- Traceable single-case execution and resumable parameter sweeps.
- Evidence-based error classification and minimal-repair guidance.
- Text `.out` analysis and optional `.outb` support through OpenFAST Toolbox or
  pyFAST.
- Controlled output comparison and reproducible provenance bundles.

## Install

Copy the `autofast` directory into your agent's skills directory, or install
the packaged `dist/autofast.skill` artifact.

Invoke it explicitly with:

```text
$autofast
```

Example:

```text
Use $autofast to inspect this OpenFAST release and help me run a
version-compatible official example with a traceable result.
```

## Typical workflow

1. Inspect the executable or model directory.
2. Establish an unchanged baseline.
3. Declare the parameter to vary and the variables to hold constant.
4. Preview and apply the smallest safe input change.
5. Run one representative case before a large sweep.
6. Diagnose failures from logs and the active dependency graph.
7. Validate execution, numerical integrity, physical plausibility, and study
   consistency.
8. Preserve inputs, hashes, commands, logs, outputs, and analysis in a
   provenance bundle.

## Design principles

- No hard-coded turbine or platform.
- No fabricated model when only a solver is present.
- Baseline before modification.
- Exact field matching and visible diffs.
- Minimal, evidence-based error repair.
- Normal termination is necessary but not sufficient.
- Inputs, versions, hashes, commands, logs, outputs, and analysis remain
  traceable.

## Requirements

- Python 3.10 or newer for bundled scripts.
- OpenFAST executable and a complete model for physical simulation.
- Optional OpenFAST Toolbox or pyFAST for binary `.outb` analysis.

The core scripts use only the Python standard library.

## OpenFAST resources

- Official repository: [OpenFAST/openfast](https://github.com/OpenFAST/openfast)
- Documentation: [openfast.readthedocs.io](https://openfast.readthedocs.io/)
- Releases: [OpenFAST releases](https://github.com/OpenFAST/openfast/releases)
- Regression tests and reference inputs:
  [OpenFAST/r-test](https://github.com/OpenFAST/r-test)

## Test

```powershell
python -m unittest discover -s autofast/tests -v
```

## Acknowledgments

AutoFAST is built to support workflows around OpenFAST and would not exist
without the OpenFAST project. We gratefully acknowledge **Jason Jonkman** for
his foundational leadership and contributions to FAST/OpenFAST, as well as the
OpenFAST maintainers, researchers, software engineers, institutional
supporters, and community contributors who continue to develop, test, document,
and share the software.

AutoFAST is an independent community project and is not an official OpenFAST or
National Laboratory of the Rockies product.

## License

MIT
