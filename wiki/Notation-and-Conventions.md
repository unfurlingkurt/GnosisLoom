# Notation and Conventions

**Unified mathematical notation system for the Aramis Field Theory (AFT) framework and biofrequency research. This page ensures consistency across all theoretical derivations, experimental reports, and computational implementations.**

---

## Core AFT Symbols

### **Field Variables**
| Symbol | Meaning | Units | Domain | Definition |
|--------|---------|-------|--------|------------|
| **Φ** | Complex substrate field | Dimensionless | Universal | Primary field variable: Φ = A e^{iθ} |
| **A** | Field amplitude | Dimensionless | Universal | Real amplitude: A = |Φ| ≥ 0 |
| **θ** | Field phase | Radians | Universal | Phase angle: θ = arg(Φ) |
| **Ω** | Vorticity field | m⁻¹ | Universal | Ω = ∇ × ∇θ (circulation density) |
| **ξ** | Healing length | Meters | Universal | ξ = √(α/V''(A₀)) |

### **Parameters and Constants**
| Symbol | Meaning | Units | Typical Value | Physical Significance |
|--------|---------|-------|---------------|----------------------|
| **α** | Vorticity coupling | J·m² | 10⁻³⁴ | Strength of spiral dynamics |
| **λ₀** | Fundamental wavelength | Meters | 10⁻³⁵ | Planck-scale substrate structure |
| **τ₀** | Fundamental time | Seconds | 10⁻⁴³ | Planck-scale temporal quantum |
| **φ** | Golden ratio | Dimensionless | 1.618... | Temporal domain scaling factor |
| **A₀** | Vacuum expectation | Dimensionless | 1 | Equilibrium field amplitude |

### **Operators and Derivatives**
| Symbol | Meaning | Action | Usage |
|--------|---------|--------|--------|
| **𝒟_μ** | Covariant derivative | ∇_μ with metric connection | Curved spacetime |
| **∇** | Gradient operator | ∂/∂x^i | Flat spacetime |
| **∇²** | Laplacian | ∂²/∂x^i∂x^i | Diffusion terms |
| **∮** | Contour integral | Integration around closed path | Circulation quantization |

---

## Biofrequency Research Symbols

### **Frequency Notation**
| Symbol | Meaning | Units | Examples | Context |
|--------|---------|-------|----------|---------|
| **f** | Frequency | Hz | 0.18 Hz (H), 7.83 Hz (Schumann) | Biological/stellar frequencies |
| **ω** | Angular frequency | rad/s | ω = 2πf | Mathematical analysis |
| **λ** | Wavelength | Meters | λ = c/f | Wave propagation |
| **ν** | Vibrational frequency | Hz | Molecular bond vibrations | Chemistry/spectroscopy |

### **Biological Classification Codes**
| Code Format | Meaning | Examples | Usage |
|-------------|---------|----------|--------|
| **ELE-X-NNN** | Element-Symbol-Frequency | ELE-H-018, ELE-C-153 | Elemental frequency database |
| **NEU-NN** | Neural cell type | NEU-01, NEU-02 | Nervous system classification |
| **CAR-NN** | Cardiac cell type | CAR-01, CAR-03 | Cardiovascular system |
| **FL-XXX** | Feedback loop | FL-OCT, FL-HBC, FL-PPT | System dynamics |
| **AA-XXX** | Amino acid type | AA-ALA, AA-GLY | Protein/molecular chemistry |

### **Stellar Anchoring System**
| Symbol | Meaning | Examples | Physical Significance |
|--------|---------|----------|----------------------|
| **Sol-X** | Sol-anchored element | Sol-H, Sol-C, Sol-O | Primary stellar anchor system |
| **Sirius-X** | Sirius-anchored | Sirius-F | Extended stellar network |
| **f_stellar** | Stellar frequency | f_Sol = base frequency | Gravitational frequency locking |

---

## Mathematical Conventions

### **Equation Numbering**
- **Core Theory**: (CT-N) for fundamental AFT equations
- **Report Equations**: (RXX-N) where XX = report number, N = equation number
- **Cross-References**: Use full notation when citing across documents

**Examples**:
- (CT-1): Kurtonian Master Equation
- (R01-3): Third equation in Report 01 (Elemental Frequency Anchors)
- (MS06-7): Seventh equation in MS06 (Somite Crystallization)

### **Units and Dimensional Analysis**
- **Natural Units**: ℏ = c = 1 where appropriate
- **SI Base Units**: Meters, seconds, kilograms for experimental work
- **Frequency Units**: Hz (not rad/s) for biological frequencies
- **Dimensionless Ratios**: φ-based scaling for temporal domains

### **Complex Number Conventions**
- **Euler Form**: z = r e^{iθ} = r(cos θ + i sin θ)
- **Imaginary Unit**: i = √(-1) (not j)
- **Conjugation**: z* = complex conjugate
- **Modulus**: |z| = √(z z*)

### **Vector and Tensor Notation**
| Notation | Meaning | Context |
|----------|---------|---------|
| **v^μ** | Contravariant vector | General relativity |
| **v_μ** | Covariant vector | General relativity |
| **∂_μ** | Partial derivative | ∂/∂x^μ |
| **g_μν** | Metric tensor | Spacetime geometry |
| **T_μν** | Stress-energy tensor | Matter and energy |

