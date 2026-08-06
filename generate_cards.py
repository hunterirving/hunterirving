#!/usr/bin/env python3
"""
Generates GitHub-pin-lookalike cards for the repos listed in repos.json.
"""

import hashlib
import json
import os
import re
import urllib.request

USER = "hunterirving"
REPOS_FILE = "repos.json"
CARD_DIR = "cards"

CARD_W = 400
PAD = 16
TITLE_SIZE = 16
DESC_SIZE = 14
DESC_LH = 20
META_SIZE = 14
META_ICON = 16
DOT_R = 5.5
MARGIN = 10
WRAP_SLACK = 4
TEXT_W = CARD_W - 2 * PAD - WRAP_SLACK
CHAR_W = {
	' ': 0.2705, '!': 0.3003, '"': 0.4668, '#': 0.6191, '$': 0.6191, '%': 0.9146, '&': 0.7007,
	"'": 0.2861, '(': 0.3711, ')': 0.3711, '*': 0.4609, '+': 0.6191, ',': 0.2861, '-': 0.4609,
	'.': 0.2861, '/': 0.2939, '0': 0.6191, '1': 0.4531, '2': 0.5928, '3': 0.6162, '4': 0.6328,
	'5': 0.6074, '6': 0.626, '7': 0.5586, '8': 0.6279, '9': 0.626, ':': 0.2861, ';': 0.2861,
	'<': 0.6191, '=': 0.6191, '>': 0.6191, '?': 0.502, '@': 0.9072, 'A': 0.6631, 'B': 0.6465,
	'C': 0.7051, 'D': 0.7158, 'E': 0.585, 'F': 0.5615, 'G': 0.7358, 'H': 0.7314, 'I': 0.2568,
	'J': 0.5273, 'K': 0.6479, 'L': 0.5571, 'M': 0.8633, 'N': 0.7314, 'O': 0.7607, 'P': 0.6245,
	'Q': 0.7607, 'R': 0.6426, 'S': 0.6265, 'T': 0.623, 'U': 0.7266, 'V': 0.6631, 'W': 0.957,
	'X': 0.668, 'Y': 0.6445, 'Z': 0.6509, '[': 0.3711, '\\': 0.2939, ']': 0.3711, '^': 0.6191,
	'_': 0.5728, '`': 0.4893, 'a': 0.541, 'b': 0.6035, 'c': 0.5488, 'd': 0.6035, 'e': 0.5605,
	'f': 0.3511, 'g': 0.5986, 'h': 0.5776, 'i': 0.2363, 'j': 0.2358, 'k': 0.5322, 'l': 0.2422,
	'm': 0.8594, 'n': 0.5728, 'o': 0.5801, 'p': 0.5996, 'q': 0.5986, 'r': 0.3701, 's': 0.5127,
	't': 0.3525, 'u': 0.5728, 'v': 0.5312, 'w': 0.7637, 'x': 0.5137, 'y': 0.5322, 'z': 0.5283,
	'{': 0.3711, '|': 0.248, '}': 0.3711, '~': 0.6191, '✂': 0.9609, '️': 0.0,
}

FONT = (
	"-apple-system,BlinkMacSystemFont,&quot;Segoe UI&quot;,&quot;Noto Sans&quot;,"
	"Helvetica,Arial,sans-serif"
)

THEMES = {
	"light": {
		"canvas": "#ffffff",
		"border": "#d1d9e0",
		"muted": "#59636e",
		"link": "#0969da",
		"ring": "#1f2328",
		"ring_opacity": "0.15",
	},
	"dark": {
		"canvas": "#0d1117",
		"border": "#3d444d",
		"muted": "#9198a1",
		"link": "#4493f8",
		"ring": None,
	},
}

