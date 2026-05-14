import re
import requests
import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime, timezone
from git import Repo

# ================= CONFIG =================
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))

HR_SESSION = os.getenv("HR_SESSION")
HR_CSRF    = os.getenv("HR_CSRF")
USERNAME   = os.getenv("HR_USERNAME", "Helaluddin")
BASE_URL   = "https://www.hackerrank.com"

def get_repo_path() -> str:
    path = os.getenv("HR_REPO_PATH")
    if not path:
        raise EnvironmentError("Set HR_REPO_PATH in your .env file.")
    return path

HEADERS = {
    "cookie":           f"_hrank_session={HR_SESSION}; _csrf_token={HR_CSRF}",
    "x-csrf-token":     HR_CSRF,
    "x-requested-with": "XMLHttpRequest",
    "content-type":     "application/json",
    "referer":          BASE_URL,
    "user-agent":       "Mozilla/5.0",
    "accept":           "application/json",
}

# ============== MAPS ==============
CATEGORY_MAP = {
    "algorithms": "Algorithms", "data-structures": "DataStructures",
    "mathematics": "Mathematics", "artificial-intelligence": "AI",
    "databases": "Databases", "shell": "Shell", "regex": "Regex",
    "functional-programming": "FunctionalProgramming",
    "interview-preparation-kit": "InterviewPrep",
    "problem-solving": "Algorithms", "python": "Python", "java": "Java",
    "c": "CPP", "cpp": "CPP", "30-days-of-code": "30DaysOfCode",
    "10-days-of-statistics": "Statistics",
    "10-days-of-javascript": "JavaScript", "sql": "SQL", "linux-shell": "Shell",
}

LANG_FOLDER_MAP = {
    "python3": "Python", "python": "Python", "pypy3": "Python", "pypy2": "Python",
    "php": "PHP", "javascript": "JavaScript", "typescript": "JavaScript",
    "cpp": "CPP", "cpp14": "CPP", "cpp17": "CPP", "c": "CPP",
    "java": "Java", "java8": "Java", "java15": "Java",
    "csharp": "CSharp", "go": "Go", "ruby": "Ruby", "swift": "Swift",
    "kotlin": "Kotlin", "rust": "Rust", "scala": "Scala", "bash": "Shell",
    "mysql": "SQL", "oracle": "SQL", "mssql": "SQL", "haskell": "Haskell",
}

LANG_EXT = {
    "python3": "py", "python": "py", "pypy3": "py", "pypy2": "py",
    "cpp": "cpp", "cpp14": "cpp", "cpp17": "cpp", "c": "c",
    "java": "java", "java8": "java", "java15": "java",
    "javascript": "js", "typescript": "ts", "php": "php", "csharp": "cs",
    "go": "go", "ruby": "rb", "swift": "swift", "kotlin": "kt",
    "rust": "rs", "scala": "scala", "bash": "sh",
    "mysql": "sql", "oracle": "sql", "mssql": "sql", "haskell": "hs",
}

LANG_COMMENT = {
    "py": "#", "js": "//", "ts": "//", "cpp": "//", "c": "//",
    "java": "//", "cs": "//", "go": "//", "rb": "#", "swift": "//",
    "kt": "//", "rs": "//", "php": "//", "scala": "//", "sh": "#",
    "sql": "--", "hs": "--",
}

# ============== TRACKER ==============
def load_tracker(repo_path: str) -> dict:
    f_path = os.path.join(repo_path, ".sync_tracker.json")
    if os.path.exists(f_path):
        with open(f_path) as f:
            return json.load(f)
    return {"synced_ids": [], "problems": {}, "counts": {}}

def save_tracker(tracker: dict, repo_path: str):
    with open(os.path.join(repo_path, ".sync_tracker.json"), "w") as f:
        json.dump(tracker, f, indent=2)

