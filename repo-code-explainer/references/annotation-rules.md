# Annotation rules and examples

These are illustrative examples, not executed validation evidence. They supplement the workflow; repository evidence determines each explanation.

## Evidence before prose

Trace `entry point → caller → transformation → output` as far as the selected scope requires. Record where claims come from: relative path and symbol, relevant config/test, or observed authorized execution. A call chain can cross languages through subprocesses, HTTP, foreign-function calls, or generated interfaces. Read both ends and the actual argument/serialization contract. An import does not prove that a branch executes in every invocation.

If `q(x)` returns `x[::-1]`, describe sequence reversal. Do not call it encryption, anonymization, sorting, or a business rule without evidence. Describe exceptions, mutation, ordering, lazy evaluation, and external side effects when relevant. Distinguish an inferred purpose from observed behavior.

## Same Python function, contrasting detail

Original:

```python
from .helpers import keep

def totals(rows):
    values = [float(row["amount"]) for row in rows if keep(row)]
    return sum(values)
```

Suppose investigation of `helpers.py` establishes `keep(row)` returns `row.get("enabled", False)` (truthiness, not strict Boolean equality). A section-level copy could be:

```python
from .helpers import keep

# Select rows using helpers.keep, convert their amounts, and return the sum.
# Filtering tests the helper's returned "enabled" value; absent means False.
def totals(rows):
    values = [float(row["amount"]) for row in rows if keep(row)]
    return sum(values)
```

A detailed copy could be:

```python
# Load the row-selection helper from this package's helpers module.
from .helpers import keep

# Sum numeric amounts from rows accepted by the helper.
def totals(rows):
    # Visit rows in order; keep returns "enabled" (absent means False).
    # Include rows with truthy results, then convert their required amount to float.
    # A missing amount or invalid numeric value raises an exception here.
    values = [float(row["amount"]) for row in rows if keep(row)]
    # Sum the converted values; an empty list produces integer 0.
    return sum(values)
```

Block mode sits between these examples: explain the filtering/conversion block and any difficult expression, with less statement-by-statement commentary. All levels retain identical original code and strings. Do not split a comprehension or multiline expression merely to explain its internal tokens.

## Syntax and tooling boundaries

Use ordinary full-line comments before complete statements whenever possible. Avoid changing indentation, quoting, line continuations, or existing trailing comments. Preserve CRLF/LF and encoding; copying text through a default decoder can alter bytes. Never insert before a shebang or displace a Python encoding cookie. Preserve decorators, pragma association, lint/type comments, coverage directives, help blocks, license headers, and formatter controls. Do not add strings/docstrings as comments.

Python's tokenizer and AST can validate a copy without running it. Compare token type/text with comments and nonsemantic newline positions removed, compare AST without location fields but with type comments, and compile for scope/syntax errors. Preserve existing directives separately; a new `# type: ignore` can affect tools despite being a comment. Static equivalence does not prove behavior of code inspecting its own source, traceback line numbers, debugger locations, or source hashes.

JavaScript/TypeScript comments must avoid template strings, regex literals, JSX text, automatic semicolon insertion hazards, bundler pragmas and source-map expectations. Native parsing is useful if already available; do not install a tool merely to call validation complete. C/C++ macros such as `__LINE__`, preprocessor continuations, and line directives can make added lines significant. Shell continuations and here-documents need similar caution. Unknown syntax means a companion explanation or unresolved status, not guessed comment insertion.

## MATLAB

Resolve `.m` using code and repository context. MATLAB uses `%`; Objective-C does not. For example:

```matlab
% Average each row across its columns; the second argument selects dimension 2.
means = mean(A, 2);
% Select the first row using MATLAB's one-based indexing.
first = A(1, :);
% Transpose and conjugate A; A.' would transpose without conjugation.
B = A';
% Build a row vector over a continued logical statement.
weights = [1, 2, ...
           3, 4];
% Visit each column index; size(A, 2) is the number of columns.
for k = 1:size(A, 2)
    % Scale column k by its matching weight.
    A(:, k) = A(:, k) * weights(k);
end
```

Do not insert an explanation between the ellipsis and its continuation. Avoid splitting logical statements, quoted text, transpose syntax, or `%{`/`%}` blocks. Preserve existing `%%` sections and function help text. Explain indexing dimensions and matrix versus elementwise operations from the actual operators. A Python helper's insertion check cannot substitute for MATLAB parsing or execution. If MATLAB/Octave is unavailable, record manual syntax review and unexecuted native checks. Octave results do not establish full MATLAB compatibility.

## Unsupported formats and packages

For `{"workers": 0, "paths": []}`, keep strict JSON unchanged. Explain that zero is a supplied numeric value and the list is empty in a companion; do not treat either as a missing choice or inject `//`/`#` comments. Document whether the consuming code treats these values specially only after reading it.

A selected package might contain `OUTPUT/src/pipeline.py`, `OUTPUT/lib/helpers.py`, and companions; it need not run alone. A project copy should also retain its needed non-secret manifest/config/assets and preserve their paths. Never quietly copy `.env`, private keys, caches, or Git internals. Disclose missing dependencies, submodules, symlinks, configuration, and generated resources. Avoid promises that all repositories/languages are supported.

## Coverage and repeat runs

Track every requested item, including not-yet-examined items. For a 100-file request with 10 annotated files, report 10 annotated and the exact remaining/skipped/unresolved records; “the repository is annotated” is false. Do not silently shrink the request to what fit one batch.

Keep original hashes and the insertion diff as provenance. Rerun from original source into a fresh sibling output and adapt to the new detail/package choices. Existing useful comments count toward the learning explanation; do not repeat them. If handed an annotated copy without its baseline, do not delete comments based on a guessed prefix. Resolve provenance or retain and report uncertainty.

## Verification interpretation

The bundled verifier is a conservative guard, not a language-general proof. Consult its `--help` and inspect JSON results. Its MATLAB mode checks insertions and continuation placement, not MATLAB syntax or executable tokens. Its `none` mode requires byte identity. New comments containing directives, existing text changes, unsupported encodings, links, or a changed original hash must not be called a pass. Use custom explanatory wording or another meaningful native check; never weaken the guard to obtain a green result.
