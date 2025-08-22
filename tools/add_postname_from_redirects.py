#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据仓库根目录下的 `_redirects` 文件，把重定向中目标的新 id 写入到 `source/_posts` 下对应文章的 YAML front-matter 中。

用法：
    python add_postname_from_redirects.py          # 预览（dry-run）
    python add_postname_from_redirects.py --apply  # 实际写入
    python add_postname_from_redirects.py --yes --apply  # 跳过确认

脚本会：
 - 解析 `_redirects` 中形如 `/YYYY/MM/DD/ID/*    posts/<new_id>/:splat` 的行
 - 在 `source/_posts` 下递归查找所有 `.md` 文件，读取 front-matter 的 `date` 字段
 - 在匹配的文章 front-matter 中添加或更新 `id: <new_id>` 字段

注：脚本输出信息使用 `print`，用中文注释和提示，运行时会打印及时反馈。
"""

import argparse
import re
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

FM_BLOCK_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n",
                         re.DOTALL | re.MULTILINE)
# 提取 date 与 id 的 front-matter 行
DATE_LINE_RE = re.compile(r"^\s*date\s*:\s*(.+)$",
                          re.IGNORECASE | re.MULTILINE)
ID_LINE_RE = re.compile(r"^\s*id\s*:\s*(.+)$",
                        re.IGNORECASE | re.MULTILINE)
# 匹配形如: /2015/02/22/1/*        posts/new-arrival/:splat
REDIRECT_RE = re.compile(
    r"^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/\*\s+posts/([^/:\s]+)")
KEY_NAME_DEFAULT = 'id'


def parse_redirects(path: Path) -> List[Tuple[str, str]]:
    """解析 `_redirects` 文件，返回条目列表：(old_id, new_id)
    只解析匹配到的行，忽略注释和无法解析的行。
    """
    entries: List[Tuple[str, str]] = []
    text = path.read_text(encoding='utf-8')
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith('#'):
            continue
        m = REDIRECT_RE.match(ln)
        if not m:
            # 忽略不匹配的重定向行
            continue
        year, month, day, old_id, new_id = m.groups()
        entries.append((old_id, new_id))
    return entries


def extract_front_matter(text: str) -> Optional[re.Match]:
    return FM_BLOCK_RE.match(text)


def extract_date_from_fm(fm_text: str) -> Optional[str]:
    m = DATE_LINE_RE.search(fm_text)
    if not m:
        return None
    date_field = m.group(1).strip().strip('\"\'')
    # 提取第一个 YYYY-MM-DD
    dm = re.search(r"(\d{4}-\d{2}-\d{2})", date_field)
    if dm:
        return dm.group(1)
    return None


def extract_id_from_fm(fm_text: str) -> Optional[str]:
    m = ID_LINE_RE.search(fm_text)
    if not m:
        return None
    id_field = m.group(1).strip().strip('\"\'')
    # 直接返回 id 字符串（不做额外格式要求）
    return id_field


def safe_yaml_value(val: str) -> str:
    # 简单的 YAML 值安全化：若值中包含空格或特殊字符，使用单引号并转义'
    if re.search(r"[\s:'\\]", val):
        return "'" + val.replace("'", "''") + "'"
    return val


def update_front_matter_text(full_text: str, key: str, value: str) -> Tuple[str, bool]:
    """在 full_text 的 front-matter 中添加或更新 key: value。返回 (new_text, changed)。
    仅修改 front-matter 的内容。
    """
    m = extract_front_matter(full_text)
    if not m:
        return (full_text, False)
    fm_content = m.group(1)
    key_re = re.compile(r"^\s*" + re.escape(key) +
                        r"\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    km = key_re.search(fm_content)
    safe_val = safe_yaml_value(value)
    if km:
        existing_raw = km.group(1).strip()
        # 移除可能的引号以便比较
        existing_unquoted = existing_raw.strip('\"\'')
        if existing_unquoted == value:
            return (full_text, False)
        # 替换该行
        new_fm = key_re.sub(f"{key}: {safe_val}", fm_content, count=1)
    else:
        # 在 fm 内容末尾添加一行（保持与原 fm 的换行风格）
        if fm_content and not fm_content.endswith('\n'):
            fm_content = fm_content + '\n'
        new_fm = fm_content + f"{key}: {safe_val}\n"

    # 用新 fm 替换原文中的相应区块
    start, end = m.start(1), m.end(1)
    new_text = full_text[:start] + new_fm + full_text[end:]
    return (new_text, True)


def find_posts(posts_dir: Path) -> List[Path]:
    return sorted(posts_dir.rglob('*.md'))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--posts-dir', '-d', default=None,
                        help='posts 目录路径，默认相对于项目：<root>/source/_posts')
    parser.add_argument('--redirects', '-r', default=None,
                        help='重定向文件路径，默认: <root>/_redirects')
    parser.add_argument('--apply', action='store_true', help='执行写入（否则只做预览）')
    parser.add_argument('--yes', action='store_true', help='在 --apply 时跳过确认')
    parser.add_argument('--key', default=KEY_NAME_DEFAULT,
                        help='要写入 front-matter 的键名，默认 postname')
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    default_posts = repo_root / 'source' / '_posts'
    posts_dir = Path(args.posts_dir).resolve(
    ) if args.posts_dir else default_posts.resolve()
    redirects_file = Path(args.redirects).resolve(
    ) if args.redirects else (repo_root / '_redirects')

    if not redirects_file.exists():
        print(f"错误：找不到重定向文件：{redirects_file}")
        sys.exit(2)
    if not posts_dir.exists() or not posts_dir.is_dir():
        print(f"错误：posts 目录不存在：{posts_dir}")
        sys.exit(2)

    print(f"读取重定向：{redirects_file}")
    entries = parse_redirects(redirects_file)
    print(f"解析到 {len(entries)} 条可用重定向条目（格式 /.../ID/* -> posts/<postname>）。")

    md_files = find_posts(posts_dir)
    print(f"在 {posts_dir} 下找到 {len(md_files)} 个 Markdown 文件，开始匹配...")

    # 建立按 id 索引： id_str -> list of files
    id_index: Dict[str, List[Path]] = {}
    for p in md_files:
        try:
            txt = p.read_text(encoding='utf-8')
        except Exception as e:
            print(f"读取文件失败，跳过：{p}，原因：{e}")
            continue
        m = extract_front_matter(txt)
        if not m:
            continue
        fm = m.group(1)
        idv = extract_id_from_fm(fm)
        if not idv:
            continue
        id_index.setdefault(idv, []).append(p)

    planned: List[Tuple[Path, str]] = []  # (file, new_id)
    skipped = 0
    for old_id, new_id in entries:
        candidates = id_index.get(old_id, [])
        if not candidates:
            print(f"未找到与 id 匹配的文章：{old_id} -> {new_id}，跳过。")
            skipped += 1
            continue
        if len(candidates) > 1:
            print(
                f"警告：存在多个具有相同 id ({old_id}) 的文章，无法唯一匹配重定向到 {new_id}，跳过。")
            for c in candidates:
                print(f"  候选：{c.relative_to(posts_dir)}")
            skipped += 1
            continue
        planned.append((candidates[0], new_id))

    print(f"\n匹配完成：将更新 {len(planned)} 个文件，跳过 {skipped} 条不可解析的重定向。\n")

    # 预览变更
    # (path, new_id, old_value_or_None)
    changes: List[Tuple[Path, str, Optional[str]]] = []
    for p, new_id in planned:
        txt = p.read_text(encoding='utf-8')
        m = extract_front_matter(txt)
        if not m:
            print(f"跳过（没有 front-matter）：{p.relative_to(posts_dir)}")
            continue
        fm = m.group(1)
        # 查找现有键
        key_re = re.compile(r"^\s*" + re.escape(args.key) +
                            r"\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
        km = key_re.search(fm)
        old = None
        if km:
            old = km.group(1).strip().strip('\"\'')
        if old == new_id:
            print(
                f"无需修改：{p.relative_to(posts_dir)} 已有 {args.key}: {new_id}")
            continue
        changes.append((p, new_id, old))

    if not changes:
        print("没有需要写入的变更。")
        return

    print('将要应用的变更：')
    for p, new_id, old in changes:
        rel = p.relative_to(posts_dir)
        if old:
            print(f"  {rel}: {args.key}: {old} -> {new_id}")
        else:
            print(f"  {rel}: 添加 {args.key}: {new_id}")

    if not args.apply:
        print('\n这是预览（dry-run）。要实际写入请使用 --apply 参数。')
        return

    if args.apply and not args.yes:
        ans = input('确认要执行以上写入操作吗？输入 y 确认：')
        if ans.lower() != 'y':
            print('取消。')
            return

    # 实际写入
    applied = 0
    for p, new_id, old in changes:
        try:
            txt = p.read_text(encoding='utf-8')
            new_txt, changed = update_front_matter_text(
                txt, args.key, new_id)
            if not changed:
                print(f"跳过（无变化）：{p.relative_to(posts_dir)}")
                continue
            p.write_text(new_txt, encoding='utf-8')
            applied += 1
            if old:
                print(
                    f"更新：{p.relative_to(posts_dir)} {args.key}: {old} -> {new_id}")
            else:
                print(
                    f"添加：{p.relative_to(posts_dir)} {args.key}: {new_id}")
        except Exception as e:
            print(f"写入失败：{p.relative_to(posts_dir)}，原因：{e}")

    print(f"\n完成：已写入 {applied} 个文件（目标 {len(changes)}）。")


if __name__ == '__main__':
    main()
