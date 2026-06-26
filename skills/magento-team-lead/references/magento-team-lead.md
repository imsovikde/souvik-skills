# Magento Team Lead Reference

Use this reference for substantial Magento Open Source or Adobe Commerce work: architecture decisions, module reviews, debugging plans, release readiness, team coordination, API design, or high-risk changes.

## Lead Intake

Capture these facts before making decisions:

- Product: Magento Open Source or Adobe Commerce.
- Version and PHP version.
- Hosting model: on-prem, Adobe Commerce Cloud, containerized, or custom platform.
- Storefront: Luma, custom theme, Hyva, PWA Studio, headless, or another stack.
- Scope: backend PHP, admin UI, frontend theme, checkout, catalog, pricing, inventory, payment, shipping, GraphQL, REST, integrations, cron, indexing, cache, deployment, or data migration.
- Release pressure: hotfix, sprint work, migration, upgrade, incident, or launch readiness.
- Constraints: third-party modules, SaaS services, ERP/PIM/OMS/payment dependencies, compliance, performance targets, and rollback expectations.

## Architecture Decision Rules

- Prefer documented extension points before overrides: service contracts, plugins, observers/events, extension attributes, UI components, layout XML, web APIs, GraphQL resolvers, declarative schema, and configuration.
- Avoid core and vendor edits. If legacy code already edits core or vendor files, plan a migration path into a custom module or composer patch with explicit ownership.
- Use dependency injection through constructors. Do not inject or call the object manager directly except in narrowly justified factories or integration-test setup.
- Use interfaces and service contracts where the dependency is a public API. Keep direct model/resource-model use local and deliberate.
- Choose plugins for targeted public method interception when ordering and side effects are clear.
- Choose observers for event-driven reactions where the event payload is stable and the reaction is naturally decoupled.
- Avoid broad class preferences unless replacing an implementation is intentional, documented, and conflict-reviewed.
- Keep module dependencies explicit in `composer.json` and `etc/module.xml`; depend on the specific modules whose public APIs or customization points are used.
- Keep setup/data changes declarative and repeatable. Plan data patches and schema patches with rollback and idempotency in mind.

## Code Review Checklist

Review Magento changes through these gates:

- Module shape: registration, composer metadata, `module.xml`, dependency declarations, area-specific config, and file placement are correct.
- DI: constructor dependencies are necessary, typed, stable, and not excessively broad; proxies/factories are used for expensive or dynamic dependencies.
- Plugins/observers: target methods or events are documented, sort order is intentional, and side effects are limited.
- APIs: REST/SOAP admin integrations and GraphQL storefront flows use the right boundary; customer/cart/order identifiers are derived from auth context where required.
- Templates: output is escaped with the right escaper method; translations wrap human-visible strings; no secrets or debug output leak.
- Performance: no accidental full collection loads, repeated repository calls in loops, avoidable cache misses, unbounded GraphQL nesting work, or unnecessary session access.
- Security: ACL, CSRF/form keys, input validation, authorization, error masking, file upload validation, and token handling are covered.
- Compatibility: change is upgrade-safe, PHP-version-safe, cache/indexer-aware, and compatible with known third-party modules.
- Tests: add or update focused unit, integration, web API, GraphQL, MFTF, or frontend tests according to the risk surface.

## Debugging Workflow

1. Reproduce with the smallest scenario and record area, store view, customer group, currency, and environment.
2. Check logs, exception reports, browser network data, queue consumers, cron status, cache state, indexer state, and integration service health.
3. Trace the Magento boundary: request route, controller/resolver/API service, service contract, model/resource model, plugin chain, observer chain, cache, indexer, and rendered output.
4. Compare local/staging/production config carefully: `app/etc/env.php`, config paths, module status, generated code, deployed static content, Composer lock, and environment variables.
5. Fix the smallest owned layer and add a regression test or documented verification step.
6. Close with root cause, blast radius, verification, rollback, and follow-up hardening.

## Release Readiness

Before merge or deployment, confirm:

- `composer install` or update path is understood and lockfile changes are intentional.
- Module enablement, `setup:upgrade`, DI compilation, static content deployment, cache flush/warmup, indexer mode, cron, queues, and config import are accounted for.
- Database patches are idempotent and safe for the target data volume.
- Feature flags, configuration defaults, admin instructions, and rollback steps are documented.
- QA covers admin workflows, storefront workflows, checkout/payment/shipping, search, customer account flows, and affected integrations.
- Monitoring is ready for errors, slow queries, queue backlog, cache churn, failed crons, and conversion-impacting storefront symptoms.

## Team Lead Behaviors

- Turn vague requests into acceptance criteria and explicit non-goals.
- Split large work into architecture, implementation, QA, DevOps, and release tasks.
- Ask for missing production-critical facts early, but continue with safe assumptions for low-risk local work.
- Prefer file-level review comments and concrete commands over generic advice.
- Name tradeoffs clearly: upgrade safety, delivery speed, extension conflict risk, performance, and test cost.
- Leave a handoff that a Magento developer, QA engineer, or release manager can follow without another meeting.
