import re
import requests
import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime, timezone
from git import Repo

# ================= CONFIG =================
# Always load .env from the same directory as this script
load_dotenv(override=True)

HR_SESSION = os.getenv("HR_SESSION")
HR_CSRF    = os.getenv("HR_CSRF")
USERNAME   = os.getenv("HR_USERNAME", "Helaluddin")

# Validated at runtime in run(), not at module level
def get_repo_path() -> str:
    path = os.getenv("HR_REPO_PATH")
    if not path:
        raise EnvironmentError("Set HR_REPO_PATH in your .env file.")
    tracker = os.path.join(path, ".sync_tracker.json")
    print(f"  📁 Repo path  : {path}")
    print(f"  📋 Tracker    : {tracker}")
    print(f"  📋 Exists     : {os.path.exists(tracker)}")
    return path

BASE_URL     = "https://www.hackerrank.com"
GRAPHQL_URL  = "https://www.hackerrank.com/graphql"

HEADERS = {
    "cookie":           f"_hrank_session={HR_SESSION}; _csrf_token={HR_CSRF}",
    "x-csrf-token":     HR_CSRF,
    "x-requested-with": "XMLHttpRequest",
    "content-type":     "application/json",
    "referer":          "https://www.hackerrank.com",
    "user-agent":       "Mozilla/5.0",
    "accept":           "application/json",
}

# ============== CATEGORY MAP ==============
CATEGORY_MAP = {
    "algorithms":                "Algorithms",
    "data-structures":           "DataStructures",
    "mathematics":               "Mathematics",
    "artificial-intelligence":   "AI",
    "databases":                 "Databases",
    "shell":                     "Shell",
    "regex":                     "Regex",
    "functional-programming":    "FunctionalProgramming",
    "interview-preparation-kit": "InterviewPrep",
    "problem-solving":           "Algorithms",
    "python":                    "Python",
    "java":                      "Java",
    "c":                         "CPP",
    "cpp":                       "CPP",
    "30-days-of-code":           "30DaysOfCode",
    "10-days-of-statistics":     "Statistics",
    "10-days-of-javascript":     "JavaScript",
    "sql":                       "SQL",
    "linux-shell":               "Shell",
}

LANG_FOLDER_MAP = {
    "python3": "Python",  "python":     "Python",
    "pypy3":   "Python",  "pypy2":      "Python",
    "php":     "PHP",     "javascript": "JavaScript",
    "typescript": "JavaScript",
    "cpp":     "CPP",     "cpp14":      "CPP",    "cpp17": "CPP",
    "c":       "CPP",
    "java":    "Java",    "java8":      "Java",   "java15": "Java",
    "csharp":  "CSharp",  "go":         "Go",
    "ruby":    "Ruby",    "swift":      "Swift",
    "kotlin":  "Kotlin",  "rust":       "Rust",
    "scala":   "Scala",   "bash":       "Shell",
    "mysql":   "SQL",     "oracle":     "SQL",    "mssql": "SQL",
    "haskell": "Haskell",
}

LANG_EXT = {
    "python3": "py",  "python":  "py",
    "pypy3":   "py",  "pypy2":   "py",
    "cpp":     "cpp", "cpp14":   "cpp",  "cpp17": "cpp",
    "c":       "c",
    "java":    "java","java8":   "java", "java15": "java",
    "javascript": "js","typescript": "ts",
    "php":     "php", "csharp":  "cs",
    "go":      "go",  "ruby":    "rb",
    "swift":   "swift","kotlin": "kt",
    "rust":    "rs",  "scala":   "scala",
    "bash":    "sh",  "mysql":   "sql",
    "oracle":  "sql", "mssql":   "sql",
    "haskell": "hs",
}

LANG_COMMENT = {
    "py": "#",   "js": "//",  "ts": "//",  "cpp": "//",
    "c":  "//",  "java":"//", "cs": "//",  "go":  "//",
    "rb": "#",   "swift":"//","kt": "//",  "rs":  "//",
    "php":"//",  "scala":"//","sh": "#",   "sql": "--",
    "hs": "--",
}

# ============== TRACKER ==============
def load_tracker(repo_path: str) -> dict:
    tracker_file = os.path.join(repo_path, ".sync_tracker.json")
    if os.path.exists(tracker_file):
        with open(tracker_file, "r") as f:
            return json.load(f)
    return {"synced_ids": [], "problems": {}, "counts": {}}

