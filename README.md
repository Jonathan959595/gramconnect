# GRAMCONNECT — Village Civic Assistance Workspace

GRAMCONNECT is a full workflow prototype for village civic assistance. It demonstrates private WhatsApp-style resident conversation, Telugu/English issue capture, deterministic complaint intelligence, administrator case management, dispatch/audit controls, electricity-outage verification, consent-aware notification workflow, and operational analytics.

## What works now

- Private resident reporting with structured landmark follow-up.
- Deterministic Telugu/English classification for drainage, electricity, water, roads, streetlights and sanitation.
- Complaint ID generation, priority and routing suggestions, duplicate-review cue, status lifecycle, department assignment, and audit trail.
- Dispatch gate that blocks a case without sharing consent, plus a clearly marked simulated dispatch reference.
- Outage draft → verification → opt-in audience matching → simulated alert → closure workflow.
- Resident communication preferences and consent controls.
- Dashboard and analytics that recalculate from the browser-local dataset.

## Honest operating mode

The app starts in **simulation mode**. All seeded residents, contact fragments, cases, alerts, and metrics are fictional. New records are stored only in the present browser using local storage. The app does not contact residents, WhatsApp, Spandana/PGRS, DISCOMs, or official systems.

Never represent sample records, simulated dispatch references, or simulated notifications as real activity. Production integrations require documented authorisation, consent, provider accounts, secure configuration, and operational ownership.

## Run locally

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`. Use **Reset sample data** to restart a demonstration.

```powershell
npm run test
```

## Suggested evaluator demo (5 minutes)

1. **Overview:** Explain the safeguards: consent, complete information, approved route, and recorded handoff.
2. **Resident inbox:** Type a Telugu or English report, analyse it, provide a landmark, generate the summary, and confirm the case.
3. **Case management:** Show the case lifecycle, suggested department, audit trail, consent gate, and simulated dispatch. A simulation reference is not a government case number.
4. **Power alerts:** Create a draft, verify it, and simulate the opt-in alert. No message/call is sent.
5. **Residents & consent / Analytics:** Explain that all records and metrics are current browser-local demonstration data.
6. **Integrations:** Distinguish implemented workflow, adapter-ready components, and formally-authorised external integrations.

## Deploy to Vercel

1. Push this folder to a Git repository.
2. Import it in Vercel; it detects Next.js automatically.
3. Use build command `npm run build`.
4. No environment variables are needed for the current simulation build.

For production, replace browser-local storage with Vercel Postgres, Neon, or Supabase and add server-side endpoints. Do not expose credentials in the browser, repository, terminal output, or chat.

## Required before collecting real data

| Area | Required work |
| --- | --- |
| Identity | Administrator sign-in, roles, access review |
| Data | Managed database, backups, retention/deletion process |
| Security | Server validation, rate limits, sessions, audit retention, media scanning |
| WhatsApp | Approved Meta Business account, webhook, opt-ins, approved templates |
| Notifications | Provider agreement, consent/opt-out, delivery receipts |
| Authority routing | Written route/owner and genuine external reference capture |
| Power data | DISCOM or authorised field-officer process |
| Operations | Named reviewers, escalation rules, SLA, privacy notice |

## Architecture boundary

```text
Resident (private WhatsApp-style UI) → intake/rules engine → case lifecycle
                                                      → administrator review
                                                      → approved authority adapter (future)

Verified outage source → human verification → consent filter → notification adapter (future)
```
