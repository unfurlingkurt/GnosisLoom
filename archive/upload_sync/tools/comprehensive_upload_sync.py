#!/usr/bin/env python3
"""
Comprehensive GnosisLoom Upload Sync
===================================

Syncs all new reports, data, and wiki pages since last upload.
Creates organized structure for easy integration.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import subprocess

class GnosisLoomUploadSync:
    """
    Comprehensive sync manager for GnosisLoom content
    """

    def __init__(self):
        self.base_path = Path("/home/kmr/LoomAgent/Stella/notebooks/BioFreqKnowledge/GnosisLoom")
        self.upload_path = self.base_path / "upload_sync"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Content categories to sync
        self.categories = {
            'wiki': ['wiki/*.md'],
            'reports': ['reports/REPORT_*.md'],
            'data': ['data/*.json'],
            'tools': ['tools/*.py', 'tools/*.json'],
            'documentation': ['*.md', 'README*']
        }

    def create_upload_structure(self):
        """Create organized upload directory structure"""

        print(f"🚀 Creating upload sync structure at {self.upload_path}")

        # Clean and create upload directory
        if self.upload_path.exists():
            shutil.rmtree(self.upload_path)
        self.upload_path.mkdir(parents=True)

        # Create category directories
        for category in self.categories.keys():
            (self.upload_path / category).mkdir()

        # Create manifest file
        manifest = {
            "sync_timestamp": self.timestamp,
            "sync_date": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "categories": list(self.categories.keys()),
            "total_files": 0,
            "file_inventory": {}
        }

        return manifest

    def sync_wiki_pages(self, manifest):
        """Sync all wiki pages"""

        print("📚 Syncing wiki pages...")

        wiki_files = []
        wiki_source = self.base_path / "wiki"
        wiki_dest = self.upload_path / "wiki"

        if wiki_source.exists():
            for md_file in wiki_source.glob("*.md"):
                dest_file = wiki_dest / md_file.name
                shutil.copy2(md_file, dest_file)
                wiki_files.append({
                    "file": md_file.name,
                    "source": str(md_file),
                    "size_kb": round(md_file.stat().st_size / 1024, 2),
                    "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
                })

        manifest["file_inventory"]["wiki"] = {
            "count": len(wiki_files),
            "files": wiki_files
        }

        print(f"   ✓ {len(wiki_files)} wiki pages synced")
        return len(wiki_files)

    def sync_reports(self, manifest):
        """Sync all research reports"""

        print("📊 Syncing research reports...")

        report_files = []
        reports_source = self.base_path / "reports"
        reports_dest = self.upload_path / "reports"

        if reports_source.exists():
            for report_file in sorted(reports_source.glob("REPORT_*.md")):
                dest_file = reports_dest / report_file.name
                shutil.copy2(report_file, dest_file)
                report_files.append({
                    "file": report_file.name,
                    "source": str(report_file),
                    "size_kb": round(report_file.stat().st_size / 1024, 2),
                    "modified": datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
                })

        manifest["file_inventory"]["reports"] = {
            "count": len(report_files),
            "files": report_files
        }

        print(f"   ✓ {len(report_files)} research reports synced")
        return len(report_files)

    def sync_data_files(self, manifest):
        """Sync all JSON data files"""

        print("💾 Syncing data files...")

        data_files = []
        data_source = self.base_path / "data"
        data_dest = self.upload_path / "data"

        if data_source.exists():
            for json_file in data_source.glob("*.json"):
                dest_file = data_dest / json_file.name
                shutil.copy2(json_file, dest_file)

                # Get file size and record count
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        record_count = len(data) if isinstance(data, (list, dict)) else 1
                except:
                    record_count = "unknown"

                data_files.append({
                    "file": json_file.name,
                    "source": str(json_file),
                    "size_kb": round(json_file.stat().st_size / 1024, 2),
                    "records": record_count,
                    "modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
                })

        manifest["file_inventory"]["data"] = {
            "count": len(data_files),
            "files": data_files
        }

        print(f"   ✓ {len(data_files)} data files synced")
        return len(data_files)

    def sync_tools(self, manifest):
        """Sync tools and utilities"""

        print("🔧 Syncing tools and utilities...")

        tool_files = []
        tools_source = self.base_path / "tools"
        tools_dest = self.upload_path / "tools"

        if tools_source.exists():
            for tool_file in tools_source.glob("*.py"):
                dest_file = tools_dest / tool_file.name
                shutil.copy2(tool_file, dest_file)
                tool_files.append({
                    "file": tool_file.name,
                    "source": str(tool_file),
                    "size_kb": round(tool_file.stat().st_size / 1024, 2),
                    "type": "python_script",
                    "modified": datetime.fromtimestamp(tool_file.stat().st_mtime).isoformat()
                })

            # Also sync JSON files in tools
            for json_file in tools_source.glob("*.json"):
                dest_file = tools_dest / json_file.name
                shutil.copy2(json_file, dest_file)
                tool_files.append({
                    "file": json_file.name,
                    "source": str(json_file),
                    "size_kb": round(json_file.stat().st_size / 1024, 2),
                    "type": "data_file",
                    "modified": datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
                })

        manifest["file_inventory"]["tools"] = {
            "count": len(tool_files),
            "files": tool_files
        }

        print(f"   ✓ {len(tool_files)} tool files synced")
        return len(tool_files)

    def create_upload_summary(self, manifest):
        """Create comprehensive upload summary"""

        print("📋 Creating upload summary...")

        # Calculate totals
        total_files = sum(cat["count"] for cat in manifest["file_inventory"].values())
        manifest["total_files"] = total_files

        # Create summary document
        summary = f"""# GnosisLoom Upload Sync Summary
