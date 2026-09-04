# NQ/MNQ MBO Research Project Design

## Goal

建立一个可复现、可安全配置的美股指数期货微观结构研究项目，用 Databento 的 CME Globex MBO 数据对 NQ 和 MNQ 进行五年范围报价，并支持小窗口探索。

## Scope

- 数据集：`GLBX.MDP3`
- schema：`mbo`
- 默认时间范围：`2021-09-04` 至 `2026-09-04`
- 默认品种：`NQ`、`MNQ`
- 默认询价范围：连续合约标识，另提供原始合约/产品根的可配置入口
- 默认探索：元数据和用户明确指定的小时间窗口；不自动下载五年原始数据
- 认证：从环境变量 `DATABENTO_API_KEY` 读取，不把密钥写入文件或日志

## Architecture

项目采用 Python 包结构，配置解析、Databento 客户端边界、询价输出和探索命令分离。CLI 负责把 YAML/命令行参数转换为 Databento 请求；核心函数返回可测试的结构化结果，终端层负责 JSON/表格展示。

## Files

- `src/us_futures_mbo/config.py`：配置模型、默认值和参数校验
- `src/us_futures_mbo/databento_client.py`：Databento API 的薄封装和错误归一化
- `src/us_futures_mbo/quote.py`：成本询价核心逻辑及 CLI
- `src/us_futures_mbo/explore.py`：元数据/小窗口探索核心逻辑及 CLI
- `config/quote.yaml`：默认报价配置
- `tests/`：不依赖网络的配置和结果解析测试
- `README.md`：安装、认证、报价、探索和授权说明

## Safety and Data Handling

- `.env`、API key、下载的数据文件、缓存和大型输出必须被 `.gitignore` 排除。
- 五年 MBO 只允许显式调用报价命令；探索命令要求明确的短时间范围或 dry-run。
- API 错误要保留可操作的错误信息，但不得回显密钥。
- 报价结果记录请求参数、计费字节数、美元金额和 Databento 原始响应摘要。

## Acceptance Criteria

1. 新项目有独立 Git 仓库，初始提交不包含密钥或原始数据。
2. 在没有 API key 时，命令给出清晰配置提示并以非零状态退出。
3. 配置可以表达 NQ/MNQ、`mbo`、五年日期范围以及 continuous/raw symbol type。
4. 询价命令能够调用 `metadata.get_cost`，并以结构化 JSON 输出报价。
5. 探索命令能够对小窗口调用 Databento metadata/历史接口，并输出 schema/字段/记录摘要。
6. 单元测试覆盖默认配置、非法日期/schema、报价响应解析和密钥不泄漏。
7. README 明确 MNQ 于 2019 年上市、数据授权/再分发限制，以及五年 MBO 可能产生的存储成本。
