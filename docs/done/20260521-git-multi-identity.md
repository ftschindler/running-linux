---
title: Git Multi-Identity via Conditional Includes
---

- **Context:** Two GitHub accounts (personal + EMU) already authenticated via SSH host aliases; need per-account `user.name` and `user.email` without manual switching

## Problem Statement

With [SSH-based multi-account authentication](./20260520-ssh-multi-account-github.md) in place, repositories are already routed to the correct GitHub account at the transport layer. However, Git commits still carry whichever `user.name` and `user.email` is set globally — meaning commits to EMU repositories show the personal identity (or vice versa) unless manually overridden per repository.

**Goal:** Automatically apply the correct author identity based on which account a repository belongs to, with zero per-repo configuration.

## Solution (Implemented)

Use Git's [`includeIf`](https://git-scm.com/docs/git-config#_conditional_includes) directive with `hasconfig:remote.*.url` matching (available since Git 2.36) to conditionally load an identity file when a repository's remote URL matches an EMU organisation.

### 1. Create identity config file

`~/.gitconfig-foo-org`:

```ini
[user]
    name = <FOO_ORG display name>
    email = <FOO_ORG email address>
```

### 2. Add conditional includes to `~/.gitconfig`

One `includeIf` rule per organisation:

```ini
[user]
    name = <personal display name>
    email = <personal noreply address>

[includeIf "hasconfig:remote.*.url:git@github.com:FOO_ORG/**"]
    path = ~/.gitconfig-foo-org
[includeIf "hasconfig:remote.*.url:git@github.com:ANOTHER_FOO_ORG/**"]
    path = ~/.gitconfig-foo-org
```

The `insteadOf` URL rewrites and `includeIf` rules are independent — place them in whichever order is readable:

```ini
[url "git@github-foo-org:FOO_ORG/"]
    insteadOf = https://github.com/FOO_ORG/
    insteadOf = git@github.com:FOO_ORG/
[url "git@github-foo-org:ANOTHER_FOO_ORG/"]
    insteadOf = https://github.com/ANOTHER_FOO_ORG/
    insteadOf = git@github.com:ANOTHER_FOO_ORG/
```

### Critical: Pattern Must Match the Stored URL

`hasconfig:remote.*.url` matches against the remote URL **as stored in `.git/config`**, regardless of any `url.<base>.insteadOf` rewrites. The `insteadOf` rewriting happens at transport time only and does not affect conditional include evaluation.

This means:

- **Correct:** `git@github.com:FOO_ORG/**` — matches the URL the user originally configured as the remote
- **Wrong:** `git@github-foo-org:**` — the host alias only exists after rewriting; it never appears in `.git/config`
- **Wrong:** `git@github.com:FOO_ORG/:**` — the extra colon before `**` is a literal character that will never match

### Organisations Without URL Rewriting

Some organisations may authenticate fine with the default SSH key (e.g. because the personal account has access) but still need the EMU author identity on commits. These only require an `includeIf` rule — no `insteadOf` rewrite:

```ini
[includeIf "hasconfig:remote.*.url:git@github.com:SHARED_ORG/**"]
    path = ~/.gitconfig-foo-org
```

### 3. Verification

```bash
# In a personal repo
git config user.email
# → <personal noreply address>

# In a FOO_ORG repo (with insteadOf rewrite)
git config user.email
# → <FOO_ORG email address>

# In a SHARED_ORG repo (identity only, no rewrite)
git config user.email
# → <FOO_ORG email address>
```

## Why Not Shell Functions

A shell function switching approach (e.g. `github_foo_org()` / `github_private()`) would:

- require remembering to invoke the function before committing
- affect the global config (wrong identity in other terminals)
- not work with Git GUIs, IDEs or background tooling

Conditional includes are automatic, per-repository and tooling-independent — matching the same design principles as the SSH layer.

## Prerequisites

- Git ≥ 2.36 (for `hasconfig:remote.*.url` support)
- [SSH multi-account setup](./20260520-ssh-multi-account-github.md) already routing URLs through host aliases

## See Also

- [SSH-Based Multi-Account GitHub Authentication](./20260520-ssh-multi-account-github.md) — prerequisite setup this builds upon
