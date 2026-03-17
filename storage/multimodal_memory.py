#!/usr/bin/env python3
"""
多模态记忆系统 v1.0
支持文本、图片、视频的向量化和跨模态检索
基于阿里云百炼多模态向量模型
"""

import os
import json
import hashlib
import time
from datetime import datetime
import sys
from pathlib import Path

# 导入配置加载器
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))
from utils.config_loader import get_config, get_workspace, get_memory_dir

# 获取配置
_config = get_config()
WORKSPACE = str(_config.workspace)
MEMORY_DIR = str(_config.memory_dir)
from pathlib import Path

# 阿里云百炼
import os
import json
import hashlib
import time
from datetime import datetime
import sys
from pathlib import Path

# 导入配置加载器
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir.parent))
from utils.config_loader import get_config, get_workspace, get_memory_dir

# 获取配置
_config = get_config()
WORKSPACE = str(_config.workspace)
MEMORY_DIR = str(_config.memory_dir)
from pathlib import Path

import dashscope
from dashscope import MultiModalEmbedding

# 配置
VECTOR_DB = str(_config.vector_db)
CONFIG = {
    "model": "qwen3-vl-embedding",  # 支持融合+独立向量
    "dimension": 1024,  # 向量维度
    "free_limit": 1_000_000,  # 100万Token免费额度
}

# 设置 API Key（仅从环境变量读取，不硬编码）
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', '')


