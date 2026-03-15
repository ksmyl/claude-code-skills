"""Tests for the nano-banana-pro skill structure and validity.

These tests validate the skill file structure, frontmatter, and script syntax
without requiring a GEMINI_API_KEY (no API calls are made).
"""

import ast
import json
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).parent.parent / "nano-banana-pro"
SKILL_MD = SKILL_DIR / "SKILL.md"
SCRIPTS_DIR = SKILL_DIR / "scripts"


class TestSkillStructure:
    """Validate the skill directory structure."""

    def test_skill_md_exists(self):
        assert SKILL_MD.exists(), "SKILL.md must exist in the skill directory"

    def test_scripts_directory_exists(self):
        assert SCRIPTS_DIR.exists(), "scripts/ directory must exist"

    def test_required_scripts_exist(self):
        expected = ["generate.py", "edit.py", "session.py"]
        for script_name in expected:
            assert (SCRIPTS_DIR / script_name).exists(), f"scripts/{script_name} must exist"

    def test_pyproject_toml_exists(self):
        assert (SKILL_DIR / "pyproject.toml").exists()

    def test_gitignore_exists(self):
        assert (SKILL_DIR / ".gitignore").exists()


class TestSkillFrontmatter:
    """Validate SKILL.md frontmatter."""

    @pytest.fixture()
    def frontmatter(self) -> dict:
        content = SKILL_MD.read_text()
        assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
        end = content.index("---", 3)
        # Simple YAML parsing without external dependency
        raw = content[3:end].strip()
        result = {}
        for line in raw.splitlines():
            if ":" in line and not line.startswith(" ") and not line.startswith("#"):
                key, _, value = line.partition(":")
                result[key.strip()] = value.strip().strip('"').strip("'")
        return result

    def test_has_name(self, frontmatter):
        assert frontmatter.get("name") == "nano-banana-pro"

    def test_has_description(self, frontmatter):
        desc = frontmatter.get("description", "")
        assert len(desc) > 20, "Description should be meaningful"
        assert "image" in desc.lower() or "nano banana" in desc.lower()

    def test_no_unsupported_fields(self, frontmatter):
        supported = {"name", "description", "argument-hint", "disable-model-invocation",
                      "user-invocable", "compatibility", "license", "metadata"}
        for key in frontmatter:
            assert key in supported, f"Unsupported frontmatter field: {key}"

    def test_has_argument_hint(self, frontmatter):
        assert frontmatter.get("argument-hint"), "Should have an argument hint"


class TestSkillContent:
    """Validate SKILL.md content quality."""

    @pytest.fixture()
    def content(self) -> str:
        return SKILL_MD.read_text()

    def test_mentions_api_key(self, content):
        assert "GEMINI_API_KEY" in content, "Must document the API key requirement"

    def test_mentions_model_id(self, content):
        assert "gemini-3-pro-image-preview" in content, "Must reference the correct model"

    def test_mentions_output_directory(self, content):
        assert "nano-banana-output" in content, "Must document the output directory"

    def test_has_generation_instructions(self, content):
        assert "generate" in content.lower() or "generation" in content.lower()

    def test_has_editing_instructions(self, content):
        assert "edit" in content.lower() or "editing" in content.lower()

    def test_has_session_instructions(self, content):
        assert "session" in content.lower() or "iterative" in content.lower()

    def test_has_error_handling_guidance(self, content):
        assert "wrong" in content.lower() or "error" in content.lower(), "Should include error handling guidance"


class TestScriptSyntax:
    """Validate that all Python scripts parse without syntax errors."""

    @pytest.mark.parametrize("script_name", ["generate.py", "edit.py", "session.py"])
    def test_script_parses(self, script_name):
        script = SCRIPTS_DIR / script_name
        source = script.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"{script_name} has syntax error: {e}")

    @pytest.mark.parametrize("script_name", ["generate.py", "edit.py", "session.py"])
    def test_script_has_main_guard(self, script_name):
        source = (SCRIPTS_DIR / script_name).read_text()
        assert '__name__' in source and '__main__' in source, f"{script_name} needs if __name__ == '__main__' guard"

    @pytest.mark.parametrize("script_name", ["generate.py", "edit.py", "session.py"])
    def test_script_has_argparse(self, script_name):
        source = (SCRIPTS_DIR / script_name).read_text()
        assert "argparse" in source, f"{script_name} should use argparse for CLI"

    @pytest.mark.parametrize("script_name", ["generate.py", "edit.py", "session.py"])
    def test_script_checks_api_key(self, script_name):
        source = (SCRIPTS_DIR / script_name).read_text()
        assert "GEMINI_API_KEY" in source, f"{script_name} must check for GEMINI_API_KEY"


class TestSessionScript:
    """Additional tests specific to the session script."""

    @pytest.fixture()
    def source(self) -> str:
        return (SCRIPTS_DIR / "session.py").read_text()

    def test_has_save_session(self, source):
        assert "save_session" in source

    def test_has_load_session(self, source):
        assert "load_session" in source

    def test_has_list_sessions(self, source):
        assert "list_sessions" in source

    def test_session_uses_json(self, source):
        assert "json" in source, "Sessions should be serialized as JSON"
