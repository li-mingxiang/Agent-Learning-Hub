import argparse
import json
import os
import socket
import sys
import urllib.error
import urllib.request

from tools import calculator


API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_MAX_STEPS = 5
DEFAULT_TIMEOUT_SECONDS = 60
SYSTEM_PROMPT = """You are a helpful assistant.
You must answer with one valid JSON object only.
Do not wrap the JSON in markdown code fences.
The JSON object must have exactly these fields:
- need_tool: boolean
- tool_name: string or null
- arguments: object
- final_answer: string or null

If the user asks for exact arithmetic, request the calculator tool:
{
  "need_tool": true,
  "tool_name": "calculator",
  "arguments": {"expression": "23 * 57"},
  "final_answer": null
}

If no tool is needed, answer directly:
{
  "need_tool": false,
  "tool_name": null,
  "arguments": {},
  "final_answer": "your answer"
}

When a tool result is provided, use it to produce the final answer:
{
  "need_tool": false,
  "tool_name": null,
  "arguments": {},
  "final_answer": "your final answer based on the tool result"
}
"""


def load_dotenv(path: str = ".env") -> None:
    """读取本地 .env 文件，把里面的 KEY=VALUE 放入当前进程环境变量。"""
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            # 跳过空行、注释行，以及不是 KEY=VALUE 格式的行。
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # 不覆盖系统里已经设置好的环境变量，方便临时调试。
            if key and key not in os.environ:
                os.environ[key] = value


def read_question() -> str:
    """从命令行参数读取问题；没有参数时再进入交互式输入。"""
    parser = argparse.ArgumentParser(description="Ask one question to an LLM.")
    parser.add_argument("question", nargs="*", help="Question text. If omitted, you will be prompted.")
    args = parser.parse_args()

    if args.question:
        return " ".join(args.question).strip()

    return input("Your question: ").strip()


