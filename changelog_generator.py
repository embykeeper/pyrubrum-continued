#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pyrubrum - An intuitive framework for creating Telegram bots
# Copyright (C) 2020 Hearot <https://github.com/hearot>
#
# This file is part of Pyrubrum.
#
# Pyrubrum is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrubrum is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrubrum. If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import time
from collections import defaultdict

from git import Repo
from pathlib import Path

CHANGELOG_FILE = "CHANGELOG.md"
COMMIT_URL_FORMAT = "https://github.com/%s/%s/commit/%%s"
COMMIT_URL = ""
COMMIT_URL_REGEX = r"git@github.com:(.+)\/(.+).git"
CONVENTIONAL_COMMITS_REGEX = r"^([a-z]+)(!)?(?:\([a-z]+\)+)?: ([^\n]+)+$"
TEMP_FILE = ".temp_post_commit"
TITLES = {
    "!": "‼️ Breaking changes",
    "build": "Build changes",
    "chore": "Other changes",
    "docs": "Documentation",
    "feat": "New features",
    "fix": "Fixes",
    "refactor": "Refactoring",
    "style": "Style changes",
    "test": "Testing changes",
}

commit_url_format = re.compile(COMMIT_URL_REGEX)
match_commit = re.compile(CONVENTIONAL_COMMITS_REGEX)

titles = defaultdict(lambda: "New features")
titles.update(TITLES)

version_tree = defaultdict(lambda: defaultdict(list))


def add_date(repo: Repo, version: str) -> str:
    if version == "Current version":
        return version

    commit = repo.commit(version)

    return "%s - %s" % (
        version,
        time.strftime("%Y-%m-%d", time.gmtime(commit.committed_date)),
    )


def commit_amend(repo: Repo):
    try:
        repo.git.add(CHANGELOG_FILE)
        repo.git.commit("--amend", "--no-edit", "--no-verify", "-S")
    finally:
        os.remove(TEMP_FILE)


def upper_first_letter(text: str) -> str:
    return text[0].upper() + text[1:]


def generate_changelog(repo: Repo):
    tags_list = sorted(repo.tags, key=lambda t: t.commit.committed_date) + [""]
    tags = iter(tags_list)
    tag = ""
    next_tag = str(next(repo.iter_commits(max_count=1, max_parents=0)))

    try:
        while True:
            tag = next_tag
            next_tag = str(next(tags))

            print(">>> FROM %s TO %s <<<" % (tag, next_tag))

            commits = repo.iter_commits(
                str(tag) + "..." + str(next_tag), reverse=True
            )

            for commit in commits:
                match = match_commit.search(commit.message.split("\n")[0])

                if match:
                    type_commit = match.group(1)
                    breaking_change = match.group(2)
                    breaking_change = (
                        breaking_change if breaking_change else ""
                    )
                    brief_message = match.group(3)
                    suffix = " "

                    if (
                        isinstance(breaking_change, str)
                        and breaking_change == "!"
                    ):
                        type_commit = "!"

                    if commit != repo.head.commit:
                        suffix += "([%s](%s))" % (
                            str(commit),
                            COMMIT_URL % str(commit),
                        )

                    version_tree[next_tag][titles[type_commit]].append(
                        (
                            ("%s" + suffix) % upper_first_letter(brief_message)
                        ).rstrip()
                    )

                    print(
                        "    " + type_commit + breaking_change + ":",
                        brief_message,
                    )
    except StopIteration:
        pass

    if "" in version_tree:
        version_tree["Current version"] = version_tree.pop("")

    changelog_file = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), CHANGELOG_FILE
    )

    with open(changelog_file, "w", encoding="utf-8") as f:
        f.write("# Changelog\n\n## Table of contents\n\n")

        for version in map(str, reversed(tags_list)):
            version = version if version else "Current version"
            version = add_date(repo, version)
            f.write(
                "   * [%s](#%s)\n"
                % (version, version.replace(".", "").replace(" ", "-"))
            )

        for version in map(str, reversed(tags_list)):
            version = version if version else "Current version"
            types = version_tree[version]

            f.write("\n## %s\n" % add_date(repo, version))

            for type_commit in sorted(types.keys()):
                commits = types[type_commit]

                f.write("\n### %s\n\n" % type_commit)

                for commit in sorted(commits):
                    f.write("   - %s\n" % commit)


if __name__ == "__main__":
    repo = Repo(os.path.dirname(os.path.realpath(__file__)))
    first_post_commit = not os.path.isfile(TEMP_FILE)
    origin_url = next(repo.remotes.origin.urls)

    if origin_url.startswith("https://"):
        COMMIT_URL = (
            origin_url.replace(".git/", "").replace(".git", "") + "/commit/%s"
        )
    else:
        match_url = commit_url_format.search(origin_url)

        if not match_url:
            raise ValueError("origin must be a valid reference")

        author, repository_name = match_url.group(1), match_url.group(2)
        COMMIT_URL = COMMIT_URL_FORMAT % (author, repository_name)

    print("COMMIT PREFIX URL: %s" % COMMIT_URL)
    if sys.argv[-1] == "generate":
        generate_changelog(repo)
    elif first_post_commit:
        Path(TEMP_FILE).touch()
        generate_changelog(repo)
        commit_amend(repo)
