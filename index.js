/**
 * 涟漪意识流 ContextEngine
 * 三层记忆架构：模糊层 + 精确层 + 深度层
 */

const { execSync } = require('child_process');

class RippleContextEngine {
  constructor(config = {}) {
    this.config = {
      fuzzyLayerTokens: 300,
      autoCollectMinTemp: 60,
      insightPath: process.env.INSIGHT_SYSTEM_PATH || '/workspace/projects/extensions/insight-system',
      // 控制是否在会话启动时加载模糊层
      autoLoadFuzzy: process.env.AUTO_LOAD_FUZZY !== 'false',
      // 控制是否自动收集对话
      autoCollect: process.env.AUTO_COLLECT !== 'false',
      ...config
    };
    this.messages = [];
    this.initialized = false;
  }

  async bootstrap() {
    this.initialized = true;
    if (this.config.autoLoadFuzzy) {
      console.log('🌊 RippleContextEngine initialized with fuzzy layer');
    } else {
      console.log('🌊 RippleContextEngine initialized (fuzzy layer disabled)');
    }
  }

  async ingest(message) {
    this.messages.push({ ...message, timestamp: Date.now() });
  }

  async assemble(budget) {
    // 只有开启 autoLoadFuzzy 时才加载模糊层
    let fuzzy = '';
    if (this.config.autoLoadFuzzy) {
      fuzzy = this.getFuzzyLayer();
    }
    
    const history = this.messages.slice(-20).slice(0, Math.floor(budget.soft / 100));
    
    return {
      system: fuzzy,
      messages: history,
      tokenEstimate: this.countTokens(fuzzy) + history.length * 50
    };
  }

  async compact() {
    const keep = Math.floor(this.messages.length * 0.3);
    this.messages = this.messages.slice(-keep);
  }

  async afterTurn(turn) {
    // 只有开启 autoCollect 时才自动收集
    if (!this.config.autoCollect) return;
    
    if (turn.assistantMessage?.content) {
      const temp = this.estimateTemp(turn.assistantMessage.content);
      if (temp >= this.config.autoCollectMinTemp) {
        this.addRipple(turn.assistantMessage.content, temp);
      }
    }
  }

  async prepareSubagentSpawn(parentContext) {
    return { messages: this.messages.slice(-5), metadata: {} };
  }

  async onSubagentEnded(result) {
    if (!this.config.autoCollect) return;
    
    if (result.success) {
      const temp = this.estimateTemp(result.output);
      if (temp >= this.config.autoCollectMinTemp) {
        this.addRipple(result.output, temp);
      }
    }
  }

  getFuzzyLayer() {
    try {
      return execSync(`cd "${this.config.insightPath}" && ./run.sh fuzzy 2>/dev/null`, {
        encoding: 'utf-8',
        timeout: 5000
      });
    } catch {
      return '';
    }
  }

  addRipple(content, temp) {
    try {
      execSync(`cd "${this.config.insightPath}" && ./run.sh ripple "${content.slice(0, 100).replace(/"/g, '\\"')}" --temp ${temp} 2>/dev/null`, {
        timeout: 3000
      });
    } catch {}
  }

  estimateTemp(content) {
    let temp = 50;
    if (/洞见|发现|创新|突破|关键/.test(content)) temp += 15;
    if (/细节|技术|实现|代码/.test(content)) temp -= 10;
    return Math.min(100, Math.max(0, temp));
  }

  countTokens(text) {
    const chinese = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    return Math.ceil(chinese / 1.7 + (text.length - chinese) / 4);
  }
}

module.exports = function(api) {
  api.registerContextEngine('insight-system', config => new RippleContextEngine(config));
};
