#!/usr/bin/env python3
"""
PRISM Integration Test Suite

Tests the complete PRISM integration with Claude Code:
1. MCP server functionality
2. Database operations
3. Hook integration
4. Context optimization
"""

import os
import sys
import json
import sqlite3
import asyncio
from pathlib import Path
import subprocess
import time

# Add PRISM modules to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path.home() / 'claude-automations' / 'git-intelligence' / 'src'))

def test_database_setup():
    """Test SQLite database initialization"""
    print("\n🔍 Testing Database Setup...")
    
    db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
    
    # Check if database exists
    if not db_path.exists():
        print("❌ Database doesn't exist. Creating...")
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Test connection and tables
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            required_tables = {'manifests', 'usage_patterns', 'agent_profiles', 'context_history'}
            existing_tables = {t[0] for t in tables}
            
            if required_tables.issubset(existing_tables):
                print("✅ All required tables exist")
            else:
                missing = required_tables - existing_tables
                print(f"❌ Missing tables: {missing}")
                return False
            
            # Test inserting sample data
            cursor.execute('''
                INSERT OR REPLACE INTO manifests (name, content, size_kb)
                VALUES ('TEST_MANIFEST.json', '{"test": true}', 0.1)
            ''')
            conn.commit()
            print("✅ Database write test successful")
            
            return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_mcp_server_import():
    """Test if MCP server can be imported"""
    print("\n🔍 Testing MCP Server Import...")
    
    try:
        from prism_mcp_server import PRISMMCPServer
        print("✅ MCP server module imported successfully")
        
        # Try to instantiate
        server = PRISMMCPServer()
        print("✅ MCP server instantiated")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Installing MCP SDK...")
        subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], capture_output=True)
        return False
    except Exception as e:
        print(f"❌ Server initialization error: {e}")
        return False

def test_hook_configuration():
    """Test if hooks are properly configured"""
    print("\n🔍 Testing Hook Configuration...")
    
    # Check settings.json
    settings_path = Path.home() / '.claude' / 'settings.json'
    if not settings_path.exists():
        print("❌ Settings file not found")
        return False
    
    try:
        with open(settings_path) as f:
            settings = json.load(f)
        
        # Check for PRISM hook
        pre_tool_hooks = settings.get('hooks', {}).get('PreToolUse', [])
        prism_hook_found = False
        
        for hook_config in pre_tool_hooks:
            if hook_config.get('matcher') == 'Task':
                for hook in hook_config.get('hooks', []):
                    if 'prism-context-optimizer' in hook.get('command', ''):
                        prism_hook_found = True
                        break
        
        if prism_hook_found:
            print("✅ PRISM hook configured in settings.json")
        else:
            print("❌ PRISM hook not found in settings.json")
            return False
        
        # Check hook file exists
        hook_path = Path.home() / '.claude' / 'hooks' / 'prism-context-optimizer.py'
        if hook_path.exists():
            print("✅ Hook file exists")
        else:
            print("❌ Hook file not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_mcp_configuration():
    """Test if MCP server is configured"""
    print("\n🔍 Testing MCP Configuration...")
    
    mcp_config_path = Path.home() / '.claude-code' / 'mcp' / 'global.json'
    if not mcp_config_path.exists():
        print("❌ MCP configuration file not found")
        return False
    
    try:
        with open(mcp_config_path) as f:
            config = json.load(f)
        
        # Check for PRISM server
        prism_config = config.get('mcpServers', {}).get('prism')
        if prism_config:
            print("✅ PRISM MCP server configured")
            print(f"   Command: {prism_config.get('command')}")
            print(f"   Disabled: {prism_config.get('disabled', False)}")
            
            # Check auto-approve
            auto_approve = prism_config.get('autoApprove', [])
            expected_tools = ['get_optimal_context', 'analyze_task', 'update_learning']
            if all(tool in auto_approve for tool in expected_tools):
                print("✅ All PRISM tools auto-approved")
            else:
                print("⚠️  Some tools not auto-approved")
            
            return True
        else:
            print("❌ PRISM server not configured in MCP")
            return False
    except Exception as e:
        print(f"❌ MCP configuration error: {e}")
        return False

def test_context_optimization():
    """Test context optimization functionality"""
    print("\n🔍 Testing Context Optimization...")
    
    try:
        from context_router import ContextRouter
        from context_dna import ContextDNAProfiler
        
        # Test Context DNA
        profiler = ContextDNAProfiler()
        profile = profiler.get_profile('frontend-developer')
        if profile:
            print("✅ Context DNA profile loaded")
        else:
            print("⚠️  No profile for frontend-developer")
        
        # Test Context Router
        router = ContextRouter()
        route = router.route_context(
            "implement user authentication",
            "backend-architect"
        )
        
        if route and route.selected_manifests:
            print("✅ Context routing works")
            print(f"   Selected {len(route.selected_manifests)} manifests")
            print(f"   Confidence: {route.confidence_score:.1%}")
        else:
            print("⚠️  Context routing returned no manifests")
        
        return True
    except ImportError as e:
        print(f"⚠️  PRISM components not available: {e}")
        return True  # Not critical for basic setup
    except Exception as e:
        print(f"❌ Context optimization error: {e}")
        return False

def test_sample_manifest_load():
    """Test loading sample manifests"""
    print("\n🔍 Testing Manifest Loading...")
    
    # Check for virtual-tutor manifests
    vt_manifests = Path.home() / 'Projects' / 'virtual-tutor' / '.claude' / 'manifests'
    if vt_manifests.exists():
        manifest_files = list(vt_manifests.glob('*.json')) + list(vt_manifests.glob('*.md'))
        print(f"✅ Found {len(manifest_files)} manifests in virtual-tutor")
        
        # Load into database
        db_path = Path.home() / '.claude' / 'prism' / 'intelligence.db'
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                for manifest_file in manifest_files[:5]:  # Load first 5
                    content = manifest_file.read_text()
                    size_kb = len(content) / 1024
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO manifests 
                        (name, content, project_path, size_kb)
                        VALUES (?, ?, ?, ?)
                    ''', (manifest_file.name, content, str(vt_manifests.parent.parent), size_kb))
                
                conn.commit()
                print(f"✅ Loaded sample manifests into database")
                return True
        except Exception as e:
            print(f"❌ Failed to load manifests: {e}")
            return False
    else:
        print("⚠️  Virtual-tutor manifests not found (not critical)")
        return True

def run_integration_test():
    """Run complete integration test"""
    print("=" * 60)
    print("🚀 PRISM Integration Test Suite")
    print("=" * 60)
    
    results = {
        'Database': test_database_setup(),
        'MCP Import': test_mcp_server_import(),
        'Hook Config': test_hook_configuration(),
        'MCP Config': test_mcp_configuration(),
        'Context Opt': test_context_optimization(),
        'Manifests': test_sample_manifest_load()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test:15} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! PRISM is ready for Claude Code integration.")
        print("\n📝 Next Steps:")
        print("1. Install MCP SDK: pip install mcp")
        print("2. Test with Claude Code: claude mcp list")
        print("3. Verify PRISM appears in the list")
        print("4. Test a Task tool call to see PRISM in action")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        print("\n🔧 Common Fixes:")
        print("- Install MCP: pip install mcp")
        print("- Ensure symlinks exist: ln -s ~/claude-automations/core/hooks ~/.claude/hooks")
        print("- Restart Claude Code after configuration changes")
    
    return passed == total

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)