# 📊 每日 AI 动态与 GitHub 热榜（2026-11-25）

> 数据统计：GitHub 热榜 5 项 · AI 动态 5 条 · 中文介绍由 DeepSeek 生成

## 一、GitHub 开源项目热度榜 TOP5

### 1. Marvisak/VIctory  ⭐ 11,883
**语言**: Rust ｜ **Stars**: 11,883 ｜ **Forks**: 1,769
**这是什么**: 这是一个用 Rust 语言编写的实验性项目，目标是尝试让《GTA VI》（侠盗猎车手6）这款主机游戏能在普通电脑上运行。它属于社区自发的“移植”尝试，并非官方版本。
**能用来做什么**: 可以用来了解游戏爱好者如何通过技术手段挑战让主机独占游戏在 PC 上跑起来，适合关注 GTA VI 动态或对游戏逆向工程感兴趣的读者围观学习。
**适用领域**: 游戏开发、逆向工程、系统编程学习
**对新手有什么帮助**: 适合对游戏底层原理好奇的新手，通过看别人怎么“折腾”能初步理解游戏运行和平台兼容是怎么回事。
🔗 [项目地址](https://github.com/Marvisak/VIctory)

### 2. xcl-dev/xcl  ⭐ 8,063
**语言**: Rust ｜ **Stars**: 8,063 ｜ **Forks**: 1,089
**这是什么**: 这是一个用 Rust 写的兼容层项目，让 Windows 电脑能够直接运行 Xbox Series 主机的游戏代码。它重新实现了 Xbox 主机的系统功能，并把主机显卡的着色器翻译成 Windows 能用的格式。
**能用来做什么**: 典型场景是在 Windows PC 上运行原本只能在 Xbox Series 上玩的游戏，类似“让电脑听懂 Xbox 游戏的语言”。
**适用领域**: 游戏兼容层、主机模拟、系统编程、图形渲染
**对新手有什么帮助**: 适合想了解“兼容层”和“模拟器”原理的新手，能帮你明白不同平台之间游戏是怎么被“翻译”过来的。
🔗 [项目地址](https://github.com/xcl-dev/xcl)

### 3. EL4CTEO/fast-anything  ⭐ 3,769
**语言**: Rust ｜ **Stars**: 3,769 ｜ **Forks**: 271
**这是什么**: 这个项目提出一个思路：不要为了提速就把整个程序用 Rust 重写，而是只找出最慢的那 5% 代码，用编程助手把它们改写成 Rust，再验证改写前后行为一致。
**能用来做什么**: 可以用来给运行缓慢的 Python、Node.js 或 Ruby 程序做“局部提速”，只优化瓶颈部分，省时省力。
**适用领域**: 性能优化、后端开发、Python/Node/Ruby 应用维护
**对新手有什么帮助**: 适合刚接触性能优化的新手，教你一种“只改关键部分”的务实思路，避免盲目重写整个项目。
🔗 [项目地址](https://github.com/EL4CTEO/fast-anything)

### 4. AFK-surf/xnulinux  ⭐ 3,670
**语言**: C ｜ **Stars**: 3,670 ｜ **Forks**: 172
**这是什么**: 这是一个用 C 语言写的项目，把苹果 macOS 的核心系统（XNU）做成一个可以加载进 Linux 的模块，相当于给 arm64 架构的 Linux 加了一层“macOS 人格”。
**能用来做什么**: 可以用来在 arm64 Linux 上研究或运行 macOS 相关的系统行为，适合做操作系统实验和兼容性探索。
**适用领域**: 操作系统研究、内核开发、跨平台兼容
**对新手有什么帮助**: 适合对操作系统内核感兴趣的新手，能帮你直观理解“内核模块”和“系统兼容层”是怎么工作的。
🔗 [项目地址](https://github.com/AFK-surf/xnulinux)

### 5. 4lwayz/portwatch-vi  ⭐ 3,202
**语言**: JavaScript ｜ **Stars**: 3,202 ｜ **Forks**: 89
**这是什么**: 这是一个用 JavaScript 写的网站，专门追踪《GTA VI》是否已经能在 PC 上运行，每天更新社区里各种重编译和模拟尝试的进展。
**能用来做什么**: 可以用来一站式查看 GTA VI 的 PC 运行进展，不用到处翻论坛，适合玩家日常关注动态。
**适用领域**: 网页开发、游戏资讯、社区追踪
**对新手有什么帮助**: 适合零基础想学做小网站的新手参考，也能直接帮你及时了解 GTA VI 在 PC 上的最新情况。
🔗 [项目地址](https://github.com/4lwayz/portwatch-vi)

## 二、昨日 AI 领域动态

### Hacker News

- **[LLM agents work for their parent companies, not for you](https://michaelharley.net/posts/2026/11/01/llm-agents-work-for-their-parent-companies-not-for-you/)**（👍 973）
  - 摘要：文章指出LLM智能体往往优先服务于其母公司（如OpenAI、Anthropic）的商业利益而非用户利益，提醒人们警惕智能体在推荐、决策中隐含的厂商偏向，值得关注AI代理的独立性与可信度问题。
- **[Working with AI](https://www.anthropic.com/research/working-with-ai)**（👍 70）
  - 摘要：一篇关于如何在日常工作中与AI协作的实践性讨论，总结使用AI工具提升效率的经验与注意事项，对希望将AI融入工作流的从业者有参考价值。

### arXiv cs.AI

- **[OmniAct: One Policy, One Million Embodiments](https://arxiv.org/abs/2611.33158v1)**
  - 摘要：论文提出OmniAct，用单一策略控制跨百万种不同形态的机器人身体，探索通用具身智能的规模化路径，对机器人基础模型与跨本体泛化研究有重要意义。

### 量子位

- **[高德发布世界模型ABot-World 0.5，支持构建音画同步、可实时重塑的AI物理世界](https://www.qbitai.com/2026/11/512454.html)**
  - 摘要：高德发布世界模型ABot-World 0.5，可生成音画同步且能实时重塑的AI物理世界，体现国内地图与出行厂商切入世界模型赛道，值得关注其在自动驾驶与空间智能上的应用潜力。

### 新智元

- **[华为云发布智能体伙伴开放计划 帮助伙伴搭建流量入口](https://aiera.com.cn/2026/11/24/other/admin/125067/%e5%8d%8e%e4%b8%ba%e4%ba%91%e5%8f%91%e5%b8%83%e6%99%ba%e8%83%bd%e4%bd%93%e4%bc%99%e4%bc%b4%e5%bc%80%e6%94%be%e8%ae%a1%e5%88%92-%e5%b8%ae%e5%8a%a9%e4%bc%99%e4%bc%b4%e6%90%ad%e5%bb%ba%e6%b5%81%e9%87%8f/)**
  - 摘要：华为云推出智能体伙伴开放计划，帮助合作伙伴搭建智能体流量入口，反映云厂商正围绕智能体生态展开渠道与平台竞争，对开发者选择智能体落地平台有参考意义。
