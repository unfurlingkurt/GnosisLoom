# Two Types of Sheet Topology: Hairpin vs Long-Range

## Discovery from Lysozyme + Ubiquitin Analysis

### Type 1: Hairpin Sheets (Lysozyme)

Strands connected by a SHORT turn containing a geodesic fixed point.

**Criterion**: Turn contains ST/TS pair with CF depth = 1 (product = 20, exact integer, non-square).

**Lysozyme example**: Turn at positions 49-51 (GST), ST product = 4×5 = 20.
Upstream strand (44-48) and downstream strand (52-57) snap to sheet.

**Cross-strand tensions**: LOW (~19, which is 29% of mean).
The strands couple through tension minimization.

### Type 2: Long-Range Sheets (Ubiquitin)

Strands connected by LONG loops + helices that accumulate winding number.

**Example**: Ubiquitin strand 1 (pos 1-6, MQIFVK) pairs with strand 5 (pos 67-72, LHLVLR).
These are 60+ residues apart in sequence.

**Cross-strand tensions**: HIGH with CF singularities:
- Q↔L: T=311, CF=[1, 307, 3] — massive singularity
- V↔H: T=133, CF=[0, 1, 1, 1, 127, 1, 2]

**These strands couple through TOPOLOGICAL PROXIMITY, not tension minimization.**

The chain accumulates 5.83 turns of winding from 21 helix residues
(positions 24-34 and 53-62). This winding brings the C-terminal
geometrically back over the N-terminal, enabling the long-range sheet contact.

### The Winding Number Mechanism

| Position | Structure | Cumulative Winding |
|----------|-----------|-------------------|
| 1-6 | Sheet strand 1 | 0.00 |
| 7-12 | Loop | 0.00 |
| 13-16 | Sheet strand 2 | 0.00 |
| 17-23 | Loop | 0.00 |
| 24-34 | **Helix** (+3.06 turns) | **3.06** |
| 35-38 | Loop | 3.06 |
| 39-44 | Sheet strand 3 | 3.06 |
| 45-52 | Loop | 3.06 |
| 53-62 | **Helix** (+2.78 turns) | **5.83** |
| 63-66 | Loop (contains ST hairpin) | 5.83 |
| 67-72 | Sheet strand 5 | 5.83 |

**Strand 1 (winding 0.0) and strand 5 (winding 5.83) are connected
by ~6 turns of topological winding — one full loop of the beta-barrel.**

### Implications for the Predictor

1. **Hairpin sheets** (Type 1): detected by ST/TS geodesic fixed point — WORKING
2. **Long-range sheets** (Type 2): require tracking cumulative winding and
   detecting when a downstream strand has accumulated enough winding to
   be topologically adjacent to an upstream strand

The winding infrastructure exists in TensionField (self.winding accumulates
+1/3.6 per helix residue and reverses at turns). The missing piece:
using the winding value to predict when long-range sheet contacts form.

### The ST Pair as Universal Sheet Marker

Ubiquitin has exactly ONE ST pair at position 65-66, in the loop between
strand 4 and strand 5. This is a local hairpin within the larger beta structure.
The other sheet connections are long-range and don't involve ST pairs.

In all of protein chemistry, only 3 amino acid pairs have CF depth = 1:
- SS (16) — perfect square, helix-internal
- **ST (20)** — distinct product, **hairpin turn**
- TT (25) — perfect square, helix-internal
