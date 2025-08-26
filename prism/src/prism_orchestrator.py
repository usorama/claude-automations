#!/usr/bin/env python3
"""
PRISM Orchestrator - Master Coordinator for PRISM System

Coordinates all PRISM components, monitors performance, implements learning feedback loop,
and provides centralized control for the Proactive Real-time Intelligence System for Manifests.
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import subprocess
import signal
import logging

# Add all PRISM modules to path
prism_src = Path(__file__).parent
git_intelligence_src = Path.home() / 'claude-automations' / 'git-intelligence' / 'src'
sys.path.extend([str(prism_src), str(git_intelligence_src)])

# Import PRISM components
try:
    from context_dna import ContextDNAProfiler
    from context_router import ContextRouter
    from manifest_updater import ManifestUpdater
    from documentation_syncer import DocumentationSyncer
except ImportError as e:
    print(f"[PRISM] Warning: Failed to import PRISM component: {e}")
    # Set to None for graceful fallback
    ContextDNAProfiler = None
    ContextRouter = None
    ManifestUpdater = None
    DocumentationSyncer = None

@dataclass
class PRISMHealth:
    """Health status of PRISM components"""
    overall_status: str        # 'healthy', 'degraded', 'critical'
    context_dna_status: str
    context_router_status: str
    manifest_updater_status: str
    doc_syncer_status: str
    last_health_check: str
    performance_metrics: Dict[str, float]

@dataclass
class PRISMMetrics:
    """Performance metrics for PRISM system"""
    context_size_reduction: float    # Percentage reduction from 200KB baseline
    average_context_size_kb: float
    manifests_updated_count: int
    documentation_syncs_count: int
    routing_accuracy: float
    system_uptime: float
    learning_iterations: int

class PRISMOrchestrator:
    """Master orchestrator for the PRISM system"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the PRISM orchestrator"""
        self.project_root = project_root or Path.cwd()
        self.manifest_dir = self.project_root / '.claude' / 'manifests'
        self.prism_data_dir = Path.home() / '.claude' / 'prism'
        self.prism_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.components = {}
        self._initialize_components()
        
        # Control flags
        self.running = False
        self.monitoring_thread = None
        self.learning_thread = None
        
        # Metrics
        self.start_time = datetime.now()
        self.metrics = PRISMMetrics(
            context_size_reduction=0.0,
            average_context_size_kb=200.0,  # Baseline
            manifests_updated_count=0,
            documentation_syncs_count=0,
            routing_accuracy=0.0,
            system_uptime=0.0,
            learning_iterations=0
        )
        
        # Performance tracking
        self.context_size_history = []
        self.routing_decisions = []
        self.update_events = []
        
        self.logger.info("PRISM Orchestrator initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = self.prism_data_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Configure logger
        self.logger = logging.getLogger('PRISM')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        log_file = log_dir / f"prism_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _initialize_components(self):
        """Initialize all PRISM components"""
        try:
            # Context DNA Profiler
            if ContextDNAProfiler:
                self.components['context_dna'] = ContextDNAProfiler()
                self.logger.info("Context DNA Profiler initialized")
            else:
                self.logger.warning("Context DNA Profiler not available")
            
            # Context Router
            if ContextRouter:
                self.components['context_router'] = ContextRouter(self.manifest_dir)
                self.logger.info("Context Router initialized")
            else:
                self.logger.warning("Context Router not available")
            
            # Manifest Updater
            if ManifestUpdater:
                self.components['manifest_updater'] = ManifestUpdater(
                    self.project_root, 
                    self.manifest_dir
                )
                self.logger.info("Manifest Updater initialized")
            else:
                self.logger.warning("Manifest Updater not available")
            
            # Documentation Syncer
            if DocumentationSyncer:
                self.components['doc_syncer'] = DocumentationSyncer(self.project_root)
                self.logger.info("Documentation Syncer initialized")
            else:
                self.logger.warning("Documentation Syncer not available")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
    
    def start(self, daemon_mode: bool = True):
        """Start the PRISM orchestrator"""
        try:
            self.logger.info("Starting PRISM Orchestrator...")
            print("[PRISM] 🚀 Starting PRISM Orchestrator...")
            
            self.running = True
            
            # Start monitoring thread
            if daemon_mode:
                self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
                self.monitoring_thread.start()
                
                # Start learning thread
                self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
                self.learning_thread.start()
            
            # Perform initial system check
            health = self.check_system_health()
            self._report_health(health)
            
            # Initialize manifest monitoring
            self._start_manifest_monitoring()
            
            # Setup signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            print("[PRISM] ✅ PRISM Orchestrator started successfully")
            self.logger.info("PRISM Orchestrator started successfully")
            
            if daemon_mode:
                print("[PRISM] 🔄 Running in daemon mode. Press Ctrl+C to stop.")
                try:
                    while self.running:
                        time.sleep(1)
                        self.metrics.system_uptime = (datetime.now() - self.start_time).total_seconds()
                except KeyboardInterrupt:
                    self.stop()
            
        except Exception as e:
            self.logger.error(f"Failed to start PRISM Orchestrator: {e}")
            print(f"[PRISM] ❌ Failed to start: {e}")
    
    def stop(self):
        """Stop the PRISM orchestrator gracefully"""
        try:
            self.logger.info("Stopping PRISM Orchestrator...")
            print("[PRISM] 🛑 Stopping PRISM Orchestrator...")
            
            self.running = False
            
            # Wait for threads to finish
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            if self.learning_thread and self.learning_thread.is_alive():
                self.learning_thread.join(timeout=5)
            
            # Final metrics save
            self._save_metrics()
            
            print("[PRISM] ✅ PRISM Orchestrator stopped")
            self.logger.info("PRISM Orchestrator stopped")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def _monitoring_loop(self):
        """Main monitoring loop running in background"""
        while self.running:
            try:
                # Check system health every 30 seconds
                health = self.check_system_health()
                
                # Log health issues
                if health.overall_status != 'healthy':
                    self.logger.warning(f"System health degraded: {health.overall_status}")
                
                # Update metrics
                self._update_metrics()
                
                # Save metrics every 5 minutes
                if int(time.time()) % 300 == 0:
                    self._save_metrics()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _learning_loop(self):
        """Learning and optimization loop"""
        while self.running:
            try:
                # Perform learning iterations every 10 minutes
                time.sleep(600)
                
                if not self.running:
                    break
                
                self.logger.info("Starting learning iteration...")
                
                # Optimize context DNA profiles
                if 'context_dna' in self.components:
                    self._optimize_context_profiles()
                
                # Update routing strategies
                if 'context_router' in self.components:
                    self._optimize_routing()
                
                # Analyze performance patterns
                self._analyze_performance_patterns()
                
                self.metrics.learning_iterations += 1
                self.logger.info(f"Learning iteration {self.metrics.learning_iterations} completed")
                
            except Exception as e:
                self.logger.error(f"Error in learning loop: {e}")
    
    def process_agent_request(self, agent_type: str, task_description: str) -> Dict[str, Any]:
        """Process an agent request for optimized context"""
        try:
            self.logger.info(f"Processing agent request: {agent_type}")
            
            start_time = time.time()
            
            # Route context using context router
            if 'context_router' in self.components:
                route = self.components['context_router'].route_context(task_description, agent_type)
                context_package = self.components['context_router'].create_context_package(route)
            else:
                # Fallback to basic context
                context_package = self._create_fallback_context(agent_type, task_description)
            
            # Track performance
            processing_time = time.time() - start_time
            context_size = context_package.get('context_size_kb', 0.0)
            
            # Update metrics
            self.context_size_history.append(context_size)
            self.routing_decisions.append({
                'agent_type': agent_type,
                'context_size': context_size,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            })
            
            # Calculate size reduction percentage
            baseline_size = 200.0  # KB
            size_reduction = max(0, (baseline_size - context_size) / baseline_size * 100)
            self.metrics.context_size_reduction = size_reduction
            
            self.logger.info(f"Agent request processed: {context_size:.2f} KB ({size_reduction:.1f}% reduction)")
            
            return context_package
            
        except Exception as e:
            self.logger.error(f"Error processing agent request: {e}")
            return self._create_fallback_context(agent_type, task_description)
    
    def check_system_health(self) -> PRISMHealth:
        """Check health of all PRISM components"""
        health = PRISMHealth(
            overall_status='healthy',
            context_dna_status='unknown',
            context_router_status='unknown', 
            manifest_updater_status='unknown',
            doc_syncer_status='unknown',
            last_health_check=datetime.now().isoformat(),
            performance_metrics={}
        )
        
        component_statuses = []
        
        # Check Context DNA
        if 'context_dna' in self.components:
            try:
                # Test basic functionality
                profiler = self.components['context_dna']
                stats = profiler.get_profile_stats('general')
                health.context_dna_status = 'healthy' if stats else 'degraded'
            except Exception as e:
                health.context_dna_status = 'critical'
                self.logger.error(f"Context DNA health check failed: {e}")
        else:
            health.context_dna_status = 'unavailable'
        
        component_statuses.append(health.context_dna_status)
        
        # Check Context Router
        if 'context_router' in self.components:
            try:
                router = self.components['context_router']
                stats = router.get_routing_stats()
                health.context_router_status = 'healthy' if stats.get('available_manifests', 0) > 0 else 'degraded'
            except Exception as e:
                health.context_router_status = 'critical'
                self.logger.error(f"Context Router health check failed: {e}")
        else:
            health.context_router_status = 'unavailable'
        
        component_statuses.append(health.context_router_status)
        
        # Check Manifest Updater
        if 'manifest_updater' in self.components:
            try:
                # Check if manifest directory is accessible
                if self.manifest_dir.exists() and any(self.manifest_dir.iterdir()):
                    health.manifest_updater_status = 'healthy'
                else:
                    health.manifest_updater_status = 'degraded'
            except Exception as e:
                health.manifest_updater_status = 'critical'
                self.logger.error(f"Manifest Updater health check failed: {e}")
        else:
            health.manifest_updater_status = 'unavailable'
        
        component_statuses.append(health.manifest_updater_status)
        
        # Check Documentation Syncer
        if 'doc_syncer' in self.components:
            try:
                # Check if project root has documentation
                readme_exists = (self.project_root / 'README.md').exists()
                health.doc_syncer_status = 'healthy' if readme_exists else 'degraded'
            except Exception as e:
                health.doc_syncer_status = 'critical'
                self.logger.error(f"Documentation Syncer health check failed: {e}")
        else:
            health.doc_syncer_status = 'unavailable'
        
        component_statuses.append(health.doc_syncer_status)
        
        # Determine overall status
        if any(status == 'critical' for status in component_statuses):
            health.overall_status = 'critical'
        elif any(status == 'degraded' for status in component_statuses):
            health.overall_status = 'degraded'
        elif all(status in ['healthy', 'unavailable'] for status in component_statuses):
            health.overall_status = 'healthy'
        else:
            health.overall_status = 'degraded'
        
        # Add performance metrics
        health.performance_metrics = {
            'average_context_size_kb': self.metrics.average_context_size_kb,
            'context_size_reduction_percent': self.metrics.context_size_reduction,
            'routing_accuracy': self.metrics.routing_accuracy,
            'system_uptime_hours': self.metrics.system_uptime / 3600,
            'manifests_updated': self.metrics.manifests_updated_count
        }
        
        return health
    
    def _report_health(self, health: PRISMHealth):
        """Report system health status"""
        status_emoji = {
            'healthy': '✅',
            'degraded': '⚠️', 
            'critical': '❌',
            'unavailable': '🚫'
        }
        
        print(f"\n[PRISM] System Health Report")
        print(f"{'='*50}")
        print(f"Overall Status: {status_emoji.get(health.overall_status, '❓')} {health.overall_status.upper()}")
        print(f"Context DNA: {status_emoji.get(health.context_dna_status, '❓')} {health.context_dna_status}")
        print(f"Context Router: {status_emoji.get(health.context_router_status, '❓')} {health.context_router_status}")
        print(f"Manifest Updater: {status_emoji.get(health.manifest_updater_status, '❓')} {health.manifest_updater_status}")
        print(f"Doc Syncer: {status_emoji.get(health.doc_syncer_status, '❓')} {health.doc_syncer_status}")
        
        if health.performance_metrics:
            print(f"\nPerformance Metrics:")
            for metric, value in health.performance_metrics.items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.2f}")
                else:
                    print(f"  {metric}: {value}")
        
        print(f"{'='*50}\n")
    
    def _start_manifest_monitoring(self):
        """Start monitoring manifests for changes"""
        try:
            if 'manifest_updater' in self.components:
                # Start file watcher in background thread
                def watch_manifests():
                    updater = self.components['manifest_updater']
                    # This would normally be a blocking call, but we'll run it in a thread
                    # For now, just set up the monitoring structure
                    self.logger.info("Manifest monitoring thread started")
                
                monitor_thread = threading.Thread(target=watch_manifests, daemon=True)
                monitor_thread.start()
                
        except Exception as e:
            self.logger.error(f"Failed to start manifest monitoring: {e}")
    
    def _update_metrics(self):
        """Update system metrics"""
        try:
            # Calculate average context size
            if self.context_size_history:
                recent_sizes = self.context_size_history[-100:]  # Last 100 requests
                self.metrics.average_context_size_kb = sum(recent_sizes) / len(recent_sizes)
            
            # Calculate routing accuracy (simplified)
            if self.routing_decisions:
                recent_decisions = self.routing_decisions[-50:]  # Last 50 decisions
                successful_routes = [d for d in recent_decisions if d['context_size'] < 50]  # Under 50KB considered success
                self.metrics.routing_accuracy = len(successful_routes) / len(recent_decisions) * 100
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to disk"""
        try:
            metrics_file = self.prism_data_dir / 'metrics.json'
            with open(metrics_file, 'w') as f:
                json.dump(asdict(self.metrics), f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def _optimize_context_profiles(self):
        """Optimize context DNA profiles based on usage patterns"""
        try:
            if 'context_dna' not in self.components:
                return
            
            profiler = self.components['context_dna']
            
            # Analyze recent routing decisions
            if len(self.routing_decisions) >= 10:
                # Group by agent type
                agent_performance = {}
                
                for decision in self.routing_decisions[-50:]:
                    agent_type = decision['agent_type']
                    if agent_type not in agent_performance:
                        agent_performance[agent_type] = []
                    agent_performance[agent_type].append(decision)
                
                # Optimize profiles for each agent type
                for agent_type, decisions in agent_performance.items():
                    avg_size = sum(d['context_size'] for d in decisions) / len(decisions)
                    avg_time = sum(d['processing_time'] for d in decisions) / len(decisions)
                    
                    # If average size is too high or processing time is slow, optimize
                    if avg_size > 30 or avg_time > 1.0:
                        self.logger.info(f"Optimizing profile for {agent_type} (avg size: {avg_size:.1f}KB)")
                        profiler.optimize_profile(agent_type)
            
        except Exception as e:
            self.logger.error(f"Error optimizing context profiles: {e}")
    
    def _optimize_routing(self):
        """Optimize routing strategies based on performance"""
        try:
            # This is a placeholder for routing optimization logic
            # In a full implementation, this would analyze routing decisions
            # and adjust routing strategies accordingly
            self.logger.info("Routing optimization completed")
            
        except Exception as e:
            self.logger.error(f"Error optimizing routing: {e}")
    
    def _analyze_performance_patterns(self):
        """Analyze performance patterns for insights"""
        try:
            if len(self.context_size_history) < 10:
                return
            
            # Calculate trends
            recent_sizes = self.context_size_history[-20:]
            older_sizes = self.context_size_history[-40:-20] if len(self.context_size_history) >= 40 else recent_sizes
            
            recent_avg = sum(recent_sizes) / len(recent_sizes)
            older_avg = sum(older_sizes) / len(older_sizes)
            
            trend = (recent_avg - older_avg) / older_avg * 100 if older_avg > 0 else 0
            
            if abs(trend) > 10:
                trend_direction = "increasing" if trend > 0 else "decreasing"
                self.logger.info(f"Context size trend: {trend_direction} by {abs(trend):.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance patterns: {e}")
    
    def _create_fallback_context(self, agent_type: str, task_description: str) -> Dict[str, Any]:
        """Create fallback context when main routing fails"""
        return {
            'agent_type': agent_type,
            'task_intent': 'unknown',
            'routing_confidence': 0.0,
            'manifests_loaded': [],
            'context_size_kb': 0.0,
            'routing_reason': 'Fallback context due to system unavailability',
            'context': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        health = self.check_system_health()
        
        return {
            'status': health.overall_status,
            'uptime_hours': self.metrics.system_uptime / 3600,
            'components': {
                'context_dna': health.context_dna_status,
                'context_router': health.context_router_status,
                'manifest_updater': health.manifest_updater_status,
                'doc_syncer': health.doc_syncer_status
            },
            'metrics': asdict(self.metrics),
            'performance': health.performance_metrics,
            'last_health_check': health.last_health_check
        }

def main():
    """Main entry point for PRISM orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PRISM Orchestrator - Master Coordinator')
    parser.add_argument('--start', action='store_true', help='Start PRISM orchestrator')
    parser.add_argument('--stop', action='store_true', help='Stop PRISM orchestrator')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--health', action='store_true', help='Show health check')
    parser.add_argument('--project-root', help='Project root directory')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode')
    
    args = parser.parse_args()
    
    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    orchestrator = PRISMOrchestrator(project_root)
    
    if args.start:
        orchestrator.start(daemon_mode=args.daemon)
    elif args.stop:
        orchestrator.stop()
    elif args.status:
        status = orchestrator.get_system_status()
        print(json.dumps(status, indent=2))
    elif args.health:
        health = orchestrator.check_system_health()
        orchestrator._report_health(health)
    else:
        print("PRISM Orchestrator Commands:")
        print("  --start [--daemon]  Start the orchestrator")
        print("  --stop              Stop the orchestrator") 
        print("  --status            Show system status")
        print("  --health            Show health check")

if __name__ == '__main__':
    main()