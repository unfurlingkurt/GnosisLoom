#!/usr/bin/env python3
"""Discrete threshold detector for folding, consciousness, and disease.

Biology operates on discrete threshold crossings, not continuous dynamics:
- Protein helix nucleation: frequency sum > 20 Hz
- Protein sheet nucleation: frequency sum > 25 Hz
- Turn formation: frequency < 5 Hz
- Consciousness binding: PLV >= 0.7 at 40 Hz gamma
- Disease onset: octave ratio drift beyond tolerance

These are geometric state transitions — the system snaps between
discrete states when threshold ratios are crossed.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .ratiospace import (
    ResonanceState, PHI, ALPHA_BASE, from_frequency, from_amino_acid,
    frequency_ratio, is_octave, coherence_check, harmonic_stability_index,
    beat_frequency, combined_frequency
)


# === Protein Folding Thresholds ===

class FoldingState(Enum):
    COIL = "random_coil"          # < 10% frequency coordination
    MOLTEN = "molten_globule"     # 40-60% coordination
    HELIX = "alpha_helix"         # nucleation > 20 Hz
    SHEET = "beta_sheet"          # nucleation > 25 Hz
    TURN = "turn"                 # flexibility < 5 Hz
    NATIVE = "native"             # full coordination


# Geometric factors from the framework
GEOMETRIC_FACTORS = {
    "alpha_helix": 0.85,
    "beta_sheet": 0.92,
    "type_I_turn": 0.65,
    "type_II_turn": 0.45,
    "random_coil": 0.20,
    "omega_loop": 0.78,
}

# Amino acid frequencies (Hz) from the database
AMINO_ACID_FREQS = {
    "GLY": 3.10, "ALA": 4.63, "VAL": 7.69, "LEU": 9.22, "ILE": 9.22,
    "PRO": 8.87, "PHE": 13.01, "TRP": 16.25, "MET": 10.95, "SER": 6.12,
    "THR": 7.65, "CYS": 8.72, "TYR": 14.54, "HIS": 11.55, "ASP": 9.51,
    "GLU": 10.33, "ASN": 7.72, "GLN": 9.25, "LYS": 10.52, "ARG": 12.62,
}

# Helix/sheet propensity (simplified from database)
HELIX_PROPENSITY = {"ALA", "LEU", "MET", "GLU", "LYS", "ARG"}
SHEET_PROPENSITY = {"VAL", "ILE", "PHE", "TYR", "TRP", "THR"}
TURN_PROPENSITY = {"GLY", "PRO", "ASN", "SER"}


@dataclass
class FoldingSimulator:
    """Discrete threshold simulator for protein folding.

    Takes a sequence of amino acid codes and determines folding state
    by checking frequency sums against discrete thresholds.
    """
    sequence: List[str] = field(default_factory=list)
    window_size: int = 4    # residues considered for nucleation
    states: List[FoldingState] = field(default_factory=list)

    def fold(self) -> List[Tuple[int, FoldingState, float]]:
        """Run the folding simulation.

        Returns list of (position, folding_state, effective_frequency) tuples.
        """
        results = []
        n = len(self.sequence)

        for i in range(n):
            # Get window of residues
            window = self.sequence[max(0, i - self.window_size // 2):
                                   min(n, i + self.window_size // 2 + 1)]

            # Sum frequencies in window
            freq_sum = sum(AMINO_ACID_FREQS.get(aa, 5.0) for aa in window)

            # Count propensities
            helix_count = sum(1 for aa in window if aa in HELIX_PROPENSITY)
            sheet_count = sum(1 for aa in window if aa in SHEET_PROPENSITY)
            turn_count = sum(1 for aa in window if aa in TURN_PROPENSITY)

            # Apply geometric factors and check thresholds
            aa = self.sequence[i]
            raw_freq = AMINO_ACID_FREQS.get(aa, 5.0)

            if turn_count >= 2 and raw_freq < 5.0:
                # Turn threshold: low frequency + turn-prone residues
                state = FoldingState.TURN
                eff_freq = raw_freq * GEOMETRIC_FACTORS["type_I_turn"]
            elif helix_count >= 3 and freq_sum * GEOMETRIC_FACTORS["alpha_helix"] > 20.0:
                # Helix nucleation threshold: > 20 Hz
                state = FoldingState.HELIX
                eff_freq = raw_freq * GEOMETRIC_FACTORS["alpha_helix"]
            elif sheet_count >= 2 and freq_sum * GEOMETRIC_FACTORS["beta_sheet"] > 25.0:
                # Sheet nucleation threshold: > 25 Hz
                state = FoldingState.SHEET
                eff_freq = raw_freq * GEOMETRIC_FACTORS["beta_sheet"]
            elif freq_sum > 15.0:
                # Molten globule: partial coordination
                state = FoldingState.MOLTEN
                eff_freq = raw_freq * GEOMETRIC_FACTORS["random_coil"]
            else:
                state = FoldingState.COIL
                eff_freq = raw_freq * GEOMETRIC_FACTORS["random_coil"]

            results.append((i, state, eff_freq))

        self.states = [r[1] for r in results]
        return results

    def coordination_percentage(self) -> float:
        """Fraction of residues in structured states (helix/sheet/turn)."""
        if not self.states:
            return 0.0
        structured = sum(1 for s in self.states
                         if s in (FoldingState.HELIX, FoldingState.SHEET, FoldingState.TURN))
        return structured / len(self.states)

    def report(self) -> str:
        """Generate a folding report."""
        results = self.fold()
        lines = ["=== Protein Folding Simulation ===\n"]
        lines.append(f"  Sequence: {''.join(self.sequence[:50])}{'...' if len(self.sequence) > 50 else ''}")
        lines.append(f"  Length: {len(self.sequence)} residues\n")

        # Summary
        state_counts = {}
        for _, state, _ in results:
            state_counts[state.value] = state_counts.get(state.value, 0) + 1

        lines.append("  Secondary Structure Prediction:")
        for state, count in sorted(state_counts.items()):
            pct = count / len(results) * 100
            bar = "█" * int(pct / 2)
            lines.append(f"    {state:20s} {count:4d} ({pct:5.1f}%) {bar}")

        lines.append(f"\n  Coordination: {self.coordination_percentage()*100:.1f}%")

        # Detailed residue view (first 60)
        lines.append("\n  Residue Map (H=helix, E=sheet, T=turn, C=coil, M=molten):")
        state_chars = {
            FoldingState.HELIX: "H", FoldingState.SHEET: "E",
            FoldingState.TURN: "T", FoldingState.COIL: "C",
            FoldingState.MOLTEN: "M", FoldingState.NATIVE: "N",
        }
        seq_line = "    " + "".join(self.sequence[:60])
        str_line = "    " + "".join(state_chars.get(r[1], "?") for r in results[:60])
        lines.append(seq_line)
        lines.append(str_line)

        return "\n".join(lines)


# === Consciousness Threshold ===

@dataclass
class ConsciousnessMonitor:
    """Monitor consciousness binding through gamma coherence.

    Consciousness emerges when:
    1. Gamma (40 Hz) mode is active (amplitude > threshold)
    2. Phase locking value (PLV) across gamma-band modes >= 0.7
    3. Octave cascade intact (10→20→40→80 Hz ratios preserved)
    """
    gamma_threshold: float = 0.3       # minimum gamma amplitude
    plv_threshold: float = 0.7         # phase locking threshold
    octave_tolerance: float = 0.1      # how much octave ratios can drift

    def check(self, modes: List[ResonanceState]) -> dict:
        """Check consciousness binding status."""
        # Find gamma-band modes
        gamma_modes = [m for m in modes if 30 <= m.frequency <= 100 and m.amplitude > 0.1]
        alpha_modes = [m for m in modes if 8 <= m.frequency <= 13 and m.amplitude > 0.1]
        beta_modes = [m for m in modes if 13 < m.frequency <= 30 and m.amplitude > 0.1]

        # Check 1: Gamma active
        gamma_active = any(m.amplitude >= self.gamma_threshold for m in gamma_modes)

        # Check 2: Phase coherence
        coh = coherence_check(gamma_modes, self.plv_threshold) if len(gamma_modes) >= 2 else {"plv": 0.0, "coherent": False}

        # Check 3: Octave cascade integrity
        cascade_intact = self._check_octave_cascade(alpha_modes, beta_modes, gamma_modes)

        # Overall binding
        bound = gamma_active and coh["coherent"] and cascade_intact

        return {
            "bound": bound,
            "gamma_active": gamma_active,
            "gamma_count": len(gamma_modes),
            "plv": coh["plv"],
            "phase_coherent": coh["coherent"],
            "cascade_intact": cascade_intact,
            "alpha_count": len(alpha_modes),
            "beta_count": len(beta_modes),
        }

    def _check_octave_cascade(self, alphas, betas, gammas) -> bool:
        """Verify 10→20→40 octave ratios are intact."""
        if not alphas or not gammas:
            return False
        for a in alphas:
            for g in gammas:
                ratio = g.frequency / a.frequency
                # Should be near 4.0 (two octaves)
                if abs(ratio - 4.0) / 4.0 < self.octave_tolerance:
                    return True
        return False


# === Disease / Decoherence Threshold ===

@dataclass
class DecoherenceTracker:
    """Track ratio drift that indicates disease onset.

    Disease = loss of geometric coherence:
    - CFS: mitochondria drops 10 Hz → 0.1 Hz (100x collapse)
    - Fibromyalgia: spinal gate 20 Hz → 5 Hz (4:1 → 1:2 ratio inversion)
    - SIDS: cardiac rhythm complete loss

    Monitors octave ratios and flags when they drift beyond tolerance.
    """
    reference_ratios: Dict[str, float] = field(default_factory=dict)
    tolerance: float = 0.2     # 20% ratio drift triggers warning
    critical: float = 0.5      # 50% drift is critical decoherence

    def set_healthy_baseline(self, modes: List[ResonanceState]):
        """Record healthy frequency ratios as reference."""
        self.reference_ratios.clear()
        for i, m1 in enumerate(modes):
            for m2 in modes[i+1:]:
                key = f"{m1.name}:{m2.name}"
                if m1.frequency > 0 and m2.frequency > 0:
                    self.reference_ratios[key] = m1.frequency / m2.frequency

    def check(self, modes: List[ResonanceState]) -> dict:
        """Check current state against healthy baseline."""
        mode_dict = {m.name: m for m in modes}
        warnings = []
        critical_flags = []

        for key, ref_ratio in self.reference_ratios.items():
            name_a, name_b = key.split(":")
            if name_a not in mode_dict or name_b not in mode_dict:
                continue
            current_ratio = mode_dict[name_a].frequency / mode_dict[name_b].frequency
            if ref_ratio == 0:
                continue
            drift = abs(current_ratio - ref_ratio) / ref_ratio

            if drift > self.critical:
                critical_flags.append({
                    "pair": key,
                    "reference_ratio": ref_ratio,
                    "current_ratio": current_ratio,
                    "drift": drift,
                    "severity": "CRITICAL",
                })
            elif drift > self.tolerance:
                warnings.append({
                    "pair": key,
                    "reference_ratio": ref_ratio,
                    "current_ratio": current_ratio,
                    "drift": drift,
                    "severity": "WARNING",
                })

        total_pairs = len(self.reference_ratios)
        healthy_pairs = total_pairs - len(warnings) - len(critical_flags)

        return {
            "healthy": len(critical_flags) == 0 and len(warnings) <= total_pairs * 0.1,
            "coherence_ratio": healthy_pairs / total_pairs if total_pairs > 0 else 1.0,
            "warnings": warnings,
            "critical": critical_flags,
            "total_pairs": total_pairs,
        }


# === DNA Base Pair Stability ===

def base_pair_stability(seq: str) -> List[dict]:
    """Analyze DNA sequence for base pair frequency stability.

    Each base pair has discrete beat-frequency locks:
    - AT: beat = 2.24 Hz (weaker, 2 H-bonds)
    - GC: beat = 3.54 Hz (stronger, 3 H-bonds)

    Returns per-position stability analysis.
    """
    from .ratiospace import from_nucleotide, beat_frequency as bf, combined_frequency as cf

    complement = {"A": "T", "T": "A", "G": "C", "C": "G"}
    results = []

    for i, base in enumerate(seq.upper()):
        comp = complement.get(base, "?")
        if comp == "?":
            results.append({"pos": i, "base": base, "stable": False})
            continue

        s1 = from_nucleotide(base)
        s2 = from_nucleotide(comp)
        beat = bf(s1, s2)
        combined = cf(s1, s2)

        # Stability: GC pairs (beat=3.54) are more stable than AT (beat=2.24)
        is_gc = base in "GC"
        stability = 0.8 if is_gc else 0.6  # GC > AT stability

        # Water clock ratio
        from .ratiospace import WATER_CLOCK
        water_ratio = beat / WATER_CLOCK

        results.append({
            "pos": i,
            "pair": f"{base}-{comp}",
            "beat_freq": beat,
            "combined_freq": combined,
            "stability": stability,
            "h_bonds": 3 if is_gc else 2,
            "water_clock_ratio": water_ratio,
        })

    return results
