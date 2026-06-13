# Stage 0：Understand What An Agent Is

## 1. 这一阶段要学什么

Stage 0 主要是先搞清楚 Agent 的基本概念，不急着写复杂代码。

这一阶段重点：

* 区分 Chatbot、Workflow、Agent、Multi-agent；
* 理解 Agent 的基本循环；
* 理解 Tools、Memory、Instructions、Guardrails 的作用；
* 知道什么任务适合 Agent，什么任务不适合；
* 初步了解 Anthropic 和 OpenAI 两篇 Agent 指南的不同侧重点。

---

## 2. 几个基本概念

### Chatbot

Chatbot 主要是聊天问答。

特点是：

* 用户问，模型答；
* 一般不主动调用工具；
* 不负责完成复杂任务。

简单理解：

> Chatbot 更像“回答问题”。

---

### Workflow

Workflow 是固定流程。

例如：

```text
输入论文
→ 提取摘要
→ 总结方法
→ 输出笔记
```

流程是开发者提前写好的，模型只是按步骤完成其中某些环节。

简单理解：

> Workflow 是“人写好流程，模型照着做”。

---

### Agent

Agent 不只是回答问题，而是可以根据当前情况决定下一步。

它通常包括：

```text
LLM + Tools + Memory/State + Loop
```

也可以理解为：

```text
Model + Tools + Instructions + Guardrails
```

简单理解：

> Agent 是“能根据反馈自己推进任务的系统”。

---

### Multi-agent

Multi-agent 是多个 Agent 分工合作。

例如：

```text
Search Agent：找资料
Reading Agent：读论文
Writing Agent：写总结
Review Agent：检查结果
```

它适合复杂任务，但初学阶段不要一上来就做 Multi-agent。

---

## 3. Agent 的基本循环

Agent 的核心循环是：

```text
Observe → Think → Act → Observe
```

对应中文：

```text
观察 → 思考 → 行动 → 再观察
```

我的理解：

* Observe：看用户输入、上下文、工具返回结果；
* Think：判断下一步该做什么；
* Act：回复用户或调用工具；
* Observe again：看行动后的反馈，再决定是否继续。

例如代码 Agent：

```text
读取报错
→ 判断可能的问题
→ 修改代码
→ 运行测试
→ 根据测试结果继续修改
```

这就是一个典型闭环。

---

## 4. Agent 的核心组成

### Model

负责理解、推理和生成。

### Tools

工具让 Agent 可以真正做事。

例如：

```text
search_web
calculator
read_file
write_file
run_python
query_database
```

没有工具时，LLM 只能回答；有工具后，Agent 可以查资料、读文件、运行代码、调用 API。

### Instructions

Instructions 是 Agent 的操作说明。

它需要告诉 Agent：

* 你是什么角色；
* 你要完成什么任务；
* 应该按什么步骤做；
* 什么时候调用工具；
* 什么时候询问用户；
* 输出格式是什么；
* 遇到异常情况怎么办。

### Memory / State

Memory 用来保存上下文和任务状态。

例如：

* 用户正在学哪个阶段；
* 已经完成了哪些步骤；
* 工具返回了什么结果；
* 用户偏好什么输出方式。

### Guardrails

Guardrails 是安全护栏。

比如：

* 限制最大工具调用次数；
* 禁止执行危险命令；
* 高风险操作前需要用户确认；
* 不能泄露隐私；
* 不能伪造引用。

---

## 5. 三种基础 Workflow 模式

### Prompt Chaining

把任务拆成多个连续步骤，前一步结果作为后一步输入。

例如：

```text
提取信息
→ 整理表格
→ 写总结
```

适合论文总结、文本整理、报告生成。

---

### Parallelization

多个独立任务同时处理。

例如：

```text
同时总结 5 篇论文
同时分析 3 个网页
同时检查多个代码文件
```

适合互不依赖的任务。

---

### Routing

