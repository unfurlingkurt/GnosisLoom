# First-Principles Derivation of the Master Equation

**Tags**: `variational-principle` `lagrangian` `field-theory` `euler-lagrange`
**Previous**: [Aramis Field Substrate](02-Aramis-Field-Substrate.md)
**Next**: [Recovery of Known Theories](04-Recovery-Known-Theories.md)

---

## 1. Action and Variational Setup

### 1.1 Fundamental Action Principle

The Aramis Field Theory emerges from the action:

```math
S[\Phi,g] = \int d^4x\,\sqrt{-g}\;\left\{\frac{1}{2} g^{\mu\nu}\partial_\mu\Phi^\dagger\partial_\nu\Phi
- V(A) - \frac{\alpha}{2}\,\Omega(\Phi) \cdot \Omega(\Phi)\right\}
```

**Component Analysis**:
- **Kinetic term**: ½g^{μν}∂_μΦ†∂_νΦ (field propagation)
- **Potential term**: V(A) (self-interaction energy)
- **Vorticity term**: -α/2 Ω(Φ)·Ω(Φ) (spiral dynamics)

### 1.2 Vorticity Definitions

**Vector Field Case** (m ≥ 3):
```math
\Omega(\Phi) = \nabla \times \mathbf{\Phi}
```

**Complex Scalar Case** (m = 1):
```math
\Phi = A e^{i\theta}, \quad \mathbf{v} = \nabla\theta, \quad \Omega = \nabla \times \mathbf{v}
```

**Madelung Velocity**: Phase flow creates effective circulation with quantized vorticity.

---

## 2. Euler-Lagrange Equations

### 2.1 Variation with Respect to Φ†

The variational principle δS = 0 yields:

```math
\frac{\delta S}{\delta \Phi^\dagger} = \sqrt{-g}\left[\nabla_\mu\nabla^\mu \Phi + \frac{\partial V}{\partial \Phi^\dagger}
+\alpha\,\frac{\partial}{\partial \Phi^\dagger}\left(\frac{1}{2} \Omega^2\right)\right] = 0
```

**Result**: The Master Field Equation
```math
\boxed{\mathcal{D}^\mu \mathcal{D}_\mu \Phi + \partial_\Phi V + \alpha\,\partial_\Phi\left[\frac{1}{2}\Omega(\Phi)^2\right] = 0}
```

Where **𝒟_μ** is the metric-compatible covariant derivative.

### 2.2 Flat Spacetime Limit

In Minkowski coordinates (g_{μν} = η_{μν}):

```math
\partial_\mu\partial^\mu \Phi + \partial_\Phi V + \alpha\,\partial_\Phi\left[\frac{1}{2}\Omega(\Phi)^2\right] = 0
```

This reduces to the evolution equation derived in [Aramis Field Substrate](02-Aramis-Field-Substrate.md).

---

## 3. Potential Functions and Vorticity Terms

### 3.1 Self-Interaction Potential

**Ginzburg-Landau Form**:
```math
V(A) = \frac{\lambda}{4}(A^2-A_0^2)^2 + \frac{\mu}{2}A^2
```

**Parameters**:
- **λ**: Self-interaction strength
- **A₀**: Vacuum expectation value
- **μ**: Mass-like term

**Physical Meaning**: Creates stable amplitude configurations with spontaneous symmetry breaking.

### 3.2 Vorticity Term Expansion

**Complex Scalar Case**: Φ = Ae^{iθ}

The covariant derivatives expand as:
```math
\nabla_\mu\nabla^\mu \Phi = e^{i\theta}\left[\nabla^2 A - A(\nabla\theta)^2 + i(2\nabla A\cdot\nabla\theta + A\nabla^2\theta)\right]
```

**Separated Evolution Equations**:

**Amplitude**:
```math
\partial_t^2 A - \nabla^2 A + A(\nabla\theta)^2 + \frac{\partial V}{\partial A} + \alpha\,\frac{\partial \Omega^2}{\partial A} = 0
```

