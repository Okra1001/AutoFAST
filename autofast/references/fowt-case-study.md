# FOWT Case-Study Lessons

These are transferable lessons from a 15 MW floating-wind study, not universal
default parameters.

- Clone a validated comparison baseline and alter only the declared forcing or
  model switch.
- Keep steady and dynamic aerodynamic variants aligned in controller,
  structure, environment, duration, time step, and outputs.
- Use manifests to prevent corrected and superseded controller results from
  being mixed.
- For long wind-speed sweeps, use deterministic names, per-case logs, and
  incremental status.
- When reproducing coupled aerodynamics in a driver, first verify prescribed
  platform motion, rotor motion, pitch, and yaw histories; only then interpret
  aerodynamic differences.
- Driver motion files may use radians while human-readable summaries use
  degrees. Record coordinate and unit conversions explicitly.
- A normal return code plus an output file is insufficient. Check termination
  text, output duration, channels, finite values, statistics window, and trends.
- When the user intends to launch a batch file manually, prepare and statically
  validate it without starting an expensive sweep.
