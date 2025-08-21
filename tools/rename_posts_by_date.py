#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按 Front Matter 的 date 字段将 source/_posts 目录下的 .md 文件移动到按年份/月份组织的目录：
    posts_dir/YYYY/MM/原文件名.md
并把与 md 文件同名的资源文件夹（若存在）一起移动到同一目标目录（目标名保持原文件名不含扩展名）。

用法：
    python rename_posts_by_date.py         # 仅预览（dry-run）
    python rename_posts_by_date.py --apply # 实际执行移动

支持选项：
    --posts-dir 路径  指定 posts 目录，默认相对于项目：<root>/source/_posts
    --apply           执行移动（否则只做预览）
    --yes             跳过确认（在 --apply 时有用）

脚本会：
 - 解析文件头部的 YAML front matter（以 "---" 包裹）
 - 在 date 字段中提取第一个 YYYY-MM-DD 格式日期
 - 目标路径为 posts_dir/YYYY/MM/<原文件名.md>
 - 若存在与原文件同名的文件夹（同目录，名字等于 md 文件的 stem），把该文件夹移动到同一目标目录下
 - 遇到冲突或无法解析会报告并跳过（避免覆盖）
"""


from __future__ import annotations
import argparse
import re
from pathlib import Path
import sys
from typing import Optional, Tuple

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
FM_BLOCK_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.DOTALL | re.MULTILINE)
DATE_LINE_RE = re.compile(r"^\s*date\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)


def extract_front_matter(text: str) -> Optional[str]:
    m = FM_BLOCK_RE.match(text)
    if m:
        return m.group(1)
    return None


def extract_date_from_fm(fm: str) -> Optional[str]:
    m = DATE_LINE_RE.search(fm)
    if not m:
        return None
    date_field = m.group(1).strip().strip('\"\'')
    dm = DATE_RE.search(date_field)
    if dm:
        return dm.group(1)
    return None


def compute_new_names(md_path: Path, posts_dir: Path) -> Tuple[Optional[Path], Optional[Path]]:
    """返回 (new_md_path or None, new_resource_dir or None)。如果不需要移动则返回 (None, None)。
    new_md_path 和 new_resource_dir 都位于 posts_dir/YYYY/MM/ 下。
    """
    try:
        text = md_path.read_text(encoding='utf-8')
    except Exception:
        return (None, None)
    fm = extract_front_matter(text)
    if not fm:
        return (None, None)
    date = extract_date_from_fm(fm)
    if not date:
        return (None, None)
    year = date[0:4]
    month = date[5:7]
    target_dir = posts_dir / year / month
    new_md = target_dir / md_path.name
    # resource dir: same directory entry named as original stem (folder)
    res_dir = md_path.with_name(md_path.stem)
    new_res_dir = target_dir / md_path.stem
    need_move_file = True
    try:
        need_move_file = md_path.resolve() != new_md.resolve()
    except Exception:
        # 如果 resolve 失败（例如目标不存在），以路径字符串比较为后备
        need_move_file = str(md_path) != str(new_md)
    need_move_dir = res_dir.exists() and res_dir.is_dir()
    # 如果资源目录在目标位置已存在并且和源相同路径，则不需要移动
    try:
        if need_move_dir and new_res_dir.exists() and res_dir.resolve() == new_res_dir.resolve():
            need_move_dir = False
    except Exception:
        pass
    return (new_md if need_move_file else None, new_res_dir if need_move_dir else None)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--posts-dir', '-d', default=None,
                        help='posts 目录路径，默认相对于项目：<root>/source/_posts')
    parser.add_argument('--apply', action='store_true', help='执行重命名（否则只做预览）')
    parser.add_argument('--yes', action='store_true', help='在 --apply 时跳过确认')
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    default_posts = script_dir.parent / 'source' / '_posts'
    posts_dir = Path(args.posts_dir).resolve() if args.posts_dir else default_posts.resolve()

    if not posts_dir.exists() or not posts_dir.is_dir():
        print(f"错误：posts 目录不存在：{posts_dir}")
        sys.exit(2)

    md_files = sorted([p for p in posts_dir.iterdir() if p.is_file() and p.suffix.lower() == '.md'])
    if not md_files:
        print("未找到任何 .md 文件（在 %s）" % posts_dir)
        return

    planned = []  # tuples (orig_md, new_md_or_None, orig_res_dir_if_exists, new_res_dir_or_None)
    for md in md_files:
        new_md, new_res = compute_new_names(md, posts_dir)
        orig_res = md.with_name(md.stem)
        planned.append((md, new_md, orig_res if orig_res.exists() and orig_res.is_dir() else None, new_res))

    rename_file_count = sum(1 for a,b,c,d in planned if b is not None)
    rename_dir_count = sum(1 for a,b,c,d in planned if d is not None)

    print(f"共扫描 {len(md_files)} 个 md 文件。计划重命名文件：{rename_file_count} 个，资源文件夹：{rename_dir_count} 个。\n")

    for md, new_md, orig_res, new_res in planned:
        if new_md is None and new_res is None:
            print(f"跳过: {md} （无法解析 date 或已是期望位置）")
            continue
        print('---')
        [md, new_md, orig_res, new_res] = [p and p.relative_to(posts_dir) 
                                           for p in (md, new_md, orig_res, new_res)]
        print(f"原文件: {md}  ")
        if new_md:
            print(f"  目标文件: {new_md}")
        else:
            print("  目标文件: 无变更")
        if orig_res and new_res:
            print(f"  资源文件夹: {orig_res} -> 目标: {new_res}")
        elif orig_res:
            print(f"  资源文件夹: {orig_res} -> 目标: 无变更")
        else:
            print("  资源文件夹: 无")

    if not args.apply:
        print('\n这是预览（dry-run）。要实际执行重命名，请使用 --apply 参数。')
        return

    if args.apply and not args.yes:
        ans = input('确认要执行以上重命名操作吗？输入 y 确认：')
        if ans.lower() != 'y':
            print('取消。')
            return

    # 执行重命名
    file_renamed = 0
    dir_renamed = 0
    for md, new_md, orig_res, new_res in planned:
        try:
            if new_md:
                # 确保目标目录存在
                new_md.parent.mkdir(parents=True, exist_ok=True)
                if new_md.exists():
                    print(f"跳过文件移动（目标已存在）：{md} -> {new_md}")
                else:
                    md.rename(new_md)
                    print(f"移动文件：{md} -> {new_md}")
                    file_renamed += 1
            if orig_res and new_res:
                # 确保目标目录存在
                new_res_parent = new_res.parent
                new_res_parent.mkdir(parents=True, exist_ok=True)
                if new_res.exists():
                    print(f"跳过文件夹移动（目标已存在）：{orig_res} -> {new_res}")
                else:
                    orig_res.rename(new_res)
                    print(f"移动文件夹：{orig_res} -> {new_res}")
                    dir_renamed += 1
        except Exception as e:
            print(f"错误处理 {md.name}：{e}")

    print(f"\n完成：文件重命名 {file_renamed} 个，文件夹重命名 {dir_renamed} 个。")


if __name__ == '__main__':
    main()
