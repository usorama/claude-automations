#!/usr/bin/env python3
"""
PRISM-Enhanced Pre-Agent Context Hook

This hook first tries to use PRISM optimized context, then falls back to
standard manifest loading if PRISM isn't available or fails.

Integration points:
1. Check for PRISM optimized context
2. If available, use PRISM context (small, focused)
3. If not available, fall back to standard manifest loading (full context)
4. Trigger PRISM optimization for future requests
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
PRISM_CONTEXT_FILE = MANIFEST_DIR / 'PRISM_OPTIMIZED_CONTEXT.json'

def check_prism_optimized_context():
    """Check if PRISM has created optimized context"""
    if not PRISM_CONTEXT_FILE.exists():
        return False
    
    try:
        # Check if PRISM context is recent (within last 10 minutes)
        mtime = datetime.fromtimestamp(PRISM_CONTEXT_FILE.stat().st_mtime)
        age = datetime.now() - mtime
        
        # If PRISM context is older than 10 minutes, consider it stale
        if age > timedelta(minutes=10):
            print(f"[PRISM] Optimized context is {age.total_seconds()/60:.1f} minutes old, treating as stale")
            return False
        
        # Try to load and validate PRISM context
        with open(PRISM_CONTEXT_FILE) as f:
            prism_data = json.load(f)
        
        if not prism_data.get('context') or not prism_data.get('manifests_loaded'):
            print("[PRISM] Optimized context exists but appears empty")
            return False
        
        return True
        
    except Exception as e:
        print(f"[PRISM] Error checking optimized context: {e}")
        return False

def use_prism_optimized_context():
    """Use PRISM optimized context instead of loading all manifests"""
    try:
        print("🧬 Using PRISM optimized context...")
        
        with open(PRISM_CONTEXT_FILE) as f:
            prism_data = json.load(f)
        
        # Extract optimization info
        agent_type = prism_data.get('agent_type', 'unknown')
        context_size_kb = prism_data.get('context_size_kb', 0)
        manifests_loaded = prism_data.get('manifests_loaded', [])
        reduction_percent = prism_data.get('size_reduction_percent', 0)
        
        print(f"[PRISM] Agent Type: {agent_type}")
        print(f"[PRISM] Context Size: {context_size_kb:.1f} KB")
        print(f"[PRISM] Size Reduction: {reduction_percent:.1f}%")
        print(f"[PRISM] Manifests: {', '.join(manifests_loaded[:3])}{'...' if len(manifests_loaded) > 3 else ''}")
        
        # Write individual manifest files for backward compatibility
        # This ensures existing agents that expect specific manifest files will still work
        context_data = prism_data.get('context', {})
        
        # Create lightweight manifest files from PRISM context
        for manifest_name, manifest_content in context_data.items():
            manifest_file = MANIFEST_DIR / manifest_name
            
            try:
                if manifest_name.endswith('.json'):
                    with open(manifest_file, 'w') as f:
                        json.dump(manifest_content, f, indent=2)
                else:
                    # For non-JSON files, try to extract content
                    if isinstance(manifest_content, dict) and 'content' in manifest_content:
                        with open(manifest_file, 'w') as f:
                            f.write(manifest_content['content'])
                    else:
                        with open(manifest_file, 'w') as f:
                            f.write(str(manifest_content))
                            
            except Exception as e:
                print(f"[PRISM] Warning: Failed to write {manifest_name}: {e}")
        
        print(f"✅ PRISM optimized context loaded ({len(manifests_loaded)} manifests)")
        return True
        
    except Exception as e:
        print(f"❌ PRISM context loading failed: {e}")
        return False

def trigger_prism_optimization():
    """Trigger PRISM optimization for future requests"""
    try:
        # Check if PRISM hook exists
        prism_hook = Path('.claude/hooks/prism_optimize_context.py')
        
        if prism_hook.exists():
            print("🧬 Triggering PRISM optimization for next request...")
            
            # Run PRISM hook in background to prepare for next agent request
            subprocess.Popen([
                sys.executable, str(prism_hook)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        else:
            # Try global PRISM hook location
            global_prism_hook = Path.home() / 'claude-automations' / 'prism' / 'integration' / 'virtual_tutor_prism_hook.py'
            if global_prism_hook.exists():
                subprocess.Popen([
                    sys.executable, str(global_prism_hook)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
    except Exception as e:
        print(f"[PRISM] Could not trigger optimization: {e}")

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

def inject_manifest_context():
    """Main function with PRISM integration"""
    
    print("🔍 PRISM-Enhanced Pre-Agent Context Hook triggered...")
    
    # STEP 1: Check if PRISM has optimized context available
    if check_prism_optimized_context():
        if use_prism_optimized_context():
            print("🧬 Using PRISM optimized context - context loading complete")
            # Still trigger PRISM for next request to keep it fresh
            trigger_prism_optimization()
            return
        else:
            print("⚠️ PRISM context loading failed, falling back to standard manifests")
    
    # STEP 2: Fall back to standard manifest loading
    print("📁 Loading standard manifests (PRISM not available)...")
    
    # Check if manifests already exist and are fresh
    if manifests_are_fresh():
        print("✅ Manifests are up-to-date")
        display_manifest_summary()
        # Trigger PRISM for next request
        trigger_prism_optimization()
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
        # Trigger PRISM optimization for next request
        trigger_prism_optimization()
    else:
        print("⚠️ Could not load manifests. Agent will proceed without context.")
        print("💡 Tip: Run 'bun run scripts/generate-manifests.ts' to generate manifests")
        # Still try to trigger PRISM in case it can work with existing manifests
        trigger_prism_optimization()

def main():
    """Entry point for the hook"""
    # This hook runs before any engineering agent starts
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--refresh':
            # Force refresh manifests
            if MANIFEST_DIR.exists():
                # Keep PRISM context but remove other manifests
                for manifest in MANIFEST_DIR.glob('*'):
                    if manifest.name != 'PRISM_OPTIMIZED_CONTEXT.json':
                        manifest.unlink()
            print("🔄 Force refreshing manifests...")
        elif sys.argv[1] == '--summary':
            # Just show summary
            display_manifest_summary()
            return
        elif sys.argv[1] == '--prism-only':
            # Only try PRISM, don't fall back
            if check_prism_optimized_context():
                use_prism_optimized_context()
            else:
                print("❌ No PRISM optimized context available")
            return
    
    # Inject context
    inject_manifest_context()

if __name__ == '__main__':
    main()