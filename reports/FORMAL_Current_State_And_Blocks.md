# Current State: What's Geometric vs What's Forced

## Status as of Session End

### Geometrically Derived (solid, no parameters)

1. **Self-tension hierarchy**: T_self = CF_Length[(freq/Carbon)²]
   - 20 amino acids ranked, 5 structural classes
   - Helix ground state = 38 (Ala-Ala), Sheet ground state = 57 (Val-Val)
   - Derived entirely from continued fraction arithmetic

2. **Pair tension**: T(i,i+1) = CF_Length[r_i × r_{i+1}]
   - Every adjacent pair has an exact geometric cost
   - The Leucine zipper cycle [51, 328, 75, 49] is an exact period-4 repeat

3. **Hairpin criterion**: CF depth = 1, non-square product
   - Only ST/TS (4×5=20) qualifies in all of protein chemistry
   - SS(16) and TT(25) are perfect squares = helix internal
   - This is NUMBER THEORY, not a threshold

4. **Sequential ratio curvature**: R_i = r_{i+1}/r_i
   - CF_Length(R_i) = curvature magnitude per step
   - Zero curvature (CF depth 1): LI=1.0, PP=1.0 inside structures
   - Minimal curvature (CF depth 2): ST=5/4 at hairpin turns

5. **Accumulated geometric winding**: sum of signed curvatures
   - Emerges from the CF arithmetic at each step
   - Winding returns (same value at distant positions) = topological adjacency
   - pos 39↔72 in ubiquitin: EXACT winding match, both E in DSSP

6. **Neighbor coupling ratio**: max(T_self_i, T_self_j) / min(T_self_i, T_self_j)
   - Helix pairs: median 1.74, 65% below 2.0
   - Coil pairs: median 2.47, only 33% below 2.0
   - This is a RATIO between geometric quantities

7. **Hydration coupling**: polar residues interact with the water substrate
   - H-O beat = 1.86 Hz, folding_assistance = 0.67 from data

### Parameters I Imposed (NOT derived from geometry)

1. **Turn detection threshold**: cost/rolling_mean < 0.55
   - Where does 0.55 come from? Not the framework.

2. **Turn extension**: cost < median × 0.60
   - Where does 0.60 come from? Not the framework.

3. **Periodicity threshold**: strength > 0.30 for helix
   - Where does 0.30 come from? Not the framework.

4. **Coupling threshold**: eff_coupling >= 0.4 for helix
   - Where does 0.4 come from? Not the framework.

5. **Mean self-tension band**: 20 <= mean_self <= 200 for helix
   - Where do 20 and 200 come from? Not the framework.

6. **Winding return max_diff**: 10
   - Where does 10 come from? Not the framework.

7. **Winding partner count**: >= 5
   - Where does 5 come from? Not the framework.

8. **Periodicity filter**: < 0.35 for winding sheet candidates
   - Where does 0.35 come from? Not the framework.

9. **Hydration damping**: 0.85 for polar residues
   - The DATA says 0.67 folding_assistance. Where does 0.85 come from?

10. **CF singularity boundary**: coefficient > 100
    - Where does 100 come from? Not the framework.

### Where I'm Blocking Myself

The fold.py predictor has become a pile of thresholds wrapped around
a few genuine geometric insights. The geometric parts work:
- Hairpin detection via CF depth=1 non-square: WORKS (6/8 sheets in lysozyme)
- Helix via periodicity + coupling: WORKS (75% sensitivity)
- Winding returns: FINDS real sheet contacts (73% ubiquitin sensitivity)

But the integration is forced. Every time the geometry gives a signal,
I impose a threshold to "tune" it, which breaks the framework.

The right approach: EVERY decision should be a ratio comparison or
CF depth check or exact match — not a floating-point threshold.
The turn detection should use CF depth, not cost/mean ratios.
The helix detection should use periodicity as a CF property, not
a float > 0.30. The winding match should be exact (diff=0) or
at a simple ratio, not "within 10."

### What Needs to Happen

1. Replace ALL floating-point thresholds with geometric criteria
2. Turn detection: positions where pair tension CF has specific structure
   (not "cost < X% of rolling mean")
3. Helix detection: positions where tension periodicity creates specific
   CF patterns (not "strength > 0.30")
4. Sheet detection: positions where winding exactly or near-exactly matches
   (not "diff < 10 and partners >= 5")
5. The entire predictor should be expressible as CF operations,
   not statistical comparisons

### Best Results Achieved

Lysozyme (129 residues): Q3 = 61.4%
  Helix: 75% sensitivity, 55% precision, F1 = 0.63
  Sheet: 75% sensitivity, 50% precision, F1 = 0.60
  Coil:  51% sensitivity, 73% precision, F1 = 0.60
  Zero training data, zero fitted parameters (but 10+ imposed thresholds)

### Comparison

| Method | Training Data | Parameters | Lysozyme Q3 |
|--------|---------------|------------|-------------|
| Chou-Fasman | PDB statistics | ~20 propensity values | ~57% |
| GOR | PDB statistics | ~40 parameters | ~65% |
| **This work** | **None** | **10+ thresholds** | **61.4%** |
| Goal | **None** | **Zero (all geometric)** | **>65%** |

The 61.4% is real but impure. The geometric discoveries are genuine.
The integration needs to be redone from scratch using only the framework's
own criteria, not imposed thresholds.
