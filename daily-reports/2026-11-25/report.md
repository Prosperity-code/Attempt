# 📊 每日 AI 动态与 GitHub 热榜（2026-11-25）

> 数据统计：GitHub 热榜 5 项 · AI 动态 5 条 · 中文介绍由 DeepSeek 生成

## 一、GitHub 开源项目热度榜 TOP5

### 1. Marvisak/VIctory  ⭐ 11,860
**语言**: Rust ｜ **Stars**: 11,860 ｜ **Forks**: 1,768
**这是什么**: 这是一个用 Rust 语言编写的实验性项目，目标是尝试让《GTA VI》（侠盗猎车手6）这款原本只在游戏主机上运行的游戏，能在普通电脑上跑起来。它属于社区自发的技术探索，并非官方版本。
**能用来做什么**: 可以用来了解游戏移植和模拟的技术原理，或者关注社区如何尝试在 PC 上运行主机独占游戏。
**适用领域**: 游戏模拟、逆向工程学习、Rust 编程实践
**对新手有什么帮助**: 适合对游戏运行原理好奇的新手围观学习，但项目尚处实验阶段，不能直接当成品游戏使用。
🔗 [项目地址](https://github.com/Marvisak/VIctory)

### 2. xcl-dev/xcl  ⭐ 8,053
**语言**: Rust ｜ **Stars**: 8,053 ｜ **Forks**: 1,087
**这是什么**: 这是一个用 Rust 写的兼容层工具，让 Windows 电脑能够直接运行 Xbox Series 主机的游戏代码。它会重新实现主机系统的底层功能，并把主机显卡的着色器翻译成 Windows 能识别的格式。
**能用来做什么**: 典型场景是在 Windows PC 上尝试运行 Xbox Series 游戏，或研究主机与 PC 之间的兼容技术。
**适用领域**: 游戏兼容层、主机模拟、图形渲染技术
**对新手有什么帮助**: 适合想了解“兼容层”如何工作的新手，能直观看到不同平台软件如何互相打通。
🔗 [项目地址](https://github.com/xcl-dev/xcl)

### 3. EL4CTEO/fast-anything  ⭐ 3,765
**语言**: Rust ｜ **Stars**: 3,765 ｜ **Forks**: 271
**这是什么**: 这个项目提出一个提速思路：不必把整个程序都用 Rust 重写，只把最慢的那 5% 关键函数用 Rust 改写即可。它提供工具帮你分析 Python、Node 或 Ruby 程序的性能瓶颈，并借助编程助手完成改写和验证。
**能用来做什么**: 当你的 Python/Node/Ruby 程序跑得慢时，可以用它定位慢函数，只重写这部分来提速。
**适用领域**: 性能优化、后端开发、编程语言混合开发
**对新手有什么帮助**: 适合已经会一点编程、想学性能优化的新手，能帮你用最小改动获得明显提速。
🔗 [项目地址](https://github.com/EL4CTEO/fast-anything)

### 4. AFK-surf/xnulinux  ⭐ 3,666
**语言**: C ｜ **Stars**: 3,666 ｜ **Forks**: 172
**这是什么**: 这是一个用 C 语言写的项目，把苹果 macOS 的核心系统（XNU）做成一个可以加载进 Linux 的模块，相当于在 arm64 架构的 Linux 上模拟出 macOS 的运行环境。
**能用来做什么**: 可用于在 Linux 设备上研究或运行 macOS 相关程序，探索跨操作系统的兼容方案。
**适用领域**: 操作系统研究、内核开发、跨平台兼容
**对新手有什么帮助**: 适合对操作系统底层感兴趣的学习者，是理解“内核”和“系统兼容”概念的进阶素材。
🔗 [项目地址](https://github.com/AFK-surf/xnulinux)

### 5. 4lwayz/portwatch-vi  ⭐ 3,192
**语言**: JavaScript ｜ **Stars**: 3,192 ｜ **Forks**: 89
**这是什么**: 这是一个用 JavaScript 写的网页小工具，专门追踪《GTA VI》是否已经能在 PC 上运行。它每天更新社区里各种重编译和模拟项目的进展，让你一眼看到最新状态。
**能用来做什么**: 想随时了解 GTA VI 在 PC 上的运行进展时，打开这个追踪页面即可查看每日更新。
**适用领域**: 游戏资讯、社区追踪、网页开发
**对新手有什么帮助**: 对游戏玩家来说很直观，能帮你省去到处搜索的时间，也适合新手学习如何做一个简单的信息追踪网页。
🔗 [项目地址](https://github.com/4lwayz/portwatch-vi)

## 二、昨日 AI 领域动态

### Hacker News

- **[LLM agents work for their parent companies, not for you](https://michaelharley.net/posts/2026/11/01/llm-agents-work-for-their-parent-companies-not-for-you/)**（👍 972）
  - 摘要：文章指出 LLM 智能体往往优先服务于其开发公司的商业利益而非用户利益，提醒人们警惕智能体在推荐、决策中的隐性偏向。
- **[Working with AI](https://www.anthropic.com/research/working-with-ai)**（👍 70）
  - 摘要：一篇探讨如何与 AI 协作的实践性文章，讨论把 AI 融入日常工作流的方法与注意事项，对提升个人生产力有参考价值。

### arXiv cs.AI

- **[OmniAct: One Policy, One Million Embodiments](https://arxiv.org/abs/2611.33158v1)**
  - 摘要：arXiv 论文提出 OmniAct，用单一策略控制上百万种不同形态的机器人身体，向通用具身智能体的跨形态泛化迈出一步。

### 量子位

- **[高德发布世界模型ABot-World 0.5，支持构建音画同步、可实时重塑的AI物理世界](https://www.qbitai.com/2026/11/512454.html)**
  - 摘要：高德发布世界模型 ABot-World 0.5，可生成音画同步且支持实时重塑的 AI 物理世界，显示地图与出行平台正切入世界模型赛道。

### 新智元

- **[华为云发布智能体伙伴开放计划 帮助伙伴搭建流量入口](https://aiera.com.cn/2026/11/24/other/admin/125067/%e5%8d%8e%e4%b8%ba%e4%ba%91%e5%8f%91%e5%b8%83%e6%99%ba%e8%83%bd%e4%bd%93%e4%bc%99%e4%bc%b4%e5%bc%80%e6%94%be%e8%ae%a1%e5%88%92-%e5%b8%ae%e5%8a%a9%e4%bc%99%e4%bc%b4%e6%90%ad%e5%bb%ba%e6%b5%81%e9%87%8f/)**
  - 摘要：华为云推出智能体伙伴开放计划，帮助合作伙伴搭建流量入口，反映云厂商正围绕智能体生态争夺应用分发渠道。
