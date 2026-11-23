# SPDX-License-Identifier: AGPL-3.0-or-later
"""Regression guards for the public-repository PR title validation workflow."""

import re
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/semantic-pr.yml"


class SemanticPullRequestWorkflowSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_only_unprivileged_pull_request_event_is_used(self) -> None:
        self.assertRegex(self.workflow, r"(?m)^on:\n  pull_request:\n")
        self.assertNotRegex(self.workflow, r"\bpull_request_target\b")

    def test_title_lint_runs_on_updates_as_well_as_open_and_edit(self) -> None:
        event = re.search(
            r"(?m)^  pull_request:\n    types:\n((?:      - [^\n]+\n)+)",
            self.workflow,
        )
        self.assertIsNotNone(event)
        assert event is not None
        types = set(re.findall(r"(?m)^      - (\w+)$", event.group(1)))
        self.assertEqual(types, {"opened", "reopened", "edited", "synchronize"})

    def test_token_is_read_only_and_scoped_to_prs(self) -> None:
        permissions = re.search(
            r"(?m)^    permissions:\n((?:      [^\n]+\n)+)",
            self.workflow,
        )
        self.assertIsNotNone(permissions)
        assert permissions is not None
        self.assertEqual(permissions.group(1).strip(), "pull-requests: read")

    def test_title_lint_only_and_no_checkout_of_untrusted_pr_code(self) -> None:
        action_uses = re.findall(r"(?m)^      - uses: ([^\n]+)$", self.workflow)
        self.assertEqual(action_uses, ["amannn/action-semantic-pull-request@v6"])
        self.assertIn("GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}", self.workflow)
        self.assertNotRegex(self.workflow, r"(?m)^\s*(?:- uses: actions/checkout@|run:|wip:|statuses:)")


if __name__ == "__main__":
    unittest.main()
