---
title: Self-Hosted FOSS Alternatives to ActiveCollab
---

Comparison of self-hostable FOSS project management tools, evaluated for _rights/permissions management_, _work assignment_ and _collaborative project management_.

OpenProject, Redmine and Tuleap were ruled out (OpenProject: poor team fit; Redmine/Tuleap: excluded by request).

## Comparison

| Tool | License | Self-Host | SSO Integration | RBAC / Permissions | Assignment | Stack · Health | Project URL |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Plane** | AGPL-3.0 (advanced roles Enterprise-gated) | [Docker Compose + K8s](https://developers.plane.so/self-hosting/overview); 2 CPU/4 GB min | [Google/GitHub OAuth](https://developers.plane.so/self-hosting/govern/google-oauth) free ✅ · [OIDC](https://developers.plane.so/self-hosting/govern/oidc-sso)/[SAML](https://developers.plane.so/self-hosting/govern/saml-sso) **Pro/Business** 💰 · [LDAP](https://developers.plane.so/self-hosting/govern/ldap) **Enterprise** 💰 | Strongest — workspace/project/teamspace scopes, custom roles, permission schemes | Assignees, @mentions, sub-items, subscribers, inbox, email/push | TypeScript · 54k★ · v1.3.1 (2026-05) | [plane.so](https://plane.so) · [github.com/makeplane/plane](https://github.com/makeplane/plane) |
| **Leantime** | AGPLv3 ✅ | [Docker/Compose](https://docs.leantime.io/installation/system-requirements); PHP 8.2+, MySQL/MariaDB | [OIDC + LDAP/AD](https://docs.leantime.io/installation/authentication-configuration) free ✅ · [SAML paid plugin](https://marketplace.leantime.io/product/advanced-auth/) 💰 | 6 roles (Owner→Read-Only), per-project | Tasks, milestones, notifications, timesheets, Gantt | PHP · 10.7k★ · v3.9.8 (2026-07) | [leantime.io](https://leantime.io) · [github.com/Leantime/leantime](https://github.com/Leantime/leantime) |
| **Taiga** | MPL-2.0 ✅ | [Docker](https://docs.taiga.io/setup-production.html); PostgreSQL + RabbitMQ + NGINX | [GitHub/GitLab OAuth](https://docs.taiga.io/setup-production.html) free ✅ · [OIDC via plugin](https://github.com/taigaio/taiga-contrib-oidc-auth) · LDAP/SAML not official ⚠️ | Granular per-project agile roles (tasks/stories/issues/wiki) | Assign tasks/stories/issues, realtime board, webhooks | Python · 839★ · v6.10.1 (2026-05) | [taiga.io](https://taiga.io) · [github.com/taigaio/taiga-back](https://github.com/taigaio/taiga-back) |
| **Kanboard** | MIT ✅ | [Docker](https://docs.kanboard.org/v1/admin/docker/); SQLite/MariaDB/PostgreSQL | [LDAP/AD](https://docs.kanboard.org/v1/admin/ldap/) + [Google OAuth2 plugin](https://github.com/kanboard/plugin-google-auth) + [reverse-proxy](https://docs.kanboard.org/v1/plugins/authentication_providers/) free ✅ · OIDC/SAML not confirmed ⚠️ | App roles + project roles + custom project roles, group access | Assignee, comments, mentions, subtasks, time tracking | PHP · 9.7k★ · v1.2.52 (2026-04) | [kanboard.org](https://kanboard.org) · [github.com/kanboard/kanboard](https://github.com/kanboard/kanboard) |
| **Vikunja** | AGPLv3 ✅ | [Docker](https://vikunja.io/docs/full-docker-example/); PostgreSQL for larger installs | [OIDC](https://vikunja.io/docs/openid/) + [LDAP](https://vikunja.io/docs/ldap/) free ✅ · SAML/social only via OIDC IdP | Coarse — read-only / read-write / admin only | Multiple assignees, mentions, reminders, webhooks | Go · 4.7k★ · v2.3.0 (2026-04) | [vikunja.io](https://vikunja.io) · [github.com/go-vikunja/vikunja](https://github.com/go-vikunja/vikunja) |

**Legend:** ✅ free in self-hosted core · 💰 paid/Enterprise-gated · ⚠️ not confirmed in official docs

## SSO Takeaways

- **Plane's SSO is heavily paid-gated** — only social OAuth is free; real enterprise SSO (OIDC/SAML/LDAP) requires a paid plan. Combined with its Enterprise-gated advanced roles, the free self-hosted edition may be thinner than it first appears.
- **Leantime and Vikunja** give you _OIDC + LDAP_ free in core — the cleanest story if you run Keycloak/Authentik/Azure AD/Okta.
- **Taiga and Kanboard** cover the basics free but have gaps (no confirmed SAML; Taiga's OIDC needs a plugin).
- If your IdP speaks _OIDC_ (most do), **Leantime** and **Vikunja** are the friction-free choices — and between those two, Leantime wins on RBAC whilst Vikunja's permissions are too coarse for serious rights management.
