# 每日 AI 动态 + GitHub 热榜推送（GitHub Actions 版）

每天北京时间 **09:00** 自动运行（含周末），生成一份报告并推送到你的钉钉群：

- **GitHub 开源项目热度榜 TOP10**：官方 Search API 抓取近 7 天新创建、Star 数最高的 10 个项目，包含中文简介 + 用途介绍
- **昨日 AI 领域动态**：聚合 Hacker News、Reddit r/MachineLearning、arXiv cs.AI、机器之心、量子位 5 个来源
- 中文简介与摘要由 **DeepSeek API** 生成
- 报告同时生成 **Markdown / Word / PDF** 三种格式，提交到仓库 `daily-reports/YYYY-MM-DD/`，钉钉消息内附下载链接

## 一、需要配置的 Secrets（2~3 个）

打开仓库 **Settings → Secrets and variables → Actions → New repository secret**：

| Secret 名称 | 必填 | 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | 是 | [platform.deepseek.com](https://platform.deepseek.com) 申请，模型为 deepseek-chat，费用很低 |
| `DINGTALK_WEBHOOK` | 是 | 钉钉群机器人 Webhook URL，见下方"创建钉钉机器人" |
| `DINGTALK_SECRET` | 否 | 仅在机器人安全设置选择了**加签**时需要 |

### 创建钉钉机器人

1. 钉钉群 → 群设置 → **机器人** → **添加机器人** → **自定义**（Webhook）
2. 安全设置二选一（推荐**加签**）：
   - **加签**：复制密钥，填入 `DINGTALK_SECRET`；
   - **自定义关键词**：关键词填 `每日报告`（报告正文含此词，无需额外配置）；
3. 复制 Webhook 地址（形如 `https://oapi.dingtalk.com/robot/send?access_token=xxx`），填入 `DINGTALK_WEBHOOK`

> ⚠️ 钉钉自定义机器人 webhook 不能直接发送文件附件，因此采用"钉钉内直接看完整 Markdown + 仓库里下载 Word/PDF"的方式。

## 二、手动测试

1. 仓库 **Actions** 页面 → 左侧 **Daily Report Push** → **Run workflow** → 绿色按钮
2. 运行成功后，查看钉钉群是否收到报告；完整文件在仓库 `daily-reports/` 目录

## 三、文件结构

```
.github/workflows/daily-report.yml   定时任务（cron: 0 1 * * * = 北京 09:00）
scripts/generate_report.py           主脚本（采集→摘要→渲染→推送）
scripts/sources.py                   数据源（GitHub 热榜 + 5 个新闻源）
scripts/llm.py                       DeepSeek 摘要（无 Key 时自动降级为原文）
scripts/render.py                    MD / DOCX / PDF 渲染
scripts/notify.py                    钉钉推送（超长自动拆条）
requirements.txt                     Python 依赖
```

## 四、自定义

- **推送时间**：修改 `.github/workflows/daily-report.yml` 中 `cron`。北京 09:00 = UTC 01:00 = `0 1 * * *`；改成下午 3 点 = UTC 07:00 = `0 7 * * *`
- **数据源**：编辑 `scripts/sources.py` 中的 `RSS_SOURCES` 和 `ai_news()` 增减来源
- **榜单口径**：`scripts/sources.py` 的 `github_trending(days=7)` 可调整统计窗口
- **不配置 DeepSeek Key**：报告仍会生成，只是用项目自带英文描述、无中文摘要

## 五、注意事项

- GitHub Actions 免费额度：私有仓库 2000 分钟/月，本任务每天约 5~10 分钟，绰绰有余
- 定时任务高峰期可能延迟几分钟执行，属正常现象
- 仓库若超过 60 天无任何提交，GitHub 可能暂停定时触发，保持仓库活跃即可
- 每次运行会向仓库新增一个 `daily-reports/日期/` 目录，属预期行为
