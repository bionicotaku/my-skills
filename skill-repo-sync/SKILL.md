---
name: skill-repo-sync
description: 将一个 skills 源目录中的 skills 同步到另一个 skills 目标目录中：输入源目录和目标目录的绝对路径，覆盖目标目录里同名的 skill 目录，并复制缺失的 skill，其他目标 skill 保持不变。适用于需要在两个本地 skills 目录之间做发布、镜像、刷新或更新的场景。
---

# Skill 仓库同步

把一个 skills 源目录中的每个顶层 skill 同步到目标 skills 目录。
调用时显式传入源目录和目标目录的绝对路径，不再依赖脚本位置去推导源仓库。

## 工作流

1. 确认源目录和目标目录都是现有目录，并且两者都使用绝对路径。
2. 运行内置脚本：

```bash
python3 {baseDir}/scripts/sync_skills.py /absolute/path/to/source-skills /absolute/path/to/destination-skills
```

3. 读取脚本输出，并报告哪些 skill 被创建或更新了。
4. 遇到任何校验错误或文件系统错误时立即停止，并报告精确的阻塞原因。

## 行为

- 将源目录下包含 `SKILL.md` 的顶层目录识别为源 skill。
- 对每个源 skill：
  - 如果目标中不存在，则创建该 skill
  - 如果目标中已经存在，则替换该目标 skill 目录
- 目标目录中的其他 skill 保持不变。
- 复制整个 skill 目录树，包括 `SKILL.md`、`scripts/`、`references/`、`assets/`、`agents/` 以及源 skill 目录里的其他文件。
- 忽略常见本地垃圾文件，例如 `.DS_Store`、`__pycache__` 和 `*.pyc`。

## 安全规则

- 要求源路径和目标路径在 shell 展开后仍然是绝对路径。
- 要求源目录和目标目录都必须已经存在。
- 拒绝把同一个目录同时作为源和目标使用。
- 只替换那些在源目录中存在的同名 skill 目录。不要删除或修改目标目录中无关的其他 skill。
- 优先使用内置脚本，不要临时改用 `cp` 或 `rsync` 等 shell 命令，以保持行为一致。

## 预演模式

使用 `--dry-run` 预览变更而不实际写入：

```bash
python3 {baseDir}/scripts/sync_skills.py /absolute/path/to/source-skills /absolute/path/to/destination-skills --dry-run
```

## 预期输出

- 打印源目录路径。
- 打印目标目录路径。
- 对每个源 skill 打印一行 `create` 或 `update`。
- 打印最终汇总，说明同步了多少个 skill。
