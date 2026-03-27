#!/usr/bin/env python3
"""
Observer Drift Analysis Tool
Investigates systematic deviations between elemental frequency calculations and DFT results
Performs higher-order derivative analysis to identify observer effect patterns
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import curve_fit
from scipy.stats import normaltest, shapiro
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

class ObserverDriftAnalyzer:
    def __init__(self, data_path):
        """Initialize analyzer with quantum frequency validation data"""
        self.data_path = data_path
        self.load_data()
        self.prepare_analysis_data()

    def load_data(self):
        """Load quantum chemistry frequency validation data"""
        with open(self.data_path, 'r') as f:
            self.raw_data = json.load(f)

        self.amino_acid_data = self.raw_data['quantum_chemistry_frequencies']['amino_acid_dft_validation']

    def prepare_analysis_data(self):
        """Extract numerical data for analysis"""
        self.amino_acids = []
        self.elemental_freq = []
        self.dft_freq = []
        self.experimental_freq = []
        self.deviations = []
        self.uncertainties = []

        for entry in self.amino_acid_data:
            self.amino_acids.append(entry['amino_acid'])
            self.elemental_freq.append(entry['elemental_frequency'])
            self.dft_freq.append(entry['dft_b3lyp_frequency'])
            self.experimental_freq.append(entry['experimental_frequency'])
            self.deviations.append(entry['deviation_percent'])
            self.uncertainties.append(entry['uncertainty'])

        # Convert to numpy arrays
        self.elemental_freq = np.array(self.elemental_freq)
        self.dft_freq = np.array(self.dft_freq)
        self.experimental_freq = np.array(self.experimental_freq)
        self.deviations = np.array(self.deviations)
        self.uncertainties = np.array(self.uncertainties)

        # Calculate absolute differences
        self.absolute_diff = self.dft_freq - self.elemental_freq
        self.relative_diff = self.absolute_diff / self.elemental_freq * 100

    def analyze_deviation_patterns(self):
        """Analyze patterns in frequency deviations"""
        results = {}

        # Basic statistics
        results['basic_stats'] = {
            'mean_deviation': float(np.mean(self.deviations)),
            'std_deviation': float(np.std(self.deviations)),
            'median_deviation': float(np.median(self.deviations)),
            'max_deviation': float(np.max(np.abs(self.deviations))),
            'min_deviation': float(np.min(np.abs(self.deviations))),
            'range_deviation': float(np.max(self.deviations) - np.min(self.deviations))
        }

        # Test for normality
        shapiro_stat, shapiro_p = shapiro(self.deviations)
        normaltest_stat, normaltest_p = normaltest(self.deviations)

        results['normality_tests'] = {
            'shapiro_wilk_statistic': float(shapiro_stat),
            'shapiro_wilk_p_value': float(shapiro_p),
            'normal_test_statistic': float(normaltest_stat),
            'normal_test_p_value': float(normaltest_p),
            'is_normal_distribution': bool(shapiro_p > 0.05 and normaltest_p > 0.05)
        }

        # Correlation analysis
        corr_freq_dev = stats.pearsonr(self.elemental_freq, self.deviations)
        corr_freq_abs_diff = stats.pearsonr(self.elemental_freq, np.abs(self.absolute_diff))

        results['correlation_analysis'] = {
            'frequency_vs_deviation_correlation': float(corr_freq_dev[0]),
            'frequency_vs_deviation_p_value': float(corr_freq_dev[1]),
            'frequency_vs_absolute_diff_correlation': float(corr_freq_abs_diff[0]),
            'frequency_vs_absolute_diff_p_value': float(corr_freq_abs_diff[1])
        }

        return results

    def higher_order_derivative_analysis(self):
        """Perform 2nd and 3rd order derivative analysis of errors"""
        results = {}

        # Sort data by frequency for derivative analysis
        sort_indices = np.argsort(self.elemental_freq)
        freq_sorted = self.elemental_freq[sort_indices]
        dev_sorted = self.deviations[sort_indices]
        abs_diff_sorted = np.abs(self.absolute_diff[sort_indices])

        # Calculate derivatives using finite differences
        # First derivative (rate of change of deviation with frequency)
        first_derivative = np.gradient(dev_sorted, freq_sorted)

        # Second derivative (acceleration of deviation change)
        second_derivative = np.gradient(first_derivative, freq_sorted)

        # Third derivative (jerk of deviation change)
        third_derivative = np.gradient(second_derivative, freq_sorted)

        results['derivative_statistics'] = {
            'first_derivative': {
                'mean': float(np.mean(first_derivative)),
                'std': float(np.std(first_derivative)),
                'max': float(np.max(first_derivative)),
                'min': float(np.min(first_derivative))
            },
            'second_derivative': {
                'mean': float(np.mean(second_derivative)),
                'std': float(np.std(second_derivative)),
                'max': float(np.max(second_derivative)),
                'min': float(np.min(second_derivative))
            },
            'third_derivative': {
                'mean': float(np.mean(third_derivative)),
                'std': float(np.std(third_derivative)),
                'max': float(np.max(third_derivative)),
                'min': float(np.min(third_derivative))
            }
        }

        # Look for oscillatory patterns
        # Frequency analysis of derivatives
        from scipy.fft import fft, fftfreq

        n = len(first_derivative)
        freqs = fftfreq(n, d=np.mean(np.diff(freq_sorted)))

        fft_first = fft(first_derivative)
        fft_second = fft(second_derivative)
        fft_third = fft(third_derivative)

        # Find dominant frequencies in each derivative
        first_dominant_freq = freqs[np.argmax(np.abs(fft_first[1:n//2])) + 1]
        second_dominant_freq = freqs[np.argmax(np.abs(fft_second[1:n//2])) + 1]
        third_dominant_freq = freqs[np.argmax(np.abs(fft_third[1:n//2])) + 1]

        results['oscillatory_analysis'] = {
            'first_derivative_dominant_frequency': float(first_dominant_freq),
            'second_derivative_dominant_frequency': float(second_dominant_freq),
            'third_derivative_dominant_frequency': float(third_dominant_freq),
            'first_derivative_amplitude': float(np.max(np.abs(fft_first[1:n//2]))),
            'second_derivative_amplitude': float(np.max(np.abs(fft_second[1:n//2]))),
            'third_derivative_amplitude': float(np.max(np.abs(fft_third[1:n//2])))
        }

        # Store derivative arrays for plotting
        self.freq_sorted = freq_sorted
        self.dev_sorted = dev_sorted
        self.first_derivative = first_derivative
        self.second_derivative = second_derivative
        self.third_derivative = third_derivative

        return results

    def polynomial_error_modeling(self):
        """Model error patterns using polynomial regression"""
        results = {}

        # Test polynomial orders 1-5
        for order in range(1, 6):
            # Create polynomial features
            poly_features = PolynomialFeatures(degree=order)
            X_poly = poly_features.fit_transform(self.elemental_freq.reshape(-1, 1))

            # Fit linear regression
            model = LinearRegression()
            model.fit(X_poly, self.deviations)

            # Predict and calculate R²
            y_pred = model.predict(X_poly)
            r2 = r2_score(self.deviations, y_pred)

            # Calculate residuals
            residuals = self.deviations - y_pred
            residual_std = np.std(residuals)

            results[f'polynomial_order_{order}'] = {
                'r2_score': float(r2),
                'residual_std': float(residual_std),
                'coefficients': [float(c) for c in model.coef_],
                'intercept': float(model.intercept_)
            }

        return results

    def observer_effect_analysis(self):
        """Analyze systematic patterns suggesting observer effects"""
        results = {}

        # Check for measurement-dependent patterns
        # 1. Frequency dependence of uncertainty
        corr_freq_uncertainty = stats.pearsonr(self.elemental_freq, self.uncertainties)

        # 2. Systematic bias analysis
        # Test if deviations show systematic trends
        positive_deviations = np.sum(self.deviations > 0)
        negative_deviations = np.sum(self.deviations < 0)
        zero_deviations = np.sum(np.abs(self.deviations) < 0.1)

        # Chi-square test for uniform distribution of signs
        from scipy.stats import chisquare
        expected_freq = [len(self.deviations) / 3] * 3
        observed_freq = [positive_deviations, negative_deviations, zero_deviations]
        chi2_stat, chi2_p = chisquare(observed_freq, expected_freq)

        results['systematic_bias_analysis'] = {
            'positive_deviations': int(positive_deviations),
            'negative_deviations': int(negative_deviations),
            'near_zero_deviations': int(zero_deviations),
            'chi2_uniformity_test': float(chi2_stat),
            'chi2_p_value': float(chi2_p),
            'is_uniform_distribution': bool(chi2_p > 0.05)
        }

        # 3. Measurement precision correlation
        results['uncertainty_correlations'] = {
            'frequency_vs_uncertainty_correlation': float(corr_freq_uncertainty[0]),
            'frequency_vs_uncertainty_p_value': float(corr_freq_uncertainty[1])
        }

        # 4. Observer-dependent clustering analysis
        # Look for groupings that might indicate measurement observer effects
        from sklearn.cluster import KMeans

        # Cluster deviations to identify measurement patterns
        X_cluster = np.column_stack([self.elemental_freq, self.deviations])

        inertias = []
        silhouette_scores = []

        for n_clusters in range(2, 6):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_cluster)
            inertias.append(kmeans.inertia_)

            from sklearn.metrics import silhouette_score
            sil_score = silhouette_score(X_cluster, cluster_labels)
            silhouette_scores.append(sil_score)

        optimal_clusters = np.argmax(silhouette_scores) + 2

        results['clustering_analysis'] = {
            'optimal_cluster_count': int(optimal_clusters),
            'silhouette_scores': [float(s) for s in silhouette_scores],
            'inertias': [float(i) for i in inertias]
        }

        return results

    def quantum_measurement_analysis(self):
        """Analyze patterns consistent with quantum measurement theory"""
        results = {}

        # 1. Heisenberg uncertainty relation analysis
        # Check if uncertainty scales with frequency (energy)

        # Calculate energy equivalent from frequency (E = hf)
        h = 6.626e-34  # Planck constant
        energy_elemental = h * self.elemental_freq * 1e12  # Convert to Hz
        energy_dft = h * self.dft_freq * 1e12

        # Energy uncertainty
        energy_uncertainty = np.abs(energy_dft - energy_elemental)

        # Check scaling with √E (characteristic of quantum systems)
        sqrt_energy_correlation = stats.pearsonr(np.sqrt(energy_elemental), energy_uncertainty)
        linear_energy_correlation = stats.pearsonr(energy_elemental, energy_uncertainty)

        results['heisenberg_analysis'] = {
            'sqrt_energy_vs_uncertainty_correlation': float(sqrt_energy_correlation[0]),
            'sqrt_energy_vs_uncertainty_p_value': float(sqrt_energy_correlation[1]),
            'linear_energy_vs_uncertainty_correlation': float(linear_energy_correlation[0]),
            'linear_energy_vs_uncertainty_p_value': float(linear_energy_correlation[1]),
            'quantum_scaling_evidence': bool(sqrt_energy_correlation[0] > linear_energy_correlation[0])
        }

        # 2. Wave function collapse signature analysis
        # Look for discrete jumps vs continuous variations

        # Calculate consecutive differences in deviations
        consecutive_diffs = np.diff(self.dev_sorted)

        # Test for discreteness vs continuity
        # Discrete systems show preferred difference values
        from scipy.stats import kstest

        # Test against uniform distribution (continuous)
        ks_stat, ks_p = kstest(consecutive_diffs, 'uniform')

        results['wave_function_collapse_analysis'] = {
            'consecutive_difference_mean': float(np.mean(consecutive_diffs)),
            'consecutive_difference_std': float(np.std(consecutive_diffs)),
            'ks_test_statistic': float(ks_stat),
            'ks_test_p_value': float(ks_p),
            'discrete_behavior_evidence': bool(ks_p < 0.05)
        }

        # 3. Observer-measurement coupling analysis
        # Check for patterns indicating measurement apparatus effects

        # Calculate "measurement strength" as deviation magnitude
        measurement_strength = np.abs(self.deviations)

        # Look for coupling between measurement strength and frequency
        coupling_correlation = stats.pearsonr(self.elemental_freq, measurement_strength)

        results['observer_coupling_analysis'] = {
            'measurement_strength_frequency_correlation': float(coupling_correlation[0]),
            'measurement_strength_frequency_p_value': float(coupling_correlation[1]),
            'strong_coupling_evidence': bool(abs(coupling_correlation[0]) > 0.5 and coupling_correlation[1] < 0.05)
        }

        return results

    def generate_observer_drift_report(self):
        """Generate comprehensive observer drift analysis report"""

        print("Analyzing observer drift patterns...")

        # Perform all analyses
        deviation_patterns = self.analyze_deviation_patterns()
        derivative_analysis = self.higher_order_derivative_analysis()
        polynomial_modeling = self.polynomial_error_modeling()
        observer_effects = self.observer_effect_analysis()
        quantum_analysis = self.quantum_measurement_analysis()

        # Combine results
        report = {
            'observer_drift_analysis': {
                'deviation_patterns': deviation_patterns,
                'higher_order_derivatives': derivative_analysis,
                'polynomial_error_modeling': polynomial_modeling,
                'observer_effect_signatures': observer_effects,
                'quantum_measurement_patterns': quantum_analysis
            },
            'metadata': {
                'total_amino_acids_analyzed': len(self.amino_acids),
                'frequency_range': [float(np.min(self.elemental_freq)), float(np.max(self.elemental_freq))],
                'deviation_range': [float(np.min(self.deviations)), float(np.max(self.deviations))],
                'analysis_timestamp': '2025-09-18'
            }
        }

        return report

    def plot_observer_drift_patterns(self, save_path=None):
        """Create visualization plots for observer drift analysis"""

        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Observer Drift Analysis: Systematic Deviations in Quantum Frequency Validation', fontsize=16)

        # Plot 1: Frequency vs Deviation
        axes[0,0].scatter(self.elemental_freq, self.deviations, alpha=0.7, s=60)
        axes[0,0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[0,0].set_xlabel('Elemental Frequency (Hz)')
        axes[0,0].set_ylabel('Deviation (%)')
        axes[0,0].set_title('Frequency-Dependent Deviations')
        axes[0,0].grid(True, alpha=0.3)

        # Plot 2: Derivative Analysis
        axes[0,1].plot(self.freq_sorted, self.first_derivative, 'b-', label='1st Derivative', linewidth=2)
        axes[0,1].plot(self.freq_sorted, self.second_derivative, 'r-', label='2nd Derivative', linewidth=2)
        axes[0,1].plot(self.freq_sorted, self.third_derivative, 'g-', label='3rd Derivative', linewidth=2)
        axes[0,1].set_xlabel('Frequency (Hz)')
        axes[0,1].set_ylabel('Derivative Value')
        axes[0,1].set_title('Higher-Order Derivatives')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)

        # Plot 3: Uncertainty vs Frequency
        axes[0,2].scatter(self.elemental_freq, self.uncertainties, alpha=0.7, s=60, c='purple')
        axes[0,2].set_xlabel('Elemental Frequency (Hz)')
        axes[0,2].set_ylabel('Experimental Uncertainty (Hz)')
        axes[0,2].set_title('Measurement Uncertainty Patterns')
        axes[0,2].grid(True, alpha=0.3)

        # Plot 4: Deviation Distribution
        axes[1,0].hist(self.deviations, bins=10, alpha=0.7, color='skyblue', edgecolor='black')
        axes[1,0].axvline(x=np.mean(self.deviations), color='red', linestyle='--',
                         label=f'Mean = {np.mean(self.deviations):.2f}%')
        axes[1,0].set_xlabel('Deviation (%)')
        axes[1,0].set_ylabel('Frequency')
        axes[1,0].set_title('Deviation Distribution')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)

        # Plot 5: Residuals Analysis
        # Fit polynomial and show residuals
        poly_features = PolynomialFeatures(degree=3)
        X_poly = poly_features.fit_transform(self.elemental_freq.reshape(-1, 1))
        model = LinearRegression()
        model.fit(X_poly, self.deviations)
        y_pred = model.predict(X_poly)
        residuals = self.deviations - y_pred

        axes[1,1].scatter(self.elemental_freq, residuals, alpha=0.7, s=60, c='orange')
        axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[1,1].set_xlabel('Elemental Frequency (Hz)')
        axes[1,1].set_ylabel('Residuals (%)')
        axes[1,1].set_title('Polynomial Model Residuals')
        axes[1,1].grid(True, alpha=0.3)

        # Plot 6: Quantum Scaling Analysis
        h = 6.626e-34
        energy = h * self.elemental_freq * 1e12
        energy_uncertainty = h * np.abs(self.dft_freq - self.elemental_freq) * 1e12

        axes[1,2].loglog(energy, energy_uncertainty, 'ro', alpha=0.7, markersize=6)
        axes[1,2].set_xlabel('Energy (J)')
        axes[1,2].set_ylabel('Energy Uncertainty (J)')
        axes[1,2].set_title('Quantum Energy Uncertainty Scaling')
        axes[1,2].grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

def main():
    """Main analysis function"""

    # Initialize analyzer
    data_path = '/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data/quantum_chemistry_frequencies.json'
    analyzer = ObserverDriftAnalyzer(data_path)

    # Generate comprehensive report
    report = analyzer.generate_observer_drift_report()

    # Save detailed analysis
    output_path = '/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data/observer_drift_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    # Generate plots
    plot_path = '/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data/observer_drift_plots.png'
    analyzer.plot_observer_drift_patterns(save_path=plot_path)

    print(f"Observer drift analysis completed!")
    print(f"Report saved to: {output_path}")
    print(f"Plots saved to: {plot_path}")

    # Print key findings
    print("\n=== KEY OBSERVER DRIFT FINDINGS ===")

    basic_stats = report['observer_drift_analysis']['deviation_patterns']['basic_stats']
    print(f"Mean deviation: {basic_stats['mean_deviation']:.3f}%")
    print(f"Standard deviation: {basic_stats['std_deviation']:.3f}%")
    print(f"Max absolute deviation: {basic_stats['max_deviation']:.3f}%")

    quantum_patterns = report['observer_drift_analysis']['quantum_measurement_patterns']
    print(f"\nQuantum scaling evidence: {quantum_patterns['heisenberg_analysis']['quantum_scaling_evidence']}")
    print(f"Discrete behavior evidence: {quantum_patterns['wave_function_collapse_analysis']['discrete_behavior_evidence']}")
    print(f"Strong observer coupling: {quantum_patterns['observer_coupling_analysis']['strong_coupling_evidence']}")

    return report

if __name__ == "__main__":
    report = main()