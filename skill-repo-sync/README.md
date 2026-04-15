# Skill Repo Sync

这是一个用于同步个人 skills 仓库内容的本地 skill。它的目标很单一：把一个源 skills 目录里的 skill 同步到另一个目标 skills 目录中。

同步规则是：

- 源仓库里有、目标目录里也有的同名 skill：整目录覆盖更新
- 源仓库里有、目标目录里没有的 skill：直接复制过去
- 目标目录里已有但源仓库里没有的其他 skill：完全不动
- 每个同步后的目标 skill 会删除顶层 `README.md`

这个 skill 现在要求显式传入两个绝对路径：源目录和目标目录。

## 这个 skill 做什么

- 把你提供的源目录当作源 skills 仓库
- 自动发现源目录里所有包含 `SKILL.md` 的顶层 skill 目录
- 将这些 skill 同步到指定目标目录
- 每个已同步的目标 skill 会在同步完成后删除顶层 `README.md`
- 同步时保留目标目录中不属于本仓库的其他 skill
- 支持 `--dry-run` 预演，不实际写入
- 忽略 `.DS_Store`、`__pycache__`、`*.pyc` 等常见无关文件

## 适用场景

- 你在这个仓库里维护自己的 skills，想批量发布到另一个 skills 目录
- 你希望把本仓库作为“个人 skill 源仓库”，定期刷新某个实际使用目录
- 你想新增一个 skill 时自动复制过去，同时更新已有同名 skill

## 使用方式

正式同步：

```bash
python3 {baseDir}/scripts/sync_skills.py /absolute/path/to/source-skills /absolute/path/to/destination-skills
```

只预览，不写入：

```bash
python3 {baseDir}/scripts/sync_skills.py /absolute/path/to/source-skills /absolute/path/to/destination-skills --dry-run
```

## 行为说明

- 源路径必须是绝对路径
- 目标路径必须是绝对路径
- 源目录必须已经存在
- 目标目录必须已经存在
- 不能把同一个目录同时作为源和目标
- 同步是按 skill 目录进行，不是按单文件做增量 merge
- 对于同名 skill，目标中的旧目录会被新的完整目录替换
- 同步完成后，会从每个已同步目标 skill 的顶层删除 `README.md`

## 输出结果

脚本会输出：

- 源目录路径
- 目标目录路径
- 每个 skill 的 `create` 或 `update` 结果
- 最终同步数量汇总

## 相关文件

- [SKILL.md](./SKILL.md)
- [scripts/sync_skills.py](./scripts/sync_skills.py)
