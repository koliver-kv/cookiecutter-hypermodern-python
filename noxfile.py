"""Nox sessions."""

from __future__ import annotations

import shutil
from pathlib import Path

import nox
import platformdirs
from nox.sessions import Session


python_versions = ["3.12", "3.11", "3.10", "3.9"]

nox.options.sessions = ["docs"]
owner, repository = "56kyle", "cookiecutter-hypermodern-python"
labels = "cookiecutter", "documentation"
bump_paths = "README.md", "docs/guide.rst", "docs/index.rst", "docs/quickstart.md"

REPO_ROOT: Path = Path(__file__).parent.resolve()
TEMPLATE_FOLDER: Path = REPO_ROOT / "{{cookiecutter.project_name}}"

COOKIECUTTER_HYPERMODERN_PYTHON_CACHE_FOLDER: Path = Path(
    platformdirs.user_cache_path(
        appname="cookiecutter-hypermodern-python",
        appauthor="56kyle",
        ensure_exists=True,
    )
).resolve()

PROJECT_DEMOS_FOLDER: Path = COOKIECUTTER_HYPERMODERN_PYTHON_CACHE_FOLDER / "project_demos"
DEFAULT_DEMO_NAME: str = "demo-project"
DEMO_ROOT_FOLDER: Path = PROJECT_DEMOS_FOLDER / DEFAULT_DEMO_NAME

GENERATE_DEMO_PROJECT_OPTIONS: tuple[str, ...] = (
    *("--repo-folder", REPO_ROOT),
    *("--demos-cache-folder", PROJECT_DEMOS_FOLDER),
    *("--demo-name", DEFAULT_DEMO_NAME),
)


@nox.session(name="generate-demo-project", python=python_versions[-1])
def generate_demo_project(session: Session) -> None:
    """Generates a demo project using the current cookiecutter."""
    session.install("cookiecutter", "platformdirs", "loguru")
    session.run(
        "python",
        "tools/generate-demo-project.py",
        *GENERATE_DEMO_PROJECT_OPTIONS,
        external=True,
    )


@nox.session(name="prepare-release")
def prepare_release(session: Session) -> None:
    """Prepare a GitHub release."""
    args = [
        f"--owner={owner}",
        f"--repository={repository}",
        *[f"--bump={path}" for path in bump_paths],
        *[f"--label={label}" for label in labels],
        *session.posargs,
    ]
    session.install("click", "github3.py")
    session.run("python", "tools/prepare-github-release.py", *args, external=True)


@nox.session(name="publish-release")
def publish_release(session: Session) -> None:
    """Publish a GitHub release."""
    args = [f"--owner={owner}", f"--repository={repository}", *session.posargs]
    session.install("click", "github3.py")
    session.run("python", "tools/publish-github-release.py", *args, external=True)


nox.options.sessions = ["linkcheck"]


@nox.session
def docs(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or ["-W", "-n", "docs", "docs/_build"]

    if session.interactive and not session.posargs:
        args = ["-a", "--watch=docs/_static", "--open-browser", *args]

    builddir = Path("docs", "_build")
    if builddir.exists():
        shutil.rmtree(builddir)

    session.install("-r", "docs/requirements.txt")

    if session.interactive:
        session.run("sphinx-autobuild", *args)
    else:
        session.run("sphinx-build", *args)


@nox.session
def linkcheck(session: Session) -> None:
    """Build the documentation."""
    args = session.posargs or [
        "-b",
        "linkcheck",
        "-W",
        "--keep-going",
        "docs",
        "docs/_build",
    ]

    builddir = Path("docs", "_build")
    if builddir.exists():
        shutil.rmtree(builddir)

    session.install("-r", "docs/requirements.txt")

    session.run("sphinx-build", *args)


@nox.session(name="dependencies-table")
def dependencies_table(session: Session) -> None:
    """Print the dependencies table."""
    session.install("tomli")
    session.run("python", "tools/dependencies-table.py", external=True)
