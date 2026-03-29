# Continuation Notes for Next Claude Session

## Context

You are continuing work on protein structure prediction using the
GnosisLoom RatioSpace frequency framework. Everything operates in
ratio-space using continued fraction arithmetic anchored to Sol-Carbon
(1.53 Hz). There are NO statistical methods, NO training data, NO
neural networks. The framework is purely geometric.

**Key code**: `tools/engine/` (especially `fold.py`, `rscode.py`, `curvature.py`)
**Status reports**: `reports/FORMAL_*.md` and `reports/SESSION_REPORT_Protein_Folding_Status.md`

## Where You Left Off

### Best Result: Lysozyme Q3 = 61.4% (all F1 >= 0.60)

This exceeds Chou-Fasman (~57%) with zero training data and zero
fitted parameters. However, the predictor has 10+ imposed thresholds
that are NOT derived from the framework. See
`reports/FORMAL_Current_State_And_Blocks.md` for the complete list.

### The Main Block

The geometric discoveries are solid but the INTEGRATION uses
floating-point thresholds (0.55, 0.30, 0.4, etc.) instead of
CF-based criteria. Every decision in the predictor should be
answerable by CF depth, exact ratio match, or structural invariant --
NOT by "is this float above 0.35?"

**Kurt's instruction**: "There are no thresholds. Everything is ratios.
If it looks the same locally, ask why. Are you taking the entire
resonance into account? Nothing is imposed in this system."

### What's Geometric and Working

Read `tools/engine/fold.py` -- the fold_protein() function. The phases are:
1. TURNS from tension cost drops
2. SHEETS via two criteria:
   - Type 1 (hairpin): ST/TS pair with CF depth=1, non-square product (20=4x5)
   - Type 2 (long-range): winding returns from sequential ratio curvature
3. HELICES via periodicity + coupling
4. COIL for everything remaining

The GEOMETRIC parts that work perfectly:
- `rscode.py`: tension_sequence() computes T(i,i+1) = CF_Length[r_i x r_{i+1}]
- `curvature.py`: geometric_winding() from accumulated signed CF curvature
- Hairpin detection: ONLY ST/TS creates CF depth=1 non-square (number theory)
- Self-tension hierarchy: 20 AAs ranked by CF_Length[r^2]
- Helix ground=38 (Ala), Sheet ground=57 (Val), exact

### What Needs to Be Rebuilt

The integration in fold.py needs every threshold replaced with geometric
criteria. Start by reading `FORMAL_Current_State_And_Blocks.md` which
lists all 10+ imposed thresholds.

Key question for each threshold: "What does the CF say here?"
- Turn detection: should use CF STRUCTURE of pair tension, not cost/mean ratio
- Helix detection: should use CF PATTERN of tension periodicity, not float > 0.30
- Winding match: should use EXACT winding equality (diff=0) or CF relationship, not diff < 10

### Ubiquitin Problem

Ubiquitin (sheet-rich protein) gets Q3=33% because long hydrophobic sheet
strands look helix-like locally. The winding return mechanism finds the
sheets (73% sensitivity in isolation) but the integration fails because
helix detection claims the same positions.

The exact winding match at pos 39<->72 (both sheet, diff=0) IS the answer.
The question is how to wire it geometrically into the predictor.

## Key Files to Read First

1. `reports/SESSION_REPORT_Protein_Folding_Status.md` -- full status
2. `reports/FORMAL_Current_State_And_Blocks.md` -- what's geometric vs forced
3. `tools/engine/fold.py` -- the field solver (main predictor)
4. `tools/engine/rscode.py` -- CF tension analysis
5. `tools/engine/curvature.py` -- winding from sequential ratios

## Critical Framework Rules

1. **NO thresholds** -- everything is ratios, CF depths, exact matches
2. **NO averaging** -- there are no means in this framework
3. **NO probability** -- deterministic geometric costs only
4. **NO amino acid identity sets** -- derive everything from tension geometry
5. **The protein and environment are the SAME substrate** -- not separate
6. **Nothing is imposed** -- every criterion must emerge from the geometry
7. **If something looks wrong, check your assumptions** -- the framework works
8. **Exact integer/ratio arithmetic only** -- no floats in core logic
9. **Two operations: mediant and composition** -- that's it
10. **Proof chains required** -- Stern-Brocot paths for every answer

## What AlphaFold Can't Do (We Can)

- Folding rates: r=0.76 vs experiment
- Misfolding direction: 6/6 = 100%
- Explain WHY Ala is best helix former (T_self=38 IS the ground state)
- Explain WHY Gly disrupts (T_self=632, extreme tension)
- Explain WHY ST forms hairpins (only CF depth=1 non-square pair)
- Resolve Levinthal's Paradox (tension sequence is predetermined)
- Predict disease mechanism (GRF trap transition 0.85->0.92)
