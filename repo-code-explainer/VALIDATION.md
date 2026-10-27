# Validation summary

Release preparation on October 26, 2026: 31 verifier tests and 8 public example/package tests passed locally on Python 3.15.0 with an existing Node runtime. The verifier suite is shipped in this folder; the separate public repository contains the example suite and actual model-produced fixtures.

The initial build also ran sixteen parent integration checks: ten original synthetic files and their inventory stayed unchanged; relative paths, both output package forms and support files were checked; Python tokens/AST/compile checks passed; JavaScript parsed; JSON remained identical and parsed with zero/empty values; and isolated Python-to-Node behavior matched. Section and detailed examples contain different comment detail. Independent review found no actionable contract defects and exercised encoding, CRLF, decorators and raw-string rejection cases.

The initial ZIP was extracted into a new directory, the 31 shipped tests passed there, metadata/relative links passed validation, and archive bytes were compared with the folder. These tests establish their scoped invariants, not universal behavioral equivalence or automatic discovery in every host.

Limits:

- MATLAB/Octave was unavailable. MATLAB examples passed insertion/continuation guards and manual review; native syntax/runtime validity remains unverified.
- Python checks compare non-comment executable tokens, normalized AST/type comments and compilation without execution. Source-inspecting and line-number-sensitive behavior can still differ. JavaScript received insertion review, Node parsing and a small runtime sample, without a JS token/AST comparison.
- The verifier's `none` mode establishes byte identity only. JSON was additionally parsed. Snapshots cover declared regular-file scope and exclusions. The agent separately reviews explanation truth, detail/package choices, safe output creation, permissions and requested coverage.
- Activation exclusions, missing choices, partial large-repository coverage and unknown-provenance reruns received actual model responses to simulated requests. Native selector behavior, a real 100-file continuation and already-annotated cleanup are not established by those responses.
- A simple direct-prompt baseline and candidate requests shared one sequential, nonblind context. Exact model/effort and task usage were unknown; no general effectiveness or cost-saving claim follows.
- Python 3.9+ is the intended helper floor. Local execution used 3.15; the public repository's CI matrix separately reports results for 3.9, 3.12 and 3.15.

No cloud service, paid API or dependency install is required. The public repository is https://github.com/HarryBurd33/repo-code-explainer. It contains a fuller claim/evidence table, reproducible tests, usage/install instructions and foundation provenance. Private build logs and machine paths are not part of this installable folder.
