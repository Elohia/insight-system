/**
 * 涟漪意识流 ContextEngine
 * 
 * 三层记忆架构：
 * - 模糊层：启动加载，极简概要 (~250 tokens)
 * - 精确层：按需检索，相关详情
 * - 深度层：完整数据，深度分析
 */

import { execSync } from 'child_process';
import { join } from 'path';
import {
  ContextEngine,
  TokenBudget,
  Message,
  AssembledContext,
  Turn,
  SubagentContext,
  SubagentResult
} from './types';

/**
 * RippleContextEngine 配置
 */
export interface RippleContextEngineConfig {
  enabled: boolean;
  fuzzyLayerTokens: number;
  maxRipplesInContext: number;
  temperatureRange: {
    min: number;
    max: number;
  };
  enableAutoCollect: boolean;
  autoCollectMinTemp: number;
  resonanceThreshold: number;
  insightSystemPath: string;
}

/**
 * 涟漪数据
 */
interface Ripple {
  id: string;
  content: string;
  temperature: number;
  tags: string[];
  timestamp: string;
}

/**
 * 水面状态
 */
interface SurfaceState {
  surface_state: string;
  ripple_count: number;
  avg_temperature: number;
  hot_tags: string[];
}

/**
 * 涟漪意识流 ContextEngine
 * 
 * 实现 OpenClaw ContextEngine 接口
 * 将涟漪意识流系统集成到上下文管理
 */
export class RippleContextEngine implements ContextEngine {
  private config: RippleContextEngineConfig;
  private messages: Message[] = [];
  private ripples: Ripple[] = [];
  private surfaceState: SurfaceState | null = null;
  private initialized = false;

  constructor(config: Partial<RippleContextEngineConfig> = {}) {
    this.config = {
      enabled: true,
      fuzzyLayerTokens: 300,
      maxRipplesInContext: 5,
      temperatureRange: { min: 0, max: 100 },
      enableAutoCollect: true,
      autoCollectMinTemp: 60,
      resonanceThreshold: 15,
      insightSystemPath: process.env.INSIGHT_SYSTEM_PATH || '/workspace/projects/extensions/insight-system',
      ...config
    };
  }

  /**
   * 1. bootstrap() - 引擎初始化
   */
  async bootstrap(): Promise<void> {
    if (this.initialized) return;

    try {
      // 加载涟漪数据
      await this.loadRipples();
      
      // 获取水面状态
      await this.loadSurfaceState();

      this.initialized = true;
      console.log('🌊 RippleContextEngine initialized');
    } catch (error) {
      console.error('Failed to initialize RippleContextEngine:', error);
      // 初始化失败时使用空状态
      this.initialized = true;
    }
  }

  /**
   * 2. ingest(message) - 消息摄入
   */
  async ingest(message: Message): Promise<void> {
    this.messages.push({
      ...message,
      timestamp: message.timestamp || Date.now()
    });
  }

  /**
   * 3. assemble(budget) - 组装上下文（核心）
   */
  async assemble(budget: TokenBudget): Promise<AssembledContext> {
    // 获取模糊层内容
    const fuzzyLayer = await this.getFuzzyLayer();
    
    // 计算可用于历史消息的 token 预算
    const fuzzyTokens = this.estimateTokens(fuzzyLayer);
    const historyBudget = budget.soft - fuzzyTokens - 100; // 预留 100 tokens 给系统提示

    // 选择最近的消息
    const recentMessages = this.selectRecentMessages(historyBudget);

    // 组装上下文
    const messages: Message[] = [];

    // 添加模糊层作为系统提示的一部分
    if (fuzzyLayer) {
      messages.push({
        role: 'system',
        content: fuzzyLayer,
        metadata: { type: 'fuzzy-layer' }
      });
    }

    // 添加历史消息
    messages.push(...recentMessages);

    return {
      system: fuzzyLayer,
      messages,
      tokenEstimate: this.estimateTokens(fuzzyLayer) + this.estimateMessages(recentMessages)
    };
  }

  /**
   * 4. compact() - 压缩上下文
   */
  async compact(): Promise<void> {
    // 保留最近的消息
    const keepCount = Math.floor(this.messages.length * 0.3);
    this.messages = this.messages.slice(-keepCount);

    // 如果开启了自动收集，将旧消息转化为涟漪
    if (this.config.enableAutoCollect) {
      for (const msg of this.messages.slice(0, -keepCount)) {
        if (msg.role === 'user' || msg.role === 'assistant') {
          await this.tryAddRipple(msg.content);
        }
      }
    }
  }

  /**
   * 5. afterTurn(turn) - 对话结束
   */
  async afterTurn(turn: Turn): Promise<void> {
    // 自动收集高价值对话
    if (this.config.enableAutoCollect) {
      const userContent = turn.userMessage.content;
      const assistantContent = turn.assistantMessage.content;
      
      // 判断是否值得添加为涟漪
      const combinedContent = `${userContent}\n${assistantContent}`;
      const temperature = this.estimateTemperature(combinedContent);
      
      if (temperature >= this.config.autoCollectMinTemp) {
        await this.addRipple(assistantContent, temperature);
      }
    }

    // 更新水面状态
    await this.loadSurfaceState();
  }