Generated: {manifest["sync_date"]}
Timestamp: {manifest["sync_timestamp"]}

## Upload Statistics

**Total Files**: {total_files}

### By Category:
"""

        for category, info in manifest["file_inventory"].items():
            summary += f"- **{category.title()}**: {info['count']} files\n"

        summary += f"""
### Detailed File Inventory:

"""

        # Add detailed inventory
        for category, info in manifest["file_inventory"].items():
            summary += f"#### {category.title()} Files ({info['count']})\n\n"

            if info["files"]:
                summary += "| File | Size (KB) | Modified |\n"
                summary += "|------|-----------|----------|\n"

                for file_info in info["files"][:20]:  # Limit to first 20 for readability
                    summary += f"| {file_info['file']} | {file_info['size_kb']} | {file_info['modified'][:10]} |\n"

                if len(info["files"]) > 20:
                    summary += f"| ... and {len(info['files']) - 20} more files | | |\n"

            summary += "\n"

        # Add key discoveries section
        summary += """
## Key Recent Developments

### New Wiki Pages
- **MS22**: Biofield Emergence Disorders - Revolutionary paradigm shift for contested medical conditions
- **MS20**: Chronic Fatigue Resonance Fracture Analysis
- **MS21**: Neural Frequency Disruption Pain Without Cause

### Major Research Reports
- **REPORT_30**: Multi-Modal Frequency Orchestration Beyond Pharmaceuticals
- **REPORT_31**: Advanced Biofield Coherence Protocols
- **REPORT_32**: Quantum Chemistry Frequency Validation Framework
- **REPORT_33**: Observer Drift Analysis First Principles Investigation
- **REPORT_UT01**: Utah Array Harmonic Integration Protocol

### Database Expansions
- Universal connection discoveries database
- Cross-kingdom coupling analysis
- AlphaGenome gene investigation results
- Genomic frequency architectures for multiple organisms

### Tool Developments
- Utah Array THz frequency induction simulator
- Comprehensive genomic discovery engines
- Universal pattern detection algorithms
- Clinical protocol validation frameworks

## Research Status

**Phase 1 Complete**: MS00-MS21 comprehensive documentation ✅
**Phase 2 In Progress**: MS22-MS25 biofield disorders and final systems
**REPORT Series**: 33+ comprehensive research reports completed
**Database**: 29+ specialized frequency databases with 1,400+ patterns
**Tools**: Advanced simulation and discovery frameworks operational

## Next Steps

1. Complete MS22-MS25 final biological systems
2. Process remaining 5 reports before REPORT_01 series
3. Implement cross-reference automation
4. Develop hierarchical concept integration
5. Finalize knowledge graph architecture

---

*GnosisLoom v2.0.0 - Universal Connection Discovery*
*"Mapping the Aramis Field from atoms to consciousness"*
"""

        # Save summary
        summary_path = self.upload_path / "UPLOAD_SUMMARY.md"
        with open(summary_path, 'w') as f:
            f.write(summary)

        # Save manifest
        manifest_path = self.upload_path / "sync_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        print(f"   ✓ Upload summary created: {summary_path}")
        print(f"   ✓ Sync manifest created: {manifest_path}")

    def create_archive(self):
        """Create compressed archive of upload sync"""

        print("📦 Creating compressed archive...")

        archive_name = f"gnosisloom_sync_{self.timestamp}"
        archive_path = self.base_path / f"{archive_name}.tar.gz"

        # Create tar.gz archive
        cmd = f"cd {self.base_path} && tar -czf {archive_name}.tar.gz upload_sync/"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            archive_size = round(archive_path.stat().st_size / (1024*1024), 2)
            print(f"   ✓ Archive created: {archive_path} ({archive_size} MB)")
            return archive_path
        else:
            print(f"   ❌ Archive creation failed: {result.stderr}")
            return None

    def run_complete_sync(self):
        """Execute complete upload sync process"""

        print("🌟 Starting GnosisLoom Comprehensive Upload Sync")
        print("="*60)

        # Create structure
        manifest = self.create_upload_structure()

        # Sync all categories
        total_synced = 0
        total_synced += self.sync_wiki_pages(manifest)
        total_synced += self.sync_reports(manifest)
        total_synced += self.sync_data_files(manifest)
        total_synced += self.sync_tools(manifest)

        # Create summary
        self.create_upload_summary(manifest)

        # Create archive
        archive_path = self.create_archive()

        print("\n" + "="*60)
        print("✅ UPLOAD SYNC COMPLETE")
        print("="*60)
        print(f"📁 Upload Directory: {self.upload_path}")
        print(f"📊 Total Files Synced: {total_synced}")
        print(f"📦 Archive: {archive_path}")
        print(f"🕒 Timestamp: {self.timestamp}")

        # Show directory structure
        print("\n📂 Upload Structure:")
        for root, dirs, files in os.walk(self.upload_path):
            level = root.replace(str(self.upload_path), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show first 5 files per directory
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")

        print("\n🚀 Ready for upload to external systems!")
        print("="*60)

        return {
            "upload_path": str(self.upload_path),
            "archive_path": str(archive_path) if archive_path else None,
            "total_files": total_synced,
            "timestamp": self.timestamp,
            "manifest": manifest
        }

def main():
    """Main execution"""

    syncer = GnosisLoomUploadSync()
    result = syncer.run_complete_sync()

    return result

if __name__ == "__main__":
    main()