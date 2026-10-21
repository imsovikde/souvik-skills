# Differential Call-Graph and Blast-Radius Audit Reference

This reference defines the technical execution rules for Pass 2 (Differential Line-Deletion and Boundary Validation Audit) and cross-file blast-radius traversal modeled on the CodeRabbit Multi-Stage Review Architecture.

## 1. The 4-Stage Differential Review Pipeline

Execute differential reviews across four isolated analytical stages before emitting findings:

### Stage A: Triage and Protected Path Lock

Enumerate all modified, added, renamed, and deleted files in the target diff (`git diff --name-status <base>...<head>`).
Verify that designated zero-touch paths (such as OAuth 2.1 token endpoints, cryptographic verifiers, or production deployment manifests) have an exact 0-byte diff. If any protected file is touched without explicit authorization, raise an immediate P0 BLOCKER.

### Stage B: AST Symbol Graph and Blast-Radius Construction

For every modified symbol (function, class, type alias, Zod schema, database table definition, or error constant), identify:
- **Upstream Callers:** Every route handler, MCP tool callback, background worker, or CLI command that invokes the symbol directly or transitively.
- **Downstream Callees:** Every repository method, external SDK call, or serializer invoked by the modified code.
- **Sibling Contract Peers:** Other handlers or adapters implementing the same interface or sharing the same output schema.

### Stage C: Ordered Inspection Sequence

Never inspect files in alphabetical order. Inspect in strict dependency order:
1. Governance and invariant specifications (`AGENTS.md`, `INVARIANTS.md`, protocol specs)
2. Data models, database migrations, and Zod/JSON schemas
3. Repository and persistence adapters
4. Domain state machines and service logic
5. Entry boundary controllers, HTTP routes, and MCP tool handlers
6. Integration and unit test suites

### Stage D: Disconfirming-Evidence Verification Filter

Before reporting any candidate bug, actively search the codebase for disconfirming evidence (such as an upstream middleware guard, a database trigger, or a wrapper sanitizer) that prevents the bug from occurring at runtime. Drop any theoretical finding that cannot be triggered through a realistic execution path. Report only verified defects with a concrete trigger trace.

## 2. Differential Line-Deletion (-) Audit Checklist

Removed lines (-) in a diff frequently cause silent regressions because reviewers focus only on added lines (+). Audit every removed line against these six checks:

| Check ID | Deleted Code Pattern | Regression Risk | Verification Action |
| :--- | :--- | :--- | :--- |
| DEL-01 | Input schema .refine(), .superRefine(), .min(), .max(), .regex(), or .strict() | Unvalidated or malformed payloads enter domain logic | Verify equivalent or stricter validation exists at the entry boundary |
| DEL-02 | Repository schema.safeParse(row) or output validation gate | Corrupted database rows or partial joins leak to callers | Confirm outbound data is still validated before leaving persistence |
| DEL-03 | WHERE owner_id = $1 or tenant filter predicate | Cross-tenant data exposure (P0 BLOCKER) | Trace every query path to confirm composite tenant isolation |
| DEL-04 | if (existing.deletedAt) or active-state filter | Soft-deleted or archived entities resurface in active lookups | Verify state-machine filter predicates remain enforced |
| DEL-05 | try / catch error mapping or transaction rollback | Partial writes persist on failure or raw driver errors leak | Confirm atomic transaction boundaries and error sanitization |
| DEL-06 | await client.listTools() or test assertion lines | Test suite passes trivially by removing the failing check | Flag as epistemic reward-hacking (P0 BLOCKER) |

## 3. Cross-File Call-Graph Traversal Protocol

When a function signature, return type, or error throw changes in File A, trace every caller in Files B, C, and D:

### 3.1 Return Type Narrowing or Widening

If a repository method changes from throwing `NotFoundError` to returning `null`, inspect every caller to ensure `null` is explicitly handled and does not dereference properties or return an empty success object.

### 3.2 Default Parameter Mutation

Check whether default parameters (for example, `includeArchived = false` changed to `includeArchived = true` or `parentId = null`) alter behavior for existing callers that omit the optional argument.

### 3.3 Shared Object Reference Mutation

Trace any object passed by reference across middleware or schema normalizers. If a helper mutates its input object in place (such as deleting `$schema` or `additionalProperties`), verify it clones the input first via `structuredClone()` so concurrent requests or alternative clients are unaffected.

### 3.4 Dead Code and Unwired Helpers

For every newly exported function, class, or constant in the diff, grep the entire repository for call sites outside `tests/`. If a helper is exported from `src/utils/` but has zero callers in production code, flag as an unwired cosmetic implementation (P1 CRITICAL).

## 4. Cross-Boundary Data Flow Auditing

Modern applications span multiple distinct architectural layers:

```
External HTTP / Webhook / RPC Boundary
       |
Input Validation Layer (Zod / Pydantic / SafeParse)
       |
Domain Service Layer (Business Rules & Transactions)
       |
Persistence Layer (ORM / SQL Query / KV Store)
       |
Outbound Serialization Layer (Response DTO & Masking)
```

### Defense-in-Depth Verification

Data must be validated at every boundary it crosses:
- **Entry Boundary:** Coerce strings, strip unknown keys, validate formats and length limits.
- **Domain Boundary:** Enforce business state preconditions (such as "order cannot be cancelled once shipped").
- **Persistence Boundary:** Scope queries to tenant ID, enforce unique constraints, and check optimistic concurrency locks.
- **Serialization Boundary:** Strip sensitive fields (passwords, internal IDs, foreign tenant metadata) before transmitting payloads.

If a bug is found at the persistence layer, do not merely patch the SQL query. Enforce validation across all upstream layers to guarantee defense-in-depth.

## 5. AST-Guided Symbol Impact Matrix

When a high-impact symbol changes (a shared schema, a base class, or a central utility), construct a formal impact matrix before proposing any fix:

| Symbol | Change Type | Upstream Callers Affected | Downstream Callees Affected | Risk Classification |
| :--- | :--- | :--- | :--- | :--- |
| `parseItemId(id)` | Return type widened to `string \| null` | All 8 callers in `routes/` and `services/` | `itemRepository.findById()` | P1 CRITICAL - callers must null-guard |
| `ItemSchema` | Required field `ownerId` added | All 3 create-flow callers | Prisma `item.create()` | P0 BLOCKER - missing field crashes persist layer |

Populate this matrix for every symbol with a fan-out of 3 or more callers before concluding Stage 1 analysis.
