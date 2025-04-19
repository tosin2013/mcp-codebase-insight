import pytest
from pathlib import Path

@pytest.fixture
def readme_content():
    readme_path = Path(__file__).parent / "README.md"
    with open(readme_path, "r") as f:
        return f.read()

