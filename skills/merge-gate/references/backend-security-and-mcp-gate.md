# Backend Security and Protocol Parity Gate Reference

This reference defines the zero-tolerance pre-merge checklist for backend architectures, database migrations, security boundaries, Model Context Protocol (MCP) implementations, and test-suite integrity.

## 1. Input and Boundary Validation (INV-14)

Data entering the application from untrusted boundaries (HTTP requests, webhooks, CLI arguments, or MCP tool calls) must be validated before reaching domain services or persistence layers.

### 1.1 Strict Schema Enforcement
- Use schema validators (Zod, TypeBox, or JSON Schema) with strict mode enabled (`.strict()` or `additionalProperties: false`) to reject unexpected fields.
- UUID and identifier parameters must be explicitly validated (e.g. `z.string().uuid()`) at the entry boundary to prevent SQL injection or malformed lookups.
- Avoid loose types: schemas containing `z.any()`, `z.unknown()`, or unchecked record types (`Record<string, any>`) on sensitive inputs are flagged as `P1 CRITICAL`.

### 1.2 Multi-Layer Defense-in-Depth
Enforce validation across four discrete layers:
1. Entry Boundary: Parse types, validate constraints, and strip dangerous payloads.
2. Domain Service: Enforce business state preconditions (e.g. items cannot be deleted if active orders exist).
3. Persistence Boundary: Scope queries to tenant ID, enforce unique constraints, and check optimistic concurrency locks.
4. Serialization Boundary: Strip sensitive metadata, private tokens, and internal IDs before emitting payloads.

## 2. Model Context Protocol (MCP) Specification Compliance

When auditing code implementing or consuming the Model Context Protocol (MCP 2025-06-18 and 2025-11-25 specifications):

### 2.1 tools/list and tools/call Parity
- Every tool listed in `tools/list` must be executable via `tools/call`.
- Input schemas advertised during discovery must match the execution schemas exactly.
- Modern capability hints must accurately reflect behavior:
  - `readOnlyHint`: Tool performs only read operations with zero mutations.
  - `destructiveHint`: Tool permanently deletes or alters persistent records.
  - `idempotentHint`: Multiple executions with identical inputs produce identical state.

### 2.2 outputSchema and Per-Return-Branch structuredContent Parity
- When a tool declares an `outputSchema`, every non-error return branch in the handler must populate `structuredContent` conforming to that schema.
- Flag any conditional return branch (such as an empty search result or cache hit) that returns only `content: [...]` while omitting `structuredContent`. Strict MCP SDK clients crash on missing structured payloads.
- Backward compatibility: Include serialized JSON within a standard `text` content block for hosts that do not consume `structuredContent`.

### 2.3 Error Handling and the isError Bypass Rule
- Operational errors (not found, unauthorized, conflict) must return `isError: true` within the result object.
- When `isError: true` is set, client SDKs (including `@modelcontextprotocol/sdk`) bypass `outputSchema` validation. Returning an error message as regular content causes strict client SDKs to validate the error string against the success schema, crashing the client.

### 2.4 Deep-Clone Schema Sanitization
- When sanitizing tool schemas for downstream LLM providers (e.g. stripping `$schema` or unsupported keywords):
  - Always deep clone the schema: `const clone = structuredClone(schema);`.
  - In-place property deletions (`delete schema.properties.foo`) corrupt the shared singleton schema across all concurrent sessions and are classified as `P1 CRITICAL`.

## 3. Database Migration and Concurrency Safety

### 3.1 Zero-Downtime Expand-and-Contract Migrations
Database schema mutations must remain backward-compatible with running application versions:

- **Adding Non-Null Columns:** Adding a `NOT NULL` column without a `DEFAULT` value halts writes in existing application instances. Use the expand-and-contract pattern:
  1. Add the column as nullable.
  2. Deploy application code that populates the column on new writes and backfills historical rows.
  3. Alter the column to `NOT NULL` in a subsequent migration.
- **Renaming Columns or Tables:** Never rename a column directly. Create the new column, dual-write to both, backfill historical data, switch reads to the new column, and drop the old column in a later release.

### 3.2 Composite Tenant Isolation ((owner_id, id))
Every query on tenant-owned data must scope records by authenticated tenant:

```typescript
// INSECURE: Allows cross-tenant probing if user guesses ID
const record = await db.item.findUnique({ where: { id } });

// SECURE: Enforces strict tenant boundary
const record = await db.item.findFirst({
  where: { id, ownerId: session.ownerId },
});
```

If an entity ID exists in the database but belongs to another tenant, the endpoint must return `NOT_FOUND` (never `FORBIDDEN` which confirms existence).

### 3.3 Atomic Concurrency and Idempotency
- Use `SELECT ... FOR UPDATE` when reading state that governs an immediate subsequent write within the same transaction.
- Implement idempotency keys (`clientRequestId`) using atomic upserts:
  ```sql
  INSERT INTO idempotency_records (tenant_id, client_request_id, response_payload)
  VALUES ($1, $2, $3)
  ON CONFLICT (tenant_id, client_request_id) DO NOTHING;
  ```

## 4. OAuth 2.1 and Cryptographic Zero-Touch Locks

### 4.1 Protected Zero-Touch Path Lock
When a repository designates authentication routes, token issuers, or security boundaries as protected:

- Compute MD5 and SHA-256 hashes of all protected files between `origin/main` and `HEAD`.
- If any byte changed, fail the merge gate immediately with exit code `2`.

### 4.2 OAuth 2.1 Directives
- PKCE is mandatory: authorization code flows must require `code_challenge` and `code_verifier` with `S256` hashing.
- Exact redirect URI matching: reject wildcards, subpaths, and regex pattern matching in redirect URIs.
- Token Hygiene: access tokens and refresh tokens must never appear in URL query parameters, command-line arguments, or application logs.

### 4.3 Secret Redaction (REDACT-01)
Before pasting logs or test traces into PR comments or review reports:

- Scrub tokens matching `ghp_`, `sk-`, `xoxb-`, `ey...`, and `BEGIN PRIVATE KEY` to `<REDACTED_SECRET>`.
- Scrub authorization headers: `Authorization: Bearer <token>` -> `Authorization: Bearer <REDACTED_SECRET>`.

## 5. Test-Harness Integrity and Reward-Hacking Detection

Verify test suites reflect real production behavior rather than gamed pass conditions:

- **Harness Client Initialization:** For MCP tests, verify `await client.listTools()` runs before any `client.callTool()` invocation to initialize the SDK schema cache.
- **No Internal Module Mocking (HACK-08):** Flag tests that mock internal application files (`vi.mock('../src/service')`) rather than real external network or storage boundaries.
- **No Tautological Assertions (HACK-09):** Flag assertions that compute expectations using the exact same formula under test.
- **No Test Suppressions:** Flag `.skip`, `.only`, `.todo`, or `.fails` directives in test files as blocking defects.