先判断输入类型，再进入对应流程。

例如客服：

```text
订单问题 → Orders Agent
维修问题 → Repairs Agent
销售问题 → Sales Agent
```

适合分类、分流、意图识别。

---

## 6. 什么时候适合用 Agent

适合 Agent 的任务通常有这些特点：

* 步骤不完全固定；
* 需要多轮判断；
* 需要调用工具；
* 需要根据结果调整下一步；
* 中间可能失败，需要修正；
* 最终结果可以被检查。

典型例子：

* 客服 Agent；
* Coding Agent；
* 论文阅读 Agent；
* 科研调研 Agent；
* 数据分析 Agent。

---

## 7. 什么时候不适合用 Agent

不适合 Agent 的任务：

* 流程很固定；
* 规则很明确；
* 普通脚本就能完成；
* 不需要模型动态判断；
* 风险很高但结果难验证。

例如：

```text
批量重命名文件
简单格式转换
固定日报生成
简单计算
```

我的理解：

> 能用脚本解决的，不要硬上 Agent。
> 能用 Workflow 解决的，不要急着做 Agent。
> 能用单 Agent 解决的，不要急着做 Multi-agent。

---

## 8. Tool Prompt Engineering

工具本身也要设计好。

因为模型调用工具时，主要依赖工具名、参数名和说明来判断怎么用。

一个好的工具定义应该写清楚：

* 工具是干什么的；
* 什么时候用；
* 什么时候不要用；
* 参数分别是什么意思；
* 输入格式有什么要求；
* 返回什么结果；
* 出错时怎么办。

差的工具：

```python
def edit(path, content):
    """Edit file."""
```

问题是太模糊。

更好的工具：

```python
def replace_file_content(absolute_file_path: str, new_content: str):
    """
    Replace the entire content of a text file.
    Use this only after reading the file first.
    absolute_file_path must be a full absolute path.
    new_content must be the complete new file content.
    """
```

我的理解：

> 工具定义本身也是 prompt。工具越清楚，Agent 越不容易用错。

---

## 9. Guardrails

Agent 因为可以自主调用工具，所以需要安全限制。

常见 guardrails：

```text
最大循环步数
超时限制
输入长度限制
敏感信息过滤
危险命令拦截
高风险操作确认
输出格式检查
人工审核
```

构建 guardrails 的思路：

1. 先找出当前应用的主要风险；
2. 先保护隐私和内容安全；
3. 根据真实失败案例继续补充；
4. 兼顾安全和用户体验。

---

## 10. Sandbox 沙盒环境

沙盒环境就是安全隔离的测试环境。

Agent 可以在里面试错，但不会影响真实系统。

例如：

* 代码 Agent 用临时代码仓库或 Docker；
* 数据库 Agent 用测试数据库；
* 文件 Agent 用临时目录；
* 机器人 Agent 用仿真环境。

我的理解：

> Agent 上线前一定要先在沙盒里跑，不要直接让它操作真实环境。

---

## 11. Multi-agent 的两种常见模式

### Manager Pattern

一个 Manager Agent 负责调度多个专业 Agent。

```text
Manager Agent
├── Search Agent
├── Reading Agent
├── Writing Agent
└── Review Agent
```

优点是结构清楚，适合初学和科研助手这类任务。

---

### Decentralized Pattern

多个 Agent 之间互相交接任务。

例如：

```text
General Agent → Billing Agent → Human Support
```

这种方式更灵活，但也更难调试，容易出现上下文丢失或来回交接。

---

## 12. Tool call 和 Handoff 的区别

### Tool call

Agent 调用工具，拿到结果后，控制权还在原 Agent 手里。

例如：

```text
Agent 调用 search_web
→ 得到搜索结果
→ Agent 继续处理
```

### Handoff

一个 Agent 把任务交给另一个 Agent，执行权转移。

例如：

```text
Triage Agent 判断是订单问题
→ 交给 Orders Agent
```

