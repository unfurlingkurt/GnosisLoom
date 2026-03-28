#!/usr/bin/env python3
"""Ratio-space state representation for the Geometric Resonance Engine.

Everything in this engine lives in ratio-space, not Euclidean space.
A state is specified by:
    - octave (int): position in 2:1 cascade from reference frequency
    - domain (int): which phi-scaled temporal domain (-4 to +1)
    - phase (float): angle 0..2*pi in oscillation cycle
    - amplitude (float): expression strength (0 = silent, 1 = full)
    - winding (int): topological charge (quantized, conserved)

No coordinates. No matrices. Ratios all the way down.
"""

import math
from dataclasses import dataclass, field
from typing import Optional

# === Constants ===

PHI = (1 + math.sqrt(5)) / 2      # 1.6180339887...
PHI_INV = 1 / PHI                  # 0.6180339887...
WATER_CLOCK = 1.86                 # H-O beat frequency (Hz) — universal reference
UBC = 497.0                        # Universal Biological Constant (Hz)
SCHUMANN = 7.83                    # Earth cavity resonance (Hz)
ALPHA_BASE = 10.0                  # Alpha brainwave — octave cascade origin

# Temporal domain phi-ratios (dimensionless scaling factors)
DOMAIN_RATIOS = {
    1: PHI,          # ultra_fast — gamma/high gamma
    0: 1.0,          # fast — beta
   -1: PHI_INV,      # medium — alpha
   -2: PHI_INV**2,   # slow — theta
   -3: PHI_INV**3,   # ultra_slow — delta
   -4: PHI_INV**4,   # quantum — sub-delta / planck
}

DOMAIN_NAMES = {
    1: "ultra_fast",
    0: "fast",
   -1: "medium",
   -2: "slow",
   -3: "ultra_slow",
   -4: "quantum",
}

# Brainwave band boundaries (Hz)
BANDS = {
    "delta":      (0.5, 4.0),
    "theta":      (4.0, 8.0),
    "alpha":      (8.0, 13.0),
    "beta":       (13.0, 30.0),
    "gamma":      (30.0, 100.0),
    "high_gamma": (100.0, 200.0),
    "ripple":     (200.0, 600.0),
}


# === Core State ===

@dataclass
class ResonanceState:
    """A single resonance mode in ratio-space.

    This is the fundamental unit — an oscillator defined entirely by
    ratios relative to reference frequencies, not by spatial coordinates.
    """
    octave: int = 0             # powers of 2 from reference (0 = alpha 10 Hz)
    domain: int = 0             # phi-domain index (-4 to +1)
    phase: float = 0.0          # radians [0, 2*pi)
    amplitude: float = 1.0      # [0, 1] expression strength
    winding: int = 0            # topological charge (quantized)
    name: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def frequency(self) -> float:
        """Compute Hz frequency from ratio coordinates."""
        return ALPHA_BASE * (2.0 ** self.octave) * DOMAIN_RATIOS.get(self.domain, 1.0)

    @property
    def domain_name(self) -> str:
        return DOMAIN_NAMES.get(self.domain, f"domain_{self.domain}")

    @property
    def band(self) -> str:
        """Which brainwave band this frequency falls in."""
        f = self.frequency
        for name, (lo, hi) in BANDS.items():
            if lo <= f < hi:
                return name
        if f < 0.5:
            return "sub_delta"
        return "supra_ripple"

    @property
    def water_clock_ratio(self) -> float:
        """Ratio to the water clock (H-O beat = 1.86 Hz)."""
        return self.frequency / WATER_CLOCK

    @property
    def schumann_ratio(self) -> float:
        """Ratio to Schumann resonance (7.83 Hz)."""
        return self.frequency / SCHUMANN

    def __repr__(self):
        return (f"ResonanceState({self.name or '?'}: oct={self.octave}, "
                f"dom={self.domain_name}, f={self.frequency:.2f} Hz, "
                f"A={self.amplitude:.2f}, w={self.winding})")


# === Ratio Arithmetic ===

def octave_distance(a: ResonanceState, b: ResonanceState) -> int:
    """Number of octave steps between two states."""
    return abs(a.octave - b.octave)


def domain_distance(a: ResonanceState, b: ResonanceState) -> int:
    """Number of phi-domain steps between two states."""
    return abs(a.domain - b.domain)


def frequency_ratio(a: ResonanceState, b: ResonanceState) -> float:
    """Ratio of frequencies (always >= 1)."""
    fa, fb = a.frequency, b.frequency
    if fa == 0 or fb == 0:
        return float('inf')
    return max(fa, fb) / min(fa, fb)


def is_octave(a: ResonanceState, b: ResonanceState, tolerance: float = 0.05) -> bool:
    """Check if two states are related by a power of 2."""
    ratio = frequency_ratio(a, b)
    if ratio == 0:
        return False
    log_ratio = math.log2(ratio)
    return abs(log_ratio - round(log_ratio)) < tolerance


def is_phi_related(a: ResonanceState, b: ResonanceState, tolerance: float = 0.05) -> bool:
    """Check if frequency ratio is near phi or its powers."""
    ratio = frequency_ratio(a, b)
    for n in range(-3, 4):
        target = PHI ** n
        if abs(ratio - target) / target < tolerance:
            return True
    return False


def nearest_integer_ratio(a: ResonanceState, b: ResonanceState) -> tuple:
    """Find the simplest integer ratio approximating the frequency ratio."""
    ratio = frequency_ratio(a, b)
    best_n, best_d, best_err = 1, 1, float('inf')
    for d in range(1, 13):
        n = round(ratio * d)
        if n < 1:
            continue
        err = abs(ratio - n / d)
        if err < best_err:
            best_n, best_d, best_err = n, d, err
    return best_n, best_d, best_err


