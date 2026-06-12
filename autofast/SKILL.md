---
name: autofast
description: Universal OpenFAST assistant for beginners and researchers. Use to bootstrap from only a release executable, inspect model dependency graphs, explain modules, safely edit input fields, run and resume cases or parameter sweeps, diagnose OpenFAST and driver errors, validate .out/.outb results, compare controlled cases, and create reproducible provenance bundles. Trigger for OpenFAST, AeroDyn, BeamDyn, ElastoDyn, ServoDyn, InflowWind, HydroDyn, SeaState, SubDyn, MoorDyn, FAST.Farm, or OpenFAST driver workflows.
license: MIT
metadata:
  version: "1.0.0"
  maturity: "stable"
---

# AutoFAST v1.0

Help users move from an OpenFAST executable or model directory to traceable,
validated simulation results. Work with any turbine or support structure.
Never invent turbine parameters or silently change physics to make a case run.

## Choose the workflow

| User state or goal | Workflow |
|---|---|
| Executable only, no inputs | Bootstrap |
| Existing model, unknown structure | Inspect |
| Change parameters | Modify |
| Run one case | Run |
| Run many controlled cases | Sweep |
| Fatal error or suspicious result | Diagnose |
| Check or compare outputs | Validate |
| Share reproducible results | Provenance |

Read only the reference needed for the active workflow:

- [Getting started](references/getting-started.md)
- [Input model and safe editing](references/input-files.md)
- [Error diagnosis](references/diagnostics.md)
- [Verification and validation](references/verification.md)
- [Sweep design](references/sweep-design.md)
- [Provenance](references/provenance.md)
- [Platform notes](references/platform-notes.md)
- [FOWT case-study lessons](references/fowt-case-study.md)

## Non-negotiable rules

1. Treat the executable as a solver, not a turbine model.
2. Discover active files from `.fst`, `.dvr`, or driver references.
3. Use a matching official example or user-supplied model; do not fabricate one.
4. Establish an unchanged baseline run before modifying a model.
5. Change only declared independent variables in controlled comparisons.
6. Match fields by identity, never by remembered line number.
7. Preserve comments, section order, placeholder lines, units, and relative paths.
8. Show a diff and reparse modified files before running them.
9. Confirm the executable, version, working directory, and runtime dependencies.
10. Test one representative case before a large sweep.
11. Record case state incrementally so interrupted sweeps can resume.
12. Diagnose from logs and the active dependency graph; use minimal repairs.
13. Require normal termination, complete outputs, expected duration, and finite data.
14. Apply consistent channels, units, and statistics windows when comparing cases.
15. Package inputs, hashes, commands, environment, logs, outputs, and analysis.

## Bootstrap

When no `.fst` or driver input exists:

1. Run `python scripts/bootstrap_openfast.py PATH --output bootstrap.json`.
2. Locate the OpenFAST executable and query its version/help output.
3. Scan again to prove that no runnable model is present.
4. Explain that a release executable alone cannot produce a physical simulation.
5. Ask what the user wants to model: learning example, known turbine, fixed
   offshore, floating, farm, or paper reproduction.
6. Prefer the official OpenFAST `r-test` or another source-pinned public model
   compatible with the executable version.
7. If network access is allowed, obtain the selected model from an authoritative
   source and record URL, tag/commit, date, and hashes.
8. If network access is unavailable, create an inspection report and request the
   complete model directory, not only the top-level `.fst`.
9. Run the original example unchanged before deriving a user case.

Never claim a simulation ran when only executable health was tested.

## Inspect

Run:

```powershell
python scripts/inspect_project.py PATH --output openfast-inspection.json
```

Use the report to identify entry files, executables, referenced files, missing
dependencies, absolute-path portability risks, and module hints. Confirm the
actual entry file with the user when multiple unrelated models are present.

## Modify

Inspect the active parent-child reference chain first. Preview scalar changes:

```powershell
python scripts/modify_input.py FILE FIELD VALUE --dry-run
```

Then apply:

```powershell
python scripts/modify_input.py FILE FIELD VALUE --backup
```

The script intentionally refuses zero or multiple exact field matches. For
tables, `OutList`, airfoil polars, or version-specific blocks, read
[Input model and safe editing](references/input-files.md) and write a
task-specific structured transformation with assertions.

## Run

```powershell
python scripts/run_case.py --executable PATH --entry CASE.fst --result-dir run-record
```

Run from the entry file's directory unless the model explicitly requires
another location. A passing case requires more than return code zero; inspect
the generated status, log, outputs, and provenance.

If the user says they will launch a generated runner themselves, stop after
input preparation and static validation.

## Sweep

Describe cases in CSV using `case_id`, `entry`, and optionally `executable`.
Run:

```powershell
python scripts/run_sweep.py cases.csv --default-executable PATH --result-dir sweep-record
```

The runner writes status after every case and skips cases already marked passed.
Keep a separate manifest describing varied and controlled parameters.

## Diagnose

Run:

```powershell
python scripts/diagnose_failure.py LOG --inspection openfast-inspection.json
```

Present the primary evidence, likely cause, confidence, verification step, and
smallest repair. Do not disable modules, reduce model fidelity, or change
several parameters at once unless the user explicitly chooses that experiment.

## Validate

Use:

```powershell
python scripts/analyze_output.py OUTPUT --start-time SECONDS
```

The script parses text `.out` directly and uses OpenFAST Toolbox or pyFAST for
`.outb` when installed. Validate run integrity before physical interpretation.
For two controlled cases, use:

```powershell
python scripts/compare_outputs.py BASELINE CANDIDATE --start-time SECONDS
```

Use project-specific acceptance limits; do not embed expected power or motion
values for a particular turbine into universal rules.

## Provenance

Create or refresh a standalone evidence bundle:

```powershell
python scripts/create_provenance.py ENTRY --executable PATH --output provenance
```

Report exactly what was prepared, modified, run, passed, failed, skipped, and
not verified. Never generalize one successful test case to an entire sweep.