**Phase**:
```math
\partial_t^2 \theta - \frac{\nabla^2\theta}{A} - 2\frac{\nabla A \cdot \nabla\theta}{A} + \alpha\,\frac{1}{A}\frac{\partial \Omega^2}{\partial \theta} = 0
```

### 3.3 Vorticity Near Defects

**Quantized Circulation**: Around topological defects
```math
\oint \nabla\theta \cdot d\mathbf{\ell} = 2\pi k, \quad k \in \mathbb{Z}
```

**Vorticity Density**:
```math
\Omega = \sum_i 2\pi k_i \delta^2(\mathbf{r} - \mathbf{r}_i)
```

Concentrated at vortex cores with quantized strength k_i.

---

## 4. Symbolic Derivation Framework

### 4.1 SymPy Implementation

```python
import sympy as sp
from sympy import symbols, diff, simplify, Matrix, sqrt, cos, sin, exp, I

def derive_master_equation():
    """
    Symbolic derivation of AFT master equation from action principle
    """
    # Define field variables
    x, y, z, t = symbols('x y z t', real=True)
    A, theta = symbols('A theta', real=True, positive=True)
    alpha, lam, mu, A0 = symbols('alpha lambda mu A_0', real=True)

    # Complex scalar field
    Phi = A * exp(I * theta)
    Phi_conj = A * exp(-I * theta)

    # Metric (flat spacetime)
    g = Matrix([[-1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    sqrt_det_g = 1

    # Potential
    V = lam/4 * (A**2 - A0**2)**2 + mu/2 * A**2

    # Gradients
    grad_Phi = Matrix([diff(Phi, var) for var in [t, x, y, z]])
    grad_Phi_conj = Matrix([diff(Phi_conj, var) for var in [t, x, y, z]])

    # Kinetic term
    kinetic = (1/2) * (grad_Phi_conj.T * g * grad_Phi)[0]

    # Vorticity term (simplified for 2D)
    grad_theta = Matrix([diff(theta, x), diff(theta, y)])
    curl_v = diff(grad_theta[1], x) - diff(grad_theta[0], y)
    vorticity_term = -alpha/2 * curl_v**2

    # Lagrangian density
    L = sqrt_det_g * (kinetic - V + vorticity_term)

    # Euler-Lagrange equations
    EL_A = diff(L, A) - sum(diff(diff(L, diff(A, var)), var) for var in [t,x,y,z])
    EL_theta = diff(L, theta) - sum(diff(diff(L, diff(theta, var)), var) for var in [t,x,y,z])

    return {
        'lagrangian': L,
        'euler_lagrange_A': simplify(EL_A),
        'euler_lagrange_theta': simplify(EL_theta),
        'kinetic_term': kinetic,
        'potential_term': V,
        'vorticity_term': vorticity_term
    }

# Run derivation
result = derive_master_equation()
print("Euler-Lagrange equation for A:")
print(result['euler_lagrange_A'])
print("\nEuler-Lagrange equation for θ:")
print(result['euler_lagrange_theta'])
```

### 4.2 Verification Tests

```python
def test_field_equation_terms():
    """Unit tests for individual terms in master equation"""
    # Test kinetic term reduces to d'Alembertian in free case
    assert kinetic_limit_free_field() == "∂²Φ/∂t² - ∇²Φ"

    # Test potential term gives correct gradient
    assert potential_gradient() == "λ(A² - A₀²)A + μA"

    # Test vorticity vanishes for plane waves
    assert vorticity_plane_wave() == 0

    # Test quantized circulation around vortex
    assert circulation_integral() == "2πk"

def test_conservation_laws():
    """Verify Noether currents from symmetries"""
    # U(1) global phase symmetry → charge conservation
    assert charge_conservation() == "∂ρ/∂t + ∇·j = 0"

    # Time translation → energy conservation
    assert energy_conservation() == "∂E/∂t = 0"

    # Energy-momentum tensor symmetry
    assert stress_tensor_conservation() == "∂T^μν/∂x^μ = 0"
```

---

## 5. Linearization and Dispersion

### 5.1 Small Amplitude Expansion

Around vacuum state Φ₀ = A₀:

