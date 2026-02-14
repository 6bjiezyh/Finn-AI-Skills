# Finn AI Skills

AI 内容创作相关 Skills 仓库，当前包含：`daily-ai-topic-planner`。

## Skills 列表

### 1) daily-ai-topic-planner
- 目录：`skills/daily-ai-topic-planner`
- 用途：为 AI 创作者生成每日选题包（长视频 + 短视频），并可上传到飞书多维表格。
- 覆盖方向：AI、n8n 自动化、AI 工具、Coze（扣子）、Vibe Coding、AIGC、AI 提效、AI 变现。

## 仓库结构

```text
Finn-AI-Skills/
  README.md
  skills/
    daily-ai-topic-planner/
      SKILL.md
      upload_feishu_bitable.py
      agents/
      assets/
      references/
      outputs/
```

## 使用方式

### 方式 A：直接克隆并引用本地路径（推荐）

```bash
git clone https://github.com/6bjiezyh/Finn-AI-Skills.git
```

然后在你的 Agent/工具中使用 Skill 路径：
- `skills/daily-ai-topic-planner/SKILL.md`

### 方式 B：通过 Skill Installer（如果你的环境支持）

- 仓库：`6bjiezyh/Finn-AI-Skills`
- Skill 子目录：`skills/daily-ai-topic-planner`

## daily-ai-topic-planner 输出约定

该 Skill 默认输出四个部分：
- `LongVideoIdeas`: 3 条
- `ShortVideoIdeas`: 7 条
- `PublishPriority`: 1 条长视频 + 2 条短视频
- `ExpandedTopicPool20`: 20 条（必选）

## Feishu 上传（可选）

脚本：`skills/daily-ai-topic-planner/upload_feishu_bitable.py`

需要在运行环境配置以下变量（建议放在 `.env`）：
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_APP_TOKEN`
- `FEISHU_TABLE_ID`

## 安全说明

- 不要提交任何真实密钥或账号凭据。
- `.env`、`outputs/`、缓存文件应加入 `.gitignore`。

## License

建议添加 `LICENSE`（例如 MIT），便于其他用户明确复用范围。
