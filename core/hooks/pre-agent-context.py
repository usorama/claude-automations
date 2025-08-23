#!/usr/bin/env python3
"""
Pre-Agent Context Hook - Loads code intelligence manifests before agent execution
"""

import subprocess
import json
import os
import sys
from pathlib import Path
import shutil
from datetime import datetime, timedelta

MANIFEST_DIR = Path('.claude/manifests')
GLOBAL_MANIFEST_DIR = Path.home() / '.claude' / 'manifests'
MANIFEST_CACHE_HOURS = 4  # Refresh manifests every 4 hours

def check_gh_cli():
    """Check if GitHub CLI is available"""
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_latest_pr_number():
    """Get the latest PR number for the current branch"""
    try:
        result = subprocess.run([
            'gh', 'pr', 'view', 
            '--json', 'number', 
            '-q', '.number'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None

def download_pr_manifests(pr_number):
    """Download manifests from PR artifacts"""
    try:
        print(f"📥 Downloading manifests from PR #{pr_number}...")
        
        # List workflow runs for the PR
        result = subprocess.run([
            'gh', 'run', 'list',
            '--workflow', 'generate-manifests.yml',
            '--json', 'databaseId,status',
            '--limit', '5'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False
        
        runs = json.loads(result.stdout)
        
        # Find the latest successful run
        for run in runs:
            if run['status'] == 'completed':
                # Download artifacts from this run
                artifact_name = f"code-manifests-{pr_number}"
                result = subprocess.run([
                    'gh', 'run', 'download',
                    str(run['databaseId']),
                    '--name', artifact_name,
                    '--dir', str(MANIFEST_DIR)
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Downloaded manifests from PR #{pr_number}")
                    return True
        
    except Exception as e:
        print(f"⚠️ Error downloading PR manifests: {e}")
    
    return False

def generate_local_manifests():
    """Generate manifests locally using the generator script"""
    script_paths = [
        Path('scripts/generate-manifests.ts'),
        Path.home() / '.claude' / 'scripts' / 'generate-manifests.ts'
    ]
    
    for script_path in script_paths:
        if script_path.exists():
            print(f"🔧 Generating manifests locally using {script_path}...")
            
            try:
                # Check which runner to use
                if shutil.which('bun'):
                    runner = 'bun'
                elif shutil.which('npx'):
                    runner = 'npx'
                    subprocess.run(['npm', 'install', '-g', 'ts-node'], capture_output=True)
                else:
                    print("⚠️ No TypeScript runner found (bun or npx)")
                    return False
                
                # Run the generator
                if runner == 'bun':
                    result = subprocess.run(
                        ['bun', 'run', str(script_path)],
                        capture_output=True,
                        text=True
                    )
                else:
                    result = subprocess.run(
                        ['npx', 'ts-node', str(script_path)],
                        capture_output=True,
                        text=True
                    )
                
                if result.returncode == 0:
                    print("✅ Generated local manifests")
                    
                    # Copy to project directory if needed
                    if GLOBAL_MANIFEST_DIR.exists() and not MANIFEST_DIR.exists():
                        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
                        for file in GLOBAL_MANIFEST_DIR.glob('*'):
                            shutil.copy2(file, MANIFEST_DIR / file.name)
                    
                    return True
                else:
                    print(f"⚠️ Generator failed: {result.stderr}")
                    
            except Exception as e:
                print(f"⚠️ Error generating manifests: {e}")
    
    return False

def manifests_are_fresh():
    """Check if existing manifests are fresh enough"""
    if not MANIFEST_DIR.exists():
        return False
    
    manifest_file = MANIFEST_DIR / 'CODEBASE_MANIFEST.yaml'
    if not manifest_file.exists():
        return False
    
    # Check age of manifest
    mtime = datetime.fromtimestamp(manifest_file.stat().st_mtime)
    age = datetime.now() - mtime
    
    return age < timedelta(hours=MANIFEST_CACHE_HOURS)

def copy_global_manifests():
    """Copy manifests from global directory to project"""
    if GLOBAL_MANIFEST_DIR.exists():
        print("📋 Copying global manifests to project...")
        MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
        
        for file in GLOBAL_MANIFEST_DIR.glob('*'):
            dest = MANIFEST_DIR / file.name
            if not dest.exists() or file.stat().st_mtime > dest.stat().st_mtime:
                shutil.copy2(file, dest)
        
        return True
    return False

def inject_manifest_context():
    """Main function to ensure manifests are available"""
    
    print("🔍 Pre-Agent Context Hook triggered...")
    
    # Check if manifests already exist and are fresh
    if manifests_are_fresh():
        print("✅ Manifests are up-to-date")
        display_manifest_summary()
        return
    
    # Try different methods to get manifests
    success = False
    
    # Method 1: Check if manifests exist globally
    if GLOBAL_MANIFEST_DIR.exists():
        success = copy_global_manifests()
    
    # Method 2: Try to download from latest PR (if in a git repo with gh CLI)
    if not success and os.path.exists('.git') and check_gh_cli():
        pr_number = get_latest_pr_number()
        if pr_number:
            success = download_pr_manifests(pr_number)
    
    # Method 3: Generate manifests locally
    if not success:
        success = generate_local_manifests()
    
    if success:
        display_manifest_summary()
    else:
        print("⚠️ Could not load manifests. Agent will proceed without context.")
        print("💡 Tip: Run 'bun run scripts/generate-manifests.ts' to generate manifests")

def display_manifest_summary():
    """Display a summary of loaded manifests"""
    if not MANIFEST_DIR.exists():
        return
    
    print("\n📊 Code Intelligence Manifests Loaded:")
    print("=" * 40)
    
    # List available manifests
    manifests = list(MANIFEST_DIR.glob('*.yaml')) + \
                list(MANIFEST_DIR.glob('*.json')) + \
                list(MANIFEST_DIR.glob('*.md'))
    
    for manifest in sorted(manifests):
        size = manifest.stat().st_size
        if size > 1024:
            size_str = f"{size // 1024}KB"
        else:
            size_str = f"{size}B"
        print(f"  ✓ {manifest.name:<30} {size_str:>8}")
    
    # Try to show key statistics
    codebase_manifest = MANIFEST_DIR / 'CODEBASE_MANIFEST.yaml'
    if codebase_manifest.exists():
        try:
            import yaml
            with open(codebase_manifest) as f:
                data = yaml.safe_load(f)
                stats = data.get('statistics', {})
                print("\n📈 Codebase Statistics:")
                print(f"  • Functions: {stats.get('total_functions', 'N/A')}")
                print(f"  • Exports: {stats.get('total_exports', 'N/A')}")
                print(f"  • Files: {stats.get('total_files', 'N/A')}")
        except Exception:
            # YAML might not be available, try basic parsing
            with open(codebase_manifest) as f:
                content = f.read()
                for line in content.split('\n'):
                    if 'total_functions:' in line:
                        print(f"  • Functions: {line.split(':')[1].strip()}")
                    elif 'total_exports:' in line:
                        print(f"  • Exports: {line.split(':')[1].strip()}")
                    elif 'total_files:' in line:
                        print(f"  • Files: {line.split(':')[1].strip()}")
    
    print("=" * 40)
    print("✅ Context ready for agent execution\n")

def main():
    """Entry point for the hook"""
    # This hook runs before any engineering agent starts
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--refresh':
            # Force refresh manifests
            if MANIFEST_DIR.exists():
                shutil.rmtree(MANIFEST_DIR)
            print("🔄 Force refreshing manifests...")
        elif sys.argv[1] == '--summary':
            # Just show summary
            display_manifest_summary()
            return
    
    # Inject context
    inject_manifest_context()

if __name__ == '__main__':
    main()