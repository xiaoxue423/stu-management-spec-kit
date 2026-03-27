#!/usr/bin/env bash

set -e

# 解析命令行参数
JSON_MODE=false
ARGS=()

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --help|-h)
            echo "Usage: $0 [--json]"
            echo "  --json    Output results in JSON format"
            echo "  --help    Show this help message"
            echo ""
            echo "Description: Deletes all markdown files in FEATURE_DIR/temp/ directory"
            exit 0
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
done

# 获取脚本目录并加载公共函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# 从公共函数获取所有路径和变量
eval $(get_feature_paths)

# 检查是否在正确的特性分支上（仅适用于 git 仓库）
check_feature_branch "$CURRENT_BRANCH" "$HAS_GIT" || exit 1

# 定义临时目录路径
TEMP_DIR="$FEATURE_DIR/temp"

# 检查临时目录是否存在
if [[ ! -d "$TEMP_DIR" ]]; then
    if $JSON_MODE; then
        printf '{"success":false,"message":"临时目录不存在: %s","deleted_files":[]}\n' "$TEMP_DIR"
    else
        echo "Warning: 临时目录不存在: $TEMP_DIR"
        echo "无需删除。"
    fi
    exit 0
fi

# 首先收集所有 markdown 文件列表（用于报告）
DELETED_FILES=()
COUNT=0

while IFS= read -r -d '' file; do
    if [[ -f "$file" ]]; then
        relative_path="${file#$TEMP_DIR/}"
        DELETED_FILES+=("$relative_path")
        COUNT=$((COUNT + 1))
        if ! $JSON_MODE; then
            echo "  ✓ 将删除: $relative_path"
        fi
    fi
done < <(find "$TEMP_DIR" -type f -name "*.md" -print0)

# 直接删除整个临时目录
if ! $JSON_MODE; then
    echo "  ✓ 删除目录: temp/"
fi
rm -rf "$TEMP_DIR"
TEMP_DIR_DELETED=true

# 输出结果
if $JSON_MODE; then
    # 构建已删除文件的 JSON 数组
    FILES_JSON="["
    for i in "${!DELETED_FILES[@]}"; do
        if [[ $i -gt 0 ]]; then
            FILES_JSON+=","
        fi
        FILES_JSON+="\"${DELETED_FILES[$i]}\""
    done
    FILES_JSON+="]"

    printf '{"success":true,"message":"已删除 %d 个 markdown 文件和临时目录","deleted_files":%s,"temp_dir_deleted":%s}\n' \
        "$COUNT" "$FILES_JSON" "$TEMP_DIR_DELETED"
else
    echo ""
    echo "汇总:"
    echo "  已删除文件数: $COUNT"
    echo "  临时目录已删除: temp/"
fi

