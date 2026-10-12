# Trading212 AI Analyst — 项目交接文档

> 文件名：`HANDOFF.ma`
> 更新时间：2026-10-12
> 目的：让新会话能够快速恢复项目背景、当前架构决策、完成情况、待办事项与不可重复踩的坑。
> 说明：本文件是项目交接记录；凡标注“待核实”的内容，都应先检查仓库实际代码、GitHub Actions 运行记录和 Cloudflare
> 部署状态，不要把规划误当成已经完成。

---

## 1. 项目目标

构建一个 Trading212 AI Analyst 系统，持续读取投资组合与市场研究数据，计算投资指标，生成 AI 投资分析，并通过 Telegram 和
React Dashboard 呈现。

最终数据链路：

```text
Trading212 / Finnhub / FRED / Gemini
                 |
                 v
      GitHub Actions + Python Pipeline
        daily_report.yml / market_close.yml
                 |
                 v
               Supabase
                 ^
                 | 只读查询
                 |
        Cloudflare Worker + FastAPI
                 ^
                 | HTTPS / JSON
                 |
      React Dashboard + TanStack Query
```

Telegram Bot 也是同一套 Python 业务能力的消费者。不要为 API 或 Dashboard 重写投资业务逻辑。

### 架构的核心分工

- **GitHub Actions**：运行定时数据采集、分析、持久化及通知任务。
- **Python Domain / Services / Repository**：唯一的业务规则与数据访问实现。
- **Supabase**：数据持久化的单一事实来源。
- **Cloudflare Worker / FastAPI**：提供受保护的只读 REST API；不负责重新运行日常分析 Pipeline。
- **React Dashboard**：消费 REST API，负责 UI、加载/错误/刷新状态与数据可视化。
- **Telegram Bot**：消费相同的业务结果并发送消息。

React 不应直接连接 Supabase；尤其不能把 Supabase Service Role Key 放入前端。

---

## 2. 已完成的工作

### 2.1 Python 后端与 Pipeline：Phase 1–4 已完成（以既有项目记录为准）

已完成的阶段：

- Phase 1：Domain Model
- Phase 2：Portfolio Analytics
- Phase 3：Data Quality / Idempotency
- Phase 4：CI + Tests，包括 pytest 基础设施、Domain、Analytics、Service、Pipeline 测试、GitHub Actions CI、Ruff 和覆盖率检查。

主要功能与组件包括：

- Trading212 API 客户端与持仓读取。
- Portfolio / Position / Analytics 等 Pydantic Domain 模型。
- 投资组合指标：总资产、现金比例、持仓权重、未实现收益、行业配置、集中度、TWR、XIRR、收益率、波动率、Sharpe、Drawdown / Max Drawdown
  等。
- Finnhub Earnings、新闻研究、FRED 宏观数据采集。
- ResearchContext 和数据源状态/容错处理。
- Gemini AI Analyst，输出结构化报告。
- Supabase 持久化与 Repository 查询方法。
- Telegram Bot、Formatter、Handlers 及集中日志能力。
- GitHub Actions 定时工作流：`daily_report.yml` 和 `market_close.yml`。
- pytest、Ruff、Coverage 和 GitHub Actions CI。

项目历史记录中，Phase 4 的一个已知提交为 `7c70816d5d7d463db0dc2e655bd1e974e248dea1`；这是历史参考，不保证是当前
HEAD。Dashboard Starter 历史提交曾记录为 `b809d016bd2b3b64ca9c3ef6a95ab3101bdf7dd9`；开始工作前请重新检查当前分支与提交。

### 2.2 Dashboard：Phase 5.1–5.4 已完成（按用户此前报告）

Dashboard 使用：

- React 19
- TypeScript
- Vite
- Tailwind CSS v4
- shadcn/ui
- TanStack Router
- TanStack Query
- Bun 作为唯一 JavaScript package manager

用户此前确认 Phase 5.4 已完成。具体组件与当前代码状态应以仓库为准，不要仅凭旧对话假定页面已完整接入真实数据。

正确的 Lovable Starter 项目：

- Project ID：`9bb2927c-09ad-43ef-aad5-380cefef8d59`
- Editor：`https://lovable.dev/projects/9bb2927c-09ad-43ef-aad5-380cefef8d59`
- Preview：`https://id-preview--9bb2927c-09ad-43ef-aad5-380cefef8d59.lovable.app`

此前另有一个误创建的 Lovable 项目 `6cbc6d29-71af-4a06-bdf2-c01fb712108c`，正确的空白 Starter 是上面的
`9bb2927c-09ad-43ef-aad5-380cefef8d59`。不要误用旧项目。

