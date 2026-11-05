# 桌宠参考与表达研究

调研日期：2026-11-05。结论用于产品设计，不代表相关人物授权或背书。

## GitHub 实现参考

| 项目 | 已核实的能力 | 本项目采用的思路 |
| --- | --- | --- |
| [arthghori/water-reminder-desktop-pet](https://github.com/arthghori/water-reminder-desktop-pet) | Python / PySide6，透明置顶、拖拽、定时气泡、喝水确认、稍后提醒、托盘、每日记录 | 最贴近需求；参考交互与技术选型 |
| [Dametime-0/desktop-pet](https://github.com/Dametime-0/desktop-pet) | PySide6，喝水/休息提醒，本地台词与人格包，透明气泡 | 提醒和日常互动分开，离线可用 |
| [zebangeth/PawPal](https://github.com/zebangeth/PawPal) | Electron 桌宠，喝水/休息提醒，Windows/macOS，本地优先 | 参考轻打扰、常驻陪伴方式 |

这是从零实现的独立项目，未复制上述项目代码或角色素材。选择 PySide6，便于先交付 Windows 透明桌宠与便携 exe。

## 用户指定的 skill

- 来源：[Roc-Dove/shao-alan-skill](https://github.com/Roc-Dove/shao-alan-skill)
- 已读取 `SKILL.md`、`references/research/01-primary-content.md`、`02-expression-dna.md`。
- 参考提交：`899ae3e77c14a07a930c21a16856dea1b8385c6d`；研究快照截至 2026-10-15。
- 许可：MIT。未把完整 skill 搬进应用；表达规则的改写归纳保留来源及许可，见 `THIRD_PARTY_NOTICES.md`。
- 使用其“口语判断 → 条件/自我校正 → 一个可执行动作”的节奏，低频使用“说实话、对吧”和有意义的短英文。
- 保留身体、注意力、生活控制权、行动等主题；不虚构其私人经历，不把原创台词标成原话。
- 仅有标题、搜索摘要或未经核对的 ASR 的内容，不能升级为本人精确引语。

应用中的所有台词均为原创风格模拟，非邵艾伦原话。原创建模不使用第一人称假冒其经历。

## 补充网络检索与大水梗

- [《大水理论流行，年轻人开始学习如何过日子》｜界面新闻｜2026-10-25](https://www.jiemian.com/article/15234992.html)：把此轮“大水理论”的传播者指向孙浩然；邵艾伦的“薄肌”是关联的另一传播线。本文只用于梗的传播背景，不用于校正 skill 中的人物模型。
- [《什么是大水理论》｜涂阿燃｜2026-10-10](https://2aran.com/articles/research/topics/big-water-theory)：第三方语境参考，不能当作本人原话证据。
- 搜索到 [2026-11-04 署名帖的第三方索引](https://xzhishu.com/tweets/3f9625fa-3dcb-4775-90ef-aacb5b54370f)，给出 [X 原帖链接](https://x.com/AlanShao111/status/2117940671621288310)。未核验原帖正文，且超出 skill 时间窗，因此未纳入台词人格依据。

设计采用“大水在手、基础出装、睡大觉”等生活化梗作原创改编，不声称大水理论由邵艾伦提出，不采用“喝得越多越成功”等伪因果。

## 喝水行为边界

[NHS：Water, drinks and hydration](https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/water-drinks-nutrition/) 建议全天规律饮水，并指出其他饮品和食物中的水分也计入摄入。应用只提醒、记录，不开具个体化饮水处方。

因此“大水”表示大瓶放在手边、分次适量喝；不鼓励一次灌完、不搞补喝、不按体重强制计算目标。默认 200 ml 只是可修改的记账单位，1600 ml 只是个人可编辑的界面目标，不代表每日总摄入建议。完成目标后仍可按个人需求记录，不额外推送冲量台词。需限水的人按医嘱使用。

## MVP 产品约定

- Windows 优先，无 API Key、无后台网络请求、无自动上传。
- 透明置顶、可拖拽、呼吸/眨眼/举水动画，点击换一句，双击打开面板，右键菜单。
- 默认 45 分钟喝水提醒，默认 20 分钟碎碎念，默认 23:00–08:00 免打扰，均可改。
- 喝了、稍后 10 分钟、暂停/恢复、系统托盘、可选系统通知。
- 本地记录、按本地日期统计、今日撤销、睡眠唤醒后最多提醒一次、不补发堆积提醒。
- 分时段/随机台词、自定义台词，不依赖在线大模型。
- 角色为原创程序绘制卡通占位形象，非真人肖像还原；可在后续版本替换授权角色素材。
