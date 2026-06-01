# Security Policy

## Supported versions

Security reports should target the latest published version of `pygraph-tool`.

Older versions may not receive security fixes unless the issue is severe and easy to patch.

## Reporting a vulnerability

If you discover a security issue, please do not open a public issue.

Instead, contact the maintainer directly:

```text
belaich.david@outlook.fr
```

Please include:

- a clear description of the issue,
- affected versions if known,
- steps to reproduce,
- possible impact,
- suggested fix if you have one.

## Scope

`pygraph-tool` is a local in-memory Python library. It does not run a server, expose network endpoints, manage authentication, or execute untrusted code by design.

Relevant security concerns may include:

- unsafe serialization behavior if added in future versions,
- unexpected execution paths,
- dependency-related issues,
- packaging or supply-chain issues.

## Response

The maintainer will review the report and decide whether a fix, advisory or patch release is needed.
