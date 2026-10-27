# Executed synthetic examples

These source files and annotated copies were authored for validation, not taken from a user's repository. The annotations were produced by an actual model execution following the skill. They are saved results, not an annotation generator.

- `source/`: the public subset of the synthetic input, including helpers, Python-to-Node bridge, MATLAB and strict JSON. The initial full build fixture also had a public-placeholder environment file, a generated minified file and an opaque file; those three excluded items are omitted here.
- `candidate-sections/`: selected `src/pipeline.py` with section summaries and guide/coverage/diff/check evidence.
- `candidate-detailed/`: a separate project copy with detailed Python/JavaScript/MATLAB comments, unchanged non-secret support files, and strict JSON plus a companion.

Paths remain relative to each input/output root. `.code-explainer/` holds the guides, coverage, patch and scoped check reports. Machine-specific source snapshots and private execution logs are not included. The guide describes the original execution; the public tests rerun the shipped structural and small runtime examples independently.

Compare `candidate-sections/src/pipeline.py` with `candidate-detailed/src/pipeline.py` to see the selected detail levels. In the detailed package, read `src/helpers.py` before `src/pipeline.py`, then follow `src/bridge.py` to `web/transform.js`. The ambiguous helper reverses its input; no business purpose is inferred. Read the JSON companion to see why valid zero and empty-array values are not treated as missing input.

The MATLAB example's original code intentionally includes unused locals and a four-column weight limit. Comments describe those facts without fixing them. Native MATLAB validation was unavailable; the saved checks disclose this.
