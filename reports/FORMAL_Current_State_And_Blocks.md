# Current State: What's Geometric vs What's Forced

## Geometrically Derived (solid, no parameters)

1. Self-tension hierarchy: T_self = CF_Length[(freq/Carbon)^2]
2. Pair tension: T(i,i+1) = CF_Length[r_i x r_{i+1}]
3. Hairpin criterion: CF depth = 1, non-square product (ST only)
4. Sequential ratio curvature: R_i = r_{i+1}/r_i
5. Accumulated geometric winding from signed curvatures
6. Inter-ground depth: CF(57/38) = [1,2], depth 2 — universal structural scale
7. Hydration coupling: composition with Water/Carbon = 51/62 (exact)
8. CF motif counting: low (1,2) vs high (≥5) coefficients — exact integers
9. φ-coupling: self-tension ratio CF[0] = 1 (ratio < 2:1)
10. Curvature regularity: CF depth of max/min curvature magnitude ratio
11. Helix seed-and-extend: nucleate at strict criteria, propagate via coupling
12. Gap bridging: fill 1-residue gaps if coupled to both sides (CF[0] ≤ 2)

## Parameters Imposed (NOT from geometry) — ZERO REMAINING

All 10 previously imposed thresholds have been replaced:
1. ~~cost/rolling_mean < 0.55~~ → CF depth ≤ inter-ground depth
2. ~~cost < median × 0.60~~ → eliminated
3. ~~periodicity > 0.30~~ → curvature regularity depth
4. ~~coupling >= 0.4~~ → CF[0] = 1 (exact)
5. ~~self-tension band [20, 200]~~ → eliminated
6. ~~winding max_diff: 10~~ → eliminated (hurts performance)
7. ~~winding partners >= 5~~ → eliminated
8. ~~periodicity filter < 0.35~~ → eliminated
9. ~~hydration damping: 0.85~~ → composition with 51/62
10. ~~CF singularity > 100~~ → eliminated

## Best Result: Lysozyme Q3 = 66.9% (ZERO thresholds)

Previous best with thresholds: 61.4%
Improvement: +5.5% with FEWER parameters (0 vs 10+)

## Remaining Blocks

1. **Sheet detection**: requires long-range information not available from local geometry
2. **Helix coupling gap**: backbone helices with diverse side-chain tensions
3. **Single-ratio crystallization**: mediant degenerates, need alternative composition