class MultimodalMemory:
    def __init__(self):
        self.db = self.load_db()
        self.usage = {"text": 0, "image": 0, "video": 0, "fusion": 0}
    
    def load_db(self):
        """加载向量数据库"""
        if os.path.exists(VECTOR_DB):
            with open(VECTOR_DB, 'r') as f:
                return json.load(f)
        return {
            "vectors": [],  # [{id, type, content, vector, metadata, timestamp}]
            "connections": [],  # 向量之间的关联
            "stats": {"total": 0, "text": 0, "image": 0, "video": 0}
        }
    
    def save_db(self):
        """保存向量数据库"""
        os.makedirs(os.path.dirname(VECTOR_DB), exist_ok=True)
        with open(VECTOR_DB, 'w') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)
    
    def generate_id(self, content):
        """生成唯一ID（仅基于内容，保证相同内容生成相同ID）"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def exists(self, content):
        """检查内容是否已存在（去重检查）"""
        content_hash = self.generate_id(content)
        for v in self.db["vectors"]:
            if v.get("id") == content_hash:
                return True
        return False
    
    def exists_by_content(self, content):
        """通过内容文本检查是否存在（更宽松的去重）"""
        content_normalized = content.strip()[:200]  # 取前200字符比较
        for v in self.db["vectors"]:
            existing = v.get("content", "").strip()[:200]
            if existing == content_normalized:
                return True
        return False
    
    def embed_text(self, text):
        """生成文本向量"""
        # 空文本检查
        if not text or not text.strip():
            print("⚠️ 文本为空，跳过向量化")
            return None
        
        # 最小长度检查
        if len(text.strip()) < 2:
            print(f"⚠️ 文本过短，跳过: {text[:20]}...")
            return None
        
        resp = MultiModalEmbedding.call(
            model=CONFIG["model"],
            input=[{'text': text.strip()}],
            parameters={'dimension': CONFIG["dimension"]}
        )
        if resp.status_code == 200:
            self.usage["text"] += 1
            return resp.output['embeddings'][0]['embedding']
        else:
            print(f"❌ 文本向量生成失败: {resp.message}")
            return None
    
    def embed_image(self, image_url):
        """生成图片向量"""
        resp = MultiModalEmbedding.call(
            model=CONFIG["model"],
            input=[{'image': image_url}]
        )
        if resp.status_code == 200:
            self.usage["image"] += 1
            return resp.output['embeddings'][0]['embedding']
        else:
            print(f"❌ 图片向量生成失败: {resp.message}")
            return None
    
    def embed_video(self, video_url):
        """生成视频向量"""
        resp = MultiModalEmbedding.call(
            model=CONFIG["model"],
            input=[{'video': video_url}]
        )
        if resp.status_code == 200:
            self.usage["video"] += 1
            return resp.output['embeddings'][0]['embedding']
        else:
            print(f"❌ 视频向量生成失败: {resp.message}")
            return None
    
    def embed_fusion(self, text, image_url=None, video_url=None):
        """生成融合向量（文本+图片+视频）"""
        content = {}
        if text:
            content['text'] = text
        if image_url:
            content['image'] = image_url
        if video_url:
            content['video'] = video_url
        
        if not content:
            return None
        
        resp = MultiModalEmbedding.call(
            model=CONFIG["model"],
            input=[content],
            parameters={'dimension': CONFIG["dimension"], 'output_type': 'dense'}
        )
        if resp.status_code == 200:
            self.usage["fusion"] += 1
            return resp.output['embeddings'][0]['embedding']
        else:
            print(f"❌ 融合向量生成失败: {resp.message}")
            return None
    
    def add_text(self, content, metadata=None, skip_dedup=False):
        """添加文本记忆（带去重和空内容检查）"""
        # 空内容检查
        if not content or not content.strip():
            print("⚠️ 内容为空，跳过添加")
            return None
        
        # 最小长度检查
        if len(content.strip()) < 2:
            print(f"⚠️ 内容过短，跳过: {content[:20]}...")
            return None
        
        # 去重检查
        if not skip_dedup and self.exists_by_content(content):
            print(f"⚠️ 内容已存在，跳过: {content[:50]}...")
            return None
        
        vector = self.embed_text(content)
        if not vector:
            return None
        
        record = {
            "id": self.generate_id(content),
            "type": "text",
            "content": content,
            "vector": vector,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.db["vectors"].append(record)
        self.db["stats"]["total"] += 1
        self.db["stats"]["text"] += 1
        self.save_db()
        
        print(f"✅ 添加文本记忆: {content[:50]}...")
        return record["id"]
    
    def add_image(self, image_url, description=None, metadata=None, skip_dedup=False):
        """添加图片记忆（带去重）"""
        # 去重检查（基于URL）
        if not skip_dedup:
            content_hash = self.generate_id(image_url)
            for v in self.db["vectors"]:
                if v.get("id") == content_hash:
                    print(f"⚠️ 图片已存在，跳过: {image_url[:50]}...")
                    return None
        
        vector = self.embed_image(image_url)
        if not vector:
            return None
        
        record = {
            "id": self.generate_id(image_url),
            "type": "image",
            "content": description or "",
            "url": image_url,
            "vector": vector,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.db["vectors"].append(record)
        self.db["stats"]["total"] += 1
        self.db["stats"]["image"] += 1
        self.save_db()
        
        print(f"✅ 添加图片记忆: {image_url[:50]}...")
        return record["id"]
    
    def add_fusion(self, text, image_url=None, video_url=None, metadata=None, skip_dedup=False):
        """添加融合记忆（带去重）"""
        content_parts = []
        if text:
            content_parts.append(text[:100])
        if image_url:
            content_parts.append("[图片]")
        if video_url:
            content_parts.append("[视频]")
        
        # 去重检查
        if not skip_dedup and text and self.exists_by_content(text):
            print(f"⚠️ 融合内容已存在，跳过: {text[:50]}...")
            return None
        
        vector = self.embed_fusion(text, image_url, video_url)
        if not vector:
            return None
        
        record = {
            "id": self.generate_id("".join(content_parts)),
            "type": "fusion",
            "content": " | ".join(content_parts),
            "text": text,
            "image_url": image_url,
            "video_url": video_url,
            "vector": vector,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.db["vectors"].append(record)
        self.db["stats"]["total"] += 1
        self.save_db()
        
        print(f"✅ 添加融合记忆: {record['content'][:50]}...")
        return record["id"]
    
    def cosine_similarity(self, a, b):
        """计算余弦相似度"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if (norm_a * norm_b) > 0 else 0
    
    def search(self, query, top_k=5, search_type="text"):
        """跨模态检索"""
        # 生成查询向量
        if search_type == "text":
            query_vector = self.embed_text(query)
        elif search_type == "image":
            query_vector = self.embed_image(query)
        else:
            query_vector = self.embed_text(query)
        
        if not query_vector:
            return []
        
        # 计算相似度
        results = []
        for record in self.db["vectors"]:
            if search_type == "text" and record["type"] not in ["text", "fusion"]:
                continue
            if search_type == "image" and record["type"] not in ["image", "fusion"]:
                continue
            
            similarity = self.cosine_similarity(query_vector, record["vector"])
            results.append({
                "id": record["id"],
                "type": record["type"],
                "content": record["content"],
                "url": record.get("url"),
                "similarity": similarity,
                "timestamp": record["timestamp"]
            })
        
        # 排序返回top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "total_memories": self.db["stats"]["total"],
            "text_memories": self.db["stats"]["text"],
            "image_memories": self.db["stats"]["image"],
            "video_memories": self.db["stats"]["video"],
            "usage": self.usage
        }


def main():
    print("🧠 多模态记忆系统 v1.0")
    print("=" * 40)
    
    memory = MultimodalMemory()
    
    # 测试：添加文本记忆
    print("\n📝 测试添加文本记忆...")
    memory.add_text(
        "我是欧皇，幻世麾下的监督者 AI，擅长洞见生成和系统优化",
        {"source": "test", "author": "欧皇"}
    )
    
    # 测试：添加图片记忆
    print("\n🖼️ 测试添加图片记忆...")
    memory.add_image(
        "https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png",
        "一张可爱的小猫图片",
        {"source": "test"}
    )
    
    # 测试：跨模态检索
    print("\n🔍 测试跨模态检索...")
    results = memory.search("AI Agent", top_k=3)
    print(f"搜索 'AI Agent' 找到 {len(results)} 条结果:")
    for r in results:
        print(f"  - [{r['type']}] {r['content'][:50]}... (相似度: {r['similarity']:.3f})")
    
    # 统计
    stats = memory.get_stats()
    print("\n📊 统计信息:")
    print(f"  总记忆数: {stats['total_memories']}")
    print(f"  文本记忆: {stats['text_memories']}")
    print(f"  图片记忆: {stats['image_memories']}")
    print(f"  API调用: {stats['usage']}")
    
    print("\n✅ 多模态记忆系统测试完成!")


if __name__ == "__main__":
    main()