# ============== FETCH SUBMISSIONS ==============
def fetch_submissions() -> list:
    all_accepted, offset, limit, page = [], 0, 50, 1
    while True:
        print(f"  📄 Fetching page {page} (offset {offset})…")
        resp = requests.get(
            f"{BASE_URL}/rest/contests/master/submissions/",
            headers=HEADERS, params={"offset": offset, "limit": limit}, timeout=15,
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

def fetch_submission_code(sub_id: str, retries: int = 3) -> str:
    """Fetch actual code for a submission by its ID, with retry on rate-limit."""
    for attempt in range(retries):
        try:
            time.sleep(1.2)  # Respect rate limit between every call
            resp = requests.get(
                f"{BASE_URL}/rest/contests/master/submissions/{sub_id}",
                headers=HEADERS, timeout=15,
            )
            if resp.status_code == 200:
                code = resp.json().get("model", {}).get("code", "")
                if code:
                    return code
                # Empty code — log raw response for debugging
                print(f"    ⚠ Empty code in response for id={sub_id}. Keys: {list(resp.json().get('model', {}).keys())}")
                return ""
            elif resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"    ⏳ Rate limited (429). Waiting {wait}s before retry {attempt+1}/{retries}…")
                time.sleep(wait)
            elif resp.status_code == 404:
                print(f"    ⚠ Submission id={sub_id} not found (404).")
                return ""
            else:
                print(f"    ⚠ HTTP {resp.status_code} for id={sub_id}")
                time.sleep(2)
        except Exception as e:
            print(f"    ⚠ Code fetch failed for id={sub_id}: {e}")
            time.sleep(2)
    return ""

# ============== FETCH CERTIFICATES & BADGES ==============
def fetch_certificates() -> dict:
    """Returns {'certificates': [...], 'badges': [...]}"""
    result = {"certificates": [], "badges": []}

    # Skill verification certificates
    try:
        resp = requests.get(
            f"{BASE_URL}/rest/hackers/{USERNAME}/skill_verification_tests/certifications",
            headers=HEADERS, timeout=15,
        )
        if resp.status_code == 200:
            for c in resp.json().get("models", []) or []:
                cert_id = c.get("certificate_id") or c.get("unique_id") or c.get("id", "")
                result["certificates"].append({
                    "name":       c.get("label", c.get("name", "Unknown")),
                    "slug":       c.get("slug", ""),
                    "level":      c.get("level", ""),
                    "score":      c.get("score", ""),
                    "percentile": c.get("percentile", ""),
                    "cert_id":    cert_id,
                    "issued":     (c.get("created_at") or "")[:10],
                    "url":        f"{BASE_URL}/certificates/{cert_id}",
                })
    except Exception as e:
        print(f"    ⚠ Certificates fetch failed: {e}")

    # Badges
    try:
        resp = requests.get(
            f"{BASE_URL}/rest/hackers/{USERNAME}/badges",
            headers=HEADERS, timeout=15,
        )
        if resp.status_code == 200:
            for b in resp.json().get("models", []) or []:
                result["badges"].append({
                    "name":   b.get("name", "Unknown"),
                    "stars":  b.get("star_count", 0),
                    "solved": b.get("solved", 0),
                    "slug":   b.get("slug", ""),
                })
    except Exception as e:
        print(f"    ⚠ Badges fetch failed: {e}")

    print(f"  🏆 {len(result['certificates'])} certificate(s), "
          f"{len(result['badges'])} badge(s) found")
    return result

def save_certificates(data: dict, repo_path: str):
    certs  = data["certificates"]
    badges = data["badges"]
    if not certs and not badges:
        print("  ℹ No certificates or badges to save.")
        return

    folder = os.path.join(repo_path, "Certificates")
    os.makedirs(folder, exist_ok=True)

    # Individual .md file per certificate
    cert_rows = ""
    for c in certs:
        level = c["level"].replace("_", " ").title() if c["level"] else "—"
        score = c["score"] or "—"
        pct   = f"{c['percentile']}%" if c["percentile"] else "—"
        cert_rows += (
            f"| [{c['name']}]({c['url']}) | {level} | {score} | {pct} | {c['issued']} |\n"
        )
        safe  = c["name"].replace(" ", "_").replace("/", "_")
        with open(os.path.join(folder, f"{safe}.md"), "w", encoding="utf-8") as f:
            f.write(f"""# 🏆 {c['name']}

| Field       | Value |
|-------------|-------|
| Issued to   | [@{USERNAME}]({BASE_URL}/profile/{USERNAME}) |
| Level       | {level} |
| Score       | {score} |
| Percentile  | {pct} |
| Issued on   | {c['issued']} |
| Certificate | [View / Download]({c['url']}) |

## Verify

[{c['url']}]({c['url']})

> Issued by [HackerRank]({BASE_URL})
""")
        print(f"    🏆 {c['name']} ({level})")

    # Badge rows
    badge_rows = ""
    for b in badges:
        stars      = "⭐" * int(b["stars"]) if b["stars"] else "—"
        badge_rows += f"| {b['name']} | {stars} | {b['solved']} |\n"

    # Certificates/README.md
    with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🏆 Certificates & Badges — @{USERNAME}

