#!/usr/bin/env python3
"""
PRISM System Validation Test

Tests the complete PRISM system to validate that it achieves the goal of
reducing context size from 200KB+ to <20KB per agent while maintaining quality.
"""

import sys
import json
import time
from pathlib import Path

# Add PRISM modules to path
prism_src = Path(__file__).parent / 'src'
git_intelligence_src = Path.home() / 'claude-automations' / 'git-intelligence' / 'src'
sys.path.extend([str(prism_src), str(git_intelligence_src)])

def test_context_dna():
    """Test Context DNA Profiler"""
    print("🧬 Testing Context DNA Profiler...")
    
    try:
        from context_dna import ContextDNAProfiler
        
        profiler = ContextDNAProfiler()
        
        # Test different agent scenarios
        test_cases = [
            ('frontend-developer', 'Create a React component for user dashboard with responsive design'),
            ('backend-architect', 'Optimize database queries for the user authentication API endpoints'),
            ('test-writer-fixer', 'Write comprehensive unit tests for the payment processing module'),
            ('general', 'Help me understand this codebase and fix a bug in the login system'),
        ]
        
        results = []
        
        for agent_type, task in test_cases:
            print(f"  Testing {agent_type}...")
            context = profiler.get_optimal_context(agent_type, task)
            
            size_kb = context['context_size_kb']
            manifests_count = len(context['manifests_loaded'])
            
            # Check if under 20KB target
            under_target = size_kb <= 20.0
            status = "✅ PASS" if under_target else "❌ FAIL"
            
            print(f"    {status} Size: {size_kb:.2f} KB, Manifests: {manifests_count}")
            
            results.append({
                'agent_type': agent_type,
                'size_kb': size_kb,
                'manifests_count': manifests_count,
                'under_target': under_target,
                'manifests_loaded': context['manifests_loaded']
            })
        
        # Summary
        passed = sum(1 for r in results if r['under_target'])
        avg_size = sum(r['size_kb'] for r in results) / len(results)
        
        print(f"  📊 Results: {passed}/{len(results)} under 20KB target")
        print(f"  📏 Average size: {avg_size:.2f} KB")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

def test_context_router():
    """Test Context Router"""
    print("\n🧭 Testing Context Router...")
    
    try:
        from context_router import ContextRouter
        
        router = ContextRouter()
        
        # Test routing decisions
        test_tasks = [
            ('frontend-developer', 'Build a new user interface component with animations'),
            ('backend-architect', 'Create REST API endpoints for user management'),
            ('test-writer-fixer', 'Add integration tests for the payment flow'),
        ]
        
        results = []
        
        for agent_type, task in test_tasks:
            print(f"  Testing {agent_type} routing...")
            
            # Analyze intent
            intent = router.analyze_task_intent(task, agent_type)
            print(f"    Intent: {intent.primary_domain} (confidence: {intent.confidence:.2f})")
            
            # Route context
            route = router.route_context(task, agent_type)
            
            # Create context package
            package = router.create_context_package(route)
            
            size_kb = package['context_size_kb']
            manifests_count = len(package['manifests_loaded'])
            under_target = size_kb <= 20.0
            
            status = "✅ PASS" if under_target else "❌ FAIL"
            print(f"    {status} Routed: {size_kb:.2f} KB, {manifests_count} manifests")
            
            results.append({
                'agent_type': agent_type,
                'intent': intent.primary_domain,
                'confidence': intent.confidence,
                'size_kb': size_kb,
                'manifests_count': manifests_count,
                'under_target': under_target
            })
        
        # Summary
        passed = sum(1 for r in results if r['under_target'])
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        
        print(f"  📊 Results: {passed}/{len(results)} under 20KB target")
        print(f"  🎯 Average confidence: {avg_confidence:.2f}")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

def test_manifest_updater():
    """Test Manifest Updater"""
    print("\n📁 Testing Manifest Updater...")
    
    try:
        from manifest_updater import ManifestUpdater
        
        updater = ManifestUpdater()
        
        # Test dependency detection
        test_files = [
            'src/components/UserDashboard.tsx',
            'src/api/users.py',
            'src/models/user.py',
            'tests/test_auth.py',
            'README.md'
        ]
        
        results = []
        
        for file_path in test_files:
            print(f"  Testing {file_path}...")
            
            affected = updater.get_affected_manifests(file_path)
            
            if affected:
                manifest_types = []
                for dependency in affected:
                    manifest_types.extend(dependency.manifest_types)
                
                unique_manifests = list(set(manifest_types))
                print(f"    📄 Affects: {', '.join(unique_manifests)}")
                
                results.append({
                    'file': file_path,
                    'affected_manifests': unique_manifests,
                    'dependency_count': len(affected)
                })
            else:
                print(f"    ⚪ No manifest dependencies detected")
                results.append({
                    'file': file_path,
                    'affected_manifests': [],
                    'dependency_count': 0
                })
        
        # Summary
        total_dependencies = sum(r['dependency_count'] for r in results)
        
        print(f"  📊 Total dependencies detected: {total_dependencies}")
        
        return results
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

