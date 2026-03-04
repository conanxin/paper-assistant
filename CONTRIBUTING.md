# Contributing

欢迎 PR 与 Issue。

## Development

```bash
cd paper-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m compileall app.py src scripts/demo_e2e.py
PYTHONPATH=. python3 scripts/demo_e2e.py
```

## PR Checklist

- [ ] 不提交 `.venv/`、`__pycache__/`、`evidence/` 产物
- [ ] `compileall` 通过
- [ ] `scripts/demo_e2e.py` 可运行
- [ ] README 已同步更新（若涉及行为变化）
- [ ] 涉及审计逻辑时补充验证说明

## Coding Style

- 保持模块边界清晰（adapter/parser/analyzer/auditor/sink/pipeline）
- 新增功能优先可验证（输出文件路径、命令结果、日志片段）
