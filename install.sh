#!/usr/bin/env bash
# RGX 操盘系统 · 一键安装脚本（macOS / Linux）
# 用法： curl -fsSL https://raw.githubusercontent.com/tuoxiaoxiai-del/RGX/master/install.sh | bash
set -euo pipefail

REPO="tuoxiaoxiai-del/RGX"
BRANCH="master"

echo "RGX 操盘系统 一键安装"
echo "======================"

# 1) 定位 WorkBuddy skills 目录（支持环境变量覆盖）
detect_skills_dir() {
  if [ -n "${WORKBUDDY_SKILLS_DIR:-}" ]; then echo "$WORKBUDDY_SKILLS_DIR"; return; fi
  local candidates=(
    "$HOME/.workbuddy/skills"
    "$HOME/.config/workbuddy/skills"
    "$HOME/Library/Application Support/workbuddy/skills"
  )
  for d in "${candidates[@]}"; do
    if [ -d "$d" ]; then echo "$d"; return; fi
  done
  echo "${candidates[0]}"
}

SKILLS_DIR="$(detect_skills_dir)"
mkdir -p "$SKILLS_DIR"

# 2) 下载仓库到临时目录
TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "==> 下载 RGX ($REPO@$BRANCH) ..."
if command -v git >/dev/null 2>&1; then
  git clone --depth 1 --branch "$BRANCH" "https://github.com/$REPO.git" "$TMP/repo" >/dev/null 2>&1 \
    || git clone --branch "$BRANCH" "https://github.com/$REPO.git" "$TMP/repo"
else
  URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" | tar -xz -C "$TMP"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$URL" | tar -xz -C "$TMP"
  else
    echo "错误：需要 git 或 curl/wget，请先安装其一。" >&2; exit 1
  fi
  # 定位解压出的目录（兼容大小写）
  if [ -d "$TMP/RGX-$BRANCH" ]; then
    mv "$TMP/RGX-$BRANCH" "$TMP/repo"
  elif [ -d "$TMP/rgx-$BRANCH" ]; then
    mv "$TMP/rgx-$BRANCH" "$TMP/repo"
  else
    first="$(ls -d "$TMP"/*/ | head -1)"
    mv "$first" "$TMP/repo"
  fi
fi

# 3) 复制技能
SRC="$TMP/repo/skills"
if [ ! -d "$SRC" ]; then echo "错误：未找到 skills 目录。" >&2; exit 1; fi

count=0
for d in "$SRC"/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  cp -r "$d" "$SKILLS_DIR/$name"
  count=$((count+1))
done

echo "==> 完成：已将 $count 个 RGX 技能安装到 $SKILLS_DIR"
echo "==> 重启 WorkBuddy 后，输入「RGX」即可启动。"
