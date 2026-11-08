#!/usr/bin/env python3
"""检查 cn_all.m3u8 直播源的有效性，去重，每个频道只保留最优一条，
并按 CCTV1~17（CCTV5+ 紧随 CCTV5）、其他频道原文件顺序输出到 cn_all_best.m3u8。

用法：
    python3 scripts/check_m3u8.py                 # 默认：读 cn_all.m3u8，写 cn_all_best.m3u8
    python3 scripts/check_m3u8.py -o xxx.m3u8     # 自定义输出
    python3 scripts/check_m3u8.py --no-check      # 只去重/择优，不联网检查
    python3 scripts/check_m3u8.py --report r.csv  # 额外输出 CSV 报告

择优规则：分辨率高者优先（从 <input>_status.m3u8 的 [1080]/[720]/[576] 标签读取，
找不到时回退到 EXTINF 里的 “(1080p)” 等标注），其次流畅度 S > 未知 > F，
最后比较本次实测的响应时间，越快越好。
"""

import argparse
import concurrent.futures
import csv
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit, urlunsplit

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
READ_LIMIT = 4096  # 只需读取开头判断是否为 M3U8 播放列表


def parse_playlist(path):
    """解析 M3U8，返回 (头部注释行, [(EXTINF, url)])。"""
    header, entries = [], []
    pending_extinf = None
    started = False
    with open(path, encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#EXTINF"):
                pending_extinf = line
                started = True
            elif line.startswith("#"):
                if not started:  # 第一条 EXTINF 之前的注释视为文件头
                    header.append(line)
                # 其余注释（如 #EXT-X-...）忽略
            elif pending_extinf is not None:
                entries.append((pending_extinf, line))
                pending_extinf = None
            # 没有 EXTINF 的裸 URL 忽略
    return header, entries


def channel_name(extinf):
    """从 EXTINF 行取频道名：最后一个逗号之后的内容。"""
    return extinf.rsplit(",", 1)[-1].strip() if "," in extinf else ""


def channel_key(name):
    """归一化频道标识，用于分组：CCTV-1 (720p) 与 CCTV1 视为同一频道。"""
    n = re.sub(r"\s*\(\s*\d{3,4}[pi]?\s*\)", "", name.strip())
    n = re.sub(r"\s*\(\s*(?:4k|hd|sd)\s*\)", "", n, flags=re.IGNORECASE)
    n = re.sub(r"^CCTV\s*-\s*", "CCTV", n, flags=re.IGNORECASE)
    return n.upper()


def quality_from_name(name):
    """从频道名里的标注提取分辨率，如 CCTV-1 (720p) -> 720，取不到返回 0。"""
    m = re.search(r"\(\s*(\d{3,4})[pi]?\s*\)", name)
    if m:
        return int(m.group(1))
    if re.search(r"\(\s*4k\s*\)", name, re.IGNORECASE):
        return 2160
    return 0


def normalize_url(url):
    """归一化 URL 用于去重：协议/主机小写，去掉默认端口，路径为空时补 '/'。"""
    url = url.strip()
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return url
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    netloc = host
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, parts.query, parts.fragment))


def load_status_quality(path):
    """从 <input>_status.m3u8 读取每个 URL 的分辨率与流畅度标签。

    返回 {归一化 URL: (分辨率, 标签)}，标签为 "S" / "F" / ""。
    """
    try:
        _, entries = parse_playlist(path)
    except OSError:
        return {}
    qmap = {}
    for extinf, url in entries:
        m = re.search(r"\[(\d+)\]", extinf)
        res = int(m.group(1)) if m else 0
        flag = "S" if "[S]" in extinf else ("F" if "[F]" in extinf else "")
        qmap[normalize_url(url)] = (res, flag)
    return qmap


def _fetch(url, timeout, unverified):
    ctx = ssl.create_default_context()
    if unverified:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    start = time.monotonic()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        body = resp.read(READ_LIMIT)
        elapsed = time.monotonic() - start
        return resp.status, resp.headers.get("Content-Type", ""), body, elapsed


