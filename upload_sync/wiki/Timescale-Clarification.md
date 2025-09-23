# Timescale Systems Clarification

**Tags**: `timescales` `phi-scaling` `dimensional-analysis` `reference`

---

## Overview

The Aramis Field Theory uses **two complementary timescale representations** that serve different purposes. This clarification prevents confusion between the mathematical core and illustrative examples.

---

## 1. φ-Based Scaling (Primary System)

**Source**: `sixtimescales.md` - Canonical LoomCore representation

### Mathematical Definition

```math
\tau_d = \phi^{n_d} \cdot \tau_0
```

Where:
- **τ_d**: Time step for domain d
- **φ = (1+√5)/2 ≈ 1.618**: Golden ratio
- **n_d**: Domain-specific exponent
- **τ_0**: Fundamental time unit

### Domain Values

| Domain | φ-Ratio | Exponent | Mathematical Basis |
|--------|---------|----------|-------------------|
| `ultra_fast` | φ ≈ 1.618 | +1 | φ¹ |
| `fast` | 1.0 | 0 | φ⁰ |
| `medium` | 0.618 | -1 | φ⁻¹ |
| `slow` | 0.382 | -2 | φ⁻² |
| `ultra_slow` | 0.236 | -3 | φ⁻³ |
| `quantum` | 0.146 | -4 | φ⁻⁴ |

### Properties

**Dimensionless**: Pure mathematical ratios independent of physical units
**Recursive**: Self-similar scaling across all domain levels
**Scale-Invariant**: Valid from quantum to cosmological applications
**Golden Ratio Foundation**: Ensures optimal information transfer between domains

---

## 2. Second-Based Timescales (Illustrative System)

**Purpose**: Educational tool for mapping φ-domains to familiar physical scales

### Example Mappings

| Domain | φ-Ratio | Example Timescale | Physical Analogs |
|--------|---------|-------------------|------------------|
| `ultra_fast` | 1.618 | ~10⁻¹⁵ s | Electromagnetic field oscillations |
| `fast` | 1.0 | ~10⁻⁹ s | Molecular bond vibrations |
| `medium` | 0.618 | ~10⁻³ s | Cellular metabolic cycles |
| `slow` | 0.382 | ~1 s | Neural oscillations, heartbeat |
| `ultra_slow` | 0.236 | ~10³ s | Circadian rhythms, organ cycles |
| `quantum` | 0.146 | ~10⁻²³ s | Planck-scale virtual processes |

### Important Limitations

**Not Fundamental**: These are approximate anchor points only
**Context-Dependent**: Actual timescales depend on system being modeled
**Illustrative Only**: Used for communication, not computation

---

## 3. Usage Guidelines

### For Core Theory and Simulations

**Always use φ-based scaling**:
```python
# Correct: dimensionless φ-ratios
alpha_d = phi_ratios[domain] * base_alpha
dt_d = phi_ratios[domain] * dt_fundamental

# Evolution with φ-scaling
Phi_new[d] = evolve_field(Phi[d], alpha_d, dt_d)
```

### For Communication and Documentation

**Use both systems with clear labeling**:
```markdown
The medium domain (φ-ratio: 0.618) operates at millisecond timescales
(~10⁻³ s) corresponding to cellular processes.
```

### For External Publications

**Lead with physical examples, specify φ-foundation**:
> "The field evolves across six temporal domains spanning from femtosecond
> electromagnetic processes to kilosecond biological rhythms, with mathematical
> scaling based on golden ratio relationships (φ = 1.618...)."

---

## 4. Mathematical Relationship

### Conversion Formula

For a specific physical system with characteristic time T₀:

```math
t_{physical} = T_0 \cdot \phi^{n_d}
```

**Example**: Neural system with T₀ = 10 ms
- **Medium domain**: t = 10ms × φ⁻¹ ≈ 6.2 ms
- **Slow domain**: t = 10ms × φ⁻² ≈ 3.8 ms
- **Ultra_slow domain**: t = 10ms × φ⁻³ ≈ 2.4 ms

### Domain Coupling Strength

```math
\eta_{dd'} = \eta_0 \cdot \exp\left(-\frac{|n_d - n_{d'}|}{N_{coupling}}\right)
```

Where coupling decreases exponentially with φ-domain separation.

---

## 5. Implementation Standards

### Code Documentation

```python
def get_domain_timescale(domain, base_time=1.0):
    """
    Get φ-scaled timescale for domain

    Args:
        domain: str, one of ['ultra_fast', 'fast', 'medium', 'slow', 'ultra_slow', 'quantum']
        base_time: float, fundamental time unit (dimensionless in φ-system)

    Returns:
        float: φ-scaled time step (dimensionless)

    Note: For physical applications, multiply by appropriate time constant
    """
    phi_ratios = {
        'ultra_fast': 1.618,
        'fast': 1.0,
        'medium': 0.618,
        'slow': 0.382,
        'ultra_slow': 0.236,
        'quantum': 0.146
    }
    return phi_ratios[domain] * base_time
```

### Error Prevention

**Common Mistake**: Mixing φ-ratios with second-based values
```python
# Wrong: mixing systems
dt = 0.618 * 1e-3  # φ-ratio × seconds = dimensional inconsistency

# Correct: consistent φ-system
dt = phi_ratios['medium'] * dt_base  # dimensionless
```

---

## 6. References

**Core Framework**: See [LoomCore Temporal Domains](../tools/temporal_domains.py)
**Field Evolution**: [Aramis Field Substrate](02-Aramis-Field-Substrate.md)
**Mathematical Foundation**: [First-Principles Derivation](03-First-Principles-Derivation.md)

---

**Summary**: Always use φ-based scaling for mathematics and computation. Second-based examples are communication tools only, clearly labeled as illustrative.