def beat_frequency(a: ResonanceState, b: ResonanceState) -> float:
    """Beat frequency between two states (Hz)."""
    return abs(a.frequency - b.frequency)


def combined_frequency(a: ResonanceState, b: ResonanceState) -> float:
    """Sum frequency of two states (Hz)."""
    return a.frequency + b.frequency


# === Factory Functions ===

def from_frequency(freq: float, name: str = "", **kwargs) -> ResonanceState:
    """Create a ResonanceState from a raw Hz frequency.

    Finds the closest (octave, domain) coordinates.
    """
    if freq <= 0:
        return ResonanceState(octave=0, domain=-4, amplitude=0.0, name=name, **kwargs)

    best_oct, best_dom, best_err = 0, 0, float('inf')
    for dom_idx, dom_ratio in DOMAIN_RATIOS.items():
        # f = ALPHA_BASE * 2^oct * dom_ratio
        # oct = log2(f / (ALPHA_BASE * dom_ratio))
        oct_exact = math.log2(freq / (ALPHA_BASE * dom_ratio))
        oct_round = round(oct_exact)
        reconstructed = ALPHA_BASE * (2.0 ** oct_round) * dom_ratio
        err = abs(freq - reconstructed) / freq
        if err < best_err:
            best_oct, best_dom, best_err = oct_round, dom_idx, err

    return ResonanceState(octave=best_oct, domain=best_dom, name=name, **kwargs)


def from_nucleotide(base: str) -> ResonanceState:
    """Create a state for a DNA nucleotide base."""
    bases = {
        "A": (6.45, "adenine"),
        "T": (4.21, "thymine"),
        "G": (7.43, "guanine"),
        "C": (3.89, "cytosine"),
        "U": (4.21, "uracil"),   # RNA — same as thymine
    }
    freq, name = bases.get(base.upper(), (0, "unknown"))
    return from_frequency(freq, name=name, metadata={"type": "nucleotide", "base": base})


def from_amino_acid(code: str, freq: float, geometric_factor: float = 1.0) -> ResonanceState:
    """Create a state for an amino acid with its geometric resonance factor."""
    effective_freq = freq * geometric_factor
    return from_frequency(effective_freq, name=code,
                          metadata={"type": "amino_acid", "raw_freq": freq,
                                    "geometric_factor": geometric_factor})


def brainwave_cascade() -> list:
    """Generate the canonical 10→20→40→80 Hz octave cascade."""
    return [
        ResonanceState(octave=0, domain=-1, name="alpha",
                       metadata={"band": "alpha", "function": "sensory_gating"}),
        ResonanceState(octave=1, domain=-1, name="beta",
                       metadata={"band": "beta", "function": "cognition"}),
        ResonanceState(octave=2, domain=-1, name="gamma",
                       metadata={"band": "gamma", "function": "consciousness_binding"}),
        ResonanceState(octave=3, domain=-1, name="high_gamma",
                       metadata={"band": "high_gamma", "function": "sensory_integration"}),
    ]


def dna_base_pairs() -> dict:
    """Generate AT and GC base pair states with beat frequencies."""
    a = from_nucleotide("A")
    t = from_nucleotide("T")
    g = from_nucleotide("G")
    c = from_nucleotide("C")
    return {
        "A": a, "T": t, "G": g, "C": c,
        "AT_combined": from_frequency(combined_frequency(a, t), name="AT_pair"),
        "GC_combined": from_frequency(combined_frequency(g, c), name="GC_pair"),
        "AT_beat": from_frequency(beat_frequency(a, t), name="AT_beat_lock"),
        "GC_beat": from_frequency(beat_frequency(g, c), name="GC_beat_lock"),
    }


# === Stability Analysis ===

def harmonic_stability_index(state: ResonanceState, reference: ResonanceState = None) -> float:
    """Compute the Harmonic Ratio Stability Index.

    S = sum(1 / |r - n|) for n in {1, 2, 3/2, 4/3, phi}
    Higher S = more stable. Measures how close the frequency ratio
    is to simple harmonic relationships.
    """
    if reference is None:
        reference = ResonanceState(octave=0, domain=-1, name="alpha_ref")  # 10 Hz

    ratio = frequency_ratio(state, reference)
    if ratio == float('inf') or ratio == 0:
        return 0.0

    targets = [1.0, 2.0, 1.5, 4/3, PHI, 3.0, 4.0, 5.0, 8.0]
    s = 0.0
    for n in targets:
        diff = abs(ratio - n)
        if diff < 0.001:
            s += 1000.0  # near-perfect match
        else:
            s += 1.0 / diff
    return s


def golden_ratio_efficiency(ratio: float) -> float:
    """Golden ratio optimization: eta = 1 - |r - phi| / phi.

    Returns 1.0 when ratio = phi, decreasing as it deviates.
    """
    return max(0.0, 1.0 - abs(ratio - PHI) / PHI)


def coherence_check(states: list, threshold: float = 0.7) -> dict:
    """Check phase coherence across a set of states.

    Returns coherence metrics and whether the consciousness
    binding threshold (PLV >= 0.7) is met.
    """
    if len(states) < 2:
        return {"plv": 1.0, "coherent": True, "n_states": len(states)}

    # Phase Locking Value: PLV = |<e^(i * delta_phase)>|
    import cmath
    total = 0 + 0j
    n_pairs = 0
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            delta = states[i].phase - states[j].phase
            total += cmath.exp(1j * delta)
            n_pairs += 1

    plv = abs(total / n_pairs) if n_pairs > 0 else 1.0

    return {
        "plv": plv,
        "coherent": plv >= threshold,
        "n_states": len(states),
        "n_pairs": n_pairs,
        "threshold": threshold,
    }
