---
name: skill-repo-sync
description: 将仓库中的 skills 同步到另一个 skills 目录中：输入目标目录的绝对路径, 覆盖目标目录里同名的 skill 目录，并复制缺失的 skill，其他目标 skill 保持不变。
---

# Skill 仓库同步

把本仓库中的每个顶层 skill 同步到目标 skills 目录。
源仓库根目录由内置 Python 脚本根据自身位置自动反推，因此调用者只需要提供目标目录的绝对路径。

## 工作流

1. 确认目标路径是一个指向现有 skills 目录的绝对路径。
2. 运行内置脚本：

```bash
python3 {baseDir}/scripts/sync_skills.py /absolute/path/to/skills
```

3. 读取脚本输出，并报告哪些 skill 被创建或更新了。
4. 遇到任何校验错误或文件系统错误时立即停止，并报告精确的阻塞原因。

## 行为

- 把这个仓库根目录视为源目录。脚本会根据自身文件位置推导出仓库根目录，不需要单独传入源路径参数。
- 将仓库根目录下包含 `SKILL.md` 的顶层目录识别为源 skill。
- 对每个源 skill：
  - 如果目标中不存在，则创建该 skill
  - 如果目标中已经存在，则替换该目标 skill 目录
- 目标目录中的其他 skill 保持不变。
- 复制整个 skill 目录树，包括 `SKILL.md`、`scripts/`、`references/`、`assets/`、`agents/` 以及源 skill 目录里的其他文件。
- 忽略常见本地垃圾文件，例如 `.DS_Store`、`__pycache__` 和 `*.pyc`。

## 安全规则

- 要求目标路径在 shell 展开后仍然是绝对路径。
- 要求目标目录必须已经存在。
- 拒绝把源仓库根目录本身作为目标目录使用。
- 只替换那些在源仓库中存在的同名 skill 目录。不要删除或修改目标目录中无关的其他 skill。
- 优先使用内置脚本，不要临时改用 `cp` 或 `rsync` 等 shell 命令，以保持行为一致。

## 预演模式

使用 `--dry-run` 预览变更而不实际写入：

```bash
python3 {baseDir}/scripts/sync_skills.py /absolute/path/to/skills --dry-run
```

## 预期输出

- 打印推导出的源仓库根目录。
- 对每个源 skill 打印一行 `create` 或 `update`。
- 打印最终汇总，说明同步了多少个 skill。
