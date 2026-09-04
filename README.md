# US Futures MBO Research

这是一个用于 NQ/MNQ CME MBO 数据研究的最小、可复现项目。Databento 数据集使用 `GLBX.MDP3`，默认 schema 为 `mbo`。

## 安装与认证

需要 Python 3.11+ 和 uv：

```powershell
uv sync --extra dev
Copy-Item .env.example .env
# 在 .env 中填写 DATABENTO_API_KEY
```

密钥只从 `DATABENTO_API_KEY` 环境变量读取，`.env` 已被 Git 忽略。不要把密钥写进命令行参数、配置文件或报告。

## 询价

修改 `config/quote.yaml` 后运行：

```powershell
uv run python -m us_futures_mbo.cli quote --config config/quote.yaml
```

该命令调用 Databento `metadata.get_cost`，只返回报价和计费字节数，不下载五年原始数据。默认范围是 2021-09-04 至 2026-09-04 的 NQ/MNQ continuous symbols；如需所有原始到期合约，应先修改 symbols 和 `stype_in`，再单独询价。

## 小窗口探索

探索必须显式指定开始和结束时间，默认最多 24 小时：

```powershell
uv run python -m us_futures_mbo.cli explore `
  --config config/quote.yaml `
  --start 2026-09-01T13:30:00Z `
  --end 2026-09-01T14:30:00Z
```

探索使用 Databento metadata 接口获取字段和记录数摘要，`raw_data_downloaded` 应为 `false`。如果要扩大窗口，必须显式加入 `--allow-large-window`。

## 带缓存的下载

下载命令要求显式提供时间范围。它会生成稳定 cache key，跳过已通过 DBN metadata 校验的文件，失败时使用 `.part` 文件，成功后写入 manifest 和 SHA-256：

```powershell
uv run python -m us_futures_mbo.cli download `
  --config config/quote.yaml `
  --start 2026-09-02T00:00:00Z `
  --end 2026-09-02T20:00:00Z
```

原始 DBN 文件按 `data/raw/...` 保存，manifest 在 `data/manifest/`。后续如需大量列筛选，可从 raw DBN 派生 Parquet；不要对 raw MBO 记录去重或重新排序，必须保留 `sequence` 顺序。

## 口径提醒

- NQ 是 E-mini Nasdaq-100 期货，MNQ 是 Micro E-mini Nasdaq-100 期货；合约乘数不同，但 MBO 数据量取决于订单事件，不取决于合约乘数。
- MNQ 于 2019 年上市，因此不存在 2019 年以前的 MNQ 历史数据。
- `mbo` 是逐订单事件级数据，通常包含 order ID、动作、方向、价格、数量和序列信息；是否能用于转售、拼车或再分发，要以 CME/Databento 的授权条款为准。
- 五年 MBO 可能产生较大的账单、下载量和存储成本；先询价，再决定是否下载。

## 开发

```powershell
uv run pytest -q
```
