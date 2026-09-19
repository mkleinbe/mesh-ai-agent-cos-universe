# Verification v4.11.1

Release verification requires:

- full repository CI;
- targeted v4.11.1 packaging tests;
- exact four-Skill bundle membership;
- complete Skill directories present before packaging;
- deterministic ZIP creation;
- SHA-256 checksum creation;
- v4.11.0 historical release publisher frozen to its original SHA;
- v4.11.1 semantic tag and release targeting the final main SHA;
- release assets attached to the v4.11.1 release;
- no agent-roster, authority, MCP, connector, runtime, or external-action expansion.

Human-controlled ChatGPT installation remains separate from repository verification.
