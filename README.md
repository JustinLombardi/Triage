# Triage

Diagnoses failed GitHub Actions checks: classifies a failure as a flaky test,
an infrastructure problem, a real bug, or a config/dependency issue, and
explains what happened in plain English.

**Stack:** FastAPI · React (Vite) · PostgreSQL · Redis/RQ · Docker Compose ·
Claude API · GitHub API

## Highlights

- **Two ways in:** paste a log in the web UI, or let a GitHub webhook trigger a
  diagnosis automatically for every failed job in a workflow run.
- **Asynchronous by design:** the API only records the request and queues it
  in Redis. A separate RQ worker fetches the log, runs the analysis, and
  writes the result to Postgres, so a slow LLM call never blocks the API.
- **Heuristics plus LLM:** a regex pre-scan (about 40 patterns across the four
  categories) gives Claude hints. If the model call fails or returns
  unparseable output, the pre-scan result is used instead, so no diagnosis is
  left stuck.
- **Structured, checkable output:** each diagnosis has a category, a 0–100
  confidence score, a root cause, a concrete next step, and evidence lines
  quoted verbatim from the log.
- **Webhook security:** GitHub deliveries are verified with HMAC-SHA256
  signatures before anything is queued.

**Status:** working prototype. In progress: turning the single-repo webhook
integration into an installable GitHub App for multi-repo and org use (see
"Known simplifications" below).

## Architecture

```
React (frontend, :5173)
        │  REST
        ↓
FastAPI (api, :8000)
        │
   ┌────┼────────────┐
   ↓    ↓             ↓
Postgres Redis    GitHub API
         │  (queue)
         ↓
       Worker (RQ)
        /      \
       ↓        ↓
   heuristics  Claude (Anthropic API)
```

- **React** — dashboard, paste-a-log form, diagnosis detail view. Polls the API.
- **FastAPI** — accepts pasted logs (`POST /api/diagnoses`) and GitHub webhook
  deliveries (`POST /api/webhooks/github`), writes a row to Postgres, and
  hands the diagnosis id to Redis. Never talks to Claude directly.
- **Postgres** — the `diagnoses` table: one row per check, its status
  (`pending` / `done` / `error`), and the result once it's ready.
- **Redis + RQ** — the queue between "a diagnosis was requested" and "a
  worker got around to it." Keeps the API fast even if the LLM call is slow.
- **Worker** — pulls a diagnosis id off the queue, fetches the log from
  GitHub if it doesn't have it yet, runs a local regex scan, calls Claude,
  and writes the result back to Postgres. This is the only thing that talks
  to Claude, and the only thing that needs `ANTHROPIC_API_KEY`.
- **GitHub API** — used two places: the API lists which jobs in a failed run
  actually failed (from the webhook payload), and the worker downloads the
  log text for a specific job.

## Two ways a diagnosis gets created

1. **Paste-based** (works today, no GitHub setup needed): open the frontend,
   go to "New diagnosis," paste a log. The API queues it immediately.
2. **GitHub webhook** (automatic, needs setup below): GitHub calls
   `/api/webhooks/github` on every completed workflow run. If it failed, the
   API looks up which jobs failed and queues one diagnosis per failed job.
   The worker fetches each job's log itself.

## Running it locally

```bash
cp .env.example .env
# edit .env: at minimum set ANTHROPIC_API_KEY. GITHUB_TOKEN and
# GITHUB_WEBHOOK_SECRET are only needed for the webhook path.
docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000 (docs at /docs)

## Setting up the GitHub webhook (optional)

1. Create a fine-grained personal access token with **Actions: Read-only**
   on the repos you want to triage. Put it in `GITHUB_TOKEN`.
2. Pick a webhook secret and put it in `GITHUB_WEBHOOK_SECRET`.
3. Expose your local API to the internet for testing (e.g. `ngrok http 8000`),
   or deploy the `api` service somewhere reachable.
4. In the repo's Settings → Webhooks → Add webhook:
   - Payload URL: `https://<your-host>/api/webhooks/github`
   - Content type: `application/json`
   - Secret: the same value as `GITHUB_WEBHOOK_SECRET`
   - Events: select "Workflow runs" only

For multiple repos or an org, a GitHub App (rather than a personal token)
is the better long-term fit — it scopes access per-repo and doesn't ride on
one person's account. The webhook handling and log-fetching code here would
stay basically the same; only the auth (`GITHUB_TOKEN`) would change to an
installation token you refresh periodically.

## Known simplifications, worth fixing before this is a real service

- **No migrations.** Tables are created with `Base.metadata.create_all()` on
  API startup. Fine for a prototype; add Alembic before the schema needs to
  change without wiping data.
- **The `Diagnosis` model is duplicated** between `api/app/models.py` and
  `worker/models.py` because they're separate Docker build contexts. Pull
  both into a shared package (e.g. `pip install -e ../core` in both
  Dockerfiles) once this grows past a prototype.
- **No auth on the API or frontend.** Anyone who can reach `:8000` can create
  diagnoses and read all of them. Add an auth layer before deploying this
  anywhere reachable from outside your team.
- **Webhook signature checking is the only security boundary** on the
  GitHub-facing endpoint — don't remove `verify_signature`.
- **One flat `diagnoses` table**, no per-repo/per-org scoping. Fine for a
  single team; add a `projects` table with access control before this is
  multi-tenant.
- **The regex heuristics are a starting set** (`worker/heuristics.py`).
  They're there to give Claude a hint and to provide a fallback if the LLM
  call fails — extend them as you see which signals actually show up in your
  logs.
