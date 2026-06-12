# AutoFAST v1.0

AutoFAST is a universal Codex/agent skill for taking OpenFAST work from an
executable or model directory to traceable, validated simulation results.

It is turbine-agnostic and supports beginner bootstrap, dependency inspection,
safe scalar edits, single runs, resumable sweeps, error diagnosis, text and
binary output analysis, controlled comparisons, and provenance bundles.

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

## Test

```powershell
python -m unittest discover -s autofast/tests -v
```

## License

MIT
