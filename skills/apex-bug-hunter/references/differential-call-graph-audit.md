# Differential Call-Graph Audit and Blast-Radius Traversal

Comprehensive guide for AST-based call graph construction, differential line-deletion (-) analysis, and cross-file blast-radius traversal.

## 1. Architectural Philosophy: Beyond Flat Diffs

Standard code review tools treat pull requests as flat, line-by-line textual diffs. This approach fails to detect regressions because code changes propagate along functional, type, and data dependencies that are invisible in isolated hunks.

When a function signature, return type, or internal invariant changes:
- Callers multiple layers above the diff may pass invalid parameters or fail to handle new error conditions.
- Downstream callees may receive unvalidated data that bypasses historical invariants.
- Sibling modules implementing the same interface may become desynchronized.

The differential call-graph audit constructs a bidirectional dependency graph around every changed symbol, establishing a bounded blast radius before any review conclusion is formed.

## 2. The 5-Stage CodeRabbit Traversal Architecture

apex-bug-hunter adapts the multi-stage review architecture pioneered by CodeRabbit, executing five sequential stages:

### Stage 1: Symbol Extraction and AST Parsing

For every modified file in the git diff:
1. Parse source files into Abstract Syntax Trees (ASTs) using language-specific parsers (TypeScript Compiler API, Python AST, Tree-Sitter, or Babel).
2. Extract all modified, added, and deleted symbols:
   - Function and method declarations.
   - Interface, type alias, and class definitions.
   - Exported constants, enum values, and route handlers.
   - Decorators, middleware annotations, and schema validators.

### Stage 2: Bidirectional Call-Graph Mapping

For each modified symbol, map dependencies in both directions:
- Fan-In (Upstream Callers): Traverse all call sites, event subscribers, and route controllers that invoke the modified symbol. Determine whether callers satisfy any new preconditions.
- Fan-Out (Downstream Callees): Traverse all internal functions, database queries, and external services invoked by the modified code. Verify that modified arguments conform to downstream invariants.

```
Upstream Route Controller (`src/api/routes/item.ts`)
       │ (calls)
       ▼
Modified Service Function (`src/services/itemService.ts:updateItem`)
       │ (calls)
       ▼
Downstream Repository Query (`src/db/itemRepository.ts:save`)
```

### Stage 3: Schema and Business Logic Precedence

Always read dependency files in this strict sequence:
1. Data Schemas and Invariant Declarations: Read database schemas, OpenAPI/Protobuf contracts, and runtime validators (Zod/TypeBox) before evaluating implementation code.
2. Business Logic and Domain Services: Read service implementations against the contract schemas.
3. Test Suites and Fixtures: Read tests last. Never infer expected behavior from test mocks; tests may encode false assumptions.

### Stage 4: High-Fan-Out Pruning vs Critical Path Auditing

When a shared utility or central type changes, the syntactic blast radius can encompass hundreds of files. Prune traversal noise using deterministic heuristics:
- Pure Type Extensions: If an interface adds an optional field (`field?: string`), callers omitting the field do not require individual audit unless they perform exhaustive property mapping or object spreading.
- Breaking Contract Mutations: If a parameter type narrows, a required field is added, or a return value can now be null or undefined, every caller on the critical execution path must be individually inspected.
- State and Concurrency Paths: Prioritize callers that perform database transactions, state-machine transitions, or asynchronous message handling.

### Stage 5: Disconfirming-Evidence Verification Pass

Before cataloging any bug, execute an active disconfirming-evidence check:
- Search for compensating controls: Did an upstream middleware or gateway already sanitize the input?
- Search for default parameters: Does an underlying database column have a default value or trigger that prevents the feared null constraint violation?
- Re-read the physical code at HEAD: Confirm that the hypothesized failure mode is reachable at runtime. If disconfirming evidence is found, discard the false positive.

## 3. Differential Line-Deletion (-) Audit

The single most frequent source of silent production outages is the accidental or careless removal of protective code. Reviewers naturally focus on added lines (+), ignoring deleted lines (-).

### Deleted Invariant Checklist

Inspect every hunk starting with `-` across the diff:

| Deleted Pattern | Outage Risk | Audit Mechanism |
| :--- | :--- | :--- |
| Removed `safeParse` or validation call | Injection of unvalidated fields into domain logic | Trace removed schema refinement to data store insertion |
| Removed `await` keyword | Unhandled promise rejection, race condition, or silent failure | Check if function returns Promise and caller expects resolved value |
| Removed authorization gate or role check | Privilege escalation or broken tenant isolation | Check if route relies on ambient middleware or is now unprotected |
| Removed transaction wrapper (`db.transaction`) | Partial database writes and state corruption | Verify whether multiple write operations execute atomically |
| Removed error boundary or catch block | Unhandled rejection crashing Node.js / worker runtime | Trace whether thrown errors reach top-level server loop |
| Removed cache invalidation key | Stale reads and inconsistent data across nodes | Check if mutation updates data without clearing Redis / memory cache |

### Line-Deletion Analysis Workflow

1. Extract all deleted lines into a unified buffer:
   ```bash
   git diff <base>...<head> | grep "^-" | grep -v "^---"
   ```
2. For each deleted block, ask: "Why was this code originally written?"
3. If the removed line was a defensive check, verify where that responsibility was transferred. If it was transferred nowhere, flag as a P1 CRITICAL defect.

## 4. Cross-Boundary Data Flow Auditing

Modern applications span multiple distinct architectural layers:

```
External HTTP / Webhook / RPC Boundary
       │
Input Validation Layer (Zod / Pydantic / SafeParse)
       │
Domain Service Layer (Business Rules & Transactions)
       │
Persistence Layer (ORM / SQL Query / KV Store)
       │
Outbound Serialization Layer (Response DTO & Masking)
```

### Defense-in-Depth Verification

Data must be validated at every boundary it crosses:
- Entry Boundary: Coerce strings, strip unknown keys, validate formats and length limits.
- Domain Boundary: Enforce business state preconditions (such as "order cannot be cancelled once shipped").
- Persistence Boundary: Scope queries to tenant ID, enforce unique constraints, and check optimistic concurrency locks.
- Serialization Boundary: Strip sensitive fields (passwords, internal IDs, foreign tenant metadata) before transmitting payloads.

If a bug is found at the persistence layer, do not merely patch the SQL query. Enforce validation across all upstream layers to guarantee defense-in-depth.
