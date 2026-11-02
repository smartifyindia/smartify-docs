# Deployment

Production is published by the existing Cloudflare Workers Builds Git integration.
Do not deploy from a local machine or add a second production deploy workflow.

- Pushes and pull requests run GitHub Actions `CI / Validate` on Node 22 and Python 3.12.
- `npm run ci` runs generator safety tests, builds the full OpenNext Worker, and checks TypeScript.
- Main requires up-to-date passing `Validate` and `Workers Builds: smartify-docs` checks, a pull request, and resolved review conversations. Force pushes and deletion are blocked, including for admins.
- Cloudflare production branch: `main`; build command: `npm run ci`; deploy command: `npx wrangler deploy`.
- Non-production branches build and upload versions using `npx wrangler versions upload`; they do not publish production.
- A failed Cloudflare build stops before deployment, preserving the current production version.
- No manual approval is required after a passing merge. GitHub Actions needs no deployment credentials; Cloudflare holds the existing build token.

Use Node 22 locally (`nvm use`) and `npm ci && npm run ci` before pushing.
Cloudflare build variables pin `NODE_VERSION=22` and `PYTHON_VERSION=3.12`.

After merging, verify the Cloudflare build status and deployed commit in the Deployments tab before calling the release live.
The custom domain is `docs.smartify.in`; `workers_dev: false` disables the public workers.dev alias.
