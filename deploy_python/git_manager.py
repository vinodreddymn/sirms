"""
===============================================================================
SIRMS Deployment Toolkit

Module : git_manager.py
Purpose: Git Operations
Version : 2.0
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass

from git import Repo, GitCommandError


class GitManagerError(Exception):
    """Raised when a Git operation fails."""


@dataclass
class GitWorkflowResult:
    branch: str
    commit: str
    committed: bool


class GitManager:
    """
    Git Operations Manager
    """

    def __init__(self, repository: str | Path):
        self.repository = Path(repository)

        if not self.repository.exists():
            raise FileNotFoundError(self.repository)

        try:
            self.repo = Repo(self.repository)
        except Exception as ex:
            raise GitManagerError(
                f"{self.repository} is not a Git repository."
            ) from ex

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def is_clean(self) -> bool:
        """
        Returns True if the repository has no pending changes.
        """
        return not self.repo.is_dirty(untracked_files=True)

    # ------------------------------------------------------------------
    # Information
    # ------------------------------------------------------------------

    @property
    def branch(self) -> str:
        return self.repo.active_branch.name

    @property
    def commit(self) -> str:
        return self.repo.head.commit.hexsha[:7]

    # ------------------------------------------------------------------
    # Git Commands
    # ------------------------------------------------------------------

    def add_all(self) -> None:
        """
        git add .
        """
        try:
            self.repo.git.add(all=True)
        except GitCommandError as ex:
            raise GitManagerError("git add failed.") from ex

    def commit_changes(self, message: str) -> bool:
        """
        git commit
        """

        if self.is_clean():
            return False

        try:
            self.repo.index.commit(message)
            return True
        except Exception as ex:
            raise GitManagerError("git commit failed.") from ex

    def push(self) -> None:
        """
        git push
        """
        try:
            origin = self.repo.remote("origin")
            origin.push()
        except Exception as ex:
            raise GitManagerError("git push failed.") from ex

    def pull(self) -> None:
        """
        git pull --ff-only
        """
        try:
            origin = self.repo.remote("origin")
            origin.pull(ff_only=True)
        except Exception as ex:
            raise GitManagerError("git pull failed.") from ex

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def workflow(
        self,
        commit_message: str,
        push: bool = False,
    ) -> GitWorkflowResult:
        """
        Complete Git workflow.
        """

        self.add_all()

        committed = self.commit_changes(commit_message)

        if push:
            self.push()

        return GitWorkflowResult(
            branch=self.branch,
            commit=self.commit,
            committed=committed,
        )