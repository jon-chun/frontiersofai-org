# Manual — Auto-deploy the `website/` subfolder to Netlify

**Date:** 2026-08-25 (revised)
**Goal:** every push to `main` in `github.com/jon-chun/programminghumanity-org`
that touches `website/**` automatically deploys the `website/` directory (the
self-contained Fall 2026 site) to Netlify. Pushes that don't touch `website/`
deploy nothing.
**Time required:** ~10 minutes one-time setup.

The `website/` directory is a pure static site (no build step, own `css/` and
`images/`). Netlify's Git integration supports deploying a **subfolder** of a
repo natively via its *base directory* setting — no GitHub Action, no tokens,
no secrets needed. That is the recommended path (Part 1). A GitHub Actions
alternative is kept in the Appendix for cases where you want CI-controlled
deploys.

> **Import or upload?** At https://app.netlify.com/start you **import the Git
> repository** (the whole repo — that's the only granularity Netlify links).
> You then point Netlify at the subfolder with **Base directory = `website`**.
> Do NOT drag-and-drop the local `website/` folder: manual uploads create a
> disconnected site that never updates on push, which defeats the goal.

---

## Part 1 — Create the site by importing the repo (one time)

1. Sign in at https://app.netlify.com (free tier is fine for this site).
2. Go to https://app.netlify.com/start → **Import an existing project** →
   **Deploy with GitHub**.
3. Authorize the Netlify GitHub App. When asked which repositories it may
   access, grant **only** `jon-chun/programminghumanity-org` (least
   privilege — you can add repos later).
4. Select `jon-chun/programminghumanity-org`. On the **site settings** screen:

   | Setting | Value |
   |---|---|
   | Branch to deploy | `main` |
   | Base directory | `website` |
   | Build command | *(leave empty — nothing to build)* |
   | Publish directory | `website` |

5. Click **Deploy**. The first deploy runs immediately (~30 s).
6. Rename the site: **Site configuration → Site details → Change site name**
   → `programminghumanity` → your URL becomes
   `https://programminghumanity.netlify.app`.

Notes on why this is sufficient:
- **Subfolder publish:** with Base directory = `website`, Netlify publishes
  only that folder's contents as the site root (`website/index.html` → `/`).
- **Subfolder-triggered deploys:** when a base directory is set, Netlify's
  default build-ignore rule skips the deploy if the push changed nothing
  under `website/` — the commit shows as a "Skipped" deploy, not a new
  publish. Blog edits, archive work, and dev-doc commits cost nothing.
- **No credentials to manage:** the Netlify GitHub App handles auth; there is
  no personal access token and nothing stored in GitHub secrets.

## Part 2 — Verify the pipeline

1. Make a trivial change, e.g. edit a comment in `website/index.html`, commit,
   push to `main`.
2. Netlify → **Deploys** tab: a new deploy appears within seconds and goes
   live in ~30 s.
3. Open `https://programminghumanity.netlify.app` — confirm the change is
   live (hard-refresh: Cmd+Shift+R).
4. Now push a commit that does NOT touch `website/` (e.g. a `dev/` doc edit)
   and confirm the Deploys tab shows it **skipped**.

## Part 3 — Optional hardening & niceties

- **Custom domain:** Site configuration → Domain management → Add domain
  (e.g. `programminghumanity.org`) → follow the DNS instructions (CNAME to
  `programminghumanity.netlify.app` or Netlify DNS). HTTPS cert is automatic.
- **Deploy previews:** the Git integration gives you preview URLs on pull
  requests automatically (Site configuration → Build & deploy → Deploy
  Previews). For a solo trunk-based workflow this rarely fires, but costs
  nothing.
- **Lock deploys to `main`:** Site configuration → Build & deploy → Branches:
  production branch `main`, branch deploys **None** — stray branches pushed
  to origin then never deploy.
- **Rollback:** Netlify → Deploys → pick any previous deploy → **Publish
  deploy**. Instant, no git involvement.
- **404 page:** add `website/404.html`; Netlify serves it automatically.
- **Headers/redirects:** add a `website/_headers` or `website/_redirects` file
  (plain text, documented at docs.netlify.com) — they deploy with the site.

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| Deploy shows whole repo / wrong root | Base or Publish directory not `website` → Site configuration → Build & deploy → Build settings |
| Push to `main` deployed nothing | Push didn't touch `website/**` (deploy is "Skipped" by design) → check the Deploys tab entry |
| Repo not listed at /start | Netlify GitHub App wasn't granted access to it → GitHub → Settings → Applications → Netlify → Repository access |
| Site stopped updating on push | Repo was renamed/moved and the link broke → Site configuration → Build & deploy → **Link to a different repository** |
| Old CSS after deploy | Browser cache → hard-refresh; Netlify serves fresh assets by default |

---

## Appendix — Alternative: deploy from GitHub Actions instead

Use this only if you want deploys under CI control (e.g. run the pytest suite
as a gate before publishing). Trade-off: you take on a personal access token,
two GitHub secrets, and a workflow file that the native integration doesn't
need. **Never run both systems** — if the site was created via Part 1, first
unlink the repo (Site configuration → Build & deploy → unlink repository).

1. Create the site without Git linkage:
   ```bash
   npm install -g netlify-cli
   netlify login                          # opens browser for auth
   cd ~/code/programminghumanity-org
   netlify sites:create --name programminghumanity
   netlify deploy --prod --dir website --site programminghumanity
   ```
   `netlify sites:create` prints the **Site ID**.
2. Create a token at https://app.netlify.com/user/applications →
   **Personal access tokens → New access token** → name it
   `gh-actions-programminghumanity` → copy it (shown once).
3. Add both as repo secrets (each command prompts for the value on stdin):
   ```bash
   gh secret set NETLIFY_AUTH_TOKEN --repo jon-chun/programminghumanity-org
   gh secret set NETLIFY_SITE_ID    --repo jon-chun/programminghumanity-org
   ```
4. Only after the secrets exist, add `.github/workflows/deploy-netlify.yml`
   (uses the official Netlify CLI — no third-party action holding the token):

   ```yaml
   name: Deploy website/ to Netlify

   on:
     push:
       branches: [main]
       paths:
         - "website/**"          # only deploy when the live site changes
     workflow_dispatch: {}        # manual "Run workflow" button as a fallback

   concurrency:
     group: netlify-deploy
     cancel-in-progress: true     # a newer push supersedes an in-flight deploy

   jobs:
     deploy:
       runs-on: ubuntu-latest
       timeout-minutes: 5
       steps:
         - uses: actions/checkout@v4
         - run: npx netlify-cli deploy --prod --dir=website --message "GH Actions deploy: ${{ github.sha }}"
           env:
             NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
             NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
   ```
5. Verify as in Part 2; failed runs appear at
   `https://github.com/jon-chun/programminghumanity-org/actions`
   (`Not authorized` → token secret wrong; `Site not found` → Site ID wrong).
