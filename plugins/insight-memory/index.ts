/**
 * Insight Memory Plugin
 *
 * 使用洞见系统替代 OpenClaw 的 memory_search 工具
 */

import { spawn } from "node:child_process";
import path from "node:path";
import os from "node:os";

const PLUGIN_ID = "insight-memory";

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
 * 解析洞见搜索结果
 */
function parseInsightResults(output: string): any[] {
    try {
        const lines = output.trim().split("\n");
        const results = [];

        for (const line of lines) {
            if (line.startsWith("- ")) {
                results.push(line.substring(2));
            }
        }

        return results;
    } catch (e) {
        return [];
    }
}

export default function (api: any) {
    // 注册洞见记忆搜索工具
    api.registerTool({
        name: "insight_memory_search",
        description: "使用洞见系统搜索记忆（深度理解 + 关联发现）",
        parameters: {
            type: "object",
            properties: {
                query: {
                    type: "string",
                    description: "搜索查询"
                },
                max_results: {
                    type: "number",
                    description: "最大结果数",
                    default: 5
                }
            },
            required: ["query"]
        },
        handler: async (args: { query: string; max_results?: number }, context: any) => {
            const { query, max_results = 5 } = args;

            console.log(`[${PLUGIN_ID}] Searching insights for: ${query}`);

            try {
                // 洞见系统路径
                const insightSystemPath = process.env.INSIGHT_SYSTEM_PATH ||
                    path.join(os.homedir(), ".openclaw", "extensions", "insight-system");

                // 运行洞见搜索
                const searchScript = path.join(insightSystemPath, "utils", "search.py");

                const output = await runPython(searchScript, [query]);

                const results = parseInsightResults(output);

                return {
                    query,
                    results: results.slice(0, max_results),
                    total: results.length,
                    source: "insight-system"
                };
            } catch (error: any) {
                console.error(`[${PLUGIN_ID}] Error:`, error.message);
                return {
                    query,
                    results: [],
                    error: error.message,
                    source: "insight-system"
                };
            }
        }
    });

    // 注册洞见记忆读取工具
    api.registerTool({
        name: "insight_memory_read",
        description: "读取指定日期的洞见记忆",
        parameters: {
            type: "object",
            properties: {
                date: {
                    type: "string",
                    description: "日期 (YYYY-MM-DD)，默认为今天"
                }
            },
            required: []
        },
        handler: async (args: { date?: string }, context: any) => {
            const date = args.date || new Date().toISOString().split("T")[0];

            console.log(`[${PLUGIN_ID}] Reading insights for date: ${date}`);

            try {
                const insightSystemPath = process.env.INSIGHT_SYSTEM_PATH ||
                    path.join(os.homedir(), ".openclaw", "extensions", "insight-system");

                const hookScript = path.join(insightSystemPath, "core", "insight_hook.py");

                const output = await runPython(hookScript, ["--deep", date]);

                return {
                    date,
                    content: output,
                    source: "insight-system"
                };
            } catch (error: any) {
                console.error(`[${PLUGIN_ID}] Error:`, error.message);
                return {
                    date,
                    content: "",
                    error: error.message,
                    source: "insight-system"
                };
            }
        }
    });

    // 注册洞见状态工具
    api.registerTool({
        name: "insight_status",
        description: "查看洞见系统状态",
        parameters: {
            type: "object",
            properties: {},
            required: []
        },
        handler: async (args: any, context: any) => {
            console.log(`[${PLUGIN_ID}] Getting insight status`);

            try {
                const insightSystemPath = process.env.INSIGHT_SYSTEM_PATH ||
                    path.join(os.homedir(), ".openclaw", "extensions", "insight-system");

                const statusScript = path.join(insightSystemPath, "utils", "status.py");

                const output = await runPython(statusScript, []);

                return {
                    status: output,
                    source: "insight-system"
                };
            } catch (error: any) {
                console.error(`[${PLUGIN_ID}] Error:`, error.message);
                return {
                    status: null,
                    error: error.message,
                    source: "insight-system"
                };
            }
        }
    });

    console.log(`[${PLUGIN_ID}] Plugin loaded - registered insight_memory_search, insight_memory_read, insight_status tools`);
}
