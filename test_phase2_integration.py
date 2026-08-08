from pathlib import Path

from src.runner.test_runner import TestRunner
from src.localizer.repository_scanner import RepositoryScanner
from src.localizer.candidate import CandidateFinder
from src.localizer.bug_localizer import BugLocalizer


def main():
    print("========== Bug Fixing Agent ==========\n")