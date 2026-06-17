# Stage 1: Build A Minimal Agent Loop

This project implements Stage 1: a minimal agent loop using the DeepSeek API, structured JSON output parsing, a safe calculator tool, tool-call parsing, tool execution, max steps, timeouts, and basic error handling.

## Status

- [x] 会用一个 LLM API 完成普通对话。
- [x] 会让模型输出结构化 JSON。
- [x] 会定义一个工具函数，例如 search、calculator、read_file。
- [x] 会解析模型的 tool call / function call。
- [x] 会执行工具，并把工具结果喂回模型。
- [x] 会给 agent loop 加最大步数、超时和错误处理。

## Run

Option 1: set your API key in PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_api_key_here"
```

Option 2: create a local `.env` file:

```text
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-v4-flash
AGENT_MAX_STEPS=5
DEEPSEEK_TIMEOUT_SECONDS=60
```

Do not put a real API key in `.env.example`.

Optional: override the model.

```powershell
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
```

Run with a command-line question:

```powershell
py main.py "请用一句话解释什么是 agent loop"
```

The program prints the first model JSON, any parsed `calculator` tool call, the tool result, and the final answer.
The loop stops when the model returns `final_answer`, or when `AGENT_MAX_STEPS` is reached.

Or run interactively:

```powershell
py main.py
```

If your machine uses `python` instead of the Windows `py` launcher, replace `py` with `python` in the commands above.

## Test Calculator

```powershell
py -c "from tools import calculator; print(calculator('2 * (3 + 4)'))"
```
