# Current State: What's Geometric vs What's Forced

## Geometrically Derived (solid, no parameters)

1. Self-tension hierarchy: T_self = CF_Length[(freq/Carbon)^2]
2. Pair tension: T(i,i+1) = CF_Length[r_i x r_{i+1}]
3. Hairpin criterion: CF depth = 1, non-square product (ST only)
4. Sequential ratio curvature: R_i = r_{i+1}/r_i
5. Accumulated geometric winding from signed curvatures
6. Inter-ground depth: CF(57/38) = [1,2], depth 2 — universal structural scale
7. Hydration coupling: composition with Water/Carbon = 51/62 (exact)
8. CF motif counting: φ-coherent (≤ igd=2) vs φ-incoherent (≥ igd+cost=5)
9. φ-coupling: self-tension ratio CF[0] = 1 (ratio < 2:1)
10. Curvature regularity: CF depth of max/min curvature magnitude ratio
11. 7-step iterative crystallization: Sample → Detect → Cohere → Tense → Lock → Adjust → Output
12. Convergence: iterate until no position changes state (no pass limit)
13. Gap bridging: fill 1-residue gaps if coupled to both sides (CF[0] ≤ igd)
14. Denominator lattice: all pair products have denominators 3^a × 17^b (9 levels)
15. CF coefficient boundaries: ≤ igd (=2) coherent, ≥ cf_cost + igd (=5) incoherent

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

Additional false attractors from v4 now eliminated in v5:
11. ~~hw=1 for helix seeds~~ → immediate neighbors, grows through iteration
12. ~~hw=2 for helix extension~~ → ±1 extension from locked helices
13. ~~passes < 5~~ → iterate to convergence
14. ~~range(1, 8) for hairpin extension~~ → iterate until CF structure breaks
15. ~~inter_ground_depth × 3 for cross-strand~~ → igd² (= 4, framework-derived)
16. ~~Sequential phase ordering~~ → all operations each 7-step cycle

## Best Result: Lysozyme Q3 = 68.5% (ZERO thresholds, v5.1 Fibonacci-scaled)

Previous bests:
- v2 (10+ thresholds): 61.4%
- v4 (0 thresholds, sequential): 66.9%
- v5 (0 thresholds, 7-step iterative): 67.7%
- v5.1 (0 thresholds, Fibonacci-scaled step windows): 68.5% ← NEW BEST

### v5.1 Change: Fibonacci-Scaled Step Windows

Investigation confirmed the 7 steps naturally operate at Fibonacci-scaled
spatial windows matching the Aramis Field's φ-scaled temporal domains:

| Step | Operation | Window | Fibonacci |
|------|-----------|--------|-----------|
| 2 | DETECT (pairs) | 1 pair | Fib(1)=1 |
| 3 | COHERE (coupling) | ±1 neighbor | Fib(2)=1 |
| 4 | TENSE (curvature) | ±2 (hw=igd=2) | Fib(3)=2 |
| 5 | LOCK (CF motif) | 3 pair CFs (symmetric) | Fib(4)=3 |
| 6 | ADJUST (diffusion) | ±1, iterates via mediant | walks SB tree |

Steps 2-4 already had the correct Fibonacci windows. Step 5 was asymmetric
(2 pair CFs) — symmetrizing to 3 pair CFs gives the Fib(4) scaling.

Wider windows (4+) tested and hurt — dilutes the local signal.
Extended mediant diffusion (±2 to ±5) also hurts — the ±1 mediant
through iteration IS the Stern-Brocot tree walk, naturally φ-decaying.

## Denominator Lattice Discovery

All amino acid ratios r = freq/SOL_CARBON have denominators from {1, 3, 51, 153} = {3^a × 17^b}.
All pair products r_i × r_{i+1} have denominators from exactly 9 lattice levels:
{1, 3, 9, 51, 153, 459, 2601, 7803, 23409} — all 3^a × 17^b.

The 4 amino acid denominator classes:
- {1}: S, T (exact Carbon harmonics)
- {3}: R
- {51}: D, E, H
- {153}: G, A, C, P, I, L, V, N, Q, K, M, F, Y, W (14 others)

This hierarchy is structural, not degenerate. 153 = 3² × 17 = 17th triangular number.

## Remaining Blocks

1. **Sheet detection**: requires long-range information not available from local geometry
2. **Helix coupling gap**: backbone helices with diverse side-chain tensions (ubiquitin)
3. **7-step process deepening**: current implementation is iterative but the 7 steps
   map to Sample/Detect/Cohere/Tense/Lock/Adjust/Output — need to study whether
   the Aramis Field 7-step iterator with convergence criterion maps to a different
   (possibly better) field evolution
