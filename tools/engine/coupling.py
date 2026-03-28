#!/usr/bin/env python3
"""Phi-scaled coupling operator and temporal domain engine.

Implements the cross-domain coupling from the Aramis Field:
    Phi^(d) <- Phi^(d) + sum_{d'!=d} eta_{dd'} * F_{dd'}(Phi^(d'))

Coupling strength decays exponentially with domain distance:
    eta_{dd'} = eta_0 * exp(-|d - d'| / N_coupling)

Within a domain, only octave (2:1) coupling is permitted —
biology selects octaves and rejects non-octave harmonics.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from .ratiospace import (
    ResonanceState, PHI, PHI_INV, ALPHA_BASE, DOMAIN_RATIOS,
    frequency_ratio, beat_frequency, is_octave, octave_distance,
    domain_distance, harmonic_stability_index, from_frequency
)


# === Coupling Parameters ===

@dataclass
class CouplingParams:
    """Parameters governing inter-mode coupling."""
    eta_0: float = 0.9          # base coupling strength
    n_coupling: float = 1.5     # domain distance decay constant
    octave_strength: float = 0.91   # intra-domain octave coupling (from data: 0.88-0.91)
    phase_lock_rate: float = 0.1    # how fast phases synchronize
    beat_threshold: float = 0.01    # minimum amplitude to generate beat frequencies
    vorticity_alpha: float = 0.05   # spiral dynamics strength (prevents singularities)


# === Coupling Functions ===

def cross_domain_coupling(source: ResonanceState, target: ResonanceState,
                           params: CouplingParams = None) -> float:
    """Compute coupling strength between two states.

    eta_{dd'} = eta_0 * exp(-|d - d'| / N_coupling) * octave_factor
    """
    params = params or CouplingParams()
    d_dist = domain_distance(source, target)
    o_dist = octave_distance(source, target)

    # Domain coupling: exponential decay with phi-domain distance
    domain_eta = params.eta_0 * math.exp(-d_dist / params.n_coupling)

    # Octave coupling: strong for 2:1, weaker for 4:1, etc.
    if o_dist == 0:
        octave_factor = 1.0
    elif is_octave(source, target):
        octave_factor = params.octave_strength ** o_dist
    else:
        # Non-octave: heavily suppressed (biology rejects these)
        octave_factor = 0.05 * (0.5 ** o_dist)

    # Amplitude modulation
    amp_factor = source.amplitude * target.amplitude

    return domain_eta * octave_factor * amp_factor


def phase_coupling_force(source: ResonanceState, target: ResonanceState,
                          coupling: float) -> float:
    """Compute the phase-pulling force between coupled oscillators.

    Kuramoto-style: d(phase)/dt = coupling * sin(phase_source - phase_target)
    """
    return coupling * math.sin(source.phase - target.phase)


def vorticity_correction(state: ResonanceState, neighbors: List[ResonanceState],
                          alpha: float = 0.05) -> float:
    """Compute the vorticity correction term (prevents singularities).

    From Kurtonian master equation: alpha * d/dPhi[1/2 * Omega(Phi)^2]
    In ratio-space, this becomes a phase-gradient penalty that
    routes energy into spiral patterns instead of collapse.

    Returns amplitude correction (added to state amplitude).
    """
    if not neighbors:
        return 0.0

    # Compute circulation: sum of phase differences around neighbors
    circulation = 0.0
    for n in neighbors:
        delta_phase = n.phase - state.phase
        # Wrap to [-pi, pi]
        delta_phase = (delta_phase + math.pi) % (2 * math.pi) - math.pi
        circulation += delta_phase

    # Winding number contribution
    winding_energy = 2 * math.pi * state.winding

    # Vorticity: |omega|^2
    omega_sq = (circulation + winding_energy) ** 2

    # Healing length: xi = sqrt(alpha / V''(A0))
    # For amplitude near 1.0: V''(A0) ~ 1, so xi ~ sqrt(alpha)
    healing_length = math.sqrt(alpha)

    # Correction: prevents amplitude from diverging
    # If amplitude is above 1 + healing_length, apply damping
    if state.amplitude > 1.0 + healing_length:
        return -alpha * omega_sq * (state.amplitude - 1.0)
    elif state.amplitude < healing_length:
        # Prevent collapse to zero
        return alpha * omega_sq * healing_length
    return 0.0


# === Temporal Domain Engine ===

@dataclass
class TemporalDomain:
    """A single phi-scaled temporal domain containing resonance modes."""
    index: int                          # domain index (-4 to +1)
    modes: List[ResonanceState] = field(default_factory=list)
    params: CouplingParams = field(default_factory=CouplingParams)

    @property
    def name(self):
        from .ratiospace import DOMAIN_NAMES
        return DOMAIN_NAMES.get(self.index, f"domain_{self.index}")

    @property
    def phi_ratio(self):
        return DOMAIN_RATIOS.get(self.index, 1.0)

    def add_mode(self, state: ResonanceState):
        state.domain = self.index
        self.modes.append(state)

    def intra_domain_step(self, dt: float):
        """Evolve modes within this domain for one timestep.

        Octave-coupled oscillators with phase synchronization.
        """
        for i, mode in enumerate(self.modes):
            # Phase advance: d(phase)/dt = 2*pi*frequency
            mode.phase = (mode.phase + 2 * math.pi * mode.frequency * dt) % (2 * math.pi)

            # Octave coupling within domain
            for j, other in enumerate(self.modes):
                if i == j:
                    continue
                coupling = cross_domain_coupling(mode, other, self.params)
                if coupling > 0.01:
                    # Phase pulling (Kuramoto)
                    force = phase_coupling_force(other, mode, coupling)
                    mode.phase = (mode.phase + self.params.phase_lock_rate * force * dt) % (2 * math.pi)

            # Vorticity correction
            neighbors = [m for k, m in enumerate(self.modes) if k != i]
            amp_correction = vorticity_correction(mode, neighbors, self.params.vorticity_alpha)
            mode.amplitude = max(0.0, min(2.0, mode.amplitude + amp_correction * dt))


@dataclass
class ResonanceEngine:
    """The six-domain phi-scaled temporal engine.

    Manages all six temporal domains and their cross-domain coupling.
    This is the main simulation container.
    """
    domains: Dict[int, TemporalDomain] = field(default_factory=dict)
    params: CouplingParams = field(default_factory=CouplingParams)
    time: float = 0.0
    beat_modes: List[ResonanceState] = field(default_factory=list)

    def __post_init__(self):
        # Initialize six temporal domains
        for d in range(-4, 2):
            if d not in self.domains:
                self.domains[d] = TemporalDomain(index=d, params=self.params)

    def add_mode(self, state: ResonanceState):
        """Add a resonance mode to the appropriate domain."""
        dom = state.domain
        if dom not in self.domains:
            self.domains[dom] = TemporalDomain(index=dom, params=self.params)
        self.domains[dom].add_mode(state)

    def all_modes(self) -> List[ResonanceState]:
        """Get all modes across all domains."""
        modes = []
        for d in sorted(self.domains.keys()):
            modes.extend(self.domains[d].modes)
        return modes

    def step(self, dt: float = 0.001):
        """Advance the engine by one timestep.

        1. Intra-domain evolution (octave coupling)
        2. Cross-domain coupling (phi-scaled)
        3. Beat frequency generation
        4. Vorticity correction
        """
        # Step 1: Intra-domain
        for domain in self.domains.values():
            domain.intra_domain_step(dt)

        # Step 2: Cross-domain coupling
        domain_indices = sorted(self.domains.keys())
        for i, d1 in enumerate(domain_indices):
            for d2 in domain_indices[i+1:]:
                self._couple_domains(d1, d2, dt)

        # Step 3: Beat frequency generation
        self._generate_beats()

        self.time += dt

    def _couple_domains(self, d1: int, d2: int, dt: float):
        """Apply cross-domain coupling between two temporal domains."""
        modes1 = self.domains[d1].modes
        modes2 = self.domains[d2].modes

        for m1 in modes1:
            for m2 in modes2:
                coupling = cross_domain_coupling(m1, m2, self.params)
                if coupling < 0.01:
                    continue

                # Bidirectional phase coupling
                force = phase_coupling_force(m1, m2, coupling)
                m1.phase = (m1.phase - self.params.phase_lock_rate * force * dt * 0.5) % (2 * math.pi)
                m2.phase = (m2.phase + self.params.phase_lock_rate * force * dt * 0.5) % (2 * math.pi)

                # Amplitude exchange (energy transfer between domains)
                amp_transfer = coupling * (m1.amplitude - m2.amplitude) * 0.01 * dt
                m1.amplitude = max(0.0, m1.amplitude - amp_transfer)
                m2.amplitude = max(0.0, m2.amplitude + amp_transfer)

    def _generate_beats(self):
        """Generate beat frequencies from interacting modes."""
        self.beat_modes.clear()
        all_modes = self.all_modes()

        for i in range(len(all_modes)):
            for j in range(i + 1, len(all_modes)):
                m1, m2 = all_modes[i], all_modes[j]
                if m1.amplitude < self.params.beat_threshold or m2.amplitude < self.params.beat_threshold:
                    continue
                bf = beat_frequency(m1, m2)
                if 0.01 < bf < 1000:  # Only biologically relevant beats
                    beat_amp = min(m1.amplitude, m2.amplitude) * 0.5
                    beat_state = from_frequency(bf, name=f"beat({m1.name},{m2.name})",
                                                 amplitude=beat_amp)
                    beat_state.metadata["source_a"] = m1.name
                    beat_state.metadata["source_b"] = m2.name
                    beat_state.metadata["type"] = "beat_frequency"
                    self.beat_modes.append(beat_state)

    def run(self, duration: float, dt: float = 0.001, sample_every: int = 100) -> list:
        """Run the engine for a duration, sampling state periodically.

        Returns list of snapshots: [(time, [mode_states], [beat_states])]
        """
        snapshots = []
        steps = int(duration / dt)
        for s in range(steps):
            self.step(dt)
            if s % sample_every == 0:
                modes_snap = [(m.name, m.frequency, m.amplitude, m.phase, m.band)
                              for m in self.all_modes()]
                beats_snap = [(b.name, b.frequency, b.amplitude)
                              for b in self.beat_modes[:10]]  # top 10 beats
                snapshots.append((self.time, modes_snap, beats_snap))
        return snapshots

    def report(self) -> str:
        """Generate a text report of current engine state."""
        lines = [f"=== Resonance Engine State (t={self.time:.4f}s) ===\n"]

        for d in sorted(self.domains.keys()):
            domain = self.domains[d]
            lines.append(f"  Domain {d} ({domain.name}, phi={domain.phi_ratio:.3f}):")
            for m in domain.modes:
                lines.append(f"    {m.name:25s}  {m.frequency:>10.2f} Hz  "
                             f"A={m.amplitude:.3f}  phase={math.degrees(m.phase):>6.1f} deg  "
                             f"w={m.winding}  [{m.band}]")
            if not domain.modes:
                lines.append("    (empty)")

        if self.beat_modes:
            lines.append(f"\n  Beat frequencies ({len(self.beat_modes)} active):")
            for b in sorted(self.beat_modes, key=lambda x: x.frequency)[:15]:
                lines.append(f"    {b.name:40s}  {b.frequency:>8.2f} Hz  A={b.amplitude:.3f}")

        # Coherence check
        all_m = self.all_modes()
        if len(all_m) >= 2:
            from .ratiospace import coherence_check
            coh = coherence_check(all_m)
            lines.append(f"\n  Phase coherence: PLV={coh['plv']:.3f} "
                         f"({'COHERENT' if coh['coherent'] else 'DECOHERENT'}, "
                         f"threshold={coh['threshold']})")

        return "\n".join(lines)