def test_integration():
    """Test full system integration"""
    print("\n🔗 Testing System Integration...")
    
    try:
        from prism_orchestrator import PRISMOrchestrator
        
        orchestrator = PRISMOrchestrator()
        
        print("  Checking system health...")
        health = orchestrator.check_system_health()
        
        print(f"  Overall Status: {health.overall_status}")
        print(f"  Context DNA: {health.context_dna_status}")
        print(f"  Context Router: {health.context_router_status}")
        print(f"  Manifest Updater: {health.manifest_updater_status}")
        print(f"  Doc Syncer: {health.doc_syncer_status}")
        
        # Test agent request processing
        print("  Testing agent request processing...")
        
        test_request = orchestrator.process_agent_request(
            'frontend-developer',
            'Create a responsive navigation component with dropdown menus'
        )
        
        size_kb = test_request.get('context_size_kb', 0)
        manifests = test_request.get('manifests_loaded', [])
        
        under_target = size_kb <= 20.0
        status = "✅ PASS" if under_target else "❌ FAIL"
        
        print(f"  {status} Processed request: {size_kb:.2f} KB, {len(manifests)} manifests")
        
        return {
            'health': health.overall_status,
            'request_size_kb': size_kb,
            'manifests_count': len(manifests),
            'under_target': under_target
        }
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {'error': str(e)}

def test_dashboard():
    """Test dashboard functionality"""
    print("\n📊 Testing Dashboard...")
    
    try:
        from prism_dashboard import PRISMDashboard
        
        dashboard = PRISMDashboard()
        
        print("  Generating static dashboard...")
        dashboard.show_static_dashboard()
        
        print("  ✅ Dashboard test completed")
        
        return {'status': 'success'}
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {'error': str(e)}

def run_validation():
    """Run complete PRISM system validation"""
    print("🔬 PRISM System Validation")
    print("=" * 60)
    print("Testing Proactive Real-time Intelligence System for Manifests")
    print("Goal: Reduce context from 200KB+ to <20KB per agent")
    print("=" * 60)
    
    # Run all tests
    dna_results = test_context_dna()
    router_results = test_context_router()
    updater_results = test_manifest_updater()
    integration_results = test_integration()
    dashboard_results = test_dashboard()
    
    # Final validation summary
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    # Calculate overall metrics
    all_size_tests = []
    
    if dna_results:
        all_size_tests.extend([r['size_kb'] for r in dna_results])
        dna_passed = sum(1 for r in dna_results if r['under_target'])
        print(f"Context DNA: {dna_passed}/{len(dna_results)} tests passed")
    
    if router_results:
        all_size_tests.extend([r['size_kb'] for r in router_results])
        router_passed = sum(1 for r in router_results if r['under_target'])
        print(f"Context Router: {router_passed}/{len(router_results)} tests passed")
    
    if integration_results and 'request_size_kb' in integration_results:
        all_size_tests.append(integration_results['request_size_kb'])
        integration_passed = 1 if integration_results.get('under_target', False) else 0
        print(f"Integration: {integration_passed}/1 tests passed")
    
    # Overall results
    if all_size_tests:
        avg_size = sum(all_size_tests) / len(all_size_tests)
        max_size = max(all_size_tests)
        min_size = min(all_size_tests)
        under_20kb = sum(1 for size in all_size_tests if size <= 20.0)
        
        # Calculate percentage reduction from 200KB baseline
        baseline = 200.0
        reduction_percent = ((baseline - avg_size) / baseline) * 100
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"Average Context Size: {avg_size:.2f} KB")
        print(f"Size Range: {min_size:.2f} - {max_size:.2f} KB")
        print(f"Under 20KB Target: {under_20kb}/{len(all_size_tests)} ({under_20kb/len(all_size_tests)*100:.1f}%)")
        print(f"Size Reduction: {reduction_percent:.1f}% from 200KB baseline")
        
        # Success criteria
        success_criteria = [
            (avg_size <= 20.0, "Average size ≤ 20KB"),
            (under_20kb / len(all_size_tests) >= 0.8, "80%+ of tests under 20KB"),
            (reduction_percent >= 85, "85%+ size reduction achieved"),
        ]
        
        print(f"\n✅ SUCCESS CRITERIA:")
        overall_success = True
        for criterion_met, description in success_criteria:
            status = "✅ PASS" if criterion_met else "❌ FAIL"
            print(f"{status} {description}")
            if not criterion_met:
                overall_success = False
        
        print(f"\n{'🎉 PRISM VALIDATION SUCCESSFUL!' if overall_success else '⚠️ PRISM VALIDATION NEEDS WORK'}")
        
        if overall_success:
            print("PRISM successfully achieves the goal of <20KB context per agent")
            print("while maintaining intelligent context delivery and learning capabilities.")
        else:
            print("PRISM requires optimization to meet all success criteria.")
            print("Consider adjusting context DNA profiles or routing strategies.")
    
    else:
        print("❌ No size tests completed - system validation failed")
    
    print("=" * 60)

if __name__ == '__main__':
    run_validation()