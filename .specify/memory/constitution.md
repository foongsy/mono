<!--
Sync Impact Report
- Version change: (unset/template) → 1.0.0
- Modified principles: N/A (initial ratification; template placeholders replaced)
- Added sections:
  - Core Principles I–X (ten decision-ready principles)
  - Domain Grounding
  - Review Checklist
  - Governance
- Removed sections: N/A (placeholder scaffold only)
- Follow-up TODOs: none
-->

# mono Constitution

## Core Principles

### I. Do Not Distribute by Default

**Rationale**: Coordination cost dominates runtime cost. Every new process,
service, or queue multiplies failure modes, ownership boundaries, and round
trips. Vertical scaling and a single deployable keep the working set and the
mental model co-located until a concrete force demands otherwise.

**Rule**: The default topology is one deployable scaled vertically. A PR that
adds a new process, service, queue, or network hop MUST include a written
justification naming exactly one of: working-set overflow, genuinely
independent compute, geographic latency, or organizational independence.
Justifications framed only in latency milliseconds, "best practice," or future
scale speculation are REJECTED.

**How To Apply**:
- Reject new microservices, sidecars, or message buses without the justification
  above attached to the PR or design note.
- Prefer threads, in-process modules, and local function calls over RPC.
- Measure coordination in round trips and ownership handoffs, not wall-clock
  microseconds alone.
- Split only when the named force is evidenced (OOM/working-set metrics,
  independent scaling curves, multi-region RTT requirements, or separate team
  deploy cadences).

### II. Optimize for Deletion, Not Extension

**Rationale**: The cheapest correct design is one an engineer can throw away.
Speculative abstractions and premature frameworks raise the cost of change
faster than they reduce duplication. Deletion capacity is the real modularity
metric.

**Rule**: A module MUST be small enough that one engineer can delete and rewrite
it in a day. Speculative abstractions (interfaces, base classes, plugin systems,
"future-proof" indirection) with fewer than three concrete call sites are
FORBIDDEN. Inline until it hurts; extract only after the third duplication or
when a clear boundary is forced by Principle I or IV.

**How To Apply**:
- In review, ask: "Could one person rewrite this module in a day?" If no, split
  or simplify before merge.
- Reject PRs that introduce an abstraction for a single implementation.
- Prefer duplication of fewer than three occurrences over a shared helper of
  unclear ownership.
- When extracting, extract the smallest sealed unit with a clear delete story.

### III. Make Dependencies Explicit

**Rationale**: Hidden coupling and import-time side effects make behavior
unverifiable from the text of a change. Reviewers cannot validate Principle V
or VII against invisible globals.

**Rule**: No hidden coupling, no implicit global state, no import-time side
effects. Every dependency of a function MUST be visible in its signature or at
the top of its file. Dependency injection MUST be used instead of singletons
for anything with external effects (I/O, clocks, randomness, config, feature
flags).

**How To Apply**:
- Reject module-level mutable state used as an implicit service locator.
- Reject imports that open connections, start threads, or read env at import
  time.
- Constructors and factory functions take collaborators as parameters; call
  sites wire them explicitly.
- A reader unfamiliar with the codebase MUST be able to list a function's
  dependencies without searching other files for ambient context.

### IV. Contract at the Boundary, Not in the Middle

**Rationale**: Semantic drift between producers and consumers is inevitable.
Versioned schemas at boundaries localize reconciliation; shared mutable schemas
in the middle spread breakage across the graph.

**Rule**: Every producer/consumer boundary (HTTP, queue, file, database, RPC)
MUST have a schema with an explicit version. Semantic reconciliation happens at
the boundary and is owned by the side that understands both contexts. Shared
mutable schemas (a single evolving type owned by everyone) are FORBIDDEN.

**How To Apply**:
- Require schema + version for new API endpoints, queue messages, file formats,
  and DB public contracts in the same PR that introduces the boundary.
- Reject PRs that change a shared DTO "in place" without a version bump and
  compatibility plan.
- Prefer expand-then-contract (Principle VII) when evolving boundary schemas.
- Internal pure functions need no versioned schema; boundaries do.

### V. Test the Transformation, Not the Plumbing

**Rationale**: Tests that assert framework wiring prove nothing about business
correctness. Coverage of owned logic and real boundaries catches the bugs that
survive review; mocks of owned code hide them.

**Rule**: Unit tests MUST cover pure transformation logic. Integration tests
MUST cover boundaries (Principle IV). Do not mock what you own; do mock what
you do not. A PR that fixes a bug MUST include a failing test that reproduces
the bug before the fix; a green CI without that test is NOT green for that PR.

**How To Apply**:
- Place business rules in pure functions and unit-test those.
- Integration-test HTTP/queue/DB/file adapters against real or containerized
  dependencies where practical.
- Reject mocks of first-party modules under the same ownership boundary.
- Block merge of bugfix PRs that lack a regression test that failed before
  the fix.

### VI. Emit Structured Events, Derive Everything Else

**Rationale**: Logs, metrics, and traces that are authored separately diverge.
One structured event primitive keeps observability coherent and queryable.
Unstructured lines cannot be joined to user-visible symptoms (Principle VIII).

**Rule**: Logs, metrics, and traces are projections of one primitive: the
structured event. High-cardinality fields (user id, request id, tenant id,
feature flag state) are REQUIRED on events that touch a request or tenant path.
Unstructured log lines in new code are FORBIDDEN.

**How To Apply**:
- Reject `print`/`console.log` string concatenation and free-form log messages
  without a structured payload in new or modified code paths.
- Require request id (and user/tenant id when applicable) on events emitted
  along a request path.