### 2.3 API / Cloudflare Worker：已成功部署，需进一步核验真实端点

用户已明确报告：

- Cloudflare Worker API 已跑通部署。
- Worker 在独立的 `api_worker/` 目录。
- Worker 入口使用 `from app.api.main import app`，即复用现有 FastAPI 应用，而不是再定义一套业务路由。

当前适配入口的目标形态：

```python
from app.api.main import app
from workers import asgi

Default = asgi.entrypoint(app)
```

这段入口只做 ASGI 适配，不应该重复定义 `/api/portfolio`、`/api/analytics` 等路由。

**待核实**：部署成功不代表所有现有 API、Supabase 查询和全部依赖都在 Cloudflare Python Workers 运行环境正常。必须测试实际只读端点、导入链、依赖和认证。

---

## 3. 现有架构与可能涉及的文件

历史项目结构：

```text
app/
├── domain/
│   ├── analytics.py
│   ├── cashflow.py
│   ├── earnings.py
│   ├── macro.py
│   ├── news.py
│   ├── portfolio.py
│   ├── position.py
│   ├── report.py
│   ├── research.py
│   └── validation.py
├── infrastructure/
│   ├── finnhub.py
│   ├── fred.py
│   ├── supabase.py
│   └── trading212.py
├── services/
│   ├── ai_analysis_service.py
│   ├── analytics_service.py
│   ├── portfolio_service.py
│   ├── research_service.py
│   └── validation_service.py
├── telegram/
├── api/                   # 当前存在与否、实际路由需从仓库确认
├── repository.py
├── storage.py
├── pipeline.py
└── logger.py

api_worker/
├── src/main.py            # 应导入 app.api.main.app
├── pyproject.toml
├── uv.lock                # 若采用 uv --locked，应提交且保持同步
└── wrangler.jsonc

dashboard/
.github/workflows/
├── daily_report.yml
├── market_close.yml
└── deploy-api-worker.yml  # 是否已创建/启用，需核实
```

请以当前仓库为准。以上是项目历史结构/目标结构，不保证每个路径与当前 HEAD 完全一致。

---

## 4. 当前架构决策

### 4.1 不重写 API

现有 `app/api/` 是唯一的 HTTP API 实现。`api_worker/` 只负责 Cloudflare 运行时适配、依赖和部署配置。

不要复制/重写业务 routes；不要在 `api_worker/src/main.py` 里重新定义路由。

### 4.2 不让 React 直连 Supabase

推荐数据流：

```text
Overview / Dashboard Page
  -> existing TanStack Query hook
  -> central API client
  -> Cloudflare Worker HTTPS endpoint
  -> FastAPI route
  -> existing Repository / Service
  -> Supabase
```

前端不保存数据库 Service Role Key。`VITE_API_BASE_URL` 是 API 地址，不是秘密；任何前端构建变量都不能用于隐藏密钥。

### 4.3 计算与查询分离

- `daily_report.yml`、`market_close.yml`：生产数据，执行 Pipeline、分析并保存。
- API：读取已持久化数据并返回 JSON。
- Dashboard：展示 API 返回值。
- 不要让浏览器刷新重新触发 Trading212 同步、AI 分析或完整 Pipeline。

### 4.4 渐进式重构，不推倒重来

用户正在考虑重构整个 `app/`。建议渐进式演进：

1. 先盘点现有代码与接口契约，冻结行为基线。
2. 统一配置、日志和依赖装配，避免 import 时产生外部副作用。
3. 将 Daily / Market Close 的编排逐步提取为可测试的 application use cases。
4. 保留现有 Domain、Services、Repository 和通过测试的业务逻辑。
5. 再整理 API query / response schema。
6. 最后验证 Worker 部署与 Dashboard 端到端流程。

建议的长期分层：

- `domain/`：纯业务规则和模型。
- `application/`：Daily、Market Close、Portfolio Query、Analytics Query 等用例和必要的 ports。
- `services/`：现有可复用业务能力；不必为了架构外观立刻移动所有代码。
- `infrastructure/`：Trading212、Supabase、Finnhub、FRED、Gemini 等外部适配。
- `api/`：HTTP routes、依赖装配、request/response schemas。
- `telegram/`：Bot、Handlers、Formatter。
- `api_worker/`：Cloudflare 适配和部署，不放第二套业务实现。

不要为了“Clean Architecture”过度引入抽象类、Protocol 或新框架。只有当测试隔离、多个实现或运行环境边界确实需要时再抽象。

---

