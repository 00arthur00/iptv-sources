#!/usr/bin/env bash
# 本地定时更新：同步 upstream -> 校验去重 -> 每频道择优 -> 推送 fork
set -euo pipefail
cd "$(dirname "$0")"

git fetch upstream
git merge --no-edit upstream/main
git push origin main

python3 scripts/check_m3u8.py --report /tmp/cn_all_best_report.csv
python3 scripts/check_m3u8.py ipv6.m3u -o ipv6_best.m3u --report /tmp/ipv6_best_report.csv

changed=0
for f in cn_all_best.m3u8 ipv6_best.m3u8; do
  old=$(git show "HEAD:$f" 2>/dev/null | grep -vE '^#(CHECKED|PROBE|PREFER):' || true)
  new=$(grep -vE '^#(CHECKED|PROBE|PREFER):' "$f" || true)
  if [ "$old" != "$new" ]; then
    changed=1
  fi
done

if [ "$changed" = "0" ]; then
  echo "播放列表无实质变化，跳过提交"
else
  git add cn_all_best.m3u8 ipv6_best.m3u8
  git commit -m "chore: 自动更新播放列表"
  git push origin main
fi