  /**
   * 6. prepareSubagentSpawn(parentContext) - 子 agent 准备
   */
  async prepareSubagentSpawn(parentContext: any): Promise<SubagentContext> {
    // 精确检索相关涟漪
    const relevantRipples = await this.searchRipples(parentContext.query || '', 3);
    
    // 只给子 agent 相关信息，不全部给
    return {
      messages: relevantRipples.map(r => ({
        role: 'system' as const,
        content: `[涟漪 ${r.temperature}°] ${r.content}`,
        metadata: { type: 'ripple', id: r.id }
      })),
      metadata: { parentRipples: relevantRipples.map(r => r.id) }
    };
  }

  /**
   * 7. onSubagentEnded(result) - 子 agent 结束
   */
  async onSubagentEnded(result: SubagentResult): Promise<void> {
    if (result.success && this.config.enableAutoCollect) {
      // 将子 agent 的重要结果添加为涟漪
      const temperature = this.estimateTemperature(result.output);
      if (temperature >= this.config.autoCollectMinTemp) {
        await this.addRipple(result.output, temperature);
      }
    }
  }

  // ============ 私有方法 ============

  /**
   * 获取模糊层内容
   */
  private async getFuzzyLayer(): Promise<string> {
    try {
      const result = execSync(
        `cd "${this.config.insightSystemPath}" && ./run.sh fuzzy --json 2>/dev/null || ./run.sh fuzzy 2>/dev/null`,
        { encoding: 'utf-8', timeout: 5000 }
      );
      
      // 提取模糊层内容
      const lines = result.split('\n');
      const startIndex = lines.findIndex(l => l.includes('水面状态'));
      if (startIndex >= 0) {
        return lines.slice(startIndex).join('\n');
      }
      
      return result;
    } catch (error) {
      // 返回简化的状态
      if (this.surfaceState) {
        return this.formatFuzzyLayer();
      }
      return '';
    }
  }

  /**
   * 格式化模糊层
   */
  private formatFuzzyLayer(): string {
    if (!this.surfaceState) return '';
    
    const lines = [
      '# 🌊 水面状态',
      `状态: ${this.surfaceState.surface_state} | 温度: ${this.surfaceState.avg_temperature}° | 涟漪: ${this.surfaceState.ripple_count}`,
      '',
      `标签: ${this.surfaceState.hot_tags.join(', ')}`,
      '',
      '## 最近涟漪'
    ];

    const recentRipples = this.ripples.slice(-5).reverse();
    for (const r of recentRipples) {
      const tags = r.tags.slice(0, 2).map(t => `#${t}`).join(' ');
      const content = r.content.length > 40 ? r.content.slice(0, 40) + '...' : r.content;
      lines.push(`[${r.temperature}°] ${content} ${tags}`);
    }

    return lines.join('\n');
  }

  /**
   * 加载涟漪数据
   */
  private async loadRipples(): Promise<void> {
    try {
      const result = execSync(
        `cd "${this.config.insightSystemPath}" && ./run.sh export 2>/dev/null`,
        { encoding: 'utf-8', timeout: 5000 }
      );
      
      // 解析 TOON 格式
      this.ripples = this.parseToonRipples(result);
    } catch (error) {
      this.ripples = [];
    }
  }

  /**
   * 解析 TOON 格式的涟漪
   */
  private parseToonRipples(toonContent: string): Ripple[] {
    const ripples: Ripple[] = [];
    const lines = toonContent.split('\n');
    
    let inRipples = false;
    for (const line of lines) {
      if (line.startsWith('ripples[')) {
        inRipples = true;
        continue;
      }
      if (line.startsWith('resonances[') || line.startsWith('#') || !line.trim()) {
        inRipples = false;
        continue;
      }
      if (inRipples && line.startsWith(' ')) {
        const parts = line.trim().split(',');
        if (parts.length >= 5) {
          ripples.push({
            id: parts[0],
            temperature: parseInt(parts[1]) || 50,
            timestamp: parts[2],
            tags: parts[3] ? parts[3].split('|') : [],
            content: parts.slice(4).join(',')
          });
        }
      }
    }
    
    return ripples;
  }

  /**
   * 加载水面状态
   */
  private async loadSurfaceState(): Promise<void> {
    try {
      const result = execSync(
        `cd "${this.config.insightSystemPath}" && ./run.sh surface --json 2>/dev/null || ./run.sh surface 2>/dev/null`,
        { encoding: 'utf-8', timeout: 5000 }
      );
      
      // 解析水面状态
      this.surfaceState = this.parseSurfaceState(result);
    } catch (error) {
      this.surfaceState = {
        surface_state: '平静',
        ripple_count: this.ripples.length,
        avg_temperature: 50,
        hot_tags: []
      };
    }
  }

