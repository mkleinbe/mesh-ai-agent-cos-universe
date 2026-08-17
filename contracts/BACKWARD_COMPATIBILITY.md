# Contract Backward Compatibility Policy

Contracts use explicit `mesh.cos.<contract>.vN` versions. Additive optional fields may be introduced within a major version only when old producers and consumers remain valid. Removing/renaming fields, changing required semantics, narrowing enums, or changing authority meaning requires a new major contract version and migration tests. Readers must reject unsupported versions rather than silently reinterpret them.