ICON_PATHS = {
	"repo": (
		"M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 "
		"0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 "
		"1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 "
		".25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z"
	),
	"star": (
		"M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 "
		"4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 "
		"6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Zm0 2.445L6.615 5.5a.75.75 "
		"0 0 1-.564.41l-3.097.45 2.24 2.184a.75.75 0 0 1 .216.664l-.528 3.084 2.769-1.456a.75.75 0 0 1 "
		".698 0l2.77 1.456-.53-3.084a.75.75 0 0 1 .216-.664l2.24-2.183-3.096-.45a.75.75 0 0 "
		"1-.564-.41L8 2.694Z"
	),
	"fork": (
		"M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 "
		"2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 "
		"6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 "
		"1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z"
	),
}

LANG_COLORS = {
	"Python": "#3572A5",
	"C": "#555555",
	"C++": "#f34b7d",
	"C#": "#178600",
	"HTML": "#e34c26",
	"CSS": "#663399",
	"JavaScript": "#f1e05a",
	"TypeScript": "#3178c6",
	"Shell": "#89e051",
	"Rust": "#dea584",
	"Go": "#00ADD8",
	"Java": "#b07219",
	"Ruby": "#701516",
	"Swift": "#F05138",
	"Lua": "#000080",
	"Assembly": "#6E4C13",
	"Makefile": "#427819",
	"Jupyter Notebook": "#DA5B0B",
	"OpenSCAD": "#e5cd45",
}


def esc(s):
	return (
		s.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
	)


def text_px(s, size):
	return sum(CHAR_W.get(c, 1.0) for c in s) * size


def wrap(s, limit, size):
	lines, cur = [], ""
	for word in s.split():
		trial = f"{cur} {word}".strip()
		if cur and text_px(trial, size) > limit:
			lines.append(cur)
			cur = word
		else:
			cur = trial
	if cur:
		lines.append(cur)
	return lines


def human(n):
	if n >= 1000:
		v = n / 1000
		return f"{v:.1f}".rstrip("0").rstrip(".") + "k"
	return str(n)


def octicon(name, x, y, size, fill):
	return (
		f'<path transform="translate({x} {y}) scale({size / 16:g})" '
		f'fill="{fill}" d="{ICON_PATHS[name]}"/>'
	)


def label(text, x, y, size, fill, weight=None):
	w = f' font-weight="{weight}"' if weight else ""
	return (
		f'<text x="{x:g}" y="{y:g}" font-family="{FONT}" font-size="{size}"{w} '
		f'fill="{fill}">{esc(text)}</text>'
	)


def card_svg(repo, theme, max_lines):
	c = THEMES[theme]
	name = repo["name"]
	lang = repo.get("language")
	stars = repo.get("stargazers_count", 0)
	forks = repo.get("forks_count", 0)
	lines = wrap(repo.get("description") or "", TEXT_W, DESC_SIZE)

	desc_top = PAD + 16 + 10
	meta_top = desc_top + max_lines * DESC_LH + 8
	card_h = meta_top + META_ICON + PAD

	body = [
		f'<rect x="0.5" y="0.5" width="{CARD_W - 1}" height="{card_h - 1}" rx="6" '
		f'fill="{c["canvas"]}" stroke="{c["border"]}"/>',
		octicon("repo", PAD, PAD + 1, 16, c["muted"]),
		label(name, PAD + 24, PAD + 13, TITLE_SIZE, c["link"], weight=600),
	]
	for i, line in enumerate(lines):
		body.append(label(line, PAD, desc_top + i * DESC_LH + 11, DESC_SIZE, c["muted"]))

	x, baseline = PAD, meta_top + 12.5
	if lang:
		cy = meta_top + 8
		body.append(
			f'<circle cx="{x + DOT_R:g}" cy="{cy}" r="{DOT_R:g}" '
			f'fill="{LANG_COLORS.get(lang, "#858585")}"/>'
		)
		if c["ring"]:
			body.append(
				f'<circle cx="{x + DOT_R:g}" cy="{cy}" r="{DOT_R - 0.5:g}" fill="none" '
				f'stroke="{c["ring"]}" stroke-opacity="{c["ring_opacity"]}"/>'
			)
		body.append(label(lang, x + 2 * DOT_R + 6, baseline, META_SIZE, c["muted"]))
		x += 2 * DOT_R + 6 + text_px(lang, META_SIZE) + 16
	for icon, count in (("star", stars), ("fork", forks)):
		if not count:
			continue
		body.append(octicon(icon, x, meta_top - 1, META_ICON, c["muted"]))
		body.append(label(human(count), x + META_ICON + 5, baseline, META_SIZE, c["muted"]))
		x += META_ICON + 5 + text_px(human(count), META_SIZE) + 16

	w, h = CARD_W + 2 * MARGIN, card_h + 2 * MARGIN
	return (
		f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
		f'viewBox="0 0 {w} {h}"><g transform="translate({MARGIN} {MARGIN})">'
		+ "".join(body)
		+ "</g></svg>"
	)


