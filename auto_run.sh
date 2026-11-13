#!/usr/bin/env bash
# 本地定时更新：同步 upstream -> 实测分辨率 -> 每频道择优（优先 720p）-> 推送 fork
set -euo pipefail
cd "$(dirname "$0")"

git fetch upstream
git merge --no-edit upstream/main
git push origin main

python3 scripts/check_m3u8.py --probe --prefer-resolution 720 --report /tmp/cn_all_best_report.csv

old=$(git show HEAD:cn_all_best.m3u8 | grep -vE '^#(CHECKED|PROBE|PREFER):' || true)
new=$(grep -vE '^#(CHECKED|PROBE|PREFER):' cn_all_best.m3u8 || true)
if [ "$old" = "$new" ]; then
  echo "cn_all_best.m3u8 无实质变化，跳过提交"
else
  git add cn_all_best.m3u8
  git commit -m "chore: 自动更新 cn_all_best.m3u8"
  git push origin main
fi
