#!/bin/bash
# 涟漪意识流命令行工具

cd "$(dirname "$0")"

case "$1" in
  ripple)
    shift
    python3 -c "
from core.three_layer_memory import ThreeLayerMemory
from core.ripple import Ripple
import sys

mem = ThreeLayerMemory('.')

content = sys.argv[1] if len(sys.argv) > 1 else 'test'
temp = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0
tags = sys.argv[5].split(',') if len(sys.argv) > 5 else []

r = Ripple(content=content, temp=temp, tags=tags)
mem.ripples.append(r)
mem.save()
print(f'✓ 涟漪已记录: [{temp:.0f}] {content[:30]}...')
" "$@" 2>/dev/null
    ;;
  
  fuzzy)
    python3 -c "
from core.three_layer_memory import ThreeLayerMemory
mem = ThreeLayerMemory('.')
print(mem.get_fuzzy_layer())
" 2>/dev/null
    ;;
  
  precise)
    shift
    python3 -c "
from core.three_layer_memory import ThreeLayerMemory
import sys

mem = ThreeLayerMemory('.')
keyword = sys.argv[1] if len(sys.argv) > 1 else ''
results = mem.query_precise(keyword=keyword, limit=5)
for r in results:
    print(f'[{r.temp:.0f}] {r.content[:60]}...')
" "$@" 2>/dev/null
    ;;
  
  status)
    python3 -c "
from core.three_layer_memory import ThreeLayerMemory
mem = ThreeLayerMemory('.')
print(f'涟漪数: {len(mem.ripples)}')
print(f'潜意识数: {len(mem.subconscious)}')
print(f'标签数: {len(mem.tag_index)}')
" 2>/dev/null
    ;;
  
  deep)
    python3 -c "
from core.three_layer_memory import ThreeLayerMemory
mem = ThreeLayerMemory('.')
print(mem.export_deep_layer())
" 2>/dev/null
    ;;
  
  *)
    echo "涟漪意识流 ContextEngine"
    echo ""
    echo "用法: $0 <命令> [参数]"
    echo ""
    echo "命令:"
    echo "  ripple <内容> --temp <温度> --tags <标签>  添加涟漪"
    echo "  fuzzy                                       查看模糊层"
    echo "  precise <关键词>                            精确检索"
    echo "  deep                                        深度层导出"
    echo "  status                                      系统状态"
    ;;
esac
