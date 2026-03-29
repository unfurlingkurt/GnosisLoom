# The Sequential Ratio Geodesic: Winding from Curvature

## The Right Representation

The winding number is NOT a counter (+1/3.6 per helix residue).
It IS the accumulated curvature of the sequential ratio path.

The sequential ratio R_i = r_{i+1} / r_i measures how the Carbon-anchored
frequency ratio CHANGES from one residue to the next. The CF expansion
of R_i encodes the curvature at that step.

## CF Depth = Curvature Type

| CF Depth | Ratio Type | Physical Meaning | Example |
|----------|-----------|------------------|---------|
| 1 | R = 1.0 (exact unity) | Zero curvature — same state continues | PP, QQ, LI, GG |
| 2 | R = simple fraction (5/4, 4/3...) | Minimal curvature — simplest transition | **ST = 5/4** (hairpin) |
| 3-5 | Moderate ratio | Structure transition | Many |
| 6+ | Complex ratio | Sharp curvature — boundary/kink | Most transitions |

## Key Findings (Ubiquitin)

**Leu-Ile (position 43, inside sheet strand 3)**: R = 1.0000 exactly.
Leu and Ile have identical frequencies (9.22 Hz). The sheet strand
maintains ZERO curvature — constant tension state.

**Ser-Thr (position 65, hairpin turn)**: R = 5/4 = 1.2500, CF = [1, 4].
The simplest non-unity transition — minimal curvature change at the
hairpin fold point. This IS the geometric signature of the turn.

**Pro-Pro (position 37, coil)**: R = 1.0000. Same amino acid repeated,
zero curvature. The chain maintains state but Pro's rigid geometry
prevents helix or sheet.

## Implication for Winding

Winding = accumulated curvature of the sequential ratio path.
- Zero-curvature steps (CF depth 1) don't change the winding.
- Minimal-curvature steps (CF depth 2) add small winding.
- High-curvature steps (CF depth 6+) add significant winding.

The total winding is the SUM of CF-lengths of the sequential ratios,
weighted by their direction (sign of the curvature). This is NOT
the simple counter we were using — it's the actual geodesic curvature.

## Implementation Note

The running multiplicative composition (product of all ratios)
diverges to 10^53 for a 76-residue protein — unsuitable for CF analysis.

The sequential ratioing (r_{i+1}/r_i) stays bounded (0.35 to 4.3)
and produces meaningful CFs at every step. This is the correct
representation for the geodesic.
