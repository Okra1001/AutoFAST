# Verification and Validation

## Four gates

### 1. Execution integrity

- return code is zero;
- expected outputs exist and are nonempty;
- log contains normal termination and no fatal error;
- output final time reaches requested duration within time-step tolerance.

### 2. Numerical integrity

- time is monotonic;
- values are finite;
- sampling interval is consistent with configuration;
- no unexplained spikes, clipping, or runaway growth;
- transient removal is declared.

### 3. Physical plausibility

- signs, units, coordinate systems, and magnitudes are understood;
- rotor speed, pitch, torque, power, and thrust follow the modeled regime;
- structural and platform motions match enabled DOFs and forcing;
- neighboring sweep cases show explainable trends.

Use model-specific references and conservation/consistency checks. Universal
hard-coded power, thrust, or motion thresholds are not valid.

### 4. Study validity

- only intended variables differ;
- software and input versions are identical or documented;
- channels, units, interpolation, and statistics windows match;
- uncertainty and metric definitions are stated;
- failed and excluded cases remain visible.

## Output formats

Text `.out` can be parsed directly. Binary `.outb` should be read with
OpenFAST Toolbox/pyFAST or another verified reader. Identify channels by exact
name and unit, not column number.

## Recommended summaries

- count, mean, standard deviation, minimum, maximum;
- selected quantiles;
- mean bias, RMSE, relative RMSE with denominator stated;
- correlation for time-series reproduction;
- extrema and fatigue metrics only with documented methods.

Never call a case physically validated merely because it terminated normally.
