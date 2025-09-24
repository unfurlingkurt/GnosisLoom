#!/usr/bin/env python3
"""
GitHub Wiki Link Converter
==========================

Converts Obsidian-style [[links]] to GitHub wiki-style [text](page) links.
"""

import os
import re
from pathlib import Path

class WikiLinkConverter:
    """Converts wiki links between formats"""

    def __init__(self, wiki_repo_dir="/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom/wiki_repo"):
        self.wiki_repo_dir = Path(wiki_repo_dir)

        # Page name mappings for GitHub wiki format
        self.page_mappings = {
            # Core theory pages (01-07)
            "Kurtonian Master Equation": "01-Kurtonian-Master-Equation",
            "Aramis Field Substrate": "02-Aramis-Field-Substrate",
            "First-Principles Derivation": "03-First-Principles-Derivation",
            "Recovery of Known Theories": "04-Recovery-Known-Theories",
            "Quantization via Resonance": "05-Quantization-Resonance",
            "Spiral Dynamics": "06-Spiral-Dynamics",
            "Testable Predictions": "07-Testable-Predictions",

            # Foundation pages
            "Elemental Frequency Anchors": "EFA01-Elemental-Frequency-Anchors",
            "Molecular Assembly Dynamics": "MAD02-Molecular-Assembly-Dynamics",
            "Molecular Chemistry Resonance": "MCR00-Molecular-Chemistry-Resonance",
            "Traditional DNA Architecture": "TDFA03-Traditional-DNA-Frequency-Architecture",
            "Q-DNA Traditional Weaving": "QTDW04-Q-DNA-Traditional-DNA-Weaving",

            # MS Series pages
            "Anatomical Resonance Map": "MS00-Anatomical-Resonance-Map",
            "Stella Foundation": "MS00-Stella-Foundation",
            "Morphogenic Frequencies": "MS01-Morphogenic-Frequencies",
            "Sensory Crystallization": "MS02-Sensory-Crystallization",
            "Vascular Fractals": "MS03-Vascular-Fractals",
            "Endocrine-Immune Coupling": "MS04-Endocrine-Immune-Coupling",
            "Digestive-Neural Entanglement": "MS05-Digestive-Neural-Entanglement",
            "Somite Crystallization": "MS06-Somite-Crystallization",
            "Temporal Morphogenic Animation": "MS08-Temporal-Morphogenic-Animation",
            "Integumentary Sensory Integration": "MS09-Integumentary-Sensory-Integration",
            "Hematopoietic Immune Architecture": "MS10-Hematopoietic-Immune-Architecture",
            "Complete Endocrine Mapping": "MS11-Complete-Endocrine-Mapping",
            "Reproductive System Development": "MS12-Reproductive-System-Development",
            "Connective Tissue Matrix": "MS13-Connective-Tissue-Matrix",
            "Metabolic Integration": "MS14-Metabolic-Integration",
            "Neural Integration Finale": "MS15-Neural-Integration-Finale",
            "Respiratory-Lymphatic Integration": "MS16-Respiratory-Lymphatic-Integration",
            "Renal-Urinary Crystallization": "MS17-Renal-Urinary-Crystallization",
            "Advanced Consciousness Filtration Mechanics": "MS17.1-Advanced-Consciousness-Filtration-Mechanics",
            "Hepatic-Detox Symphony": "MS18-Hepatic-Detox-Symphony",
            "Digestive Completion": "MS19-Digestive-Completion-Second-Brain-Awakens",
            "Chronic Fatigue Resonance Fracture": "MS20-Chronic-Fatigue-Post-Viral-Resonance-Fracture",
            "Neural Frequency Disruption Pain": "MS21-Neural-Frequency-Disruption-Pain-Without-Cause",
            "Biofield Emergence Disorders": "MS22-Biofield-Emergence-Disorders",
            "Autoimmune Frequency Confusion": "MS23-Autoimmune-Frequency-Confusion",
            "Prion Misfolding Mysteries": "MS24-Prion-Misfolding-Mysteries",
            "Sudden Death Regulation": "MS25-Sudden-Death-Regulation",

            # Report series pages
            "Nerve Regeneration Scaffolds": "NRSP05-Nerve-Regeneration-Scaffold-Proteins",
            "Nerve Frequency Effects": "NFEA06-Nerve-Frequency-Effects-Analysis",
            "Therapeutic Delivery Systems": "TFDS07-Therapeutic-Frequency-Delivery-Systems",

            # Navigation pages
            "Reports Index": "Reports-Index",
            "Notation and Conventions": "Notation-and-Conventions",
            "Home": "Home",
            "Concept Graph": "Concept-Graph",
            "Resonance Motif Index": "Resonance-Motif-Index",

            # Placeholders for missing pages
            "Scaffold-Nerve Protocols": "NRSP05-Nerve-Regeneration-Scaffold-Proteins", # Link to closest available
            "Van Gelder Analysis": "NFEA06-Nerve-Frequency-Effects-Analysis", # Link to closest available
            "Utah Clinical Protocol": "TFDS07-Therapeutic-Frequency-Delivery-Systems", # Link to closest available
            "Quantum-Classical Transitions": "05-Quantization-Resonance", # Link to closest available
            "Universal Architecture": "02-Aramis-Field-Substrate", # Link to closest available
            "Observer Drift Analysis": "07-Testable-Predictions", # Link to closest available
            "Quantum Chemistry Validation": "EFA01-Elemental-Frequency-Anchors", # Link to closest available
        }

    def convert_obsidian_to_github_links(self, text):
        """Convert [[text]] links to [text](page) format"""

        def replace_link(match):
            link_text = match.group(1)

            # Check if we have a mapping for this page
            if link_text in self.page_mappings:
                page_name = self.page_mappings[link_text]
                return f"[{link_text}]({page_name})"
            else:
                # Try to find a close match or create a reasonable page name
                page_name = link_text.replace(" ", "-").replace(":", "").replace("'", "")
                print(f"Warning: No mapping found for '{link_text}', using '{page_name}'")
                return f"[{link_text}]({page_name})"

        # Pattern to match [[text]] links
        pattern = r'\[\[([^\]]+)\]\]'
        return re.sub(pattern, replace_link, text)

    def convert_file(self, file_path):
        """Convert links in a single file"""
        print(f"Converting links in {file_path.name}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Convert the links
            converted_content = self.convert_obsidian_to_github_links(content)

            # Write back the converted content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(converted_content)

            print(f"   ✓ Converted {file_path.name}")

        except Exception as e:
            print(f"   ❌ Error converting {file_path.name}: {e}")

    def convert_all_wiki_files(self):
        """Convert all markdown files in the wiki repo"""
        print("🔗 Converting Obsidian links to GitHub wiki format...")
        print("=" * 60)

        if not self.wiki_repo_dir.exists():
            print(f"❌ Wiki repo directory not found: {self.wiki_repo_dir}")
            return False

        # Find all markdown files
        md_files = list(self.wiki_repo_dir.glob("*.md"))

        if not md_files:
            print("❌ No markdown files found")
            return False

        print(f"Found {len(md_files)} markdown files to convert")

        for md_file in sorted(md_files):
            self.convert_file(md_file)

        print("\n" + "=" * 60)
        print(f"✅ Converted links in {len(md_files)} files")
        print("=" * 60)

        return True

def main():
    """Main execution"""
    converter = WikiLinkConverter()
    return converter.convert_all_wiki_files()

if __name__ == "__main__":
    main()