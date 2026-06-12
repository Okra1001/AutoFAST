# Error Diagnosis

## Evidence order

1. Earliest fatal or severe message in stdout/stderr.
2. Entry file and active dependency graph.
3. OpenFAST/module summary files.
4. Executable version and runtime dependencies.
5. Last valid simulation time and affected module.
6. Input diff from the unchanged baseline.

Later errors are often consequences of the first one.

## Diagnostic classes

### Paths and files

Symptoms: cannot open file, file not found, invalid path.

Check the run directory, path ownership, quoting, case sensitivity, absolute
paths from another machine, and whether the complete model tree was copied.

### Input schema or version

Symptoms: error reading line, invalid value, unexpected end of file.

Compare against a same-version official input. Check required placeholder lines,
section order, quotes, booleans, table lengths, and release compatibility.

### Runtime library or controller

Symptoms: missing DLL/shared library, controller load failure, symbol error.

Check architecture, library search path, controller configuration, and whether
the binary was built for the current OS and OpenFAST interface.

### Initial conditions and coupling

Symptoms: large startup transient, constraint failure, immediate instability.

Check equilibrium, initial rotor speed/pitch, enabled DOFs, mooring/platform
state, gravity/buoyancy balance, and controller compatibility.

### Numerical instability

Symptoms: NaN, Inf, solver convergence failure, rapidly increasing values.

Find the first affected time and module. Check time step, discretization,
structural modes, controller commands, aerodynamic validity, and environmental
inputs. Reduce a time step only as a declared diagnostic experiment.

### Output request

Symptoms: invalid channel or missing expected channel.

Validate `OutList` spelling against the active module/version. Do not substitute
a similarly named channel without checking meaning and units.

## Response format

```text
Primary finding:
Evidence:
Likely cause:
Confidence:
Verification:
Minimal repair:
What must remain unchanged:
```

If evidence is insufficient, say so and request the exact log and model chain.
