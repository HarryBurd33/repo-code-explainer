# repo-code-explainer

A reusable Codex skill for learning an unfamiliar codebase through **separate annotated copies**. The agent investigates relevant entry points, callers, dependencies and data flow, then adds explanations using the language's native comments. Original source remains untouched.

Each invocation chooses:

| Choice | Options |
| --- | --- |
| Explanation detail | Section summaries; block explanations plus difficult lines; nearly every meaningful executable statement; custom |
| Output package | Selected files preserving relative paths plus guide; separate project copy plus guide; custom |

Already-supplied choices are accepted. Missing choices are asked for that invocation. Missing scope is resolved after enough inspection to suggest useful starting points. Copies go into a **fresh destination outside the original source tree**.

## Install globally for Codex

Ask Codex:

```text
Use $skill-installer to install the skill from
https://github.com/HarryBurd33/repo-code-explainer/tree/main/repo-code-explainer
into ~/.agents/skills so it is available across my local repositories.
```

Or clone and copy it yourself (Python 3.9+):

```sh
git clone https://github.com/HarryBurd33/repo-code-explainer.git repo-code-explainer-source
python3 -c 'from pathlib import Path; import shutil; shutil.copytree("repo-code-explainer-source/repo-code-explainer", Path.home() / ".agents" / "skills" / "repo-code-explainer")'
```

The copy command refuses an existing destination. Review existing customizations before updating; do not merge or overwrite them blindly.

`~/.agents/skills` is Codex's user-wide local skill location. It applies across projects on that machine/account; remote/cloud environments and other machines need their own installation. It does not grant access to files outside a chat's permissions. Codex detects new skills automatically; use your next turn, and restart Codex if the skill does not appear. See [official skill documentation](https://learn.chatgpt.com/docs/build-skills).

## Use it

In a Codex chat with access to the target repository, mention the skill and specify your choices:

```text
Use $repo-code-explainer on /work/my-project.
Scope: the CLI entry point through parsing and output.
Detail: block explanations plus difficult individual lines.
Package: selected annotated files plus a guide.
Destination: a fresh /work/my-project-learning directory.
Explain in plain English for a reader new to Python.
```

Another example:

```text
Use repo-code-explainer on this MATLAB project.
Annotate src/ at nearly every meaningful statement,
deliver a separate project copy plus a guide, and explain in Spanish.
```

You receive annotated files, a guide with reading order and uncertainties, a coverage record, a reviewable diff, and actual validation results. A selected-files package may need the original project's context to run. Chat-only explanations, bug fixes, refactoring and ordinary code review do not by themselves select this skill.

## What has been checked

The bundled Python verifier checks source hashes/inventory, insertion-only changes, native comment lines, and—for Python—non-comment tokens, normalized AST/type comments and compilation without execution. It has 31 adversarial unit tests. Public fixture tests cover the two detail levels, both package forms, mixed Python/JavaScript behavior, unchanged strict JSON, and MATLAB continuation placement. [Examples](examples/README.md) contain actual model-produced annotated copies.

Strict JSON has no native comments, so it is preserved unchanged with a companion explanation. MATLAB mode provides conservative insertion checks and explicitly leaves native syntax/runtime validation unverified when MATLAB is unavailable. Other languages use available native tools or disclosed manual checks; universal support is not promised. Passing tests and matching Python structure cannot prove equivalence for source-inspecting or line-number-sensitive code. The agent authors explanations; this is not an automatic annotation executable.

See [validation evidence and limits](VALIDATION.md), [full skill instructions](repo-code-explainer/SKILL.md), and [foundation inspection](repo-code-explainer/FOUNDATIONS.md).

## Run checks

No third-party Python packages are needed. Node is needed for the JavaScript/bridge fixture tests; those tests skip when it is absent.

```sh
python3 -m unittest discover -s repo-code-explainer/tests -v
python3 -m unittest discover -s tests -v
python3 repo-code-explainer/scripts/verify_annotations.py --help
```

GitHub Actions runs the suites on Python 3.9, 3.12 and 3.15. A CI configuration is not evidence of a passing run; use the repository's Actions results for current outcomes.

## License

[MIT](LICENSE). All shipped instructions, examples, tests and helper code are original material. Third-party projects and documentation were inspected as references; no code or protected documentation text was incorporated.
