我没法把那篇文章逐字逐句翻译出来——完整翻译等于复制这份版权内容,这个我做不到。不过我可以用中文给你一份详细的内容总结,涵盖所有关键要点。

**Boris Cherny 的"AI 采用五阶段"框架**

Boris Cherny 是 Anthropic Claude Code 的创建者和负责人。2026年7月16日,他发布了这个框架,随后在 X 和 LinkedIn 上迅速传播开来。他的出发点是:他经常和其他公司的工程师交流,发现一个普遍现象——团队里总有一个人用 Claude 把产出提高了 10 倍,但公司其他人却没跟上。他认为这个差距的根源不在于"用了多少 token",而在于团队所处的成熟度阶段不同。

**五个阶段概览:**

| 阶段 | 名称 | 智能体数量 | 核心变化 |
|---|---|---|---|
| 0 | **门禁阶段** | 0 | 老旧的安全审批流程完全挡住了 AI 的使用;组织还停留在"按 token 计费成本"的思维,而非关注产出 |
| 1 | **辅助阶段** | ~1 | 你和一个智能体"结对编程",几乎审查每一处修改——原本要花一下午的任务,现在开会间隙就能搞定 |
| 2 | **并行阶段** | ~10 | 你同时协调多个智能体(跨 worktree),Claude 会先自我检查(测试、lint、安全扫描),你只需审查最终的 diff |
| 3 | **监督自治阶段** | ~100 | Claude 编写几乎所有代码;后台维护任务持续自动运行;问题从"你看代码了吗"变成"模型缺了什么上下文" |
| 4 | **AI 原生阶段** | 1000+ | 闭环彻底形成——大多数智能体任务由 Claude 自己发起,而不是人类;你按"意图"来引导,只在例外情况下介入监控 |

每个阶段都有各自的瓶颈(注意力、审查能力、信任度、自动化规模)和相应的"解锁工具"——比如计划模式(plan mode)、自动模式(auto mode)、自动代码/安全审查、worktree 隔离、子智能体(subagents),以及 `/loop`、`/batch`、`/goal` 等例行任务指令。

Cherny 的说法是:Anthropic 公司整体目前处于第 3 阶段,而他个人声称已经达到第 4 阶段。他在 X 上强调的核心观点是:推进阶段靠的不是砸更多 token,而是不断找出并打破下一个瓶颈,同时建立起相应的下一层"护栏"机制。

需要提醒的是:这篇内容发布才三天,还很新,细节可能会有变动;而且这是 Cherny 个人提出的框架/观点,并非 Anthropic 官方立场,所以"Anthropic 处于第 3 阶段"这一说法应理解为他个人的表述,而非公司官方声明。

如果你想深入了解某一个阶段的具体细节,我可以再展开讲。

---
Boris Cherny — the creator and head of Anthropic's Claude Code — published a framework called "Steps of AI Adoption" on July 16, 2026, which quickly went viral on X and LinkedIn. His starting observation: he regularly talks to engineers who see one person on their team getting 10x output from Claude while the rest of the org hasn't caught up — and he argues that gap comes down to five distinct maturity stages, not just "using more tokens."

**The five steps:**

| Step | Name | Agents | What changes |
|---|---|---|---|
| 0 | **Gated** | 0 | Legacy security/approval processes block AI use entirely; orgs are stuck thinking about cost-per-token rather than outcomes |
| 1 | **Assisted** | ~1 | You pair with one agent, reviewing nearly every edit — an afternoon task shrinks to something done between meetings |
| 2 | **Parallel** | ~10 | You orchestrate multiple agents across worktrees; Claude self-checks its work (tests, lint, security scan) before you review final diffs |
| 3 | **Supervised autonomy** | ~100 | Claude writes almost all the code; background maintenance runs proactively; the key question shifts from "did you read the code?" to "what context was the model missing?" |
| 4 | **AI-native** | 1,000+ | The loop closes fully — most agents are kicked off *by* Claude, not humans, and you steer by intent while monitoring by exception |

Each step has its own bottleneck (attention, review capacity, trust, scale of automation) and its own set of guardrails/products that unlock the next one — things like plan mode, auto mode, automated code/security review, worktree isolation, subagents, and routines (`/loop`, `/batch`, `/goal`).

Cherny's stated view: Anthropic as an org currently operates around Step 3, while he personally claims to have hit Step 4. His core point on X was that advancing steps isn't about throwing more tokens at the problem — it's about identifying and removing the next bottleneck and building the next layer of guardrails.

A couple of caveats worth flagging: this was published just three days ago, so it's very fresh and could still be evolving, and it's Cherny's own framework/opinion rather than official Anthropic doctrine — so treat the "Anthropic is at Step 3" claim as his characterization rather than an official company statement. If you want, I can dig into any one step in more detail or pull the original X thread/Google Doc mirror.