## 5. 推荐 API 契约（需要对照真实代码核验）

计划中的只读接口：

| Endpoint                                 | 用途            |
|------------------------------------------|---------------|
| `GET /api/health`                        | Worker 服务健康检查 |
| `GET /api/portfolio`                     | 最新投资组合概览      |
| `GET /api/positions`                     | 最新持仓          |
| `GET /api/history?days=365`              | 历史资产/收益曲线     |
| `GET /api/analytics`                     | 收益与风险指标       |
| `GET /api/report` 或 `/api/report/latest` | 最新 AI 报告      |
| `GET /api/news`                          | 新闻            |
| `GET /api/earnings`                      | 财报日历          |

**不要假设这些路径都已经实现。** 之前曾出现过 `/api/report/latest` 路径与实际路由不一致的问题。接入 Dashboard 前，先检查
FastAPI 路由注册、OpenAPI `/docs` 或 `/openapi.json`，以实际 endpoint 为准。前端 Query hooks 必须使用真实路径和真实响应
schema。

建议在数据响应中提供实际数据更新时间/来源状态，让 Dashboard 能区分“API 正常”和“数据新鲜”。不要返回硬编码更新时间。

---

## 6. 当前卡点与风险

### 6.1 Worker 部署成功不等于完整后端兼容

Cloudflare Python Workers 的运行环境与普通 CPython 不完全相同，某些原生扩展或依赖可能不兼容。项目历史依赖包括：

- Supabase Python SDK
- Pydantic
- `pyxirr`
- pandas
- Google GenAI SDK
- 其他用于完整 Pipeline 的依赖

不应该把 `requirements.txt` 所有依赖无差别塞入 Worker。先验证 API 的实际导入链和依赖。尤其要避免 Worker 在 import
阶段就导入只用于每日分析的重依赖。

如果完整依赖不适合 Workers，不要重写全部业务代码；考虑拆出更薄的查询 API、把不兼容部分隔离，或把 FastAPI 放在常规 Python
托管环境，Cloudflare 继续承担合适的边缘入口能力。

### 6.2 Worker 的源码打包路径

`api_worker/src/main.py` 导入根目录的 `app.api.main` 时，部署包必须包含正确的 `app/` 源码及运行依赖。

之前讨论过在 CI 中把根目录 `app/` 复制到 `api_worker/src/app/`。这只是一个可选的构建策略，并未在此文中认定为已实现。实施前要先确认
`pywrangler` 的实际打包规则、`main` 配置和当前成功部署方式。

如果采用生成副本策略：

- 源码只在根目录 `app/` 维护。
- CI 构建时复制。
- 生成目录加入 `.gitignore`，不要提交第二份业务代码。
- 测试 Worker 包确实能导入 `app.api.main`。

### 6.3 Dashboard API 接入

需要核实：

- Overview 当前是否还在使用 mock data。
- TanStack Query hooks 的实际文件和 query keys。
- API 路径、响应字段、加载/错误/刷新状态。
- `VITE_API_BASE_URL` 的环境配置。
- GitHub Pages 和 Lovable Preview 的实际域名是否在 CORS 允许范围内。

CORS 不是认证。个人投资数据不能因为配置了 CORS 就视为安全。

### 6.4 私人投资数据安全

如果 Dashboard 和 Worker 是公开地址，任何人可能尝试直接请求 API。上线前必须考虑访问认证/授权。仅仅隐藏页面按钮、配置 CORS
或不在 README 公开 URL 都不构成 API 访问控制。

- `CLOUDFLARE_API_TOKEN`、Supabase Service Role Key 只能保存在服务端 Secret。
- 不把密钥放进 React `VITE_*` 变量或构建产物。
- API 第一阶段尽量只读。
- 限制 CORS 到真实需要的域名，但同时实施认证。

### 6.5 数据状态与 Pipeline 可观测性

两条 Pipeline 不会同时完成。需要区分：

- Trading212 关键数据失败；
- Finnhub / FRED 等可选数据源失败；
- Portfolio snapshot 保存成功但 AI 报告失败；
- Daily 成功但 Market Close 尚未执行；
- API 正常但数据库中的数据是旧的。

历史上采用的降级原则：

- Trading212 / 关键 Supabase 操作属于关键路径；关键数据不可用时不要生成误导性完整报告。
- Finnhub、FRED、Gemini 等可按业务规则降级。
- 如果 Gemini 返回 `None`，仍应尽可能保存有效快照/历史并发送简化 Telegram 消息，不要保存空报告。
- 记录每个 collector 的 status 和异常，避免一个数据源失败导致所有状态信息丢失。

