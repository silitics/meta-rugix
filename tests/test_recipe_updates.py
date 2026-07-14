from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.update_rugix_recipes import (
    Release,
    Version,
    create_recipes,
    eligible_releases,
)


class RecipeUpdateTests(unittest.TestCase):
    def test_selects_only_stable_releases_after_baseline(self) -> None:
        payloads = [
            {"tag_name": "v1.1.2", "draft": False, "prerelease": False},
            {"tag_name": "v1.2.0", "draft": False, "prerelease": False},
            {"tag_name": "v1.2.1-dev.1", "draft": False, "prerelease": True},
            {"tag_name": "v1.2.1", "draft": False, "prerelease": False},
            {"tag_name": "v1.3.0", "draft": True, "prerelease": False},
            {"tag_name": "latest", "draft": False, "prerelease": False},
        ]

        releases = eligible_releases(payloads, Version.parse("1.2.0"))

        self.assertEqual(releases, [Release(Version.parse("1.2.1"), "v1.2.1")])

    def test_creates_both_recipes_without_overwriting_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            ctrl = root / "meta-rugix-core/recipes-rugix/rugix-ctrl"
            bundler = root / "meta-rugix-core/recipes-rugix/rugix-bundler"
            ctrl.mkdir(parents=True)
            bundler.mkdir(parents=True)
            (ctrl / "rugix-ctrl.inc").write_text("")
            (bundler / "rugix-bundler-native.inc").write_text("")
            release = Release(Version.parse("1.2.1"), "v1.2.1")
            commit = "a" * 40

            created = create_recipes(root, [release], resolver=lambda _: commit)
            created_again = create_recipes(
                root, [release], resolver=lambda _: self.fail("tag resolved twice")
            )

            self.assertEqual(
                created,
                [
                    ctrl / "rugix-ctrl_1.2.1.bb",
                    bundler / "rugix-bundler-native_1.2.1.bb",
                ],
            )
            self.assertEqual(created_again, [])
            expected = f'SRCREV = "{commit}"\n\nrequire rugix-ctrl.inc\n'
            self.assertEqual((ctrl / "rugix-ctrl_1.2.1.bb").read_text(), expected)


if __name__ == "__main__":
    unittest.main()
