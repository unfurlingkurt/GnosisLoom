# Current State: What's Geometric vs What's Forced

## Geometrically Derived (solid, no parameters)

1. Self-tension hierarchy: T_self = CF_Length[(freq/Carbon)^2]
2. Pair tension: T(i,i+1) = CF_Length[r_i x r_{i+1}]
3. Hairpin criterion: CF depth = 1, non-square product (ST only)
4. Sequential ratio curvature: R_i = r_{i+1}/r_i
5. Accumulated geometric winding from signed curvatures
6. Neighbor coupling ratio for helix vs coil
7. Hydration coupling from H-O beat (1.86 Hz)

## Parameters Imposed (NOT from geometry) -- must be replaced

1. Turn detection: cost/rolling_mean < 0.55
2. Turn extension: cost < median x 0.60
3. Periodicity threshold: strength > 0.30
4. Coupling threshold: >= 0.4
5. Self-tension band: [20, 200]
6. Winding max_diff: 10
7. Winding partner count: >= 5
8. Periodicity filter: < 0.35
9. Hydration damping: 0.85
10. CF singularity boundary: > 100

## Best Result: Lysozyme Q3 = 61.4%

Geometric discoveries work. Integration is impure.
Every threshold must become a CF depth check, exact ratio, or structural invariant.
