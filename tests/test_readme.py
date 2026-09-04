from pathlib import Path


def test_readme_documents_safe_databento_workflow():
    text = Path("README.md").read_text(encoding="utf-8")
    for phrase in ("DATABENTO_API_KEY", "metadata.get_cost", "GLBX.MDP3", "mbo", "原始数据"):
        assert phrase in text