def save_tracker(tracker: dict, repo_path: str):
    tracker_file = os.path.join(repo_path, ".sync_tracker.json")
    with open(tracker_file, "w") as f:
        json.dump(tracker, f, indent=2)

# ============== FETCH ALL SUBMISSIONS ==============
def fetch_submissions() -> list:
    all_accepted = []
    offset    = 0
    limit     = 50
    page      = 1

    while True:
        print(f"  📄 Fetching page {page} (offset {offset})…")
        resp = requests.get(
            f"{BASE_URL}/rest/contests/master/submissions/",
            headers=HEADERS,
            params={"offset": offset, "limit": limit},
            timeout=15,
        )
        if resp.status_code == 401:
            print("  ⚠ Session expired — refresh HR_SESSION and HR_CSRF.")
            break
        resp.raise_for_status()
        data   = resp.json()
        models = data.get("models", [])
        if not models:
            break

        accepted = [s for s in models if s.get("status") == "Accepted"]
        all_accepted.extend(accepted)
        print(f"     → {len(models)} fetched, {len(accepted)} accepted")

        if not data.get("next"):
            break

        offset += limit
        page   += 1
        time.sleep(0.4)

    print(f"\n  Total accepted: {len(all_accepted)}")
    return all_accepted

# ============== FETCH PROBLEM DETAIL (safe) ==============
def fetch_problem_detail(challenge_slug: str) -> dict:
    """
    Returns track/difficulty/tags for a challenge.
    Handles cases where `track` is None or missing (interview kit, etc.)
    """
    try:
        resp = requests.get(
            f"{BASE_URL}/rest/contests/master/challenges/{challenge_slug}",
            headers=HEADERS,
            timeout=15,
        )
        if resp.status_code != 200:
            return _default_detail()

        data  = resp.json().get("model", {})
        track = data.get("track")           # ← may be None for some problems

        # ── safe guard: track can be None or not a dict ──
        if not isinstance(track, dict):
            track = {}

        return {
            "track":      track.get("slug", "algorithms"),
            "track_name": track.get("name", "Algorithms"),
            "difficulty": data.get("difficulty_name", "Unknown"),
            "tags":       [t.get("name", "") for t in (data.get("tags") or [])],
            "score":      data.get("max_score", 0),
        }
    except Exception as e:
        print(f"    ⚠ Could not fetch detail for {challenge_slug}: {e}")
        return _default_detail()

def _default_detail() -> dict:
    return {
        "track":      "algorithms",
        "track_name": "Algorithms",
        "difficulty": "Unknown",
        "tags":       [],
        "score":      0,
    }

# ============== BUILD FILE CONTENT ==============
def build_file(sub: dict, detail: dict, attempt_num: int, ext: str) -> str:
    comment = LANG_COMMENT.get(ext, "#")
    name    = sub.get("challenge", {}).get("name", sub.get("challenge_id", "Unknown"))
    slug    = sub.get("challenge_id", "")
    date    = datetime.fromtimestamp(
        int(sub.get("created_at_epoch", time.time())), tz=timezone.utc
    ).strftime("%Y-%m-%d")

    header = (
        f"{comment} {name}\n"
        f"{comment} Difficulty : {detail['difficulty']}\n"
        f"{comment} Track      : {detail.get('track_name', '')}\n"
        f"{comment} Tags       : {', '.join(detail['tags'])}\n"
        f"{comment} Solved on  : {date}\n"
        f"{comment} Attempt    : #{attempt_num}\n"
        f"{comment} HackerRank : {BASE_URL}/challenges/{slug}/problem\n\n"
    )
    return header + (sub.get("code") or "")

