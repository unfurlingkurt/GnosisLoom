#!/usr/bin/env python3
"""GnosisLoom Geometric Resonance Engine — Demonstration.

Run: python -m tools.engine.demo
  or: python tools/engine/demo.py
"""

import math
import sys
from pathlib import Path

# Handle imports whether run as module or script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.engine.ratiospace import (
    ResonanceState, PHI, ALPHA_BASE, WATER_CLOCK, SCHUMANN, UBC,
    from_frequency, from_nucleotide, brainwave_cascade, dna_base_pairs,
    frequency_ratio, beat_frequency, is_octave, is_phi_related,
    nearest_integer_ratio, harmonic_stability_index, golden_ratio_efficiency,
    coherence_check, DOMAIN_RATIOS, DOMAIN_NAMES,
)
from tools.engine.coupling import (
    ResonanceEngine, TemporalDomain, CouplingParams,
    cross_domain_coupling, vorticity_correction,
)
from tools.engine.thresholds import (
    FoldingSimulator, FoldingState, ConsciousnessMonitor,
    DecoherenceTracker, base_pair_stability, AMINO_ACID_FREQS,
)


def divider(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_ratiospace():
    """Demonstrate ratio-space representation."""
    divider("1. RATIO-SPACE: THE SIX TEMPORAL DOMAINS")

    print("  Each domain scales by phi (1.618...) from its neighbor:\n")
    print(f"  {'Domain':12s} {'Index':>6s} {'phi-Ratio':>10s} {'10 Hz at':>12s} {'Band':>12s}")
    print(f"  {'─'*12} {'─'*6} {'─'*10} {'─'*12} {'─'*12}")
    for d in sorted(DOMAIN_RATIOS.keys(), reverse=True):
        ratio = DOMAIN_RATIOS[d]
        freq = ALPHA_BASE * ratio
        state = from_frequency(freq)
        print(f"  {DOMAIN_NAMES[d]:12s} {d:>6d} {ratio:>10.4f} {freq:>10.2f} Hz {state.band:>12s}")

    print(f"\n  Golden ratio phi = {PHI:.10f}")
    print(f"  Water clock = {WATER_CLOCK} Hz (H-O beat)")
    print(f"  Universal Biological Constant = {UBC} Hz")
    print(f"  Schumann resonance = {SCHUMANN} Hz")


def demo_octave_cascade():
    """Demonstrate the brainwave octave cascade."""
    divider("2. THE OCTAVE CASCADE: 10 → 20 → 40 → 80 Hz")

    cascade = brainwave_cascade()
    print("  Biology selects ONLY octave harmonics (2:1 ratios).")
    print("  Non-octave frequencies (30, 50, 60, 70 Hz) are absent.\n")

    prev = None
    for state in cascade:
        ratio_str = ""
        if prev:
            r = state.frequency / prev.frequency
            ratio_str = f"  ×{r:.0f} from {prev.name}"
        print(f"  {state.name:15s}  {state.frequency:>8.2f} Hz  "
              f"octave={state.octave}  domain={state.domain_name}{ratio_str}")
        prev = state

    # Check all pairs are octave-related
    print("\n  Octave verification:")
    for i in range(len(cascade)):
        for j in range(i+1, len(cascade)):
            a, b = cascade[i], cascade[j]
            n, d, err = nearest_integer_ratio(a, b)
            print(f"    {a.name:12s} → {b.name:12s}: "
                  f"ratio {n}:{d} (err={err:.4f})  "
                  f"octave={is_octave(a, b)}")

    # Schumann bridge
    schumann = from_frequency(SCHUMANN, name="schumann")
    alpha = cascade[0]
    ratio = frequency_ratio(schumann, alpha)
    print(f"\n  Schumann-Alpha bridge: {SCHUMANN}/{ALPHA_BASE} = {ratio:.3f}")
    print(f"    NOT an integer ratio — this is a phi-domain bridge, not an octave.")
    print(f"    phi-related = {is_phi_related(schumann, alpha)}")


def demo_dna_frequency():
    """Demonstrate DNA base pair frequency architecture."""
    divider("3. DNA FREQUENCY ARCHITECTURE")

    pairs = dna_base_pairs()

    print("  Nucleotide bases sit in the alpha/theta band:\n")
    print(f"  {'Base':10s} {'Frequency':>10s} {'Band':>12s} {'Water Ratio':>12s}")
    print(f"  {'─'*10} {'─'*10} {'─'*12} {'─'*12}")
    for base in ["C", "T", "A", "G"]:
        s = pairs[base]
        print(f"  {s.name:10s} {s.frequency:>8.2f} Hz {s.band:>12s} {s.water_clock_ratio:>10.2f}x")

    print(f"\n  Base pair locking (discrete beat frequencies):\n")
    at = pairs["AT_beat"]
    gc = pairs["GC_beat"]
    at_comb = pairs["AT_combined"]
    gc_comb = pairs["GC_combined"]

    print(f"  AT pair: combined = {at_comb.frequency:.2f} Hz, beat = {at.frequency:.2f} Hz (2 H-bonds)")
    print(f"  GC pair: combined = {gc_comb.frequency:.2f} Hz, beat = {gc.frequency:.2f} Hz (3 H-bonds)")
    print(f"\n  AT combined ({at_comb.frequency:.2f} Hz) ≈ alpha baseline ({ALPHA_BASE} Hz)")
    print(f"  GC combined ({gc_comb.frequency:.2f} Hz) ≈ Sol-Arcturus beat (11.3 Hz)")
    print(f"\n  A/T frequency ratio: {pairs['A'].frequency / pairs['T'].frequency:.3f}")
    print(f"  G/C frequency ratio: {pairs['G'].frequency / pairs['C'].frequency:.3f}")

    # DNA sequence stability
    seq = "ATCGATCGATCG"
    print(f"\n  Base pair stability for sequence: {seq}")
    stability = base_pair_stability(seq)
    for bp in stability:
        bar = "█" * int(bp["stability"] * 20)
        print(f"    pos {bp['pos']:2d}: {bp['pair']}  beat={bp['beat_freq']:.2f} Hz  "
              f"H-bonds={bp['h_bonds']}  {bar}")


def demo_protein_folding():
    """Demonstrate discrete threshold protein folding."""
    divider("4. PROTEIN FOLDING: DISCRETE THRESHOLDS")

    print("  Folding uses discrete frequency thresholds, not continuous dynamics:")
    print("    Helix nucleation: freq_sum × 0.85 > 20 Hz")
    print("    Sheet nucleation: freq_sum × 0.92 > 25 Hz")
    print("    Turn formation: residue freq < 5 Hz + turn-prone neighbors\n")

    # Example: a mixed-structure peptide
    seq = ["ALA", "LEU", "GLU", "ALA", "LEU", "MET",   # helix segment
           "GLY", "PRO", "ASN",                           # turn
           "VAL", "ILE", "PHE", "TYR", "VAL", "ILE",    # sheet segment
           "GLY", "SER",                                   # turn
           "ALA", "ARG", "LEU", "GLU"]                    # helix

    sim = FoldingSimulator(sequence=seq, window_size=4)
    print(sim.report())

    print(f"\n  Amino acid frequencies driving the thresholds:")
    print(f"  {'AA':5s} {'Freq':>8s} {'Band':>10s}")
    print(f"  {'─'*5} {'─'*8} {'─'*10}")
    for aa in ["GLY", "ALA", "VAL", "LEU", "PHE", "TRP"]:
        f = AMINO_ACID_FREQS[aa]
        s = from_frequency(f)
        print(f"  {aa:5s} {f:>6.2f} Hz {s.band:>10s}")


def demo_consciousness():
    """Demonstrate consciousness binding threshold."""
    divider("5. CONSCIOUSNESS BINDING: 40 Hz GAMMA COHERENCE")

    monitor = ConsciousnessMonitor()

    # Healthy state: all modes active and phase-locked
    print("  Healthy state (octave cascade intact, gamma active):\n")
    healthy_modes = [
        ResonanceState(octave=0, domain=-1, name="alpha", amplitude=0.8, phase=0.0),
        ResonanceState(octave=1, domain=-1, name="beta", amplitude=0.7, phase=0.1),
        ResonanceState(octave=2, domain=-1, name="gamma", amplitude=0.9, phase=0.05),
        ResonanceState(octave=3, domain=-1, name="high_gamma", amplitude=0.6, phase=0.15),
    ]
    result = monitor.check(healthy_modes)
    for k, v in result.items():
        print(f"    {k:20s}: {v}")

    # CFS state: mitochondria collapsed, gamma weakened
    print(f"\n  CFS state (mitochondrial collapse, gamma weakened):\n")
    cfs_modes = [
        ResonanceState(octave=0, domain=-1, name="alpha", amplitude=0.4, phase=0.0),
        ResonanceState(octave=1, domain=-1, name="beta", amplitude=0.3, phase=0.8),
        # Gamma frequency shifted and weakened
        from_frequency(25.0, name="gamma_cfs", amplitude=0.2, phase=2.1),
        ResonanceState(octave=3, domain=-1, name="high_gamma", amplitude=0.1, phase=1.5),
    ]
    result = monitor.check(cfs_modes)
    for k, v in result.items():
        print(f"    {k:20s}: {v}")


def demo_decoherence():
    """Demonstrate disease as ratio decoherence."""
    divider("6. DISEASE = RATIO DECOHERENCE")

    tracker = DecoherenceTracker(tolerance=0.2, critical=0.5)

    # Set healthy baseline
    healthy = [
        from_frequency(10.0, name="mitochondria"),
        from_frequency(20.0, name="spinal_gate"),
        from_frequency(40.0, name="brain_gamma"),
        from_frequency(80.0, name="cortex"),
        from_frequency(1.54, name="heart"),
        from_frequency(100.0, name="ATP_synthase"),
    ]
    tracker.set_healthy_baseline(healthy)
    print(f"  Healthy baseline: {len(tracker.reference_ratios)} ratio pairs tracked\n")

    # Check healthy
    result = tracker.check(healthy)
    print(f"  Healthy check: coherence={result['coherence_ratio']:.0%}, "
          f"healthy={result['healthy']}")

    # Simulate CFS: mitochondria collapse
    print(f"\n  Simulating CFS (mitochondria 10 Hz → 0.1 Hz):\n")
    cfs = [
        from_frequency(0.1, name="mitochondria"),    # 100x collapse!
        from_frequency(5.0, name="spinal_gate"),     # 75% drop
        from_frequency(25.0, name="brain_gamma"),    # 37.5% drop
        from_frequency(80.0, name="cortex"),
        from_frequency(1.2, name="heart"),           # 22% drop
        from_frequency(20.0, name="ATP_synthase"),   # 80% drop
    ]
    result = tracker.check(cfs)
    print(f"  CFS check: coherence={result['coherence_ratio']:.0%}, "
          f"healthy={result['healthy']}")
    print(f"  Warnings: {len(result['warnings'])}, Critical: {len(result['critical'])}")

    if result['critical']:
        print(f"\n  Critical decoherence events:")
        for c in result['critical'][:5]:
            print(f"    {c['pair']:35s} ratio {c['reference_ratio']:.2f} → {c['current_ratio']:.2f} "
                  f"(drift {c['drift']:.0%})")


def demo_engine_run():
    """Demonstrate the full resonance engine."""
    divider("7. RESONANCE ENGINE: SIX-DOMAIN SIMULATION")

    engine = ResonanceEngine(params=CouplingParams(
        eta_0=0.9, n_coupling=1.5, octave_strength=0.91,
        phase_lock_rate=0.1, vorticity_alpha=0.05,
    ))

    # Populate with brainwave cascade
    for state in brainwave_cascade():
        engine.add_mode(state)

    # Add Schumann resonance (planetary domain)
    schumann = from_frequency(SCHUMANN, name="schumann")
    schumann.domain = -2  # slow domain (theta)
    engine.add_mode(schumann)

    # Add mitochondrial base
    mito = from_frequency(10.0, name="mitochondria")
    mito.domain = -1  # medium domain
    engine.add_mode(mito)

    # Add heart rhythm
    heart = from_frequency(1.54, name="heart")
    heart.domain = -3  # ultra_slow domain
    engine.add_mode(heart)

    # Add water clock
    water = from_frequency(WATER_CLOCK, name="water_clock")
    water.domain = -3
    engine.add_mode(water)

    print("  Initial state:")
    print(engine.report())

    # Run for a short time
    print(f"\n  Running 100 steps (dt=0.001s)...")
    snapshots = engine.run(duration=0.1, dt=0.001, sample_every=50)

    print(f"\n  After evolution:")
    print(engine.report())

    # Show coupling strengths
    print(f"\n  Cross-domain coupling matrix:")
    modes = engine.all_modes()
    print(f"  {'':20s}", end="")
    for m in modes[:6]:
        print(f" {m.name[:8]:>8s}", end="")
    print()
    for m1 in modes[:6]:
        print(f"  {m1.name[:20]:20s}", end="")
        for m2 in modes[:6]:
            c = cross_domain_coupling(m1, m2)
            if m1.name == m2.name:
                print(f"    —   ", end="")
            else:
                print(f" {c:>7.3f}", end="")
        print()


def demo_harmonic_stability():
    """Show stability analysis across key frequencies."""
    divider("8. HARMONIC STABILITY INDEX")

    print("  How stable is each frequency relative to the alpha baseline (10 Hz)?")
    print("  Higher S = more harmonically stable.\n")

    test_freqs = [
        (WATER_CLOCK, "water_clock"),
        (SCHUMANN, "schumann"),
        (10.0, "alpha"),
        (20.0, "beta"),
        (40.0, "gamma"),
        (80.0, "high_gamma"),
        (6.45, "adenine"),
        (7.43, "guanine"),
        (1.54, "heart"),
        (UBC, "UBC_497"),
    ]

    ref = from_frequency(ALPHA_BASE, name="alpha_ref")
    results = []
    for freq, name in test_freqs:
        state = from_frequency(freq, name=name)
        s = harmonic_stability_index(state, ref)
        ratio = freq / ALPHA_BASE
        phi_eff = golden_ratio_efficiency(ratio)
        results.append((name, freq, s, ratio, phi_eff))

    results.sort(key=lambda x: x[2], reverse=True)

    print(f"  {'Entity':15s} {'Hz':>10s} {'Stability':>10s} {'Ratio':>8s} {'phi-eff':>8s}")
    print(f"  {'─'*15} {'─'*10} {'─'*10} {'─'*8} {'─'*8}")
    for name, freq, s, ratio, phi_eff in results:
        bar = "█" * min(50, int(s / 20))
        print(f"  {name:15s} {freq:>10.2f} {s:>10.1f} {ratio:>8.3f} {phi_eff:>8.3f}  {bar}")


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║         GNOSISLOOM GEOMETRIC RESONANCE ENGINE                   ║
    ║         Ratio-Space Computation — No Linear Algebra             ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    demo_ratiospace()
    demo_octave_cascade()
    demo_dna_frequency()
    demo_protein_folding()
    demo_consciousness()
    demo_decoherence()
    demo_engine_run()
    demo_harmonic_stability()

    divider("SUMMARY")
    print("  This engine operates entirely in ratio-space:")
    print("  - States defined by (octave, domain, phase, amplitude, winding)")
    print("  - No spatial coordinates, no matrices, no linear algebra")
    print("  - Phi-scaled temporal domains with octave-only selection")
    print("  - Discrete thresholds for folding, consciousness, disease")
    print("  - Beat frequencies generate emergent oscillations")
    print("  - Vorticity prevents singularities (spiral dynamics)")
    print("  - Disease = ratio decoherence (geometric, not chemical)")
    print()


if __name__ == "__main__":
    main()