---

## 13. Declarative Graph 和 Code-first

### Declarative Graph

提前把流程图定义好。

优点：

* 可视化清楚；
* 适合固定流程。

缺点：

* 流程复杂后图会很乱；
* 要提前定义很多分支；
* 可能需要学习框架自己的写法。

### Code-first

用普通代码写流程逻辑。

例如：

```python
if user_intent == "refund":
    refund_agent.run(input)
elif user_intent == "shipping":
    shipping_agent.run(input)
else:
    general_agent.run(input)
```

优点是灵活，适合动态任务。

---

## 14. Prompt Template

Prompt Template 是提示词模板。

不要每个场景都写一套 prompt，而是写一个通用模板，再替换变量。

例如：

```text
你是一个 {role} Agent。

任务场景：{use_case}
业务规则：{policy}
可用工具：{tools}
输出格式：{output_format}
特殊限制：{constraints}
```

好处：

* 方便维护；
* 方便扩展；
* 避免写很多重复 prompt；
* 不必过早拆成 Multi-agent。

---

## 15. Anthropic 和 OpenAI 两篇指南的区别

### Anthropic

更偏 Agent 的底层思想和模式。

重点：

* 先用 LLM API，不要一上来依赖复杂框架；
* 理解 chain、parallel、route；
* Agent 本质是 LLM 在循环中根据反馈调用工具；
* 工具接口要认真设计。

一句话：

> Anthropic 更像是在讲 Agent 的基本原理。

---

### OpenAI

更偏工程落地和产品设计。

重点：

* Agent = Model + Tools + Instructions；
* 先判断场景是否适合 Agent；
* 优先做单 Agent；
* 复杂后再考虑 Multi-agent；
* 重视 Guardrails 和上线安全。

一句话：

> OpenAI 更像是在讲怎么把 Agent 做成一个可靠系统。

---

## 16. 对我后续学习有用的方向

### 论文阅读 Agent

目标：

```text
读取论文
总结方法
提取实验
分析贡献和局限
生成中文笔记
```

需要的工具：

```text
read_pdf
search_papers
summarize_section
save_markdown
```

---

### 科研调研 Agent

目标：

```text
搜索论文
筛选相关工作
整理代表方法
比较不同路线
输出调研报告
```

需要的工具：

```text
search_web
search_papers
read_abstract
compare_methods
export_report
```

---

### Coding Agent

目标：

```text
读取代码
定位 bug
修改文件
运行测试
根据报错继续修改
输出修改说明
```

需要的工具：

```text
search_files
read_file
write_file
run_tests
show_diff
```

---

## 17. Stage 0 复习重点

必须掌握：

* Chatbot / Workflow / Agent / Multi-agent 的区别；
* Agent loop：Observe → Think → Act → Observe；
* Model、Tools、Instructions、Memory、Guardrails 的作用；
* chain、parallel、route 三种 workflow；
* tool prompt engineering 的基本原则；
* guardrails 和 sandbox 的作用；
* tool call 和 handoff 的区别；
* 为什么不要过早做 Multi-agent。

简单了解：

* MCP；
* Hooks；
* Declarative graph vs Code-first；
* Prompt template；
* Manager pattern 和 Decentralized pattern。

---

## 18. Stage 0 小结

我目前对 Agent 的理解：

> Agent 不是一个新模型，而是一个由 LLM 驱动的任务执行系统。它在 instructions 的指导下使用 tools，在 guardrails 的限制内，根据环境反馈不断推进任务。

学习 Agent 的顺序应该是：

```text
先理解概念
→ 学基础 workflow
→ 直接调用 LLM API
→ 学 tool calling
→ 手写最小 agent loop
→ 加 memory / RAG / guardrails
→ 最后再学框架和 multi-agent
```

当前最重要的结论：

> 不要一开始追求复杂框架。先把单 Agent、工具调用、反馈循环和安全限制理解清楚。