🔗 Profile: [{BASE_URL}/profile/{USERNAME}]({BASE_URL}/profile/{USERNAME})

---

## 📜 Skill Certificates

| Certificate | Level | Score | Percentile | Issued |
|-------------|-------|-------|------------|--------|
{cert_rows}
---

## 🥇 Badges

| Badge | Stars | Problems Solved |
|-------|-------|-----------------|
{badge_rows}
""")
    print(f"  📄 Certificates/README.md saved")

# ============== FETCH PROBLEM DETAIL ==============
def fetch_problem_detail(slug: str) -> dict:
    try:
        resp = requests.get(
            f"{BASE_URL}/rest/contests/master/challenges/{slug}",
            headers=HEADERS, timeout=15,
        )
        if resp.status_code != 200:
            return _default_detail()
        data  = resp.json().get("model", {})
        track = data.get("track")
        if not isinstance(track, dict):
            track = {}
        return {
            "track":      track.get("slug", "algorithms"),
            "track_name": track.get("name", "Algorithms"),
            "difficulty": data.get("difficulty_name", "Unknown"),
            "tags":       [t.get("name", "") for t in (data.get("tags") or [])],
        }
    except Exception as e:
        print(f"    ⚠ Detail fetch failed for {slug}: {e}")
        return _default_detail()

def _default_detail() -> dict:
    return {"track": "algorithms", "track_name": "Algorithms",
            "difficulty": "Unknown", "tags": []}

# ============== BUILD & SAVE SOLUTION ==============
def build_file(sub: dict, detail: dict, attempt_num: int, ext: str) -> str:
    comment = LANG_COMMENT.get(ext, "#")
    name    = sub.get("challenge", {}).get("name", sub.get("challenge_id", "Unknown"))
    slug    = sub.get("challenge_id", "")
    date    = datetime.fromtimestamp(int(sub.get("created_at_epoch", time.time())),
                                     tz=timezone.utc).strftime("%Y-%m-%d")
    return (
        f"{comment} {name}\n"
        f"{comment} Difficulty : {detail['difficulty']}\n"
        f"{comment} Track      : {detail.get('track_name', '')}\n"
        f"{comment} Tags       : {', '.join(detail['tags'])}\n"
        f"{comment} Solved on  : {date}\n"
        f"{comment} Attempt    : #{attempt_num}\n"
        f"{comment} HackerRank : {BASE_URL}/challenges/{slug}/problem\n\n"
    ) + (sub.get("code") or "")

def save_solution(sub: dict, detail: dict, attempt_num: int, repo_path: str) -> str:
    track    = detail.get("track", "algorithms")
    category = CATEGORY_MAP.get(track, track.replace("-", " ").title())
    slug     = sub.get("challenge_id", "unknown")
    name     = sub.get("challenge", {}).get("name", slug)
    title    = (name.replace(" ", "_").replace(":", "").replace("'", "")
                    .replace('"', "").replace("/", "_").replace("\\", "_"))
    lang     = sub.get("language", "python3").lower()
    ext      = LANG_EXT.get(lang, "txt")
    filename = "solution" if attempt_num == 1 else f"solution_{attempt_num}"
    content  = build_file(sub, detail, attempt_num, ext)
    date_str = datetime.fromtimestamp(int(sub.get("created_at_epoch", time.time())),
                                      tz=timezone.utc).strftime("%Y-%m-%d")

    # 1. DSA/<Category>/<Title>/<lang>/
    dsa_folder = os.path.join(repo_path, "DSA", category, title, lang)
    os.makedirs(dsa_folder, exist_ok=True)
    with open(os.path.join(dsa_folder, f"{filename}.{ext}"), "w", encoding="utf-8") as f:
        f.write(content)
    write_problem_readme(os.path.dirname(dsa_folder), sub, detail, date_str, name)
    print(f"    ✅ DSA  → DSA/{category}/{title}/{lang}/{filename}.{ext}")

    # 2. Programming Languages/<Lang>/<Title>/
    lf = LANG_FOLDER_MAP.get(lang, lang.capitalize())
    pl_folder = os.path.join(repo_path, "Programming Languages", lf, title)
    os.makedirs(pl_folder, exist_ok=True)
    with open(os.path.join(pl_folder, f"{filename}.{ext}"), "w", encoding="utf-8") as f:
        f.write(content)
    write_pl_readme(pl_folder, sub, detail, date_str, lf, name)
    print(f"    ✅ Lang → Programming Languages/{lf}/{title}/{filename}.{ext}")
    return category

# ============== READMEs ==============
def write_problem_readme(folder, sub, detail, date, name):
    lang_rows = ""
    if os.path.isdir(folder):
        for ld in sorted(os.listdir(folder)):
            lp = os.path.join(folder, ld)
            if not os.path.isdir(lp):
                continue
            for sol in sorted(f for f in os.listdir(lp) if f.startswith("solution")):
                lang_rows += f"| `{ld}` | [{sol}](./{ld}/{sol}) |\n"
    slug = sub.get("challenge_id", "")
    with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {name}\n\n| Field | Value |\n|-------|-------|\n"
                f"| Difficulty | {detail['difficulty']} |\n"
                f"| Track | {detail.get('track_name','')} |\n"
                f"| Tags | {', '.join(f'`{t}`' for t in detail['tags'])} |\n"
                f"| Last solved | {date} |\n"
                f"| Link | [HackerRank]({BASE_URL}/challenges/{slug}/problem) |\n\n"
                f"## Solutions\n\n| Language | File |\n|----------|------|\n{lang_rows}")

def write_pl_readme(folder, sub, detail, date, lang_name, name):
    sol_rows = "".join(f"| [{s}](./{s}) |\n"
                       for s in sorted(f for f in os.listdir(folder) if f.startswith("solution")))
    slug = sub.get("challenge_id", "")
    with open(os.path.join(folder, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {name}\n\n| Field | Value |\n|-------|-------|\n"
                f"| Difficulty | {detail['difficulty']} |\n"
                f"| Language | {lang_name} |\n"
                f"| Tags | {', '.join(f'`{t}`' for t in detail['tags'])} |\n"
                f"| Last solved | {date} |\n"
                f"| Link | [HackerRank]({BASE_URL}/challenges/{slug}/problem) |\n\n"
                f"## Attempts\n\n| File |\n|------|\n{sol_rows}")

def generate_language_index_readmes(repo_path):
    pl_root = os.path.join(repo_path, "Programming Languages")
    if not os.path.isdir(pl_root):
        return
    for lang_name in sorted(os.listdir(pl_root)):
        lang_path = os.path.join(pl_root, lang_name)
        if not os.path.isdir(lang_path):
            continue
        problems = sorted(d for d in os.listdir(lang_path)
                          if os.path.isdir(os.path.join(lang_path, d)))
        rows = "\n".join(f"| [{p}](./{p}/) |" for p in problems)
        with open(os.path.join(lang_path, "README.md"), "w") as f:
            f.write(f"# {lang_name} Solutions\n\n{len(problems)} problem(s) solved."
                    f"\n\n| Problem |\n|---------|\n{rows}\n")

# ============== MAIN README ==============
def generate_main_readme(tracker: dict, repo_path: str, cert_data: dict):
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
            f"| [{p.get('title',slug)}]({BASE_URL}/challenges/{slug}/problem) "
            f"| {diff} | {cat} "
            f"| {', '.join(f'`{l}`' for l in langs)} | {p.get('date','')} |"
        )

    cat_rows  = "\n".join(f"| {c} | {n} |"
                           for c, n in sorted(category_count.items(), key=lambda x: -x[1]))
    lang_rows = "\n".join(f"| [{l}](./Programming%20Languages/{l}/) | {n} |"
                           for l, n in sorted(lang_count.items(), key=lambda x: -x[1]))

    # Certificate summary for README
    cert_summary = ""
    for c in cert_data.get("certificates", []):
        level = c["level"].replace("_", " ").title() if c["level"] else ""
        cert_summary += f"| [{c['name']}]({c['url']}) | {level} | {c['issued']} |\n"

    diff_header = " | ".join(difficulty_count.keys()) if difficulty_count else "Easy | Medium | Hard"
    diff_sep    = "---|" * max(len(difficulty_count), 1)
    diff_vals   = " | ".join(str(difficulty_count[d]) for d in difficulty_count) if difficulty_count else "0 | 0 | 0"

    with open(os.path.join(repo_path, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🎯 HackerRank Solutions — @{USERNAME}

Auto-synced with Python · Last updated: {datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}

🔗 Profile: [{BASE_URL}/profile/{USERNAME}]({BASE_URL}/profile/{USERNAME})

## 📊 Stats

| Total | {diff_header} |
|-------|{diff_sep}
| {total} | {diff_vals} |

## 🏆 Certificates

> Full details → [`Certificates/`](./Certificates/)

| Certificate | Level | Issued |
|-------------|-------|--------|
{cert_summary}
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
    git_dir = os.path.join(repo_path, ".git")
    if not os.path.isdir(git_dir):
        print(f"  ⚠ No git repo at {repo_path}. Run: git init && git remote add origin <url>")
        return
    repo = Repo(repo_path)
    repo.git.add(A=True)
    if not repo.is_dirty(index=True, working_tree=True, untracked_files=True):
        print("Nothing new to commit.")
        return
    repo.index.commit(
        f"🤖 Auto-sync HackerRank [{datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC]"
    )
    repo.remote(name="origin").push()
    print("🚀 Pushed to GitHub!")

# ============== MAIN ==============
def run():
    if not HR_SESSION or not HR_CSRF:
        raise EnvironmentError("Set HR_SESSION and HR_CSRF in your .env file.")

    repo_path  = get_repo_path()
    tracker    = load_tracker(repo_path)
    synced_ids = set(tracker["synced_ids"])
    counts     = tracker.setdefault("counts", {})
    new_count  = 0

    print(f"🔍 Fetching submissions for @{USERNAME}…\n")
    submissions = fetch_submissions()
    print()

    for sub in reversed(submissions):
        sub_id = str(sub.get("id"))
        if sub_id in synced_ids:
            continue

        slug = sub.get("challenge_id", "")
        lang = sub.get("language", "python3").lower()
        name = sub.get("challenge", {}).get("name", slug)
        print(f"  ⬇ {name} ({lang})  [id={sub_id}]")

        #detail            = fetch_problem_detail(slug)
        #count_key         = f"{slug}::{lang}"

        # Fetch actual code from individual submission endpoint
        sub["code"] = fetch_submission_code(sub_id)
        if not sub["code"]:
            print(f"    ⚠ No code returned for id={sub_id}, skipping.")
            continue

        detail            = fetch_problem_detail(slug)
        count_key         = f"{slug}::{lang}"


        attempt_num       = counts.get(count_key, 0) + 1
        counts[count_key] = attempt_num
        category          = save_solution(sub, detail, attempt_num, repo_path)

        date_str = datetime.fromtimestamp(int(sub.get("created_at_epoch", time.time())),
                                          tz=timezone.utc).strftime("%Y-%m-%d")
        existing = tracker["problems"].get(slug, {})
        langs    = existing.get("langs", [])
        if lang not in langs:
            langs.append(lang)

        tracker["problems"][slug] = {
            "title": name, "difficulty": detail["difficulty"],
            "category": category, "langs": langs, "lang": lang, "date": date_str,
        }
        synced_ids.add(sub_id)
        tracker["synced_ids"].append(sub_id)
        new_count += 1
        time.sleep(0.5)

    # Always sync certificates (independent of submissions)
    print("\n🏆 Fetching certificates and badges…")
    cert_data = fetch_certificates()
    save_certificates(cert_data, repo_path)

    generate_language_index_readmes(repo_path)
    generate_main_readme(tracker, repo_path, cert_data)
    save_tracker(tracker, repo_path)

    if new_count or cert_data["certificates"] or cert_data["badges"]:
        push_to_github(repo_path)

    print(f"\n✅ Done! {new_count} new submission(s) synced.")

if __name__ == "__main__":
    run()
