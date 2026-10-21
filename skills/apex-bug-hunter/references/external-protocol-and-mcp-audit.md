# External Protocol, Model Context Protocol, and Security Audit

This reference governs Pass 1 (External Specification Grounding), Pass 3 (Contract, Protocol, and Output Schema Parity Audit), and Pass 5 (Security, Tenant Isolation, and Error Sanitization Audit).

## 1. Model Context Protocol (MCP) Specification Invariants

The Model Context Protocol (MCP) defines open standards for connecting AI models to external tools, resources, and prompts. In modern MCP specifications (2025-06-18 and 2025-11-25), implementations must satisfy strict protocol invariants:

### 1.1 tools/list and tools/call Parity

Every tool advertised in `tools/list` must be executable via `tools/call`.
- **Schema Consistency:** The `inputSchema` advertised during tool listing must be identical to the validation schema enforced during tool execution.
- **Capability Annotations:** Verify modern tool hints are accurately declared:
  - `readOnlyHint`: Declares the tool executes purely read operations with zero side effects.
  - `destructiveHint`: Flags whether the tool permanently deletes or alters data, signaling the host to prompt the human user for confirmation.
  - `idempotentHint`: Declares whether multiple executions with identical inputs produce identical state.

### 1.2 outputSchema and structuredContent Compliance

Modern MCP tools declare an optional JSON Schema `outputSchema` describing the data shape returned upon successful execution.
- **Structured Content Requirement:** When a tool defines an `outputSchema`, its execution result must populate `structuredContent` conforming to that exact schema. Returning only unstructured `text` violates the protocol contract.
- **Backward Compatibility Text:** For hosts that do not yet consume `structuredContent`, the tool must also serialize the structured data as a JSON string within a standard `text` content block.
- **Empty Branch Coverage:** Every conditional return path in the tool handler must populate `structuredContent`. A branch that returns only a `text` block with an empty list or message while omitting `structuredContent` violates the contract and crashes strict SDK clients.

### 1.3 Payload Truncation vs. Schema Integrity

If an outbound interceptor or response builder truncates oversized tool outputs (for example, capping responses at a maximum character or byte budget):
- Never truncate the raw JSON string in `content[0].text` while leaving `structuredContent` either missing, un-truncated, or stripped of required schema fields (`items`, `total`, `nextCursor`, `truncated: true`).
- Truncation must happen at the structured domain array level (slicing items to fit the budget and setting `truncated: true` and `nextCursor`) before serializing content and validating `structuredContent` against `outputSchema`.

### 1.4 Error Serialization (isError: true)

When a tool execution fails due to validation, missing entities (`NOT_FOUND`), collisions (`CONFLICT`), or ambiguity (`AMBIGUOUS`):
- The tool must return `isError: true` within the `CallToolResult`.
- The tool must provide human-readable failure details inside a `text` content block.
- **Error Bypass Rule:** When `isError: true` is set, client SDKs (including `@modelcontextprotocol/sdk`) must bypass `outputSchema` validation. If a tool fails to set `isError: true` and returns an error message as normal content, the client SDK will attempt to validate the error string against the success `outputSchema`, resulting in a client-side schema validation crash.

### 1.5 Multi-Client Schema Sanitization and Immutability

When an MCP server sanitizes JSON Schemas for specific downstream LLM providers (for example, stripping `additionalProperties`, `$schema`, `format`, or converting `anyOf` unions for Gemini, OpenAI, or Claude tool definitions):
- Always deep-clone (`structuredClone(schema)`) the canonical tool schema before mutating properties.
- Never mutate the registered schema object in place, as in-place mutation corrupts subsequent `tools/list` responses and server-side validation for other connected clients.

### 1.6 Static Manifest and Encoding Hygiene

If the repository publishes static tool manifests (`mcp.json`, `tools.json`, `openapi.json`, or `.well-known/` discovery files):
- Verify 1:1 parity between static manifests and live runtime `tools/list` output (tool count, names, `inputSchema`, `outputSchema`, and annotations).
- Verify all JSON and source files are encoded in clean UTF-8 with zero Byte Order Mark (`0xEF 0xBB 0xBF` BOM) and zero unescaped control characters.

## 2. OAuth 2.1 and RFC 8707 Resource Indicator Invariants

When auditing authentication, token exchange, or MCP HTTP transport boundaries:

### 2.1 Protected Zero-Touch Enforcement
If the user designates OAuth routes or auth modules as protected, verify `git diff` is 0 bytes across those files.

### 2.2 Audience and Resource Binding (RFC 8707)
Verify access tokens are validated against the specific MCP server resource URI / `aud` claim to prevent confused-deputy token replay across services.

### 2.3 PKCE Enforcement
Verify authorization code flows require `code_challenge` and `code_verifier` (`S256`) and reject plain or missing PKCE parameters.

### 2.4 Strict Redirect URI Matching
Confirm redirect URIs are compared using exact string/URI matching against pre-registered allowlists with zero open-redirect wildcards.

### 2.5 Token Hygiene in Logs and URLs
Access tokens and refresh tokens must never appear in query strings, URLs, or command-line arguments. Audit logging configurations to guarantee authorization headers (`Bearer ey...`) are stripped or masked prior to log persistence.

## 3. Multi-Tenant Isolation and Error Sanitization (Pass 5)

### 3.1 Composite Tenant Lookup ((owner_id, id))

Every SQL query, ORM lookup, update, and delete on tenant-owned tables must bind both the authenticated `owner_id` (or `tenant_id`) and the entity `id` in the WHERE clause:

```typescript
// INSECURE: Allows cross-tenant data access if user guesses ID
const item = await db.item.findUnique({ where: { id: requestedId } });

// SECURE: Enforces strict tenant boundary
const item = await db.item.findFirst({
  where: { id: requestedId, tenantId: session.tenantId },
});
```

If an entity ID exists in the database but belongs to a different tenant, the lookup must return `NOT_FOUND` (identical to a non-existent ID) so cross-tenant probing cannot enumerate foreign IDs.

### 3.2 Foreign Key Tenant Consistency

When inserting child records with foreign keys (e.g. adding an `OrderItem` to an `Order`):
- Verify that both the parent `Order` and the new `OrderItem` belong to the same authenticated `tenant_id`.
- Prevent attackers from associating items with foreign tenant parents by forging foreign key IDs.

### 3.3 Grant-Tier Field Redaction

When sharing or delegated access grants (`viewer`, `commenter`, `public_link`) are supported, verify that outbound serializers strip internal metadata, private notes, owner email addresses, and billing identifiers unauthorized for that grant tier.

### 3.4 Database and Driver Error Sanitization

Never expose raw PostgreSQL/SQLite error strings (such as `duplicate key value violates unique constraint "idx_items_owner_parent_name"`), table names, or stack traces in HTTP or MCP responses. Map driver error codes (such as SQLSTATE `23505` or `23503`) to deterministic domain error codes (`CONFLICT`, `NOT_FOUND`, `INVALID_INPUT`).

### 3.5 Row-Level Security (RLS) Verification

When using PostgreSQL Row-Level Security or similar database-native isolation:
- Verify that RLS policies are enabled on all tables containing multi-tenant data (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY; ALTER TABLE ... FORCE ROW LEVEL SECURITY`).
- Confirm that the database role used by the application server does NOT bypass RLS via `BYPASSRLS` privilege or `SET ROLE` escalation.
- Test cross-tenant access by authenticating as Tenant A and requesting a known Tenant B record ID. The query must return zero rows.
