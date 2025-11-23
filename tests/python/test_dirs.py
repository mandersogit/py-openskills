from openskills.utils import get_search_dirs, get_skills_dir, resolve_destination


def test_get_skills_dir_defaults_to_global_agent(tmp_path) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()

    path = get_skills_dir(home_dir=home_dir)

    assert path == home_dir / ".agent/skills"


def test_get_skills_dir_project_universal(tmp_path) -> None:
    cwd = tmp_path / "project"
    cwd.mkdir()

    path = get_skills_dir(project_local=True, universal=True, cwd=cwd)

    assert path == cwd / ".agent/skills"


def test_get_search_dirs_priority(tmp_path) -> None:
    cwd = tmp_path / "project"
    home_dir = tmp_path / "home"
    cwd.mkdir()
    home_dir.mkdir()

    dirs = get_search_dirs(cwd=cwd, home_dir=home_dir)

    assert dirs == [
        cwd / ".agent/skills",
        home_dir / ".agent/skills",
        cwd / ".claude/skills",
        home_dir / ".claude/skills",
    ]


def test_resolve_destination_defaults_to_project(tmp_path) -> None:
    cwd = tmp_path / "project"
    home_dir = tmp_path / "home"
    cwd.mkdir()
    home_dir.mkdir()

    destination = resolve_destination(cwd=cwd, home_dir=home_dir)

    assert destination.target_dir == cwd / ".agent/skills"
    assert destination.folder == ".agent/skills"
    assert destination.scope == "project"
    assert destination.label.startswith("project")


def test_resolve_destination_claude_special_case(tmp_path) -> None:
    cwd = tmp_path / "project"
    cwd.mkdir()

    destination = resolve_destination(universal=False, cwd=cwd, home_dir=tmp_path)

    assert destination.target_dir == cwd / ".claude/skills"
    assert destination.folder == ".claude/skills"
    assert destination.scope == "project"


def test_resolve_destination_honors_global_universal(tmp_path) -> None:
    cwd = tmp_path / "project"
    home_dir = tmp_path / "home"
    cwd.mkdir()
    home_dir.mkdir()

    destination = resolve_destination(global_install=True, universal=True, cwd=cwd, home_dir=home_dir)

    assert destination.target_dir == home_dir / ".agent/skills"
    assert destination.folder == ".agent/skills"
    assert destination.scope == "global"
    assert "~/.agent/skills" in destination.label
