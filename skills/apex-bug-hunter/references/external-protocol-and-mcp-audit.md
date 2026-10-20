# External Protocol, Model Context Protocol, and Security Audit

Comprehensive reference for auditing Model Context Protocol (MCP) implementations, OAuth 2.1 security invariants, and database multi-tenant isolation.

## 1. External Protocol Grounding Principle

When a codebase interacts with an external protocol, standard, or SDK, developers frequently rely on outdated intuition or shallow code snippets. This generates subtle contract mismatches that compile cleanly but fail under real production traffic.

Before auditing or implementing code that interacts with external protocols, research and verify against the official specification.

## 2. Model Context Protocol (MCP) Audit Architecture

The Model Context Protocol (MCP) defines open standards for connecting AI models to external tools, resources, and prompts. In modern MCP specifications (2025-06-18 and 2025-11-25), implementations must satisfy strict protocol invariants:

### Protocol Invariant 1: tools/list and tools/call Parity

Every tool advertised in `tools/list` must be executable via `tools/call`.
- Schema Consistency: The `inputSchema` advertised during tool listing must be identical to the validation schema enforced during tool execution.
- Capability Annotations: Verify modern tool hints are accurately declared:
  - `readOnlyHint`: Declares the tool executes purely read operations with zero side effects.
  - `destructiveHint`: Flags whether the tool permanently deletes or alters data, signaling the host to prompt the human user for confirmation.
  - `idempotentHint`: Declares whether multiple executions with identical inputs produce identical state.

### Protocol Invariant 2: outputSchema and structuredContent Compliance

Modern MCP tools declare an optional JSON Schema `outputSchema` describing the data shape returned upon successful execution.
- Structured Content Requirement: When a tool defines an `outputSchema`, its execution result must populate `structuredContent` conforming to that exact schema. Returning only unstructured `text` violates the protocol contract.
- Backward Compatibility Text: For hosts that do not yet consume `structuredContent`, the tool must also serialize the structured data as a JSON string within a standard `text` content block.

### Protocol Invariant 3: The isError Schema Validation Bypass Rule

When an operational failure occurs (such as file not found, unauthorized tenant, or invalid query):
- The tool must return `isError: true` within the `CallToolResult`.
- The tool must provide human-readable failure details inside a `text` content block.
- Error Bypass Rule: When `isError: true` is set, client SDKs (including `@modelcontextprotocol/sdk`) must bypass `outputSchema` validation. If a tool fails to set `isError: true` and returns an error message as normal content, the client SDK will attempt to validate the error string against the success `outputSchema`, resulting in a client-side schema validation crash.

### Protocol Invariant 4: Deep-Clone Schema Sanitization

Servers serving multiple concurrent LLM clients often sanitize schemas dynamically (e.g. stripping internal fields based on client role).
- In-Place Mutation Trap: Sanitizers that delete properties directly from a shared schema object (`delete schema.properties.secretField`) mutate the server-wide singleton. Sibling client connections will receive corrupted, truncated schemas.
- Deep Clone Invariant: Sanitizers must operate on deep clones (`structuredClone(schema)`) before performing modifications.

### Protocol Invariant 5: Manifest Parity and Encoding Hygiene

Static manifest files (`plugin.json`, `marketplace.json`, tool manifests) must remain byte-identical in semantic meaning to live endpoints:
- Zero BOM: Files must be encoded in UTF-8 without Byte Order Marks (BOM). A UTF-8 BOM (`EF BB BF`) crashes many standard JSON and YAML parsers.
- No Drift: Tool descriptions and version strings must never drift between static plugin manifests and runtime registration handlers.

## 3. OAuth 2.1 Security and Authentication Invariants

OAuth 2.1 consolidates modern OAuth best practices, eliminating insecure legacy flows. Audit all authentication modules for compliance:

### PKCE Enforcement

Proof Key for Code Exchange (PKCE) is mandatory for all OAuth 2.1 authorization code flows:
- Enforce PKCE (`code_challenge` with method `S256` and `code_verifier`) across both public clients (Single Page Apps, mobile apps) and confidential server-rendered clients.
- Verify that authorization code exchange rejects requests lacking a valid `code_verifier`.

### Refresh Token Rotation and Revocation

- Long-lived, non-expiring refresh tokens are prohibited.
- Enforce Refresh Token Rotation: Every refresh request issues a new refresh token and invalidates the previous token.
- Reuse Detection: If an invalidated refresh token is presented, the authorization server must immediately revoke all tokens previously granted to that authorization session.

### Redirect URI Exact Matching

- Wildcards, partial regex matches, and path traversals in `redirect_uri` are strictly forbidden.
- The authorization server must perform exact string matching against pre-registered client redirect URIs.

### Token Hygiene in Logs and URLs

- Access tokens and refresh tokens must never appear in query strings, URLs, or command-line arguments.
- Audit logging configurations to guarantee authorization headers (`Bearer ey...`) are stripped or masked prior to log persistence.

## 4. Multi-Tenant Isolation and Database Security

Tenant data leakage is an existential security failure. Audit all database layers for isolation invariants:

### The Composite Key Invariant

In multi-tenant systems, never execute lookups using only a record's primary key (`id`):

```typescript
// INSECURE: Allows cross-tenant data access if user guesses ID
const item = await db.item.findUnique({ where: { id: requestedId } });

// SECURE: Enforces strict tenant boundary
const item = await db.item.findFirst({
  where: { id: requestedId, tenantId: session.tenantId },
});
```

A database lookup that queries by record identifier without scoping to the authenticated tenant or owner identifier is classified as a P1 CRITICAL defect.

### Foreign Key Tenant Consistency

When inserting child records with foreign keys (e.g. adding an `OrderItem` to an `Order`):
- Verify that both the parent `Order` and the new `OrderItem` belong to the same authenticated `tenant_id`.
- Prevent attackers from associating items with foreign tenant parents by forging foreign key IDs.

### Database Driver Error Sanitization

Never return raw database exceptions to API consumers:
- Raw errors leak schema structures, table names, constraint definitions, and database engine versions.
- Catch database exceptions at the repository boundary and transform them into generic domain errors (`DatabaseError`, `ConflictError`, `NotFoundError`).