建议后续增加 `pipeline_runs`（或类似）运行记录，存储 `run_id`、pipeline 名称、开始/结束时间、整体状态、各数据源状态、最后成功更新时间和错误摘要。具体
schema 先检查现有表，避免重复设计。

---

## 7. 踩过的坑：绝对不要再踩

### 架构与实现

1. **不要让 React 直接查询 Supabase。** 统一通过 FastAPI API，业务规则与数据访问留在 Python。
2. **不要在 Worker 重写一套 API。** 复用 `app/api/`，Worker 入口只负责 ASGI 适配。
3. **不要把 Worker 当成 Pipeline 执行环境。** 日常采集和 AI 分析继续由现有 GitHub Actions 执行。
4. **不要未经验证把全部 Python 依赖迁进 Worker。** `pyxirr`、pandas 等必须实际测试兼容性。
5. **不要在 import 阶段执行昂贵/有副作用的操作。** 不要模块导入时自动同步 Trading212、调用 Gemini、发送 Telegram 或进行数据库写入。
6. **不要让 routes 直接重做 analytics 计算。** 复用现有 Service / Repository。
7. **不要在 API 和 Dashboard 两边重复定义业务规则。** API schema 是数据契约，前端负责展示。

### 数据与容错

8. **不要把 `report=None` 当成整个 Pipeline 必须失败。** 按业务规则保留已成功的数据，发送 fallback 通知，并跳过空报告持久化。
9. **不要让可选研究数据源失败就抹掉有效的 Portfolio 快照。** 区分关键依赖与可降级依赖。
10. **不要把 API health 当成数据 freshness。** 需要单独显示数据更新时间和 Pipeline 状态。
11. **不要假设 `/api/report/latest` 一定存在。** 曾出现过路径错误；以实际 FastAPI route/OpenAPI 为准。
12. **不要忽略数据库 schema 约束。** 之前 Supabase 出现过 `news_sentiment_check` constraint 错误。确保 sentiment
    值符合数据库允许枚举；同时检查 dataclass/Pydantic 字段映射，例如 earnings 日期映射到数据库 `earnings_date`。

### CI / 依赖 / 部署

13. **不要不加判断地省略 lockfile。** Dashboard 已选择 Bun 作为唯一 JS package manager，应提交正确的 Bun lockfile，并让 CI
    使用 Bun；不要混用 npm、pnpm、Bun 产生多个锁文件。
14. **不要在 Windows 上生成一个被 Linux CI 误用的平台相关依赖锁定结果。** 曾遇到 `@rolldown/binding-win32-x64-msvc` 与
    Linux runner 的 `EBADPLATFORM`。CI 应使用与所选 package manager 匹配的锁文件，并在 Linux runner 上验证。
15. **不要漏掉 Bun 的安装步骤。** 曾发生 GitHub Actions runner 上 `bun` 命令不存在。
16. **不要忽略 Node/Vite 版本要求。** 曾使用 Node `20.15.0`，而 Vite 要求 `20.19+` 或 `22.12+`。CI/本地使用满足项目版本要求的
    Node。
17. **不要盲目相信 GitHub Pages 已部署成功。** 过去 `https://yhuang060122.github.io/Telegram212/` 曾返回 404；部署后要验证
    Pages artifact、base path、路由 fallback 和实际 URL。
18. **不要因为本地能跑就认为 Worker 能跑。** 本地 CPython 与 Cloudflare Python Workers 运行时有差异。
19. **不要把 API Token、Gemini Key、Trading212 Key、Supabase Service Role Key 提交到仓库或前端。**
20. **不要在 GitHub Actions 中只部署 `api_worker/` 的入口而忘记它导入的根目录 `app/`。** 必须验证部署产物包含源码和运行依赖。
21. **不要声称 Workflow、Worker 或 Dashboard 功能已完成，除非查看过真实代码/运行结果。** 计划和已验证状态要明确区分。

### 用户协作方式

22. 用户希望通过自己动手学习。默认给出分阶段代码和操作步骤，用户本地运行测试后再提交 PR。
23. **不要直接修改 GitHub 仓库、创建分支、提交或开 PR，除非用户明确要求直接代办。**
24. 每个阶段建议独立 branch、测试和 PR，不要用一次大 PR 混合移动文件、改变逻辑和部署配置。

---

## 8. 推荐下一步行动清单

按优先级推进，不要一开始就全量重构。

### Step 0 — 新会话恢复现场

