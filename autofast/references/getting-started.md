# Getting Started

## Maturity levels

1. **Solver health**: the executable starts and reports version/help.
2. **Official smoke test**: an unchanged, version-compatible official case runs.
3. **Reference model**: the selected turbine/support-structure model runs unchanged.
4. **Derived case**: declared parameter changes run and pass validation.
5. **Study**: a controlled sweep and analysis are reproducible from provenance.

Do not skip directly from level 1 to a claimed engineering result.

## Executable-only directory

An OpenFAST release executable does not contain a wind turbine definition.
If no `.fst`, `.dvr`, or driver input exists:

- verify the executable;
- report the absence of a model;
- identify the user's modeling goal;
- obtain a matching official example or request a complete model directory;
- record its source and version;
- run it unchanged first.

Useful authoritative starting points include the OpenFAST repository, OpenFAST
`r-test`, official reference turbines, and model repositories explicitly linked
from OpenFAST documentation. Match releases/tags where possible.

## Selecting a first model

- Learning solver basics: smallest official regression case with few dependencies.
- Land-based turbine: official land-based reference model.
- Fixed offshore: reference turbine plus fixed support-structure case.
- Floating offshore: complete coupled platform, hydrodynamics, and mooring case.
- Farm studies: FAST.Farm examples after single-turbine OpenFAST validation.
- Paper reproduction: source-pinned files from the authors or cited repository.

Do not choose a turbine merely because its files happen to be nearby.

## Beginner interaction

Explain:

- which file is the entry point;
- which modules are active;
- what the requested parameter physically means;
- which file owns that parameter;
- what remains controlled;
- what evidence will define success.

Offer a dry run and a single representative case before expensive execution.