def load_repos():
	with open(REPOS_FILE) as f:
		names = json.load(f)
	if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
		raise SystemExit(f"{REPOS_FILE} must be a JSON array of repo names")
	return names


def fetch(user):
	token = os.environ.get("GITHUB_TOKEN")
	headers = {"Accept": "application/vnd.github+json", "User-Agent": "pin-cards"}
	if token:
		headers["Authorization"] = f"Bearer {token}"
	url = f"https://api.github.com/users/{user}/repos?per_page=100&type=owner"
	req = urllib.request.Request(url, headers=headers)
	with urllib.request.urlopen(req) as resp:
		return {r["name"]: r for r in json.load(resp)}


def main():
	repos = fetch(USER)
	branch = os.environ.get("GITHUB_REF_NAME", "main")
	entries = []
	for name in load_repos():
		repo = repos.get(name)
		if repo is None:
			print(f"  ! skipping {name} (not found)")
			continue
		entries.append(repo)
		print(f"  + {name}")

	os.makedirs(CARD_DIR, exist_ok=True)
	keep = set()

	def card_url(repo, theme, max_lines):
		svg = card_svg(repo, theme, max_lines)
		fname = f"{repo['name']}-{theme}.svg"
		keep.add(fname)
		path = os.path.join(CARD_DIR, fname)
		if not os.path.exists(path) or open(path).read() != svg:
			with open(path, "w") as f:
				f.write(svg)
		v = hashlib.sha256(svg.encode()).hexdigest()[:8]
		return f"https://raw.githubusercontent.com/{USER}/{USER}/{branch}/{CARD_DIR}/{fname}?v={v}"

	max_lines = max(len(wrap(r.get("description") or "", TEXT_W, DESC_SIZE)) for r in entries)
	cards = []
	for repo in entries:
		name = repo["name"]
		alt = esc(f"{name} — {repo.get('description') or ''}".strip().strip("—").strip())
		light = card_url(repo, "light", max_lines)
		dark = card_url(repo, "dark", max_lines)
		cards.append(
			f'<a href="https://github.com/{USER}/{name}">'
			f'<picture><source media="(prefers-color-scheme: dark)" srcset="{dark}">'
			f'<img src="{light}" width="{CARD_W + 2 * MARGIN}" align="top" alt="{alt}">'
			"</picture></a>"
		)

	for stale in sorted(set(os.listdir(CARD_DIR)) - keep):
		os.remove(os.path.join(CARD_DIR, stale))
		print(f"  - {CARD_DIR}/{stale}")

	with open("readme.md") as f:
		readme = f.read()
	body = '<div align="center">' + "".join(cards) + "</div>"
	new = re.sub(
		r"(<!-- PINS:START -->).*?(<!-- PINS:END -->)",
		lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}",
		readme,
		flags=re.S,
	)
	with open("readme.md", "w") as f:
		f.write(new)
	print("readme.md updated")


if __name__ == "__main__":
	main()
