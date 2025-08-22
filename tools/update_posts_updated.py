#!/usr/bin/env python3
"""
Interactive helper: for each markdown in source/_posts, if front matter lacks `updated`,
show git commits touching the file and let the user pick one to set `updated`.

Usage:
  python tools/update_posts_updated.py [--preview] [--posts-dir PATH]

--preview: don't modify files, only show choices
--posts-dir: path to posts folder (default: source/_posts)

This script uses simple print/input for interaction.
"""
import argparse
import os
import re
import subprocess
from datetime import datetime


def find_front_matter(text):
    # Return (start_idx, end_idx, front_matter_text)
    # start_idx and end_idx are indices in text where the '---' lines start and end (inclusive of separators)
    m = re.match(r"\s*---\s*\n", text)
    if not m:
        return None
    start = m.start()
    # find the next line that is /^---\s*$/
    lines = text.splitlines(keepends=True)
    # first line is the opening '---'
    end_line = None
    for i in range(1, len(lines)):
        if re.match(r"^---\s*$", lines[i]):
            end_line = i
            break
    if end_line is None:
        return None
    # compute char indices
    fm_text = ''.join(lines[0:end_line+1])
    # start index is 0 (we only support fm at top)
    return (0, len(fm_text), fm_text)


def has_updated(fm_text):
    # crude check whether front matter contains an `updated:` key at line start (allow spaces)
    return re.search(r"^\s*updated\s*:\s*", fm_text, flags=re.MULTILINE) is not None


def insert_updated(fm_text, updated_val):
    # Try to insert updated after the date: line if present, otherwise after the opening --- line
    lines = fm_text.splitlines()
    inserted = False
    for i, line in enumerate(lines):
        if re.match(r"^\s*date\s*:\s*", line):
            # insert after this line
            lines.insert(i+1, f"updated: {updated_val}")
            inserted = True
            break
    if not inserted:
        # find first line that's '---' and insert after it
        for i, line in enumerate(lines):
            if re.match(r"^---\s*$", line):
                lines.insert(i+1, f"updated: {updated_val}")
                inserted = True
                break
    if not inserted:
        # fallback: append before final closing '---' if present
        if len(lines) >= 2:
            lines.insert(-1, f"updated: {updated_val}")
        else:
            lines.append(f"updated: {updated_val}")
    return '\n'.join(lines) + '\n'


def git_commits_for_file(repo_root, file_path):
    # Returns list of dicts: {hash, time_iso, body}
    # Use git log --follow with custom separators
    rel_path = os.path.relpath(file_path, repo_root)
    cmd = [
        'git', 'log', '--follow', '--pretty=format:%H%x1f%cI%x1f%B%x1e', '--', rel_path
    ]
    try:
        out = subprocess.check_output(cmd, cwd=repo_root)
    except subprocess.CalledProcessError:
        return []
    raw = out.decode('utf-8', errors='replace')
    if not raw:
        return []
    parts = raw.strip('\x1e').split('\x1e')
    commits = []
    for p in parts:
        fields = p.split('\x1f')
        if len(fields) >= 3:
            h, t, body = fields[0], fields[1], fields[2]
            commits.append({'hash': h.strip(), 'time': t, 'body': body.strip()})
    return commits


def show_commit_diff(repo_root, commit_hash, file_path):
    rel_path = os.path.relpath(file_path, repo_root)
    cmd = ['git', 'show', commit_hash, '--', rel_path]
    try:
        out = subprocess.check_output(cmd, cwd=repo_root)
        print(out.decode('utf-8', errors='replace'))
    except subprocess.CalledProcessError as e:
        print('Failed to get diff:', e)


def show_commit_full(repo_root, commit_hash):
    cmd = ['git', 'show', '--no-patch', '--pretty=format:%H%n%ci%n%s%n%n%b', commit_hash]
    try:
        out = subprocess.check_output(cmd, cwd=repo_root)
        print(out.decode('utf-8', errors='replace'))
    except subprocess.CalledProcessError as e:
        print('Failed to get commit info:', e)


def get_remote_origin_url(repo_root):
    try:
        out = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], cwd=repo_root)
        return out.decode().strip()
    except Exception:
        return None


def commit_web_url_from_remote(remote_url, commit_hash):
    if not remote_url:
        return None
    url = remote_url.strip()
    # git@github.com:owner/repo.git -> https://github.com/owner/repo
    if url.startswith('git@'):
        url = url.replace(':', '/', 1)
        url = url.replace('git@', 'https://')
    # strip .git
    if url.endswith('.git'):
        url = url[:-4]
    # if it's already https, keep it
    return url + '/commit/' + commit_hash


