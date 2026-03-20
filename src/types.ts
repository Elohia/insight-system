/**
 * ContextEngine 接口定义
 * 基于 OpenClaw ContextEngine 规范
 */

/**
 * Token 预算
 */
export interface TokenBudget {
  soft: number;   // 软上限
  hard: number;   // 硬上限
}

/**
 * 消息
 */
export interface Message {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  timestamp?: number;
  metadata?: Record<string, any>;
}

/**
 * 组装后的上下文
 */
export interface AssembledContext {
  system?: string;
  messages: Message[];
  tokenEstimate: number;
}

/**
 * Turn（一轮对话）
 */
export interface Turn {
  userMessage: Message;
  assistantMessage: Message;
  toolCalls?: any[];
}

/**
 * 子 agent 上下文
 */
export interface SubagentContext {
  messages: Message[];
  metadata?: Record<string, any>;
}

/**
 * 子 agent 结果
 */
export interface SubagentResult {
  success: boolean;
  output: string;
  metadata?: Record<string, any>;
}

/**
 * ContextEngine 接口
 * 七个钩子，管住上下文的一生
 */
export interface ContextEngine {
  /**
   * 1. bootstrap() - 引擎初始化
   */
  bootstrap(): Promise<void>;

  /**
   * 2. ingest(message) - 消息摄入
   */
  ingest(message: Message): Promise<void>;

  /**
   * 3. assemble(budget) - 组装上下文（核心）
   */
  assemble(budget: TokenBudget): Promise<AssembledContext>;

  /**
   * 4. compact() - 压缩上下文
   */
  compact(): Promise<void>;

  /**
   * 5. afterTurn(turn) - 对话结束
   */
  afterTurn(turn: Turn): Promise<void>;

  /**
   * 6. prepareSubagentSpawn(parentContext) - 子 agent 准备
   */
  prepareSubagentSpawn(parentContext: any): Promise<SubagentContext>;

  /**
   * 7. onSubagentEnded(result) - 子 agent 结束
   */
  onSubagentEnded(result: SubagentResult): Promise<void>;
}

/**
 * 插件 API
 */
export interface PluginAPI {
  registerContextEngine(id: string, factory: (config: any) => ContextEngine): void;
}
