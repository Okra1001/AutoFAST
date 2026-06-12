# Input Model and Safe Editing

## Dependency model

Start from `.fst` for coupled OpenFAST or the relevant driver input. Resolve
referenced files relative to the file that contains each reference unless the
format states otherwise.

Common modules include:

- ElastoDyn and BeamDyn: structural dynamics;
- AeroDyn and OLAF: rotor aerodynamics and wake;
- InflowWind: wind input;
- ServoDyn and controller libraries: control and actuation;
- HydroDyn and SeaState: hydrodynamics and waves;
- SubDyn: substructure dynamics;
- MoorDyn: mooring dynamics;
- IceDyn, OrcaFlex interface, and FAST.Farm where applicable.

The inspector uses conservative file-reference heuristics. Verify unusual or
version-specific references against the active file format documentation.

## Scalar lines

Many OpenFAST scalar records follow:

```text
VALUE    FieldName    - description
```

Safe modification requires:

- exact field-name match;
- exactly one match;
- preservation of suffix/comment and newline style;
- atomic replacement;
- reparse and diff after writing.

## Structures requiring dedicated handling

Do not treat these as ordinary scalar fields:

- tabular data and station lists;
- `OutList` blocks terminated by `END`;
- airfoil polar tables;
- combined-case driver tables;
- free-form file lists;
- matrix or mode-shape data;
- generated wind files and binary resources.

For these, parse section boundaries and column headers, validate row/column
counts and units, then write with an explicit schema.

## Version awareness

OpenFAST input schemas evolve. Read headers and executable output, retain
unknown fields, and compare against examples from the same release. A parser
must fail visibly when it cannot prove a safe edit.

## Controlled modifications

For every case, record:

- source template;
- file and field changed;
- old and new values;
- unit;
- scientific purpose;
- variables explicitly held constant.

Diff all generated files against the baseline. Unexpected differences invalidate
the comparison until explained.