def check_url(url, timeout):
    """检查单个链接，返回 (是否有效, 说明, 耗时秒)。证书错误时用无校验 SSL 重试一次。"""
    for attempt in (0, 1):
        try:
            status, ctype, body, elapsed = _fetch(url, timeout, unverified=attempt == 1)
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}", 0.0
        except socket.timeout:
            return False, f"超时(>{timeout}s)", 0.0
        except Exception as e:
            reason = getattr(e, "reason", e)
            if attempt == 0 and isinstance(reason, ssl.SSLCertVerificationError):
                continue
            return False, f"{type(reason).__name__}: {reason}"[:150], 0.0

        text = body.decode("utf-8", "ignore") if body else ""
        if status == 200 and ("#EXTM3U" in text or "#EXTINF" in text):
            return True, f"200 {ctype}".strip(), elapsed
        if status == 200 and text.lstrip().startswith("#EXT"):
            return True, f"200 {ctype}".strip(), elapsed
        return False, f"HTTP {status}，内容不是 M3U8", elapsed
    return False, "未知错误", 0.0


def best_rank(item, qmap):
    """择优排序键（越小越好）：分辨率降序、流畅度 S > 未知 > F、实测响应时间升序。"""
    extinf, url, _detail, elapsed = item
    name = channel_name(extinf)
    res, flag = qmap.get(normalize_url(url), (0, ""))
    if res == 0:
        res = quality_from_name(name)
    flag_rank = {"S": 2, "": 1, "F": 0}.get(flag, 1)
    return (-res, -flag_rank, elapsed)


CCTV_KEY_RE = re.compile(r"^CCTV(\d+)(\+)?$")


def cctv_sort_key(item):
    """排序键：CCTV 按编号升序（CCTV5+ 紧随 CCTV5），其余频道排在其后。"""
    key = channel_key(channel_name(item[0]))
    m = CCTV_KEY_RE.match(key)
    if m:
        return (0, int(m.group(1)), 1 if m.group(2) else 0)
    if key.startswith("CCTV"):
        return (0, 10000, 0)  # CCTV4K 等非数字频道排在数字频道之后
    return (1, 0, 0)


def sort_cctv_first(items):
    """CCTV 频道按编号在前，其他频道保持原有相对顺序。"""
    decorated = [(cctv_sort_key(it), i, it) for i, it in enumerate(items)]
    decorated.sort(key=lambda t: (t[0], t[1]))
    return [it for _, _, it in decorated]


