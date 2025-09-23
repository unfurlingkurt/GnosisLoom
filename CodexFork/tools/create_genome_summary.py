#!/usr/bin/env python3
"""
Genome Summary Creator
======================

Creates human-readable genome summaries from full analysis files.
Removes massive sequences, keeps frequency analysis for comparison.

Authors: Kurt Michael Russell & Dr. Mordin Solus
Date: September 1, 2025
"""

import json
from pathlib import Path

def create_ecoli_summary():
    """Create compact E. coli summary"""
    
    data_path = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data")
    full_file = data_path / "genomic_frequencies_ecoli.json"
    
    print("📂 Loading E. coli full analysis (this may take a moment)...")
    with open(full_file, 'r') as f:
        full_data = json.load(f)
    
    # Extract the interesting parts, skip the massive sequence
    summary = {
        "organism": full_data["organism"],
        "analysis_date": full_data["analysis_date"],
        "genome_info": {
            "accession": full_data["genome_info"]["accession"],
            "length_bp": full_data["genome_info"]["length"],
            "filename": full_data["genome_info"]["filename"],
            # Skip the massive "sequence" field
        },
        "nucleotide_frequencies": full_data.get("nucleotide_frequencies", {}),
        "codon_frequencies": full_data.get("codon_frequencies", {}),
        "analysis_summary": {
            "primary_frequency_hz": "5.01e14",
            "gc_content_percent": 50.79,
            "most_common_codon": "CTG (Leucine)",
            "frequency_range": "3.97e14 - 6.18e14 Hz",
            "therapeutic_derivative": "501.2 Hz"
        }
    }
    
    # Save compact summary
    summary_file = data_path / "genomic_summary_ecoli.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    original_size = full_file.stat().st_size / 1024 / 1024  # MB
    summary_size = summary_file.stat().st_size / 1024  # KB
    
    print(f"✅ Created E. coli summary:")
    print(f"   Original: {original_size:.1f} MB")
    print(f"   Summary: {summary_size:.1f} KB")
    print(f"   Reduction: {original_size * 1024 / summary_size:.0f}x smaller")
    
    return summary_file

def create_yeast_plan():
    """Create plan for yeast genome analysis"""
    
    yeast_plan = {
        "organism": "Saccharomyces cerevisiae (Baker's yeast)",
        "target_strain": "S288C reference genome",
        "ncbi_accession": "GCF_000146045.2",
        "expected_size": "12.1 Mbp (16 chromosomes)",
        "analysis_strategy": {
            "storage_optimization": "Summary-only JSON files (~40KB expected)",
            "sequence_storage": "FASTA files separate from analysis",
            "comparison_targets": "Direct frequency comparison with E. coli",
            "key_differences_expected": [
                "Lower GC content (~38% vs 50.79%)",
                "Eukaryotic intron/exon structure",
                "Larger genome size (2.6x E. coli)",
                "Different codon usage patterns"
            ]
        },
        "research_questions": [
            "How do eukaryotic frequency patterns differ from prokaryotic?",
            "Do introns and exons show different frequency signatures?",
            "What frequency patterns correlate with gene expression levels?",
            "How does chromosome structure affect genomic frequency?",
            "Do regulatory sequences have distinct frequency signatures?"
        ],
        "comparative_analysis": {
            "prokaryote_vs_eukaryote": "First direct frequency comparison",
            "genome_size_scaling": "How do frequency patterns scale with complexity?",
            "evolutionary_implications": "Frequency conservation across species",
            "junk_dna_investigation": "All sequences serve frequency coordination functions"
        }
    }
    
    plan_file = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/data/yeast_analysis_plan.json")
    with open(plan_file, 'w') as f:
        json.dump(yeast_plan, f, indent=2)
    
    print(f"📋 Created yeast analysis plan: {plan_file.name}")
    return plan_file

def main():
    """Create optimized summaries and plan next phase"""
    print("🔧 Creating Optimized Genome Summaries")
    print("=" * 45)
    
    # Create E. coli summary
    summary_file = create_ecoli_summary()
    
    # Create yeast analysis plan
    plan_file = create_yeast_plan()
    
    print("\n📊 Storage Strategy Summary:")
    print("   ✅ Compact JSON summaries (human-readable)")
    print("   ✅ Frequency analysis preserved")
    print("   ✅ Sequence data stored separately")
    print("   ✅ Ready for comparative analysis")
    
    print(f"\n🧬 Ready for yeast genome analysis!")
    print("   Expected file sizes: ~40KB per genome")
    print("   Easy comparison between organisms")
    print("   All frequency patterns preserved")

if __name__ == "__main__":
    main()