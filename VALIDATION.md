# Validation and limits

Local release preparation on October 26, 2026 used Python 3.15.0 and an existing Node runtime. **31 verifier tests and 8 public example/package tests passed.** No third-party Python package was installed. Run the two commands in README.md to reproduce them.

## Publication verification

- [The first hosted CI run](https://github.com/HarryBurd33/repo-code-explainer/actions/runs/40453095094) passed both suites on Python **3.9, 3.12 and 3.15**. All three jobs completed successfully, including the Node-backed example checks.
- The published skill was downloaded by Codex's skill installer into the user-wide skill directory. All eight installed files matched the published package hashes, and the installed verifier's 31 tests passed.
- Codex CLI **0.164.0** returned the skill from its native `skills/list` API, with `forceReload: true`, while called from an unrelated temporary directory. It reported `scope: user`, `enabled: true`, and no related loading errors. This discovery check started no model turn and establishes local user-wide discovery, not automatic synchronization to other machines/cloud environments.
- GitHub reported public visibility, SPDX license **MIT**, the intended default branch, and ten relevant repository topics. The published commit was read back and matched the local tested source.

## Capability evidence

| Capability or claim | Actual evidence | Limit |
| --- | --- | --- |
| Original source remains untouched | Hash/inventory comparison of ten initial synthetic input files; public runtime tests execute copies and recheck source bytes | A snapshot covers its declared files/exclusions, not arbitrary omitted files |
| Comments preserve executable text | Python executable tokens, normalized AST/type comments and compilation; adversarial mutations rejected | Source/line introspection and toolchains can observe inserted comments |
| Chosen detail and package | Actual model-produced section-level selected files and detailed project copy; paths, companions and supporting-file identity checked | Small synthetic sample; no universal model-quality guarantee |
| Repository understanding | Model read helper implementation and both ends of Python-to-Node path; output explains reversal, truthy filtering, JSON transport, coercion and errors | No business intent inferred from names; new repositories require fresh investigation |
| Mixed-language execution | Isolated original and annotated copies both produce total 5.5, empty total 0, labels ba/tac/empty, and bridge output [0, 2, 6] | Small Python/JavaScript behavioral sample; not proof of equivalence |
| MATLAB comments | Actual `%` annotations preserve lines and ellipsis continuation; manual review and conservative helper guard pass | MATLAB/Octave was unavailable; native syntax/runtime unverified |
| Unsupported inline formats | Strict JSON is byte-identical, parses, retains numeric zero and empty array, and has a companion explanation | Companion is not an inline annotation |
| Per-run choices and reruns | Consecutive section/selected and detailed/project requests used different fresh outputs from originals, without stacked comments | Unknown-provenance annotated inputs were tested by model response, not automatic cleanup |
| Activation and incomplete scope | Actual model responses reject annotation activation for chat-only explanation/bug-fix and report 90 unresolved of a hypothetical 100 requested files | Response-level checks, not an actual 100-file job or guaranteed automatic selector behavior |
| Safe file/evidence handling | Tests reject stale hashes, changed inventory, traversal, source/report symlinks, existing evidence files, in-tree evidence outputs and altered original text | Agent must separately enforce package destination, content accuracy, permissions and completeness |
| Installable package | Original ZIP extracted and 31 shipped tests passed; metadata and relative links validated; final bytes read back | A folder or ZIP alone does not establish native discovery in every host |

The main SKILL.md is a workflow followed by a capable coding agent. Its Python script is an optional preservation verifier, not an autonomous annotation engine. The skill has filesystem/terminal requirements, and project access remains subject to each chat's permissions. Network/paid services and private source upload are unnecessary.

Initial evidence included an independent Skill Finder inspection, a construction agent for the verifier, an independent contract/resource review with adversarial invocations, and an independent model executor. Parent review reconciled actual outputs and all sixteen frozen acceptance groups. Two explanatory wording points were tightened: the caller tests the helper's raw return value for truthiness, and local hashing reads bytes even when values are never shown or copied.

The direct-prompt baseline ran first, then the skill's two requests ran in the same model context. This comparison was sequential and nonblind; overlapping fixture patterns and source familiarity prevent a controlled claim about improvement or savings. Exact inherited model/effort and task-specific usage were unavailable.

The public `examples/` contain a sanitized subset of those synthetic inputs and actual annotated output packages. Private snapshots, machine paths, raw logs and semantic checkpoint state are excluded. Original retrieval provenance and reuse-right decisions are in `repo-code-explainer/FOUNDATIONS.md`; all shipped material is original and MIT licensed.

CI is configured for Python 3.9, 3.12 and 3.15. Availability and actual results must be read from Actions, not inferred from configuration. Compatibility with languages or environments outside the stated checks remains conditional on the tools and evidence available during each invocation.
