
<div align="center">

# 📺 iptv-sources

**IPTV 直播数据分享 | 每天自动采集更新**

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Channels](https://img.shields.io/badge/Channels-46+-orange)
![Auto Update](https://img.shields.io/badge/Auto_Update-每日-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

![Last Commit](https://img.shields.io/github/last-commit/best-fan/iptv-sources)
![Commit Activity](https://img.shields.io/github/commit-activity/m/best-fan/iptv-sources)
![Visitors](https://hits.sh/github.com/best-fan/iptv-sources.svg?style=flat&label=Visitors&labelColor=34275f&color=8957e5)

</div>

## 🚀 项目简介

这是一个功能强大的 IPTV 直播数据采集和汇总地址的仓库。项目可以从多个来源获取直播源数据，进行有效性验证，并生成标准的 M3U8 播放列表文件。

**✨ 核心特点：**
- 🔄 **每日自动更新** - 每日凌晨自动运行采集确保直播源的有效性
- ✅ **智能验证** - 自动检测可播放性
- 📊 **数据分类** - 按频道类型整理


## 📁 项目结构

```bash
iptv-sources/
├── 📋 cn_all.m3u8                 # 完整播放列表（46+个频道）
├── 📋 cn_all_status.m3u8          # 完整播放列表（46+个频道 含分辨率、流畅度）
├── 📋 cn_all_best.m3u8            # 本地生成：每个频道精选一条，CCTV 编号在前
├── 📡 ipv6.m3u                    # IPv6 直播源列表（来源：fanmingming/live）
├── 📡 ipv6_best.m3u               # 本地生成：IPv6 每频道精选一条
├── 📡 cn_cctv.m3u8                # 央视频道列表
├── 📡 cn_cctv_status.m3u8         # 央视频道列表（含分辨率、流畅度）
├── 🏢 cn_province.m3u8            # 卫视频道列表  
├── 🏢 cn_province_status.m3u8     # 卫视频道列表（含分辨率、流畅度）  
├── 💎 cn_pay.m3u8                 # 付费频道列表
├── 💎 cn_pay_status.m3u8          # 付费频道列表（含分辨率、流畅度）
├── 🛠️ scripts/check_m3u8.py       # 本地校验/去重/择优脚本
├── 🛠️ auto_run.sh                 # 本地定时更新脚本（同步 + 生成 + 推送）
└── 📖 README.md                   # 项目说明文档
```

## ✨ 功能特性

<div align="center">

| 功能 | 状态 | 图标 | 描述 |
|------|------|------|------|
| **多源数据采集** | ✅ | 🔍 | 支持从多个网站和 API 获取直播源数据 |
| **有效性验证** | ✅ | ✅ | 自动检测直播源的可播放性和响应时间 |
| **频道分类** | ✅ | 📺 | 支持央视、卫视、付费频道等多种分类 |
| **智能去重** | ✅ | 🎯 | 自动去除重复的直播源 |
| **清晰度排序** | ✅ | 📊 | 按视频清晰度自动排序 |
| **跨域检测** | ✅ | 🌐 | 检测直播源是否支持跨域访问 |
| **M3U8 生成** | ✅ | 📝 | 生成标准格式的 M3U8 播放列表 |

</div>

## 📺 支持频道类型

### 🇨🇳 央视频道
- **包含**:📡 CCTV-1 到 CCTV-17，CCTV-4K 等
- **文件**: `cn_cctv.m3u8`

### 🏢 卫视频道  
- **包含**:🏙️ 北京卫视、湖南卫视、东方卫视等 37 个省级卫视
- **文件**: `cn_province.m3u8`

### 💎 付费频道
- **包含**:💰 凤凰中文、金鹰纪实、茶友频道等 45 个付费频道
- **文件**: `cn_pay.m3u8`

### 📋 完整列表
- **包含**: 📺所有 46+ 个频道
- **文件**: `cn_all.m3u8`



## 📡 播放源地址


### 🎯 源播放文件

以下是项目生成的播放列表文件，可以直接在支持 M3U8 格式的播放器中使用：

| 文件名称 | 频道数量 | 描述 | 源链接 | 代理链接 |
|----------|----------|------|----------|----------|
| `cn_all.m3u8` | 46+ | 完整播放列表（包含所有频道） | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8) |[下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all.m3u8) |
| `cn_all_status.m3u8` | 46+ | 完整播放列表（含分辨率、流畅度） | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all_status.m3u8) |[下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_all_status.m3u8) |
| `cn_cctv.m3u8` | 10+ | 央视频道列表 | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_cctv.m3u8) |[下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_cctv.m3u8) |
| `cn_cctv_status.m3u8` | 10+ | 央视频道列表（含分辨率、流畅度） | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_cctv_status.m3u8) |[下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_cctv_status.m3u8) |
| `cn_province.m3u8` | 37 | 卫视频道列表 | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_province.m3u8) | [下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_province.m3u8) |
| `cn_province_status.m3u8` | 37 | 卫视频道列表（含分辨率、流畅度） | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_province_status.m3u8) | [下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_province_status.m3u8) |
| `cn_pay.m3u8` | 45 | 付费频道列表 | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_pay.m3u8) |[下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_pay.m3u8) |
| `cn_pay_status.m3u8` | 45 | 付费频道列表（含分辨率、流畅度） | [下载](https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_pay_status.m3u8) |[下载](https://gh.bravetimes.cn/https://raw.githubusercontent.com/best-fan/iptv-sources/master/cn_pay_status.m3u8) |




### 📱 使用方式

1. **直接下载使用**：
   - 点击上方链接下载对应的 M3U8 文件
   - 在支持 M3U8 格式的播放器中打开文件

2. **在线播放**：
   - 使用支持网络播放的播放器
   - 输入文件原始链接地址

3. **推荐播放器**：
   - **VLC Media Player** - 跨平台支持
   - **PotPlayer** - Windows 平台
   - **IINA** - macOS 平台
   - **MX Player** - 移动端





## 🛠️ 本地校验与去重工具

`scripts/check_m3u8.py` 用于在本地校验 M3U8 直播源的有效性、按 URL 去重，每个频道只保留最优一条，并生成 CCTV 编号优先的完整列表 `cn_all_best.m3u8`。

### 常用命令

```bash
# 校验、去重、每频道择优，生成 cn_all_best.m3u8
python3 scripts/check_m3u8.py
```

### 择优规则

频道分组：`CCTV1`、`CCTV-1 (720p)`、`CCTV-2财经`、`CCTV-9 纪录` 等写法会归并到同一个 CCTV 频道，确保每个频道最终只有一条。

1. **分辨率**：默认高者优先；若指定 `--prefer-resolution N`（如 `720`），优先选该分辨率的源，没有时才按最高分辨率（加 `--probe` 时优先使用 ffprobe 实测值；否则读取同目录 `<输入文件>_status.m3u8` 中的 `[1080]/[720]/[576]` 标签，缺失时回退到频道名中的 `(1080p)` 等标注）
2. **流畅度**：`[S]` > 未知 > `[F]`
3. **响应速度**：以上相同时，本次实测响应最快的优先

### 主要参数

| 参数 | 说明 |
|------|------|
| `[input]` | 输入文件（默认仓库根目录 `cn_all.m3u8`） |
| `-o, --output` | 输出文件（默认 `<input>_best.m3u8`，即 `cn_all_best.m3u8`） |
| `--status FILE` | 指定分辨率标签来源，默认自动查找 `<input>_status.m3u8` |
| `--timeout` / `--workers` | 单链接超时（默认 10 秒）/ 并发数（默认 32） |
| `--report FILE` | 输出 CSV 检查报告（含无效、重复、非最佳条目与分辨率） |
| `--no-check` | 跳过联网检查，只做去重/择优 |
| `--probe` | 用 ffprobe 实测每个源的真实分辨率（需安装 ffmpeg，约 2 分钟并消耗流量；失败自动回退到 status 标签） |
| `--prefer-resolution N` | 优先选择分辨率为 N（如 720）的源，没有时再按最高分辨率择优 |

脚本默认流程：读取仓库根目录的 `cn_all.m3u8` → 有效性检查 → URL 去重 → 每频道择优 → CCTV 编号优先排序 → 写入 `cn_all_best.m3u8`；`auto_run.sh` 会同时处理 `ipv6.m3u` 并生成 `ipv6_best.m3u8`。运行结束会打印每个频道保留的链接、无效链接及原因。



## 🙏 数据源致谢

本项目的数据源部分数据于以下优秀的开源项目，感谢这些项目的贡献者：

- **mzky/checklist** - https://github.com/mzky/checklist
- **ssili126/tv** - https://github.com/ssili126/tv
- **hujingguang/ChinaIPTV** - https://github.com/hujingguang/ChinaIPTV
- **kaige-cai/live** - https://github.com/kaige-cai/live
- **BurningC4/Chinese-IPTV** - https://github.com/BurningC4/Chinese-IPTV
- **iptv-org/iptv** - https://iptv-org.github.io
- **ibert.me** - https://m3u.ibert.me

## ⚠️ 注意事项

<div align="center">

| 注意事项 | 图标 | 说明 |
|----------|------|------|
| **遵守条款** | 📜 | 请遵守相关网站的使用条款 |
| **定期更新** | 🔄 | 直播源可能会随时失效，需要定期更新 |
| **学习用途** | 🎓 | 仅供学习和研究使用 |
| **法律责任** | ⚖️ | 用户需自行承担使用责任 |

</div>

---

## ⭐ Star 趋势

<div align="center">

[![Star History Chart](https://api.star-history.com/svg?repos=best-fan/iptv-sources&type=Date)](https://star-history.com/#best-fan/iptv-sources&Date)

</div>

---
## 📄 许可证
本项目采用 **MIT** 许可证，仅供学习和研究使用。

---
<div align="center">

**🌟 如果这个项目对你有帮助，请给个 Star！**

</div>





