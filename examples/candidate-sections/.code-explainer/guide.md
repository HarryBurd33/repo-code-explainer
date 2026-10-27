# Code reading guide

Scope: src/pipeline.py. Detail: section summaries. Package: selected files plus guide.

Read `src/helpers.py:keep` and `q` in the original context before `src/pipeline.py:totals` and `labels`: keep returns the raw enabled value with False as its default; the comprehension tests that returned value for truthiness, and q reverses a sliceable value. Totals filters, converts accepted amounts to float, then sums. Labels reverses each required label in row order. The existing MESSAGE comment already explains its literal hash character.

The selected copy is a reading artifact and needs the original package context to import helpers.

Evidence: source README.md, src/helpers.py, src/pipeline.py, src/bridge.py, web/transform.js, matlab/scale_columns.m, config/settings.json were read. No tests or manifest were present. No callers beyond the bridge-to-Node path were found in this small fixture. Behavior and error notes are static/manual observations, not observed runtime results or documented design intent.

Excluded from the project package: environment file (potential secrets), generated/bundle.min.js (minified generated code), opaque.dat (binary/opaque data). Environment values were not inspected for explanations or copied into the package; the snapshot helper locally read and hashed the fixture environment file. This does not establish secret safety. Supporting README.md and helpers.py are retained unchanged in the project copy, and only selected source is annotated. The selected-files package contains only its requested file and companions.

Validation actually run: source full-inventory snapshot check passed for its recorded regular-file scope; Python insertion, tokens, AST including type comments, and compile guards passed.  See checks.json for exact outcomes. No project code was executed, no dependencies installed, and runnable whole-project behavior has not been verified. Inserted lines can affect source inspection and debugging line numbers. Git status was unavailable because the supplied source is not a Git repository.

All selected files were examined. JSON inline annotation is unsupported and explicitly skipped with its companion supplied. No requested file remains unexamined. See coverage.json and annotations.patch for coverage and inserted explanations.