def get_api_key() -> str:
    """从环境变量读取 DeepSeek API key，缺失时给出清楚错误。"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("Missing DEEPSEEK_API_KEY environment variable.")
    return api_key


def get_int_env(name: str, default: int) -> int:
    """读取正整数环境变量；没有设置时使用默认值。"""
    value = os.getenv(name)
    if value is None:
        return default

    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc

    if parsed_value <= 0:
        raise RuntimeError(f"{name} must be greater than 0.")
    return parsed_value


def extract_text(response_data: dict) -> str:
    """从 DeepSeek Chat Completions 响应中取出 assistant 的文本内容。"""
    try:
        # DeepSeek 兼容 OpenAI Chat Completions 响应结构。
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected DeepSeek API response: {response_data}") from exc

    if not isinstance(content, str):
        raise RuntimeError(f"Unexpected answer type from DeepSeek API: {type(content).__name__}")
    return content.strip()


def parse_model_json(text: str) -> dict:
    """解析模型输出的 JSON，并检查 agent 决策所需的基础字段。"""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model did not return valid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}") from exc

    if not isinstance(data, dict):
        raise RuntimeError("Model JSON must be an object.")

    required_fields = ("need_tool", "tool_name", "arguments", "final_answer")
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise RuntimeError(f"Model JSON is missing required fields: {', '.join(missing_fields)}")

    if not isinstance(data["need_tool"], bool):
        raise RuntimeError("Model JSON field 'need_tool' must be a boolean.")
    if data["tool_name"] is not None and not isinstance(data["tool_name"], str):
        raise RuntimeError("Model JSON field 'tool_name' must be a string or null.")
    if not isinstance(data["arguments"], dict):
        raise RuntimeError("Model JSON field 'arguments' must be an object.")
    if data["final_answer"] is not None and not isinstance(data["final_answer"], str):
        raise RuntimeError("Model JSON field 'final_answer' must be a string or null.")

    return data


def parse_tool_call(model_json: dict) -> dict | None:
    """当模型请求工具时，解析并校验工具名和参数。"""
    if not model_json["need_tool"]:
        return None

    tool_name = model_json["tool_name"]
    arguments = model_json["arguments"]

    if tool_name != "calculator":
        raise RuntimeError(f"unknown tool: {tool_name}")

    # 当前只支持 calculator(expression=...) 这一种工具调用格式。
    expression = arguments.get("expression")
    if not isinstance(expression, str) or not expression.strip():
        raise RuntimeError("calculator tool requires a non-empty 'expression' argument.")

    return {
        "tool_name": tool_name,
        "arguments": {
            "expression": expression,
        },
    }


def execute_tool_call(tool_call: dict) -> str:
    """执行已经校验过的工具调用，并返回工具结果字符串。"""
    tool_name = tool_call["tool_name"]
    arguments = tool_call["arguments"]

    if tool_name == "calculator":
        # 第 5 项只支持 calculator；后续新增工具时再扩展这里。
        return calculator(arguments["expression"])

    raise RuntimeError(f"unknown tool: {tool_name}")


def call_llm(messages: list[dict], timeout_seconds: int) -> str:
    """调用 DeepSeek API，让模型按 SYSTEM_PROMPT 和 messages 返回 JSON 字符串。"""
    api_key = get_api_key()
    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)

    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
        "stream": False,
    }
    # urllib 需要 bytes 类型的请求体。
    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # HTTPError 里通常包含服务端返回的 JSON 错误信息，读出来便于排查。
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM API request failed: HTTP {exc.code}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM API request failed: {exc.reason}") from exc
    except socket.timeout as exc:
        raise RuntimeError(f"LLM API request timed out after {timeout_seconds} seconds.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM API returned invalid response JSON: {exc.msg}") from exc

    answer = extract_text(response_data)
    if not answer:
        raise RuntimeError("LLM API returned no text answer.")
    return answer


def build_tool_result_message(tool_call: dict, tool_result: str) -> dict:
    """把工具执行结果包装成一条消息，交给模型生成最终回答。"""
    return {
        "role": "user",
        "content": (
            "Tool result:\n"
            f"tool_name: {tool_call['tool_name']}\n"
            f"arguments: {json.dumps(tool_call['arguments'], ensure_ascii=False)}\n"
            f"result: {tool_result}\n\n"
            "Now return the final JSON answer. Set need_tool to false, "
            "tool_name to null, arguments to {}, and final_answer to a natural language answer."
        ),
    }


def run_agent(question: str, max_steps: int, timeout_seconds: int) -> tuple[dict, list[dict]]:
    """运行最小 agent loop：模型决策、执行工具、把结果喂回模型，直到得到最终回答。"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = []

    for step in range(1, max_steps + 1):
        raw_answer = call_llm(messages, timeout_seconds)
        parsed_answer = parse_model_json(raw_answer)
        tool_call = parse_tool_call(parsed_answer)

        step_info = {
            "step": step,
            "model_json": parsed_answer,
            "tool_call": tool_call,
            "tool_result": None,
        }
        trace.append(step_info)

        if not tool_call:
            if not parsed_answer["final_answer"]:
                raise RuntimeError("Model returned no final_answer and did not request a tool.")
            return parsed_answer, trace

        try:
            tool_result = execute_tool_call(tool_call)
        except Exception as exc:
            raise RuntimeError(f"tool execution failed: {exc}") from exc

        step_info["tool_result"] = tool_result
        messages.append({"role": "assistant", "content": raw_answer})
        messages.append(build_tool_result_message(tool_call, tool_result))

    raise RuntimeError(f"Reached max_steps={max_steps} without a final answer.")


def main() -> int:
    """程序入口：读取问题、调用模型、必要时执行工具并让模型生成最终回答。"""
    load_dotenv()

    question = read_question()
    if not question:
        print("Question cannot be empty.")
        return 1

    try:
        max_steps = get_int_env("AGENT_MAX_STEPS", DEFAULT_MAX_STEPS)
        timeout_seconds = get_int_env("DEEPSEEK_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
        final_answer, trace = run_agent(question, max_steps, timeout_seconds)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for step_info in trace:
        print(f"\nStep {step_info['step']} model JSON:")
        print(json.dumps(step_info["model_json"], ensure_ascii=False, indent=2))

        if step_info["tool_call"]:
            print("\nTool call parsed:")
            print(json.dumps(step_info["tool_call"], ensure_ascii=False, indent=2))
            print("\nTool result:")
            print(step_info["tool_result"])

    print("\nFinal answer:")
    print(final_answer["final_answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
