---
title: Unlocking SSH Key Passphrases Automatically with KDE Plasma
---

- **Context:** Manjaro Linux with KDE Plasma, passphrase-protected SSH keys, and a systemd user session (SDDM login manager)

## Problem Statement

Passphrase-protected SSH keys must be unlocked to be usable. A per-shell `ssh-agent` spawned from `~/.bashrc` only covers interactive terminals and never loads the keys, so:

- GUI applications and IDEs (e.g. Neovim's `vim.pack` plugin installer) run with no usable agent and either prompt on a non-existent TTY or fail outright with `Permission denied (publickey)`.
- The agent is bound to a shell session rather than the login session, so different terminals see different agents.
- Passphrases must be re-entered repeatedly instead of being cached for the session.

This is the natural follow-up to [SSH-Based Multi-Account GitHub Authentication](20260520-ssh-multi-account-github.md), which notes the agent is optional; here we make key unlocking convenient and tooling-independent.

**Requirements:**

- A single agent for the entire login session, visible to GUI apps and non-interactive tools alike
- Each passphrase entered at most once, via a native KDE dialog
- Passphrases remembered across reboots (stored encrypted in KWallet, auto-unlocked at login)

## Solution (Implemented)

Use the distribution's systemd user `ssh-agent.socket`, export `SSH_AUTH_SOCK` session-wide via `environment.d`, let SSH add keys on first use, and route passphrase prompts through `ksshaskpass` so they can be remembered in KWallet.

### 1. Enable the systemd user agent socket

Most distributions ship an `ssh-agent` user unit that is disabled by default:

```bash
systemctl --user enable --now ssh-agent.socket
```

This provides a stable socket at `${XDG_RUNTIME_DIR}/ssh-agent.socket` for the whole session. The bundled unit guards itself with `ConditionEnvironment=!SSH_AGENT_PID`, so any competing agent (see step 4) must be removed.

### 2. Export the socket and askpass helper session-wide

Create or edit `~/.config/environment.d/ssh_askpass.conf` so both GUI and shell processes agree on the agent and prompt helper:

```ini
# https://wiki.archlinux.org/title/KDE_Wallet#Using_the_KDE_Wallet_to_store_ssh_key_passphrases
SSH_AUTH_SOCK=${XDG_RUNTIME_DIR}/ssh-agent.socket
SSH_ASKPASS=/usr/bin/ksshaskpass
SSH_ASKPASS_REQUIRE=prefer
```

`SSH_ASKPASS_REQUIRE=prefer` is the critical value: a previous `never` forbids the graphical prompt, which is exactly what makes non-interactive clones (with no TTY) fail. `prefer` lets the KDE dialog appear even when there is no controlling terminal.

Files in `~/.config/environment.d/` are read by the systemd user manager and Plasma **at login** (alphabetical order, last file wins). Keep a single file for these variables to avoid one file silently overriding another.

### 3. Add keys to the agent on first use

Ensure `~/.ssh/config` has a global directive above any `Host` blocks:

```ssh-config
AddKeysToAgent yes
```

The first time a key is used, SSH adds it to the agent and caches it for the remainder of the session, so each passphrase is entered only once.

### 4. Remove any per-shell agent spawn

Delete or disable the old `~/.bashrc` (or `~/.zshrc`) block that spawns its own agent, e.g.:

```bash
# REMOVE - conflicts with the systemd ssh-agent.socket
if ! pgrep -u "$USER" ssh-agent > /dev/null; then
  ssh-agent > "$XDG_RUNTIME_DIR/ssh-agent.env"
fi
if [[ ! "$SSH_AUTH_SOCK" ]]; then
  source "$XDG_RUNTIME_DIR/ssh-agent.env" >/dev/null
fi
```

A shell-spawned agent sets `SSH_AGENT_PID`, which trips the unit's `ConditionEnvironment` guard and shadows the good socket.

### 5. Log out and back in

`environment.d` changes only take effect at login. After re-login, the first `git`/`ssh` operation to a host pops a `ksshaskpass` dialog. Enter the passphrase and **tick "Remember"** to store it in KWallet; subsequent uses are silent.

### Verification

```bash
# Should point at the systemd socket, not a shell-spawned agent
echo "$SSH_AUTH_SOCK"
# → /run/user/1000/ssh-agent.socket

systemctl --user is-enabled ssh-agent.socket   # → enabled
systemctl --user is-active  ssh-agent.socket   # → active

# Fresh agent responds but is empty until first use
ssh-add -l
# → The agent has no identities.

# First run: KDE prompt with "Remember"; afterwards silent
ssh -T git@github.com
# → Hi <username>! You've successfully authenticated ...
```

## How It Works

Three layers cooperate:

1. **systemd user socket:** `ssh-agent.socket` starts the agent on demand and exposes a fixed socket path for the login session, independent of any shell.
2. **`environment.d`:** exports `SSH_AUTH_SOCK` and the askpass helper into the session environment inherited by every process - GUI, shell and non-interactive tool.
3. **`AddKeysToAgent` + `ksshaskpass` + KWallet:** SSH loads a key on first use, `ksshaskpass` renders the passphrase prompt as a native dialog, and KWallet stores the passphrase encrypted. Because KWallet is auto-unlocked at login by PAM (`pam_kwallet` `auto_start` in the SDDM stack), remembered passphrases are available without any further prompt after reboot.

Since the agent lives at the session (not shell) layer, tools that never open a terminal - IDEs, Git GUIs, plugin managers - all authenticate transparently.

## Trade-offs

- **KWallet must auto-unlock.** Silent operation across reboots depends on KWallet being unlocked at login. If the SDDM PAM stack does not run `pam_kwallet` (or the wallet has a password differing from the login password), a wallet prompt will appear once per session.
- **`kwallet5` vs `kwalletd6` PAM mismatch.** Some distributions ship `pam_kwallet5.so` in the PAM stack whilst running `kwalletd6`. Unlock usually still works, but if remembered passphrases do not persist across reboots, install the KF6-matching `kwallet-pam` package and confirm the PAM module is referenced in `/etc/pam.d/sddm`.
- **Login-manager specific.** The auto-unlock path assumes SDDM. Other display managers (GDM, LightDM, LY) need their own PAM `pam_kwallet` integration or a different keyring.
- **First-use prompt remains.** Even with KWallet, the very first use of each key after enabling this shows one dialog (to capture and remember the passphrase).

## References

- [Arch Wiki: KDE Wallet - storing SSH key passphrases](https://wiki.archlinux.org/title/KDE_Wallet#Using_the_KDE_Wallet_to_store_ssh_key_passphrases)
- [Arch Wiki: SSH keys - ssh-agent](https://wiki.archlinux.org/title/SSH_keys#ssh-agent)
- [systemd: environment.d](https://www.freedesktop.org/software/systemd/man/latest/environment.d.html)
- [OpenSSH ssh_config: AddKeysToAgent](https://man.openbsd.org/ssh_config#AddKeysToAgent)
- [SSH-Based Multi-Account GitHub Authentication](20260520-ssh-multi-account-github.md) - companion entry on per-account key routing
