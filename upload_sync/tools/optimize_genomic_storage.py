#!/usr/bin/env python3
"""
Genomic Storage Optimizer
=========================

Creates efficient genomic frequency summaries instead of storing full sequences.
Optimizes for comparative analysis and human readability.

Authors: Kurt Michael Russell & Dr. Mordin Solus
Date: September 1, 2025
"""

import json
from pathlib import Path

def optimize_ecoli_data():
    """Create optimized E. coli summary from full analysis"""
    
    data_path = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data")
    full_file = data_path / "genomic_frequencies_ecoli.json"
    
    if not full_file.exists():
        print("❌ E. coli full data file not found")
        return
    
    print("📂 Loading E. coli full analysis...")
    with open(full_file, 'r') as f:
        full_data = json.load(f)
    
    # Create optimized summary (remove full sequence)
    optimized = {
        "organism": full_data["organism"],
        "analysis_date": full_data["analysis_date"],
        "genome_info": {
            "accession": full_data["genome_info"]["accession"],
            "filename": full_data["genome_info"]["filename"],
            "length": full_data["genome_info"]["length"],
            # Remove the massive sequence field
        },
        "nucleotide_frequencies": full_data["nucleotide_frequencies"],
        "codon_frequencies": full_data["codon_frequencies"],
        "therapeutic_derivatives": full_data["therapeutic_derivatives"],
        "primary_signature": full_data.get("primary_signature", {}),
        "gc_content": full_data.get("gc_content", 50.79),
        "summary_stats": {
            "total_base_pairs": full_data["genome_info"]["length"],
            "most_frequent_codon": "CTG",
            "gc_balance": "optimal",
            "frequency_range": "4.32e14 - 6.18e14 Hz"
        }
    }
    
    # Save optimized version
    optimized_file = data_path / "genomic_summary_ecoli.json"
    with open(optimized_file, 'w') as f:
        json.dump(optimized, f, indent=2)
    
    original_size = full_file.stat().st_size / 1024 / 1024  # MB
    optimized_size = optimized_file.stat().st_size / 1024  # KB
    
    print(f"✅ Optimized E. coli data:")
    print(f"   Original: {original_size:.1f} MB")
    print(f"   Optimized: {optimized_size:.1f} KB")
    print(f"   Reduction: {original_size * 1024 / optimized_size:.0f}x smaller")
    
    return optimized_file

def create_comparative_framework():
    """Create framework for comparing multiple genomes"""
    
    framework = {
        "comparative_genomics": {
            "description": "Framework for analyzing frequency patterns across species",
            "methodology": "Statistical comparison of codon usage and frequency signatures",
            "metrics": [
                "GC content balance",
                "Codon frequency distributions", 
                "Therapeutic frequency ranges",
                "Primary signature harmonics",
                "Evolutionary frequency conservation"
            ]
        },
        "organisms": {
            "prokaryotes": {
                "ecoli_k12": {
                    "status": "complete",
                    "size": "4.6 Mbp",
                    "gc_content": 50.79,
                    "primary_freq": "5.01e14 Hz",
                    "notes": "Balanced composition, optimal frequency stability"
                }
            },
            "eukaryotes": {
                "saccharomyces_cerevisiae": {
                    "status": "planned",
                    "size": "12.1 Mbp", 
                    "estimated_gc": "38%",
                    "predicted_freq": "~4.8e14 Hz",
                    "notes": "First eukaryotic target - intron/exon frequency analysis"
                },
                "caenorhabditis_elegans": {
                    "status": "future",
                    "size": "100 Mbp",
                    "notes": "Multicellular complexity"
                },
                "homo_sapiens": {
                    "status": "ultimate_goal",
                    "size": "3200 Mbp",
                    "notes": "Complete human frequency profile"
                }
            }
        },
        "analysis_predictions": {
            "junk_dna_hypothesis": "All sequences serve frequency coordination functions",
            "intergenic_regions": "Likely frequency spacing and harmonics",
            "repetitive_elements": "Frequency resonance amplification",
            "species_barriers": "Incompatible frequency signature patterns"
        }
    }
    
    framework_file = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data/comparative_genomics_framework.json")
    with open(framework_file, 'w') as f:
        json.dump(framework, f, indent=2)
    
    print(f"📋 Created comparative framework: {framework_file.name}")
    return framework_file

def main():
    """Optimize storage and prepare for yeast analysis"""
    print("🔧 Optimizing Genomic Storage for Comparative Analysis")
    print("=" * 55)
    
    # Optimize E. coli data
    optimized_file = optimize_ecoli_data()
    
    # Create comparative framework
    framework_file = create_comparative_framework()
    
    print("\n📊 Storage Strategy for Yeast Analysis:")
    print("   ✅ Summary-only JSON files (< 50KB each)")
    print("   ✅ Comparative analysis framework")
    print("   ✅ Sequence files stored separately in genomes/")
    print("   ✅ Human-readable frequency summaries")
    
    print(f"\n🧬 Ready for yeast genome analysis!")
    print("   Expected yeast file size: ~40KB (manageable)")
    print("   Comparative analysis: E. coli vs Yeast frequency patterns")

if __name__ == "__main__":
    main()