---

## Sign Conventions

### **Metric Signature**
- **Spacetime**: (-,+,+,+) signature
- **Spatial**: (+,+,+) for 3D Euclidean
- **Time Direction**: x^0 = ct (positive future)

### **Phase Conventions**
- **Quantum Mechanics**: ψ = A e^{-iωt + ikx}
- **Field Theory**: Φ = A e^{i(kx - ωt)}
- **Circulation**: Right-hand rule for ∇ × v

### **Fourier Transforms**
```math
\tilde{f}(k) = \int_{-\infty}^{\infty} f(x) e^{-ikx} dx
```
```math
f(x) = \frac{1}{2\pi} \int_{-\infty}^{\infty} \tilde{f}(k) e^{ikx} dk
```

---

## Confidence and Rigor Classifications

### **Theoretical Rigor Levels**
| Level | Badge | Meaning | Requirements |
|-------|-------|---------|--------------|
| **Derived** | `[derived]` | Proven from AFT principles | Mathematical derivation from core theory |
| **Validated** | `[validated]` | Experimentally confirmed | Independent experimental verification |
| **Simulated** | `[simulated]` | Computationally verified | Numerical simulation agreement |
| **Hypothesis** | `[hypothesis]` | Theoretical prediction | Consistent with theory, awaiting test |
| **Speculative** | `[speculative]` | Early-stage idea | Requires further theoretical development |

### **Falsification Criteria**
Each scientific claim must include:
- **Testable Prediction**: Specific measurable outcome
- **Falsification Threshold**: Quantitative disagreement level
- **Experimental Pathway**: How to perform the test
- **Timeline**: When results could be available

**Template**: "Falsified if [specific measurement] deviates by more than [threshold] from predicted value [X] within [experimental context]."

---

## Cross-Reference Standards

### **Internal Linking**
- **WikiLinks**: [[Page Name]] for internal wiki pages
- **Section Links**: [[Page Name#Section]] for specific sections
- **Equation References**: See equation (RXX-N) in [[Report Title]]

### **External References**
- **Data Files**: Direct path `/data/filename.md` or `/data/notebook.ipynb`
- **Literature**: Standard academic citation format
- **Software**: Version numbers and exact parameters

### **Provenance Requirements**
Every derived result must include:
1. **Source Data**: Exact file paths and checksums
2. **Computational Environment**: Software versions and dependencies
3. **Parameters**: All numerical values and random seeds
4. **Processing Steps**: Reproducible command sequence

---

## Special Notation for Multi-Domain Systems

### **Temporal Domain Scaling (φ-based)**
| Domain | φ-Ratio | Exponent | Usage |
|--------|---------|----------|--------|
| **ultra_fast** | 1.618 | +1 | φ¹ electromagnetic processes |
| **fast** | 1.0 | 0 | φ⁰ molecular vibrations |
| **medium** | 0.618 | -1 | φ⁻¹ cellular processes |
| **slow** | 0.382 | -2 | φ⁻² organ functions |
| **ultra_slow** | 0.236 | -3 | φ⁻³ circadian rhythms |
| **quantum** | 0.146 | -4 | φ⁻⁴ quantum processes |

### **Color-Frequency Relationships**
Based on inherent frequency properties (not arbitrary assignments):
- **Red**: Low frequency, foundational elements
- **Blue**: High frequency, energetic processes
- **Green**: Mid-range, biological optimization
- **Violet**: Quantum-scale, substrate effects

---

## Computational Standards

### **Numerical Precision**
- **Default**: Double precision (64-bit floating point)
- **High Precision**: Arbitrary precision for theoretical calculations
- **Experimental**: Precision matching measurement uncertainty
- **Thresholds**: Relative tolerance 10⁻¹² for theoretical, 10⁻⁶ for experimental

### **Random Number Generation**
- **Seeds**: Always specified for reproducibility
- **Generators**: Mersenne Twister MT19937 default
- **Distributions**: Clearly stated (uniform, normal, etc.)

### **File Naming Conventions**
- **Reports**: `REPORT_XX_Title_Keywords.md`
- **Data**: `report_XX_data_type.json` or `.csv`
- **Notebooks**: `RXX_analysis_description.ipynb`
- **Figures**: `RXX_figure_N_description.png/pdf`

---

## Version Control and Updates

- **Page Updates**: Increment version number and update timestamp
- **Major Changes**: Document in revision history
- **Cross-Reference Updates**: Automated checking for broken links
- **Notation Changes**: Backward compatibility or global update

**Version Format**: vX.Y.Z where X = major changes, Y = additions, Z = corrections

---

**See Also**:
- [[Reports Index]] - Complete catalog of all research reports
- [[Concept Graph]] - Visual relationship mapping
- [[Kurtonian Master Equation]] - Core theoretical framework
- [[Testable Predictions]] - Experimental validation standards

**Last Updated**: 2025-09-22
**Version**: v1.0
**Maintenance**: Automated consistency checking across all wiki pages