# repo-code-explainer

Create separate copies of code annotated with learning comments after tracing the relevant repository behavior. Originals remain untouched. Each invocation chooses detail and package; source repositories are not scanned in the background.

The installation-ready folder is `repo-code-explainer/`. Install the whole folder at `~/.agents/skills/repo-code-explainer` for user-wide local Codex discovery, then use it on your next turn. If it does not appear, restart Codex. This covers local projects on that machine/account; other machines and remote/cloud environments need their own installation. See [official skill documentation](https://learn.chatgpt.com/docs/build-skills). The skill works without Skill Forge.

Example requests:

> Use $repo-code-explainer on this repository. Scope the CLI-to-parser path, use block explanations plus difficult lines, and deliver selected annotated files plus a guide to a fresh destination outside the repository.

> Use repo-code-explainer on `/work/project`, scope the CLI-to-parser path, use block explanations plus difficult lines, and deliver selected files with a guide to a fresh `/work/project-learning` directory.

> Use repo-code-explainer for `src/`, nearly every meaningful statement, as a separate project copy. Include the non-secret support files needed for reading that path. Explain in Spanish for a new Python reader.

> Prepare annotated copies of this MATLAB function using section summaries and selected files plus a guide.

“Explain this function in chat,” “fix this bug,” and “review this PR” do not by themselves select this skill.

Runtime needs file listing/search/read, fresh-directory creation/copy/write, and diffs. Python 3.9+ runs the optional standard-library verifier; no third-party Python packages, paid API, or cloud service is needed. Existing parsers/compilers/tests improve validation but are not assumed installed. The verifier checks preservation; the agent investigates and authors the explanations.

Run local helper tests with:

```sh
python3 -m unittest discover -s repo-code-explainer/tests -v
python3 repo-code-explainer/scripts/verify_annotations.py --help
```

See [the skill](SKILL.md), [annotation rules](references/annotation-rules.md), [validation results](VALIDATION.md), and [foundation provenance](FOUNDATIONS.md). Validation distinguishes executed checks from illustrative examples and unexecuted native checks. No tool can guarantee equivalence for every language or code that inspects its own source/line numbers.
