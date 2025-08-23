#!/usr/bin/env python3
"""
Unit tests for GitStateAnalyzer

Using Framework: Testing Strategy
- Comprehensive test coverage
- Test both happy paths and edge cases
- Use fixtures for consistent test data
- Mock external dependencies (git operations)
"""

import pytest
from pathlib import Path
import tempfile
import git
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.analyzer import (
    GitStateAnalyzer,
    RepositoryState,
    FileChange,
    ChangesSummary,
    WorkPattern
)


class TestGitStateAnalyzer:
    """
    Test suite for GitStateAnalyzer
    
    Using Framework: Test Organization
    - Grouped by functionality
    - Clear test names describing what's being tested
    - Each test focuses on single aspect
    """
    
    def test_initialization_with_valid_repo(self, temp_repo):
        """Test analyzer initializes with valid repository"""
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        assert analyzer.repo_path == Path(temp_repo.working_dir).resolve()
        assert analyzer.repo is not None
    
    def test_initialization_with_invalid_path(self, tmp_path):
        """Test analyzer raises error for non-git directory"""
        with pytest.raises(ValueError, match="Not a git repository"):
            GitStateAnalyzer(tmp_path)
    
    def test_get_repository_state_clean(self, temp_repo):
        """Test state detection for clean repository"""
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        state = analyzer.get_repository_state()
        
        assert isinstance(state, RepositoryState)
        assert state.branch == "main" or state.branch == "master"
        assert state.is_clean() is True
        assert state.total_changes == 0
        assert state.has_uncommitted is False
        assert state.has_untracked is False
    
    def test_get_repository_state_with_changes(self, temp_repo):
        """Test state detection with uncommitted changes"""
        # Add a new file
        test_file = Path(temp_repo.working_dir) / "test.py"
        test_file.write_text("print('test')")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        state = analyzer.get_repository_state()
        
        assert state.is_clean() is False
        assert state.has_untracked is True
        assert state.total_changes == 1
    
    def test_get_uncommitted_changes_untracked(self, temp_repo):
        """Test detection of untracked files"""
        # Add untracked files
        (Path(temp_repo.working_dir) / "new_feature.py").write_text("# New feature")
        (Path(temp_repo.working_dir) / "test_feature.py").write_text("# Test")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        
        assert len(changes) == 2
        assert all(c.change_type == 'added' for c in changes)
        assert 'new_feature.py' in [c.path for c in changes]
    
    def test_get_uncommitted_changes_modified(self, temp_repo):
        """Test detection of modified files"""
        # Modify existing file
        readme = Path(temp_repo.working_dir) / "README.md"
        readme.write_text("# Updated README\nNew content")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        
        assert len(changes) == 1
        assert changes[0].change_type == 'modified'
        assert changes[0].path == 'README.md'
    
    def test_categorize_changes(self, temp_repo):
        """Test file categorization"""
        # Create files of different types
        files = {
            "src/feature.py": "source",
            "test_feature.py": "test",
            "config.json": "config",
            "README.md": "documentation",
            "styles.css": "style"
        }
        
        for filepath, expected_category in files.items():
            path = Path(temp_repo.working_dir) / filepath
            path.parent.mkdir(exist_ok=True)
            path.write_text(f"# {filepath}")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        categories = analyzer.categorize_changes(changes)
        
        # Check categorization
        assert len(categories) > 0
        assert 'source' in categories or 'test' in categories
    
    def test_generate_change_summary(self, temp_repo):
        """Test change summary generation"""
        # Create various changes
        (Path(temp_repo.working_dir) / "new.py").write_text("# New file")
        (Path(temp_repo.working_dir) / "README.md").write_text("# Modified")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        summary = analyzer.generate_change_summary()
        
        assert isinstance(summary, ChangesSummary)
        assert summary.total_files == 2
        assert len(summary.added_files) == 1
        assert len(summary.modified_files) == 1
        assert summary.work_pattern != WorkPattern.UNKNOWN
    
    def test_detect_work_pattern_feature(self, temp_repo):
        """Test feature pattern detection"""
        # Create feature-like changes
        src_dir = Path(temp_repo.working_dir) / "src"
        src_dir.mkdir()
        (src_dir / "new_feature.py").write_text("# New feature implementation")
        (src_dir / "feature_utils.py").write_text("# Feature utilities")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        pattern = analyzer.detect_work_pattern(changes)
        
        assert pattern == WorkPattern.FEATURE
    
    def test_detect_work_pattern_testing(self, temp_repo):
        """Test testing pattern detection"""
        # Create test files
        (Path(temp_repo.working_dir) / "test_module.py").write_text("# Tests")
        (Path(temp_repo.working_dir) / "module.test.js").write_text("// Tests")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        pattern = analyzer.detect_work_pattern(changes)
        
        assert pattern == WorkPattern.TESTING
    
    def test_detect_work_pattern_documentation(self, temp_repo):
        """Test documentation pattern detection"""
        # Create documentation files
        (Path(temp_repo.working_dir) / "API.md").write_text("# API Docs")
        (Path(temp_repo.working_dir) / "CHANGELOG.md").write_text("# Changelog")
        docs_dir = Path(temp_repo.working_dir) / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.md").write_text("# User Guide")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        pattern = analyzer.detect_work_pattern(changes)
        
        assert pattern == WorkPattern.DOCUMENTATION
    
    def test_detect_work_pattern_configuration(self, temp_repo):
        """Test configuration pattern detection"""
        # Create config files
        (Path(temp_repo.working_dir) / "config.json").write_text("{}")
        (Path(temp_repo.working_dir) / "settings.yaml").write_text("key: value")
        (Path(temp_repo.working_dir) / ".env").write_text("VAR=value")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        changes = analyzer.get_uncommitted_changes()
        pattern = analyzer.detect_work_pattern(changes)
        
        assert pattern == WorkPattern.CONFIGURATION
    
    def test_file_categorization(self, temp_repo):
        """Test individual file categorization"""
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        
        test_cases = [
            ("src/main.py", "source"),
            ("test_main.py", "test"),
            ("README.md", "documentation"),
            ("styles.css", "style"),
            ("config.json", "config"),
            ("data.csv", "data"),
            ("image.png", "asset"),
            ("unknown.xyz", "other")
        ]
        
        for filepath, expected in test_cases:
            category = analyzer._categorize_file(filepath)
            assert category == expected, f"Expected {filepath} to be {expected}, got {category}"
    
    def test_get_recent_commits(self, temp_repo):
        """Test recent commits retrieval"""
        # Add some commits
        for i in range(3):
            file_path = Path(temp_repo.working_dir) / f"file{i}.txt"
            file_path.write_text(f"Content {i}")
            temp_repo.index.add([str(file_path)])
            temp_repo.index.commit(f"Commit {i}")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        commits = analyzer.get_recent_commits(limit=2)
        
        assert len(commits) == 2
        assert commits[0]['message'] == "Commit 2"
        assert commits[1]['message'] == "Commit 1"
        assert all('hash' in c for c in commits)
        assert all('author' in c for c in commits)
    
    def test_empty_repository_handling(self):
        """Test handling of empty repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty git repo
            repo = git.Repo.init(tmpdir)
            
            analyzer = GitStateAnalyzer(tmpdir)
            state = analyzer.get_repository_state()
            
            # Should handle gracefully
            assert state.total_changes == 0
            assert state.last_commit_hash is None
    
    def test_large_changeset_performance(self, temp_repo):
        """Test performance with many changes"""
        # Create many files
        for i in range(100):
            file_path = Path(temp_repo.working_dir) / f"file_{i}.py"
            file_path.write_text(f"# File {i}")
        
        analyzer = GitStateAnalyzer(temp_repo.working_dir)
        
        # Should complete within reasonable time
        import time
        start = time.time()
        changes = analyzer.get_uncommitted_changes()
        summary = analyzer.generate_change_summary(changes)
        elapsed = time.time() - start
        
        assert len(changes) == 100
        assert elapsed < 2.0  # Should complete within 2 seconds
        assert summary.total_files == 100


class TestRepositoryState:
    """Test RepositoryState dataclass"""
    
    def test_is_clean(self):
        """Test clean state detection"""
        state = RepositoryState(
            branch="main",
            has_uncommitted=False,
            has_untracked=False,
            total_changes=0,
            ahead_of_remote=0,
            behind_remote=0
        )
        assert state.is_clean() is True
        
        state.has_uncommitted = True
        assert state.is_clean() is False
    
    def test_needs_sync(self):
        """Test sync detection"""
        state = RepositoryState(
            branch="main",
            has_uncommitted=False,
            has_untracked=False,
            total_changes=0,
            ahead_of_remote=0,
            behind_remote=0
        )
        assert state.needs_sync() is False
        
        state.ahead_of_remote = 2
        assert state.needs_sync() is True
        
        state.ahead_of_remote = 0
        state.behind_remote = 3
        assert state.needs_sync() is True


class TestChangesSummary:
    """Test ChangesSummary dataclass"""
    
    def test_to_dict(self):
        """Test dictionary conversion"""
        summary = ChangesSummary(
            total_files=5,
            added_files=["a.py", "b.py"],
            modified_files=["c.py"],
            deleted_files=["d.py"],
            work_pattern=WorkPattern.FEATURE,
            lines_added=100,
            lines_deleted=50
        )
        
        result = summary.to_dict()
        
        assert result['total_files'] == 5
        assert result['added'] == 2
        assert result['modified'] == 1
        assert result['deleted'] == 1
        assert result['work_pattern'] == 'feature'
        assert result['lines_added'] == 100
        assert result['lines_deleted'] == 50


# Integration test
@pytest.mark.integration
def test_full_workflow(temp_repo):
    """
    Test complete analyzer workflow
    
    Using Framework: Integration Testing
    - Tests multiple components working together
    - Validates end-to-end functionality
    """
    # Setup: Create various changes
    work_dir = Path(temp_repo.working_dir)
    
    # Add source files
    src_dir = work_dir / "src"
    src_dir.mkdir()
    (src_dir / "feature.py").write_text("def new_feature(): pass")
    (src_dir / "utils.py").write_text("# Utilities")
    
    # Add test file
    (work_dir / "test_feature.py").write_text("def test_feature(): assert True")
    
    # Add documentation
    (work_dir / "API.md").write_text("# API Documentation")
    
    # Modify existing README
    (work_dir / "README.md").write_text("# Updated Project\nNow with new features!")
    
    # Initialize analyzer
    analyzer = GitStateAnalyzer(work_dir)
    
    # Get repository state
    state = analyzer.get_repository_state()
    assert not state.is_clean()
    assert state.total_changes == 5
    
    # Get changes
    changes = analyzer.get_uncommitted_changes()
    assert len(changes) == 5
    
    # Categorize changes
    categories = analyzer.categorize_changes(changes)
    assert 'source' in categories
    assert 'test' in categories
    assert 'documentation' in categories
    
    # Generate summary
    summary = analyzer.generate_change_summary(changes)
    assert summary.total_files == 5
    assert summary.work_pattern == WorkPattern.FEATURE
    
    # Verify complete workflow succeeded
    assert len(summary.added_files) == 4
    assert len(summary.modified_files) == 1