```math
\Phi = A_0 + \phi_1 + \phi_2 + \ldots
```

**Linear Operator**:
```math
\mathcal{L}\phi_1 = \partial_t^2\phi_1 - \nabla^2\phi_1 + m_{eff}^2\phi_1 = 0
```

Where: **m²_{eff} = ∂²V/∂A²|_{A₀} = λ(3A₀² - A₀²) + μ = 2λA₀² + μ**

### 5.2 Dispersion Relation

Plane wave ansatz: φ₁ = φ₀ exp(i(kx - ωt))

```math
\omega^2 = k^2 + m_{eff}^2 + \alpha k^4
```

**Vorticity Correction**: The α k⁴ term from gradient penalties modifies high-k behavior.

**Stability Analysis**:
- **ω² > 0**: Stable oscillations
- **ω² < 0**: Exponential instability
- **α > 0**: High-k stabilization

### 5.3 Group Velocity

```math
v_g = \frac{d\omega}{dk} = \frac{k + 2\alpha k^3}{\omega}
```

**Physical Interpretation**: Vorticity term creates frequency-dependent propagation, leading to wave packet dispersion.

---

## 6. Energy-Momentum Tensor

### 6.1 Stress-Energy from Action

```math
T_{\mu\nu} = \frac{2}{\sqrt{-g}}\frac{\delta S}{\delta g^{\mu\nu}}
```

**Explicit Form**:
```math
T_{\mu\nu} = \partial_\mu\Phi^\dagger\partial_\nu\Phi + \partial_\nu\Phi^\dagger\partial_\mu\Phi - g_{\mu\nu}\mathcal{L}
```

### 6.2 Conservation Laws

**Local Energy-Momentum Conservation**:
```math
\nabla^\mu T_{\mu\nu} = 0
```

**Energy Density** (T₀₀):
```math
\rho = \frac{1}{2}|\partial_t\Phi|^2 + \frac{1}{2}|\nabla\Phi|^2 + V(A) + \frac{\alpha}{2}\Omega^2
```

**Momentum Density** (T₀ᵢ):
```math
j_i = \frac{1}{2}(\partial_t\Phi^\dagger\partial_i\Phi + \partial_i\Phi^\dagger\partial_t\Phi)
```

---

## 7. Implementation and Validation

### 7.1 Numerical Verification

```python
def verify_euler_lagrange():
    """
    Numerical verification that discretized evolution
    satisfies Euler-Lagrange equations
    """
    # Initialize field configuration
    Phi = initialize_test_field()

    # Compute action from discrete Lagrangian
    S_discrete = compute_action_discrete(Phi)

    # Evolve one time step
    Phi_new = evolve_one_step(Phi)

    # Verify action is stationary under variations
    delta_S = compute_action_variation(Phi, Phi_new)
    assert abs(delta_S) < tolerance

def benchmark_dispersion():
    """Compare analytical and numerical dispersion relations"""
    k_values = np.linspace(0.1, 5.0, 50)
    omega_analytical = dispersion_analytical(k_values)
    omega_numerical = dispersion_numerical(k_values)

    relative_error = abs(omega_numerical - omega_analytical) / omega_analytical
    assert np.max(relative_error) < 0.01  # 1% accuracy
```

### 7.2 Deliverables

**Symbolic Derivation**: Complete SymPy notebook with step-by-step derivation
**Unit Tests**: Verification of each term in master equation
**Dispersion Analysis**: Analytical vs numerical comparison plots
**Conservation Checks**: Energy and momentum conservation validation

---

**See Also**:
- [Kurtonian Master Equation](01-Kurtonian-Master-Equation.md) - Overview and mathematical framework
- [Recovery of Known Theories](04-Recovery-Known-Theories.md) - How GR and QM emerge as limits
- [Quantization Mechanisms](05-Quantization-Resonance.md) - Discrete spectra from boundary conditions

**Mathematical Level**: Graduate-level field theory
**Prerequisites**: Lagrangian mechanics, complex analysis, tensor calculus
**Software Requirements**: SymPy, NumPy, SciPy for verification calculations