  /**
   * 解析水面状态
   */
  private parseSurfaceState(output: string): SurfaceState {
    const lines = output.split('\n');
    let state = '平静';
    let rippleCount = 0;
    let avgTemp = 50;
    const tags: string[] = [];

    for (const line of lines) {
      if (line.includes('状态:')) {
        state = line.includes('活跃') ? '活跃' : line.includes('沸腾') ? '沸腾' : '平静';
      }
      if (line.includes('涟漪:') || line.includes('涟漪数:')) {
        const match = line.match(/(\d+)/);
        if (match) rippleCount = parseInt(match[1]);
      }
      if (line.includes('温度:')) {
        const match = line.match(/(\d+\.?\d*)/);
        if (match) avgTemp = parseFloat(match[1]);
      }
      if (line.includes('标签:')) {
        const tagStr = line.split('标签:')[1]?.trim();
        if (tagStr) {
          tags.push(...tagStr.split(',').map(t => t.trim()).filter(Boolean));
        }
      }
    }

    return {
      surface_state: state,
      ripple_count: rippleCount,
      avg_temperature: avgTemp,
      hot_tags: tags
    };
  }

  /**
   * 搜索涟漪
   */
  private async searchRipples(query: string, maxResults: number): Promise<Ripple[]> {
    if (!query) return this.ripples.slice(-maxResults);

    const queryLower = query.toLowerCase();
    const results: Array<[number, Ripple]> = [];

    for (const ripple of this.ripples) {
      let score = 0;
      
      // 内容匹配
      if (ripple.content.toLowerCase().includes(queryLower)) {
        score += 10;
      }
      
      // 标签匹配
      if (ripple.tags.some(t => t.toLowerCase().includes(queryLower))) {
        score += 5;
      }
      
      // 温度权重
      score += ripple.temperature / 20;

      if (score > 0) {
        results.push([score, ripple]);
      }
    }

    results.sort((a, b) => b[0] - a[0]);
    return results.slice(0, maxResults).map(([_, r]) => r);
  }

  /**
   * 添加涟漪
   */
  private async addRipple(content: string, temperature: number, tags: string[] = []): Promise<void> {
    try {
      const tagStr = tags.length > 0 ? `--tags ${tags.join(',')}` : '';
      execSync(
        `cd "${this.config.insightSystemPath}" && ./run.sh ripple "${content.replace(/"/g, '\\"')}" --temp ${temperature} ${tagStr} 2>/dev/null`,
        { encoding: 'utf-8', timeout: 5000 }
      );
      
      // 更新本地缓存
      this.ripples.push({
        id: `r${Date.now()}`,
        content,
        temperature,
        tags,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to add ripple:', error);
    }
  }

  /**
   * 尝试添加涟漪
   */
  private async tryAddRipple(content: string): Promise<void> {
    const temperature = this.estimateTemperature(content);
    if (temperature >= this.config.autoCollectMinTemp) {
      await this.addRipple(content, temperature);
    }
  }

  /**
   * 估算水温
   */
  private estimateTemperature(content: string): number {
    // 基于内容特征估算水温
    let temp = 50;

    // 包含关键词
    const hotKeywords = ['洞见', '发现', '创新', '突破', '关键', '重要', '核心'];
    const coolKeywords = ['细节', '技术', '实现', '代码', '配置'];

    for (const kw of hotKeywords) {
      if (content.includes(kw)) temp += 10;
    }
    for (const kw of coolKeywords) {
      if (content.includes(kw)) temp -= 5;
    }

    // 内容长度
    if (content.length > 200) temp += 5;
    if (content.length > 500) temp += 5;

    return Math.min(100, Math.max(0, temp));
  }

  /**
   * 选择最近的消息
   */
  private selectRecentMessages(budget: number): Message[] {
    const result: Message[] = [];
    let totalTokens = 0;

    // 从最近的开始添加
    for (let i = this.messages.length - 1; i >= 0; i--) {
      const msg = this.messages[i];
      const tokens = this.estimateTokens(msg.content);

      if (totalTokens + tokens > budget) break;

      result.unshift(msg);
      totalTokens += tokens;
    }

    return result;
  }

  /**
   * 估算 token 数
   */
  private estimateTokens(text: string): number {
    // 简单估算：中文约 1.7 字符/token，英文约 4 字符/token
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    const otherChars = text.length - chineseChars;
    return Math.ceil(chineseChars / 1.7 + otherChars / 4);
  }

  /**
   * 估算消息列表的 token 数
   */
  private estimateMessages(messages: Message[]): number {
    return messages.reduce((sum, msg) => sum + this.estimateTokens(msg.content), 0);
  }
}

// 导出工厂函数
export default function (api: { registerContextEngine: (id: string, factory: (config: any) => ContextEngine) => void }) {
  api.registerContextEngine('insight-system', (config: Partial<RippleContextEngineConfig>) => {
    return new RippleContextEngine(config);
  });
}