def open_commit_in_browser(repo_root, commit_hash):
    remote = get_remote_origin_url(repo_root)
    web = commit_web_url_from_remote(remote, commit_hash)
    if web is None:
        print('Could not determine remote URL to open on GitHub')
        return
    try:
        import webbrowser
        webbrowser.open(web)
        print('Opened in browser:', web)
    except Exception as e:
        print('Failed to open browser:', e)


def format_commit_preview(commit, max_lines=3):
    body = commit['body']
    # split into lines and take first few non-empty lines
    lines = [l for l in body.splitlines() if l.strip()]
    if not lines:
        # fallback to empty string
        lines = ['(no commit message)']
    preview = '\n'.join(lines[:max_lines])
    return preview


def find_repo_root(start_path):
    # run git rev-parse --show-toplevel
    try:
        out = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=start_path)
        return out.decode().strip()
    except Exception:
        return start_path


def process_file(repo_root, filepath, preview_only=False):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    fm = find_front_matter(text)
    if not fm:
        print(f"Skipping {filepath}: no front matter found")
        return False
    start, end, fm_text = fm
    if has_updated(fm_text):
        print(f"Skipping {filepath}: 'updated' already present")
        return False
    commits = git_commits_for_file(repo_root, filepath)
    if not commits:
        print(f"No git history found for {filepath}")
        return False
    print('\n' + '='*60)
    print(f"File: {filepath}")
    print('Found commits:')
    for i, c in enumerate(commits[:20], start=1):
        t = c['time']
        preview = format_commit_preview(c, max_lines=3)
        print(f"[{i}] {t} \n{preview}\n")
    help_msg = "Actions: v=show diff for this file in that commit, m=show full commit message, o=open commit on GitHub.\nYou can enter e.g. '1v' to preview commit 1's diff, or just '1' to pick it. Blank to skip."
    print(help_msg)
    while True:
        choice = input('Choice> ').strip()
        if choice == '':
            print('Skipped')
            return False
        # match like '1v' or '12mo'
        m = re.match(r'^(\d+)([a-zA-Z]+)?$', choice)
        if not m:
            print("Invalid input. Enter a number, number+actions (e.g. 1v), 'h' for help, or blank to skip")
            if choice.lower() in ('h', 'help'):
                print(help_msg)
            continue
        idx = int(m.group(1)) - 1
        if idx < 0 or idx >= len(commits[:20]):
            print('Number out of range')
            continue
        actions = m.group(2) or ''
        chosen = commits[idx]
        # perform actions
        if actions:
            for a in actions:
                if a.lower() == 'v':
                    print('\n--- diff for commit', chosen['hash'], '---')
                    show_commit_diff(repo_root, chosen['hash'], filepath)
                elif a.lower() == 'm':
                    print('\n--- full commit info ---')
                    show_commit_full(repo_root, chosen['hash'])
                elif a.lower() == 'o':
                    open_commit_in_browser(repo_root, chosen['hash'])
                else:
                    print('Unknown action:', a)
            # after actions, continue prompting
            continue
        # no actions: treat as selection
        # parse chosen['time'] (ISO) and format to `YYYY-MM-DD HH:MM:SS`
        try:
            dt = datetime.fromisoformat(chosen['time'])
            updated_val = dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            updated_val = chosen['time']
        print(f"Selected time: {updated_val}")
        if preview_only:
            print('(preview mode) Not writing file')
            return True
        # write back: replace fm_text with inserted
        new_fm = insert_updated(fm_text, updated_val)
        new_text = new_fm + text[end:]
        # write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_text)
        print(f"Wrote updated to {filepath}")
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true', help='Do not write files; only preview')
    parser.add_argument('--posts-dir', default=os.path.join('source', '_posts'), help='Path to posts dir')
    args = parser.parse_args()

    repo_root = find_repo_root(os.getcwd())
    posts_dir = os.path.join(repo_root, args.posts_dir) if not os.path.isabs(args.posts_dir) else args.posts_dir

    if not os.path.isdir(posts_dir):
        print(f"Posts directory not found: {posts_dir}")
        return

    # walk .md files
    md_files = []
    for root, _, files in os.walk(posts_dir):
        for fn in files:
            if fn.lower().endswith('.md'):
                md_files.append(os.path.join(root, fn))

    if not md_files:
        print('No markdown files found under', posts_dir)
        return

    print(f'Found {len(md_files)} markdown files under {posts_dir}')
    modified_count = 0
    for fp in sorted(md_files):
        changed = process_file(repo_root, fp, preview_only=args.preview)
        if changed:
            modified_count += 1
    print('\nDone. Modified files:', modified_count)


if __name__ == '__main__':
    main()
