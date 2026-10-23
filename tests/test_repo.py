"""Tests for the package itself: plugin manifests, install commands, names. Standard library only.

    python3 -m unittest discover -s tests -v
"""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
URL = "https://github.com/aldushmedia/arena"


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as fh:
        return fh.read()


class Package(unittest.TestCase):
    def test_plugin_and_marketplace_are_called_arena(self):
        plugin = json.loads(read(".claude-plugin", "plugin.json"))
        self.assertEqual(plugin["name"], "arena")
        self.assertEqual(plugin["homepage"], URL)
        self.assertEqual(plugin["repository"], URL)
        market = json.loads(read(".claude-plugin", "marketplace.json"))
        self.assertEqual(market["name"], "arena")
        self.assertEqual(market["plugins"][0]["name"], "arena")
        self.assertEqual(market["plugins"][0]["homepage"], URL)

    def test_readme_installs_from_aldushmedia_arena(self):
        readme = read("README.md")
        for line in ("git clone %s.git" % URL,
                     "cp -r arena/skills/arena ~/.claude/skills/",
                     "/plugin marketplace add aldushmedia/arena",
                     "/plugin install arena@arena",
                     "`/arena:arena`"):
            self.assertIn(line, readme)

    def test_the_skill_and_its_command_are_still_arena(self):
        text = read("skills", "arena", "SKILL.md")
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1)
        self.assertIn("name: arena\n", fm + "\n")
        self.assertIn("Lo que el usuario escribió después de `/arena`", text)

    def test_no_old_package_name_left(self):
        old = "arena-" + "skill"  # split so this file does not match itself
        bad = []
        for root, dirs, files in os.walk(REPO):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for name in files:
                path = os.path.join(root, name)
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    if old in fh.read():
                        bad.append(os.path.relpath(path, REPO))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