- Derive dashboards and alerts from event fields; do not invent parallel metric
  names that cannot join back to events.
- Prefer a single event schema library over ad-hoc logger calls.

### VII. Recovery over Prevention

**Rationale**: Prevention fails under novelty. The operational contract is
revertibility: users are protected by fast undo, not by perfect foresight.

**Rule**: Every change MUST be revertible in under five minutes without a code
change. Feature flags MUST gate risky paths. Schema and data migrations MUST
follow expand-then-contract. Rollback MUST be exercised as part of the deploy
procedure, not assumed.

**How To Apply**:
- Reject deploys that can only be undone by a hotfix commit.
- Require feature flags for behavior that is uncertain, gradual, or
  high-blast-radius.
- Split breaking migrations: expand (compatible) → dual-write/read → contract
  (remove old) across separate deploys.
- Document and periodically run the rollback path; a deploy checklist that
  omits rollback verification is incomplete.

### VIII. Attention Is Finite

**Rationale**: Noise trains people to ignore signals. Alerts without
user-visible symptoms and runbooks consume the same attention budget as real
incidents.

**Rule**: Every alert MUST correspond to a user-visible symptom and a runbook
link. Dashboards are saved queries, not decoration. Signals that have not fired
a useful page in 90 days MUST be deleted or downgraded out of paging.

**How To Apply**:
- Reject new paging alerts that lack a symptom statement and runbook URL in the
  same change.
- Prefer joining structured events (Principle VI) over vanity charts.
- Schedule a 90-day review; delete unused alerts/dashboards in the same PR
  that adds capacity elsewhere when possible.
- "Interesting to look at" is not a justification for a dashboard panel.

### IX. Value Is Realized at the User, Not at Merge

**Rationale**: Merge is a git event. Value and risk land when users exercise
the change under observation. Calling a merged PR "shipped" hides incomplete
work.

**Rule**: A PR is not done until the change is in users' hands, observable
(Principle VI), and revertible (Principle VII). "Shipped" means deployed,
instrumented, and monitored — not merged.

**How To Apply**:
- Definition of done for feature work: deployed to the target environment,
  events/metrics present, rollback path known.
- Reject "follow-up PR for instrumentation" as a substitute for shipping
  observability with the feature.
- Status updates say "deployed" or "merged (not shipped)" — never equate merge
  with ship.
- Canaries and staged rollouts count toward shipped only for the cohorts that
  received the change.

### X. Commands Are Discoverable; Local Dev Matches CI

**Rationale**: Hidden arguments and CI-only steps create a permanent
works-on-my-machine gap. A single named command surface is the contract between
humans and automation.

**Rule**: Every repeatable action (build, test, lint, migrate, deploy, seed)
MUST be a single named command listed in one place and runnable with no hidden
arguments. The command a developer runs locally MUST be the same command CI
runs. CI-only shell steps, undocumented makefile targets, and ambient env
requirements not declared beside the command list are FORBIDDEN. If a new
contributor cannot list every project command in 30 seconds from that one
place, the interface is broken.

**How To Apply**:
- Maintain one command index (e.g., root `Makefile`, `justfile`, or `package.json`
  scripts — pick one primary surface) that lists build/test/lint/migrate/deploy/seed.
- CI workflows MUST invoke those named commands, not inline duplicate scripts.
- Reject PRs that add CI steps without updating the local command surface.
- Document required tools next to the command list; do not rely on tribal
  knowledge.

## Domain Grounding

These principles are first-principles constraints across five domains. Use the
mapping in review when a change sits on a domain boundary:

| Domain | Primary principles |
| --- | --- |
| Distributed systems | I, IV, VII |
| Software design | II, III, V |
| Data engineering | IV, V, VII |
| DevOps | VII, IX, X |
| Observability | VI, VIII, IX |

A change may touch multiple domains; the stricter applicable rule wins.

## Review Checklist

Reviewers MUST be able to point at a diff and name a violated principle without
interpretation. Use this checklist on every PR:

1. New process/service/queue? → written force from Principle I, or reject.
2. New abstraction with <3 call sites? → reject (II).
3. Hidden globals, import-time I/O, or invisible deps? → reject (III).
4. Boundary without versioned schema? → reject (IV).
5. Bug fix without regression test; mocks of owned code? → reject (V).
6. New unstructured logs; missing required event fields? → reject (VI).
7. Not revertible in <5 minutes without a code change? → reject (VII).
8. New page without symptom + runbook? → reject (VIII).
9. Claiming "shipped" at merge without deploy/instrument/monitor? → reject (IX).
10. New CI-only or undocumented command path? → reject (X).

## Governance

This constitution supersedes informal practice, style preferences, and
"industry defaults" when they conflict. Ambiguity is resolved in favor of the
more restrictive principle.

**Amendments**:
- Propose changes as a PR that edits only `.specify/memory/constitution.md`
  (unless a follow-up Spec Kit command is explicitly run).
- Include an updated Sync Impact Report, version bump, and rationale.
- Amendments require review approval like any other governance change.

**Versioning**:
- MAJOR: remove or redefine a principle incompatibly.
- MINOR: add a principle/section or materially expand guidance.
- PATCH: clarifications, wording, non-semantic refinements.

**Compliance**:
- All PRs and reviews MUST verify applicable principles using the Review
  Checklist.
- Exceptions require a time-bounded waiver in the PR description naming the
  principle, the reason, and the removal date of the waiver.
- Complexity and distribution MUST be justified under Principle I and II; silence
  is non-compliance.

**Version**: 1.0.0 | **Ratified**: 2026-08-12 | **Last Amended**: 2026-08-12