- [ ] 查看当前 Git 分支、工作区状态、最近提交和未提交修改。
- [ ] 读取 README、`pyproject.toml`、`requirements.txt`、`app/api/main.py`、实际 routes。
- [ ] 读取 `api_worker/src/main.py`、`api_worker/pyproject.toml`、`api_worker/wrangler.jsonc`、`uv.lock`（如果存在）。
- [ ] 检查 `.github/workflows/daily_report.yml`、`market_close.yml`、`deploy-api-worker.yml` 实际内容和最近运行状态。
- [ ] 检查 Dashboard 的 API client、TanStack Query hooks、Overview 页面是否接入真实数据。
- [ ] 用 FastAPI OpenAPI/route 清单核实实际接口，不从历史计划推断接口存在。

### Step 1 — 建立重构基线

- [ ] 本地运行现有 pytest、Ruff、coverage。
- [ ] 确认两个现有 Pipeline 的入口与运行参数。
- [ ] 记录 Supabase 当前表、约束和 Repository 方法。
- [ ] 为关键行为建立/补齐集成测试，不在同一提交里同时重构和改变业务结果。

### Step 2 — 整理配置和装配

- [ ] 统一环境变量读取与配置校验。
- [ ] 检查 import-time side effects。
- [ ] 将客户端、Repository 和 Service 初始化集中装配。
- [ ] 为测试提供可替换的 Repository / Gateway，不要求一次性引入大型 DI 框架。

### Step 3 — 抽取 Pipeline Use Cases

- [ ] 把 Daily Report 编排逐步抽取成可测试的 use case。
- [ ] 把 Market Close 编排逐步抽取成独立 use case。
- [ ] GitHub Actions 保留为轻量入口，负责环境配置、调用用例和退出码。
- [ ] 保留两条 Pipeline 的时间表和各自业务边界。

### Step 4 — 验证 API / Worker

- [ ] 验证 `/api/health`。
- [ ] 验证一个真实 Supabase 只读端点。
- [ ] 验证 positions、history、analytics、report 等实际存在的端点。
- [ ] 检查认证、CORS、超时、错误响应和数据更新时间。
- [ ] 检查 Worker 依赖兼容性与部署包导入路径。
- [ ] 为部署增加自动 Smoke Test；失败时不能把“部署命令成功”误认为服务可用。

### Step 5 — Dashboard 接入

- [ ] 建立/复用集中 API Client。
- [ ] 统一 API Base URL。
- [ ] 复用 TanStack Query hooks。
- [ ] 用真实 response schema 替换 mock data。
- [ ] 保留 loading、error、refresh、retry 和数据更新时间。
- [ ] 确保 React 不直接连接 Supabase。
- [ ] 验证 GitHub Pages 与 Lovable Preview 的 API 访问与认证流程。

### Step 6 — 可观测性和安全

- [ ] 评估是否新增 `pipeline_runs` 记录表。
- [ ] 显示 Daily 与 Market Close 最近成功/失败状态。
- [ ] 对关键路径错误发送 Telegram 告警。
- [ ] 对个人财务数据 API 配置认证/授权。
- [ ] 检查所有 secrets 不进入日志、前端构建产物或仓库。

---

## 9. 开始新会话时的工作原则

1. 先检查实际文件与 Git 状态，再提出具体改动；不要依赖旧上下文假设当前代码仍然一样。
2. 不要先做大规模文件搬迁。先建立测试基线，再逐步重构。
3. 先保证 `daily_report.yml` 和 `market_close.yml` 稳定，再改 API 和 Dashboard。
4. 每次改动只解决一个清晰的问题，并说明文件路径、修改原因、验证命令和预期结果。
5. 用户本地运行测试后再提交；默认由用户自行创建分支和 PR。
6. 如果需要最新 Cloudflare Workers、FastAPI、GitHub Actions 或 Bun 的平台行为，先核对官方文档，不依赖过时记忆。
7. 对任何未验证的内容标注“待核实”，不把建议当作完成事实。
8. 最终架构要保持单一业务逻辑来源：Pipeline 生产数据，Supabase 保存，FastAPI/Worker 提供查询，React 展示，Telegram 通知。

---

## 10. 新会话第一条建议提示

可以在新会话中发送：

> 请先阅读 `HANDOFF.md`，然后检查当前仓库的真实文件和 Git 状态。不要直接修改 GitHub。先核实 `app/api/`、`api_worker/`、两条现有
> GitHub Actions、Dashboard hooks 和当前测试结果，再给出一个最小风险的下一步 PR 计划。重点是渐进式重构，不重复实现 API，不让
> React 直连 Supabase，也不影响现有 daily_report 与 market_close 流程。
