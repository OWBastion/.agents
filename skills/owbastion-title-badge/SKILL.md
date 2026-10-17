---
name: owbastion-title-badge
description: 为 owbastion.com 的称号（成就）制作统一风格的六边形徽章图标：根据称号信息写出图像生成提示词，调用图像模型（或交给用户用 Gemini 等工具生成）得到洋红底原图，再抠底、去水印、按固定尺寸居中，产出可发布的透明 PNG。用于新增称号图标、重做或替换某个称号图标、批量补全缺失图标、把洋红底原图处理成透明 PNG；也用于用户说“给这个称号做个图标 / 徽章”“去掉 Gemini 水印和背景”。不用于称号目录数据、发放规则或 Portal 代码改动，也不用于网站品牌、英雄或地图素材。
---

# OWBastion 称号徽章

所有称号徽章共用一个固定的六边形金铜外壳，只有中央图案不同；这样玩家仅凭中央图案就能认出称号。流程分三步：写提示词、生成洋红底原图、后处理成透明 PNG。素材归 `owbastion-assets` 仓库所有，只在那里放文件。

## 路径约定

以下路径以 workspace 根目录为基准，`$ASSETS` 即 `owbastion-assets/assets/achievements`。

| 内容 | 位置 | 说明 |
| --- | --- | --- |
| 空白母版 | 本 skill 的 `assets/badge-master.png` | 生成时必须同时提供给图像模型 |
| 原图（洋红底，含水印） | `$ASSETS/original/achievement-<slug>.png` | 被 gitignore，仅留本地 |
| 成品透明 PNG | `$ASSETS/achievement-<slug>.png` | 发布件；CI 会自动生成 WebP 并上传 R2 |
| 提示词记录 | `owbastion-assets/prompts/achievements/<slug>.md` | 保留生成来源；`*.md` 被 gitignore，仅留本地 |

`<slug>` 用小写英文、数字、连字符，表达称号含义（`iron-gate`，不用拼音堆叠），已有文件名不要改，避免破坏引用。动手前先看 `$ASSETS` 与 `prompts/achievements/` 里有没有同名或同主题的称号，有就问清是重做还是新增。

## 步骤

1. **收集称号信息。** 需要：称号名称、类别、解锁条件、slug。中央主题、主色、额外参考图缺失时自己提出方案并说明理由，不要为这些追问；只有称号含义本身不明时才问用户。
2. **写提示词。** 读 [提示词模板](references/prompt-template.md)，只替换 `{{}}` 字段，外壳、背景和禁止项保持原文。同类称号先看 `owbastion-assets/prompts/achievements/` 里已有的写法，保持系列一致。把完整提示词存到 `prompts/achievements/<slug>.md`（头部写分类、状态、额外参考）。
3. **生成原图。** 能调用图像生成工具时，附上 `assets/badge-master.png`（及额外参考图）生成，存为 `$ASSETS/original/achievement-<slug>.png`。没有图像工具时，把提示词交给用户，说明需要连同母版图一起上传，并请用户把结果放到上述路径，然后继续。
4. **检查原图。** 打开原图确认：外框与母版一致、背景为纯 #FF00FF、中央主体完整且在内层面板内、没有文字数字。不合格就按模板末尾的失败表调整提示词重新生成，不要靠后期修补；水印和洋红底由脚本处理，不属于不合格。
5. **后处理。**
   ```bash
   uv run .agents/skills/owbastion-title-badge/scripts/finalize_badge.py \
     owbastion-assets/assets/achievements/original/achievement-<slug>.png \
     owbastion-assets/assets/achievements/achievement-<slug>.png \
     --preview <scratch-dir>/<slug>-preview.png
   ```
   脚本只依赖 `uv`（依赖写在脚本头部，自动安装）。它会：抠掉与边界相连的洋红底、丢弃徽章以外的所有碎块（Gemini 角标水印随之消失）、消除边缘洋红色溢、把徽章缩放到宽 1596 px 并居中放入 2048×2048 透明画布，与已发布的成品几何一致。预览图是白、深、灰三底的对照图，写到会话的临时目录，用完删除。
6. **验收。** 读脚本输出与预览图，确认：画布 2048×2048；徽章约 1594×1766 且中心约 (1024,1024)；四角 alpha 为 0；`magenta-like px` 为 0；在白、深、灰三种底上边缘都没有洋红或白色毛边，也没有残留水印；缩小到 64×64 仍能认出主体。主体本身偏洋红/粉紫时，脚本只会抠掉与边界相连的背景，内部颜色保留，但要重点检查边缘。
7. **交付。** 报告新增或修改的文件、验收结果。不要提交、推送或发布；`owbastion-assets` 的 AGENTS.md 要求这些由维护者决定。需要上线时说明：推送到 `main` 后 `publish-assets` 工作流会上传 PNG 并生成 WebP，称号目录里的图标引用由 `owbastion.codes` 侧负责，不在此处改动。

## 边界

- 不改母版外壳、不设计新外框、不为单个称号变更徽章尺寸；整套一致比单个好看更重要。
- 不做后期涂抹文字或手绘修补。原图不合格就重新生成。
- 覆盖已存在的成品前，先确认目标称号和影响，并保留旧文件的可恢复路径（用 `trash` 而非永久删除）。
