"""Pytest configuration and fixtures"""
import pytest
from pathlib import Path
import tempfile
import git

@pytest.fixture
def temp_repo():
    """Create a temporary git repository for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        # Add initial commit
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Repository")
        repo.index.add([str(readme)])
        repo.index.commit("Initial commit")
        yield repo

@pytest.fixture
def sample_changes():
    """Sample file changes for testing"""
    return {
        "added": ["src/new_feature.py"],
        "modified": ["src/existing.py", "README.md"],
        "deleted": ["src/old_feature.py"]
    }
