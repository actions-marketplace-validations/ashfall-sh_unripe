# Compatibility

This is the proposed v1.0 contract. It describes the current interfaces
that scripts and integrations can build on. The project is still pre-1.0.

## Command-line checks

For `unripe check`:

| Exit status | Meaning |
| --- | --- |
| `0` | The check passed under the selected policy. |
| `1` | At least one dependency was too new or its age was unknown under the default fail policy. |
| `2` | The check could not run or complete. This includes invalid arguments, unreadable lockfiles, and scans with no lockfiles. |

`--unknown warn` lets unknown ages pass while still reporting them.
`--exit-zero` turns a policy failure (`1`) into process status `0`.
Operational errors still fail. The JSON report preserves the underlying
policy result. Invalid arguments or configuration can fail before a JSON
report is produced.

## Reports and configuration

Read machine output using [JSON schema 1](json.md). Consumers should accept
additional fields and ecosystem names. A removed field or a change in
its meaning requires a new schema number. Human-readable output can
change as diagnostics improve.

Policy files use TOML. See the [configuration reference](../README.md#configuration)
for supported keys. An explicit `--config` takes precedence over
`UNRIPE_CONFIG`. Otherwise the command looks for `.unripe.toml` or
`[tool.unripe]` in `pyproject.toml` from the current directory up to the
repository root. Without a repository it searches only the current
directory. Unknown configuration keys produce an error.

## Python API

`unripe.__version__` is the installed version string.
`unripe.scan(paths=None, min_age="3d", exclude=(), since=None, cache=True)`
returns a list of findings. It builds policy from its arguments and does
not load a project policy file. Inspect each finding's `state` to decide
whether it passes your policy. The function raises `unripe.check.Problem`
when there are no lockfiles, a lockfile cannot be read, or the Git ref
cannot be used. An empty result is possible after a successful check of
a lockfile with no matching dependencies.

Registry adapters, cache files, and internal Python modules may change
without notice.
