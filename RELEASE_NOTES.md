# AutoFAST v1.0.0

Initial stable release.

## Included

- executable-only bootstrap assessment;
- project and dependency inspection;
- conservative OpenFAST scalar parser;
- exact, atomic input modification with dry-run and backup;
- single-case execution evidence;
- resumable CSV sweep runner;
- evidence-based failure classification;
- text `.out` analysis;
- optional `.outb` analysis through OpenFAST Toolbox or pyFAST;
- controlled two-output comparison;
- dependency and executable provenance;
- universal workflow references and FOWT-derived case-study lessons;
- standard-library unit tests.

## Known boundaries

- The dependency inspector is conservative rather than a complete schema parser.
- It reports unresolved references for review because some belong to disabled
  modules.
- Tables, `OutList`, airfoil polars, and version-specific blocks require
  dedicated structured transformations.
- Physical acceptance criteria remain model- and study-specific.