def main():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser(
        description="检查 cn_all.m3u8 并生成每频道最优的 cn_all_best.m3u8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("input", nargs="?", default=os.path.join(repo_dir, "cn_all.m3u8"),
                    help="输入的 m3u8 文件（默认仓库根目录的 cn_all.m3u8）")
    ap.add_argument("-o", "--output", help="输出文件（默认 <input>_best.m3u8）")
    ap.add_argument("--status",
                    help="提供分辨率标签的 status 文件；默认自动查找 <input 去掉后缀>_status.m3u8，"
                         "传空字符串则不使用")
    ap.add_argument("--timeout", type=float, default=10, help="单个链接超时秒数（默认 10）")
    ap.add_argument("--workers", type=int, default=32, help="并发数（默认 32）")
    ap.add_argument("--report", help="把检查结果写入 CSV 报告")
    ap.add_argument("--no-check", action="store_true", help="只去重/择优，不联网检查")
    args = ap.parse_args()

    header, entries = parse_playlist(args.input)
    if not entries:
        print(f"错误：{args.input} 中没有找到任何有效条目", file=sys.stderr)
        return 2

    # 分辨率/流畅度来源：默认自动找同名 _status 文件
    status_path = args.status
    if status_path is None:
        status_path = re.sub(r"\.[^.]+$", "", args.input) + "_status.m3u8"
        if not os.path.exists(status_path):
            status_path = ""
    qmap = load_status_quality(status_path) if status_path else {}
    if qmap:
        print(f"分辨率标签来源：{status_path}（{len(qmap)} 条）", file=sys.stderr)

    total = len(entries)

    # 1) 按归一化 URL 去重（保留首次出现的条目）
    seen = {}
    deduped = []
    duplicates = []
    for extinf, url in entries:
        key = normalize_url(url)
        if key in seen:
            duplicates.append((channel_name(extinf), url, seen[key]))
            continue
        seen[key] = channel_name(extinf)
        deduped.append((extinf, url))

    # 2) 并发检查
    results = {}
    if not args.no_check:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(check_url, url, args.timeout): url for _, url in deduped}
            done = 0
            for fut in concurrent.futures.as_completed(futures):
                url = futures[fut]
                try:
                    results[url] = fut.result()
                except Exception as e:  # 理论上 check_url 不会抛出
                    results[url] = (False, f"检查异常: {e}", 0.0)
                done += 1
                if done % 25 == 0 or done == len(futures):
                    print(f"  已检查 {done}/{len(futures)} ...", file=sys.stderr)

    # 3) 区分有效 / 无效
    valid, invalid = [], []
    for extinf, url in deduped:
        ok, detail, elapsed = results.get(url, (True, "未检查", 0.0))
        (valid if ok else invalid).append((extinf, url, detail, elapsed))

    # 4) 每个频道只保留最优的一条
    valid_before_best = len(valid)
    valid_snapshot = list(valid)  # 供报告使用（含被择优移除的条目）
    best_groups = {}
    dropped_best = []  # (EXTINF, url, 保留的 url)
    groups = {}
    for i, item in enumerate(valid):
        groups.setdefault(channel_key(channel_name(item[0])), []).append(i)
    kept = [True] * len(valid)
    for key, idxs in sorted(groups.items()):
        best_i = min(idxs, key=lambda i: best_rank(valid[i], qmap))
        for i in idxs:
            kept[i] = i == best_i
            if i != best_i:
                dropped_best.append((valid[i][0], valid[i][1], valid[best_i][1]))
        item = valid[best_i]
        res, flag = qmap.get(normalize_url(item[1]), (0, ""))
        if res == 0:
            res = quality_from_name(channel_name(item[0]))
        best_groups[key] = (item, res, flag, len(idxs))
    removed_n = len(valid) - sum(kept)
    valid = [item for i, item in enumerate(valid) if kept[i]]

    # 5) 排序：CCTV 编号在前，其余频道保持原顺序
    valid = sort_cctv_first(valid)

    # 6) 汇总并写输出
    default_out = re.sub(r"\.[^.]+$", "", args.input) + "_best.m3u8"
    out_path = args.output or default_out
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header or ["#EXTM3U"]) + "\n")
        f.write(f"#CHECKED: {stamp} valid={valid_before_best}/{len(deduped)} "
                f"output={len(valid)} source={args.input}\n")
        f.write("#BEST: one per channel\n")
        f.write("#ORDER: CCTV ascending first, then other channels\n")
        for extinf, url, _, _ in valid:
            f.write(extinf + "\n" + url + "\n")

    if args.report:
        with open(args.report, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["channel", "url", "ok", "detail", "elapsed_ms", "note"])
            valid_pairs = {(extinf, url) for extinf, url, _, _ in valid}
            dropped_map = {(e, u): ku for e, u, ku in dropped_best}
            for extinf, url, detail, elapsed in valid_snapshot + invalid:
                ok = (extinf, url) in valid_pairs or (extinf, url) in dropped_map
                note = ""
                if (extinf, url) in dropped_map:
                    note = f"非最佳，已移除（保留 {dropped_map[(extinf, url)]}）"
                w.writerow([channel_name(extinf), url, "1" if ok else "0",
                            detail, f"{elapsed * 1000:.0f}", note])
            for ch, url, kept_ch in duplicates:
                w.writerow([ch, url, "", "重复，已移除", "", f"与 {kept_ch} 重复"])

    # 7) 打印摘要
    print()
    print(f"总数：{total} 条")
    print(f"重复移除：{len(duplicates)} 条")
    print(f"检查（去重后）：{len(deduped)} 条")
    print(f"有效：{valid_before_best} 条    无效：{len(invalid)} 条")
    print(f"每频道择优：{len(best_groups)} 个频道，移除 {removed_n} 条")
    print(f"输出条目：{len(valid)} 条    {out_path}")
    if args.report:
        print(f"报告：{args.report}")

    if duplicates:
        print("\n重复条目：")
        for ch, url, kept_ch in duplicates:
            print(f"  [{ch}] {url}  (与 {kept_ch} 的链接重复)")

    if best_groups:
        print("\n每频道最优：")
        for key, (item, res, flag, n) in best_groups.items():
            name, url, _, elapsed = item
            qdesc = f"{res}p" if res else "未知分辨率"
            if flag:
                qdesc += f" [{flag}]"
            print(f"  {key}：{n} 条中保留 {url}  ({qdesc}, {elapsed * 1000:.0f}ms)")

    if invalid:
        print("\n无效条目：")
        for extinf, url, detail, _ in invalid:
            print(f"  [{channel_name(extinf)}] {url}  -> {detail}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
