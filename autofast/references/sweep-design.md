# Sweep Design

## Separate design from execution

Maintain:

- baseline identifier;
- varied parameters and units;
- controlled parameters;
- case naming rule;
- entry file per case;
- statistics window;
- expected outputs;
- analysis plan.

Use CSV for a flat execution manifest and JSON/YAML or Markdown for the richer
scientific contract.

## Generation rules

- clone the nearest validated baseline;
- generate deterministic names;
- assert each requested edit;
- diff first, middle, and last cases;
- check all references before execution;
- avoid mutating a shared dependency when cases require different values.

## Execution rules

- pass one representative case first;
- write status after each case;
- retain per-case logs;
- skip only cases whose prior status and evidence still pass;
- stop or quarantine after failure according to user preference;
- limit parallelism based on memory, licenses, and I/O.

## Fair comparison

For paired model comparisons, keep environment, control, structure, duration,
time step, initial conditions, output channels, and analysis identical unless
one is the declared independent variable.