# ============== SAVE SOLUTION ==============
def save_solution(sub: dict, detail: dict, attempt_num: int, repo_path: str):
    track    = detail.get("track", "algorithms")
    category = CATEGORY_MAP.get(track, track.replace("-", " ").title())
    slug     = sub.get("challenge_id", "unknown")
    name     = sub.get("challenge", {}).get("name", slug)

    # Sanitize title for filesystem (remove colons, quotes, etc.)
    title    = (name.replace(" ", "_").replace(":", "")
                    .replace("'", "").replace('"', "")
                    .replace("/", "_").replace("\\", "_"))

    lang     = sub.get("language", "python3").lower()
    ext      = LANG_EXT.get(lang, "txt")
    filename = "solution" if attempt_num == 1 else f"solution_{attempt_num}"
    content  = build_file(sub, detail, attempt_num, ext)
    date_str = datetime.fromtimestamp(
        int(sub.get("created_at_epoch", time.time())), tz=timezone.utc
    ).strftime("%Y-%m-%d")

    # 1. DSA/<Category>/<Title>/<lang>/
    dsa_folder = os.path.join(repo_path, "DSA", category, title, lang)
    os.makedirs(dsa_folder, exist_ok=True)
    with open(os.path.join(dsa_folder, f"{filename}.{ext}"), "w", encoding="utf-8") as f:
        f.write(content)
    write_problem_readme(os.path.dirname(dsa_folder), sub, detail, date_str, name)
    print(f"    ✅ DSA  → DSA/{category}/{title}/{lang}/{filename}.{ext}")

    # 2. Programming Languages/<Lang>/<Title>/
    lang_folder_name = LANG_FOLDER_MAP.get(lang, lang.capitalize())
    pl_folder = os.path.join(repo_path, "Programming Languages", lang_folder_name, title)
    os.makedirs(pl_folder, exist_ok=True)
    with open(os.path.join(pl_folder, f"{filename}.{ext}"), "w", encoding="utf-8") as f:
        f.write(content)
    write_pl_readme(pl_folder, sub, detail, date_str, lang_folder_name, name)
    print(f"    ✅ Lang → Programming Languages/{lang_folder_name}/{title}/{filename}.{ext}")

    return category

# ============== READMEs ==============
def write_problem_readme(folder: str, sub: dict, detail: dict, date: str, name: str):
    lang_rows = ""
    if os.path.isdir(folder):
        for lang_dir in sorted(os.listdir(folder)):
            lp = os.path.join(folder, lang_dir)
            if not os.path.isdir(lp):
                continue
            for sol in sorted(f for f in os.listdir(lp) if f.startswith("solution")):
                lang_rows += f"| `{lang_dir}` | [{sol}](./{lang_dir}/{sol}) |\n"

    slug = sub.get("challenge_id", "")
    with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# {name}

| Field       | Value |
|-------------|-------|
| Difficulty  | {detail['difficulty']} |
| Track       | {detail.get('track_name', '')} |
| Tags        | {', '.join(f'`{t}`' for t in detail['tags'])} |
| Last solved | {date} |
| Link        | [HackerRank]({BASE_URL}/challenges/{slug}/problem) |

## Solutions

| Language | File |
|----------|------|
{lang_rows}""")

def write_pl_readme(folder: str, sub: dict, detail: dict, date: str, lang_name: str, name: str):
    sol_rows = "".join(
        f"| [{s}](./{s}) |\n"
        for s in sorted(f for f in os.listdir(folder) if f.startswith("solution"))
    )
    slug = sub.get("challenge_id", "")
    with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# {name}

| Field       | Value |
|-------------|-------|
| Difficulty  | {detail['difficulty']} |
| Language    | {lang_name} |
| Tags        | {', '.join(f'`{t}`' for t in detail['tags'])} |
| Last solved | {date} |
| Link        | [HackerRank]({BASE_URL}/challenges/{slug}/problem) |

## Attempts

| File |
|------|
{sol_rows}""")

def generate_language_index_readmes(repo_path: str):
    pl_root = os.path.join(repo_path, "Programming Languages")
    if not os.path.isdir(pl_root):
        return
    for lang_name in sorted(os.listdir(pl_root)):
        lang_path = os.path.join(pl_root, lang_name)
        if not os.path.isdir(lang_path):
            continue
        problems = sorted(d for d in os.listdir(lang_path) if os.path.isdir(os.path.join(lang_path, d)))
        rows     = "\n".join(f"| [{p}](./{p}/) |" for p in problems)
        with open(os.path.join(lang_path, "README.md"), "w") as f:
            f.write(f"# {lang_name} Solutions\n\n{len(problems)} problem(s) solved.\n\n| Problem |\n|---------|\n{rows}\n")

