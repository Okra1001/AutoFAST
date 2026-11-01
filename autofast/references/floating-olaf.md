# Floating wind and OLAF: study design

Use the actual solver version, source, model and logs as authority. Confirm executable and driver versions separately; an input accepted by one is not necessarily accepted by another. Preserve original models and use isolated cases. Check the live status and honor explicit pause instructions before any restart.

## Floating model

Audit consistent water depth across the main input, SeaState, moorings and hydrodynamic coefficient provenance. Changing WtrDpth alone does not regenerate potential-flow coefficients. Check hydrostatics, displaced volume, member buoyancy, wave-grid coverage and clamp warnings. Switching to Morison-only changes the model; treat it as a separate, explicitly chosen comparison. A short smoke test establishes initialization, not long-term equilibrium. Screen no-wind still-water equilibrium, then representative wind/wave cases and timestep/grid sensitivity before a campaign.

## OLAF / FVW

Read documentation matching the installed solver and inspect active OLAF inputs. Design time step, wake discretization, physical wake age/length, free and frozen regions and startup discard for the particular operating point. When refining time step, preserve comparable physical wake duration, not merely panel count. Assess convergence of relevant loads and motions versus time step, wake length, regularization and relevant solver approximations; do not call agreement with BEM experimental validation. A short startup run cannot establish a developed wake. Record estimated versus verified wake length and any beta-feature limitations.

## Comparisons and interpretation

Declare controlled inputs, degrees of freedom, controller state, initial operating point, output definitions and common statistics windows. Separate startup transient, solver completion, numerical convergence, applicability warnings and physical validation. Inspect all logs, including successful runs: e.g. UA Mach warnings remain model limitations even if a sensitivity test is stable. Use absolute tolerances or a stated denominator floor for near-zero quantities. For spectra, check stationarity and transient decay before describing a window as steady. Identify diagnostic reconstruction as such, and do not infer physical collision from distances between discretized wake points and blade control points.

Local examples (historical evidence, not universal settings): `E:/数据库fowt/IEA22_campaign_20261024/MODEL_AUDIT.md`, `E:/数据库fowt/IEA15_FVW_StillWater_20261024/README.md`, `E:/数据库fowt/wake_catch_20261015/README.md`, `E:/数据库fowt/iec_eog_fvw_20261016/README.md`. Consult actual current status before relying on them.
