#!/bin/bash
# WeCard - 快速添加Lottie动画到图标库
# 用法: ./add-lottie-animation.sh <动画文件.json> <动画名称> <类别>

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/opt/qwcard"
ANIMATIONS_DIR="$PROJECT_ROOT/public/assets/animations"
ICON_LIBRARY="$PROJECT_ROOT/config/icon-library.js"

# 显示帮助
show_help() {
    echo "用法: $0 <动画文件.json> <动画名称> <类别> [子目录]"
    echo ""
    echo "参数："
    echo "  动画文件     要添加的Lottie JSON文件路径"
    echo "  动画名称     动画的中文名称（如：'点赞动画'）"
    echo "  类别         动画类别（contact/action/business/interaction等）"
    echo "  子目录       可选，动画存放的子目录（默认：interaction）"
    echo ""
    echo "示例："
    echo "  $0 like.json 点赞动画 interaction"
    echo "  $0 /tmp/star.json 星星闪烁 business stars"
    echo ""
    echo "可用类别："
    echo "  - contact: 联系相关"
    echo "  - action: 操作动作"
    echo "  - business: 商业相关"
    echo "  - interaction: 交互动画"
    echo "  - status: 状态指示"
    exit 1
}

# 检查参数
if [ $# -lt 3 ]; then
    show_help
fi

ANIM_FILE="$1"
ANIM_NAME="$2"
CATEGORY="$3"
SUBDIR="${4:-interaction}"

# 检查动画文件是否存在
if [ ! -f "$ANIM_FILE" ]; then
    echo -e "${RED}错误: 动画文件不存在: $ANIM_FILE${NC}"
    exit 1
fi

# 生成key（文件名转为kebab-case）
FILENAME=$(basename "$ANIM_FILE")
ANIM_KEY=$(echo "${FILENAME%.*}" | tr '[:upper:]' '[:lower:]' | tr '_' '-')

# 创建目标目录
TARGET_DIR="$ANIMATIONS_DIR/$SUBDIR"
mkdir -p "$TARGET_DIR"

# 复制动画文件
TARGET_FILE="$TARGET_DIR/$FILENAME"
echo -e "${YELLOW}复制动画文件...${NC}"
cp "$ANIM_FILE" "$TARGET_FILE"
echo -e "${GREEN}✓ 已复制到: $TARGET_FILE${NC}"

# 更新icon-library.js
echo -e "${YELLOW}更新图标库配置...${NC}"

# 查找LOTTIE_ANIMATIONS数组的插入位置（在数组结束前）
NEW_ENTRY="  {
    key: '$ANIM_KEY',
    name: '$ANIM_NAME',
    path: '$SUBDIR/$FILENAME',
    category: '$CATEGORY',
    preview: '/assets/animations/$SUBDIR/$FILENAME'
  },"

# 使用sed在最后一个}]之前插入（临时方案）
# 更安全的做法是手动添加或使用Node.js脚本
echo ""
echo -e "${GREEN}✓ 动画已添加！${NC}"
echo ""
echo "请手动将以下配置添加到 $ICON_LIBRARY 的 LOTTIE_ANIMATIONS 数组中："
echo ""
echo -e "${YELLOW}$NEW_ENTRY${NC}"
echo ""
echo "位置示例："
echo "export const LOTTIE_ANIMATIONS = ["
echo "  // ... 现有动画"
echo "$NEW_ENTRY"
echo "]"
echo ""
echo "然后运行以下命令重启前端："
echo "  systemctl restart wecard-nuxt.service"

