#!/usr/bin/env python3
"""Create Yocto recipes for new stable Rugix releases."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_BASELINE = "1.2.0"
DEFAULT_RELEASES_API = "https://api.github.com/repos/rugix/rugix/releases"
DEFAULT_REPOSITORY = "https://github.com/rugix/rugix.git"

_VERSION_RE = re.compile(
    r"^(?:v)?(?P<major>0|[1-9][0-9]*)\."
    r"(?P<minor>0|[1-9][0-9]*)\."
    r"(?P<patch>0|[1-9][0-9]*)$"
)
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> Version:
        match = _VERSION_RE.fullmatch(value)
        if match is None:
            raise ValueError(f"invalid stable Rugix version: {value!r}")
        return cls(*(int(match.group(name)) for name in ("major", "minor", "patch")))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class Release:
    version: Version
    tag: str


def fetch_releases(api_url: str = DEFAULT_RELEASES_API) -> list[dict[str, Any]]:
    """Fetch all GitHub releases, following the REST API's pagination."""
    releases: list[dict[str, Any]] = []
    page = 1

    while True:
        separator = "&" if "?" in api_url else "?"
        url = f"{api_url}{separator}per_page=100&page={page}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "meta-rugix-recipe-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token := os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.load(response)
        except (urllib.error.URLError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"unable to fetch Rugix releases from {url}: {error}"
            ) from error

        if not isinstance(payload, list):
            raise RuntimeError(
                f"unexpected response from Rugix releases API: {payload!r}"
            )

        page_releases = [item for item in payload if isinstance(item, dict)]
        releases.extend(page_releases)
        if len(payload) < 100:
            return releases
        page += 1


def eligible_releases(
    payloads: Iterable[dict[str, Any]], baseline: Version
) -> list[Release]:
    """Return stable, published releases newer than the configured baseline."""
    releases: dict[Version, Release] = {}

    for payload in payloads:
        if payload.get("draft") or payload.get("prerelease"):
            continue

        tag = payload.get("tag_name")
        if not isinstance(tag, str) or not tag.startswith("v"):
            continue

        try:
            version = Version.parse(tag)
        except ValueError:
            continue

        if version > baseline:
            releases[version] = Release(version=version, tag=tag)

    return [releases[version] for version in sorted(releases)]


def resolve_tag(tag: str, repository: str = DEFAULT_REPOSITORY) -> str:
    """Resolve a lightweight or annotated Git tag to its commit."""
    ref = f"refs/tags/{tag}"
    result = subprocess.run(
        ["git", "ls-remote", repository, ref, f"{ref}^{{}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"git exited with status {result.returncode}"
        raise RuntimeError(f"unable to resolve Rugix tag {tag}: {detail}")

    refs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        try:
            commit, name = line.split("\t", 1)
        except ValueError:
            continue
        refs[name] = commit

    commit = refs.get(f"{ref}^{{}}") or refs.get(ref)
    if commit is None or _COMMIT_RE.fullmatch(commit) is None:
        raise RuntimeError(f"Rugix tag {tag} did not resolve to a commit")
    return commit


def create_recipes(
    root: Path,
    releases: Iterable[Release],
    resolver: Callable[[str], str] = resolve_tag,
) -> list[Path]:
    """Create any missing ctrl and bundler recipes for the given releases."""
    recipe_specs = (
        (
            root / "meta-rugix-core/recipes-rugix/rugix-ctrl",
            "rugix-ctrl",
            "rugix-ctrl.inc",
        ),
        (
            root / "meta-rugix-core/recipes-rugix/rugix-bundler",
            "rugix-bundler-native",
            "rugix-bundler-native.inc",
        ),
    )

    for directory, _, include in recipe_specs:
        if not (directory / include).is_file():
            raise RuntimeError(f"missing recipe include: {directory / include}")

    created: list[Path] = []
    for release in releases:
        targets = [
            (directory / f"{name}_{release.version}.bb", include)
            for directory, name, include in recipe_specs
        ]
        missing = [(path, include) for path, include in targets if not path.exists()]
        if not missing:
            continue

        commit = resolver(release.tag)
        if _COMMIT_RE.fullmatch(commit) is None:
            raise RuntimeError(
                f"Rugix tag {release.tag} resolved to invalid commit {commit!r}"
            )

        for path, include in missing:
            path.write_text(f'SRCREV = "{commit}"\n\nrequire {include}\n')
            created.append(path)

    return created


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="meta-rugix checkout to update (default: current directory)",
    )
    parser.add_argument(
        "--baseline",
        default=DEFAULT_BASELINE,
        help=f"oldest supported Rugix version (default: {DEFAULT_BASELINE})",
    )
    parser.add_argument(
        "--releases-api", default=DEFAULT_RELEASES_API, help=argparse.SUPPRESS
    )
    parser.add_argument(
        "--repository", default=DEFAULT_REPOSITORY, help=argparse.SUPPRESS
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        baseline = Version.parse(args.baseline)
        payloads = fetch_releases(args.releases_api)
        releases = eligible_releases(payloads, baseline)
        created = create_recipes(
            args.root.resolve(),
            releases,
            resolver=lambda tag: resolve_tag(tag, args.repository),
        )
    except (RuntimeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if created:
        for path in created:
            print(f"Created {path.relative_to(args.root.resolve())}")
    else:
        print(f"No new stable Rugix recipes after {baseline}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
