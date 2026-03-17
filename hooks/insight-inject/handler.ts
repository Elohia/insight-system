import { spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import os from "os";

/**
 * Insight Inject Hook
 *
 * 在 AI 运行前自动注入相关洞见到上下文中
 */

const HOOK_NAME = "insight-inject";

/**
 * 运行 Python 脚本并获取输出
 */
async function runPython(scriptPath: string, args: string[] = []): Promise<string> {
    return new Promise((resolve, reject) => {
        const proc = spawn("python3", [scriptPath, ...args], {
            cwd: path.dirname(scriptPath),
            env: { ...process.env },
        });

        let stdout = "";
        let stderr = "";

        proc.stdout.on("data", (data) => {
            stdout += data.toString();
        });

        proc.stderr.on("data", (data) => {
            stderr += data.toString();
        });

        proc.on("close", (code) => {
            if (code === 0) {
                resolve(stdout);
            } else {
                reject(new Error(`Python script failed: ${stderr}`));
            }
        });
    });
}

/**
 * 解析洞见输出的内容
 */
function parseInsightOutput(output: string): { context: string; reversePrompt?: string } {
    const lines = output.trim().split("\n");
    let context = "";
    let reversePrompt = "";

    let inContext = false;
    let inReversePrompt = false;

    for (const line of lines) {
        if (line.includes("模糊层") || line.includes("工具思维") || line.includes("反向提示")) {
            inContext = true;
        }

        if (line.includes("反向提示") || line.includes("💭")) {
            inReversePrompt = true;
            inContext = false;
        }

        if (inContext && line.trim()) {
            context += line + "\n";
        }
        if (inReversePrompt && line.trim()) {
            reversePrompt += line + "\n";
        }
    }

    return { context: context.trim(), reversePrompt: reversePrompt.trim() };
}

/**
 * 主 handler
 */
const handler = async (event: any) => {
    // 只处理 agent:start 和 command:new 事件
    if (event.type !== "agent" && event.type !== "command") {
        return;
    }

    if (event.type === "command" && event.action !== "new") {
        return;
    }

    console.log(`[${HOOK_NAME}] Running insight inject hook...`);

    try {
        // 洞见系统路径
        const insightSystemPath = process.env.INSIGHT_SYSTEM_PATH ||
            path.join(os.homedir(), ".openclaw", "extensions", "insight-system");

        const hookScript = path.join(insightSystemPath, "core", "insight_hook.py");

        // 检查脚本是否存在
        try {
            await fs.access(hookScript);
        } catch {
            console.log(`[${HOOK_NAME}] Insight hook script not found: ${hookScript}`);
            return;
        }

        // 运行洞见 hook
        console.log(`[${HOOK_NAME}] Running: ${hookScript} --startup`);
        const output = await runPython(hookScript, ["--startup"]);

        if (!output.trim()) {
            console.log(`[${HOOK_NAME}] No insight output`);
            return;
        }

        // 解析输出
        const { context, reversePrompt } = parseInsightOutput(output);

        if (context) {
            console.log(`[${HOOK_NAME}] Injecting ${context.length} chars of context`);

            // 将洞见内容注入到消息中
            if (event.messages) {
                // 添加系统消息
                const insightMessage = {
                    role: "system",
                    content: `【洞见系统注入】\n${context}`,
                };

                // 插入到消息开头（在任何现有 system 消息之后）
                const systemIdx = event.messages.findIndex((m: any) => m.role === "system");
                if (systemIdx >= 0) {
                    event.messages.splice(systemIdx + 1, 0, insightMessage);
                } else {
                    event.messages.unshift(insightMessage);
                }
            }

            // 如果有反向提示，添加到 context 中
            if (reversePrompt) {
                console.log(`[${HOOK_NAME}] Reverse prompt: ${reversePrompt}`);
                // 反向提示会在消息中显示
            }
        }

        console.log(`[${HOOK_NAME}] Done!`);

    } catch (error: any) {
        console.error(`[${HOOK_NAME}] Error:`, error.message);
    }
};

export default handler;
