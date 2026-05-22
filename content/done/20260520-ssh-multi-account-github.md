---
title: SSH-Based Multi-Account GitHub Authentication
---

- **Date:** 2026-05-20
- **Context:** Manjaro Linux with two GitHub accounts (personal + EMU) requiring tooling-independent auth

> Edit this document [on Github](https://github.com/ftschindler/running-linux/edit/main/content/done/20260520-ssh-multi-account-github.md)

## Problem Statement

With two GitHub accounts - a personal one and a work EMU (Enterprise Managed User) account tied to an organisation `FOO_ORG` - authentication needs to route to the correct account depending on the repository URL. Neither `gh auth` (supports only one account at a time) nor `ksshaskpass` for HTTPS (not picked up by all Git GUIs) provides a reliable, tooling-independent solution.

Additionally, GitHub does not allow the same SSH key to be registered on more than one account, so a dedicated key per account is mandatory. SSH keys also have an advantage over fine-grained PATs for EMU organisations: they can be SSO-authorised by the user directly via the GitHub UI, whilst fine-grained PATs require manual approval by an enterprise owner.

**Requirements:**

- Automatic account selection based on repository URL
- Works with any Git tooling (CLI, Git GUI, IDE, lazygit, etc.)
- No interactive prompts or credential helpers that only work in terminals

## Solution (Implemented)

Dedicated SSH keys per account, an SSH config with host aliases for key selection and a Git `insteadOf` rewrite to transparently route URLs.

### 1. Generate SSH keys

Create one key per account, using distinct filenames:

```bash
# Personal account
ssh-keygen -t ed25519 -C "$(whoami)@$(uname -n)-$(date -I)" -f ~/.ssh/github

# FOO_ORG EMU account
ssh-keygen -t ed25519 -C "$(whoami)@$(uname -n)-$(date -I)" -f ~/.ssh/github_foo_org
```

Ensure the keys have correct permissions:

```bash
chmod 600 ~/.ssh/github ~/.ssh/github_foo_org
chmod 644 ~/.ssh/github.pub ~/.ssh/github_foo_org.pub
```

### 2. Register public keys on GitHub

Add each public key to the corresponding GitHub account under
**Settings → SSH and GPG keys → New SSH key**:

```bash
# Copy personal key to clipboard
xclip -selection clipboard < ~/.ssh/github.pub

# Copy EMU key to clipboard
xclip -selection clipboard < ~/.ssh/github_foo_org.pub
```

### 3. Configure SSH host aliases

Add to `~/.ssh/config`:

```ssh-config
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github
    IdentitiesOnly yes

Host github-foo-org
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_foo_org
    IdentitiesOnly yes
```

`IdentitiesOnly yes` prevents the SSH agent from offering other keys, ensuring only the specified key is used for each host alias.

### 4. Configure Git URL rewriting

Add to `~/.gitconfig` (or use `git config --global`):

```ini
[url "git@github-foo-org:FOO_ORG/"]
    insteadOf = https://github.com/FOO_ORG/
    insteadOf = git@github.com:FOO_ORG/
```

This rewrites any URL under the `FOO_ORG` organisation - whether HTTPS or SSH - to route through the `github-foo-org` host alias, which selects the EMU key. All other `github.com` URLs use the default host entry with the personal key.

### Verification

```bash
# Test personal key authentication
ssh -T github.com
# → Hi <personal-username>! You've successfully authenticated ...

# Test EMU key authentication
ssh -T github-foo-org
# → Hi <emu-username>! You've successfully authenticated ...

# Verify URL rewriting for an EMU repo
git ls-remote https://github.com/FOO_ORG/some-repo.git
# Should authenticate as the EMU account

# Verify personal repos still work
git ls-remote git@github.com:your-username/some-repo.git
# Should authenticate as the personal account
```

### Extending for Additional Organisations

For further organisations on the same EMU account, add `insteadOf` lines:

```ini
[url "git@github-foo-org:FOO_ORG/"]
    insteadOf = https://github.com/FOO_ORG/
    insteadOf = git@github.com:FOO_ORG/
[url "git@github-foo-org:ANOTHER_FOO_ORG/"]
    insteadOf = https://github.com/ANOTHER_FOO_ORG/
    insteadOf = git@github.com:ANOTHER_FOO_ORG/
```

For a separate account with its own key, add another SSH host alias and corresponding `insteadOf` block.

## How It Works

The mechanism operates at two layers:

1. **Git layer** (`insteadOf`): Before any network operation, Git rewrites the remote URL. An HTTPS URL like `https://github.com/FOO_ORG/repo.git` becomes `git@github-foo-org:FOO_ORG/repo.git`.
2. **SSH layer** (host alias): SSH resolves `github-foo-org` via `~/.ssh/config`, connecting to `github.com` but presenting the EMU key.

Because this happens at the transport layer, it is invisible to any tooling built on top of Git.

## Trade-offs

- **No per-repo configuration:** Account selection is determined solely by the organisation in the URL. Repositories outside the configured organisations always use the personal key.
- **HTTPS remotes are transparently converted to SSH:** If a workflow strictly requires HTTPS (e.g. behind a corporate proxy that blocks SSH), this approach will not work. In that case, consider [Git Credential Manager](https://github.com/git-ecosystem/git-credential-manager) with its multi-account support.
- **SSH agent optional:** The keys can be loaded into `ssh-agent` for passphrase caching, but the setup works without it - SSH reads the key files directly.

## References

- [Arch Wiki: SSH keys](https://wiki.archlinux.org/title/SSH_keys) - key generation, permissions, agent configuration
- [GitHub Docs: Generating a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [GitHub Docs: Adding a new SSH key to your account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
- [Git Documentation: url.\<base\>.insteadOf](https://git-scm.com/docs/git-config#Documentation/git-config.txt-urlltbasegtinsteadOf)
- [GitHub Docs: About Enterprise Managed Users](https://docs.github.com/en/enterprise-cloud@latest/admin/identity-and-access-management/understanding-iam-for-enterprises/about-enterprise-managed-users)