# ============== MAIN README ==============
def generate_main_readme(tracker: dict, repo_path: str):
    problems         = tracker.get("problems", {})
    total            = len(problems)
    difficulty_count = {}
    category_count   = {}
    lang_count       = {}
    rows             = []

    for slug, p in sorted(problems.items(), key=lambda x: x[1].get("title", "")):
        diff = p.get("difficulty", "Unknown")
        difficulty_count[diff] = difficulty_count.get(diff, 0) + 1
        cat  = p.get("category", "Misc")
        category_count[cat]    = category_count.get(cat, 0) + 1
        langs = p.get("langs", [p.get("lang", "")])
        for l in langs:
            fn = LANG_FOLDER_MAP.get(l.lower(), l)
            lang_count[fn] = lang_count.get(fn, 0) + 1
        rows.append(
            f"| [{p.get('title', slug)}]({BASE_URL}/challenges/{slug}/problem) "
            f"| {diff} | {cat} "
            f"| {', '.join(f'`{l}`' for l in langs)} "
            f"| {p.get('date', '')} |"
        )

    diff_header = " | ".join(difficulty_count.keys())
    diff_sep    = "---|" * len(difficulty_count)
    diff_vals   = " | ".join(str(difficulty_count[d]) for d in difficulty_count)
    cat_rows    = "\n".join(f"| {c} | {n} |" for c, n in sorted(category_count.items(), key=lambda x: -x[1]))
    lang_rows   = "\n".join(f"| [{l}](./Programming%20Languages/{l}/) | {n} |" for l, n in sorted(lang_count.items(), key=lambda x: -x[1]))

    with open(os.path.join(repo_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🎯 HackerRank Solutions — @{USERNAME}

Auto-synced with Python · Last updated: {datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

## 📊 Stats

| Total | {diff_header} |
|-------|{diff_sep}
| {total} | {diff_vals} |

## 🗂️ Browse by Topic

| Category | Problems |
|----------|----------|
{cat_rows}

## 💻 Browse by Language

| Language | Solutions |
|----------|-----------|
{lang_rows}

## 📋 All Solutions

| Title | Difficulty | Category | Languages | Last Solved |
|-------|------------|----------|-----------|-------------|
{chr(10).join(rows)}
""")
    print("  📄 README.md updated")

# ============== GIT PUSH ==============
def push_to_github(repo_path: str):
    # Auto-initialise if the folder has no .git yet
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.isdir(git_dir):
        print(f"  ⚠ No git repo found at {repo_path}")
        print("  Run these commands first:")
        print(f"    cd {repo_path}")
        print("    git init")
        print("    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git")
        print("    git branch -M main")
        return
    repo = Repo(repo_path)
    repo.git.add(A=True)
    if not repo.is_dirty(index=True, working_tree=True, untracked_files=True):
        print("Nothing new to commit.")
        return
    repo.index.commit(
        f"🤖 Auto-sync HackerRank solutions [{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC]"
    )
    repo.remote(name="origin").push()
    print("🚀 Pushed to GitHub!")

# ============== MAIN ==============
def run():
    if not HR_SESSION or not HR_CSRF:
        raise EnvironmentError("Set HR_SESSION and HR_CSRF in your .env file.")

    repo_path  = get_repo_path()    # raises clearly if missing
    tracker    = load_tracker(repo_path)
    synced_ids = set(tracker["synced_ids"])
    counts     = tracker.setdefault("counts", {})
    new_count  = 0

    print(f"🔍 Fetching ALL HackerRank submissions for @{USERNAME}…\n")
    submissions = fetch_submissions()
    print()

    for sub in reversed(submissions):       # oldest-first → chronological attempt#
        sub_id = str(sub.get("id"))
        if sub_id in synced_ids:
            continue

        slug = sub.get("challenge_id", "")
        lang = sub.get("language", "python3").lower()
        name = sub.get("challenge", {}).get("name", slug)
        print(f"  ⬇ {name} ({lang})  [id={sub_id}]")

        detail = fetch_problem_detail(slug)

        count_key         = f"{slug}::{lang}"
        attempt_num       = counts.get(count_key, 0) + 1
        counts[count_key] = attempt_num

        category = save_solution(sub, detail, attempt_num, repo_path)

        date_str = datetime.fromtimestamp(
            int(sub.get("created_at_epoch", time.time())), tz=timezone.utc
        ).strftime("%Y-%m-%d")

        existing = tracker["problems"].get(slug, {})
        langs    = existing.get("langs", [])
        if lang not in langs:
            langs.append(lang)

        tracker["problems"][slug] = {
            "title":      name,
            "difficulty": detail["difficulty"],
            "category":   category,
            "langs":      langs,
            "lang":       lang,
            "date":       date_str,
        }
        synced_ids.add(sub_id)
        tracker["synced_ids"].append(sub_id)
        new_count += 1
        time.sleep(0.5)

    if new_count:
        generate_language_index_readmes(repo_path)
        generate_main_readme(tracker, repo_path)
        save_tracker(tracker, repo_path)
        push_to_github(repo_path)
        print(f"\n✅ Done! {new_count} new submission(s) synced.")
    else:
        print("\n✅ Everything already up to date.")

if __name__ == "__main__":
    run()
