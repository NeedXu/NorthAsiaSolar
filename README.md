# North Asia Solar Intelligence

个人北亚光伏情报工作台，覆盖日本、韩国、台湾。React 19 + TypeScript + Vite，中文 UI，深浅主题与移动端布局。

## 当前状态

代码已具备「公开 RSS → 每日采集 → JSON 归档 → GitHub Pages → 浏览器读取」流程，并增加受 GitHub 权限保护的公开访问开关。**已于 2026-11-04 成功部署网站，首页与数据 HTTP 验证已通过；关闭方式正在验证**。网站地址：https://needxu.github.io/NorthAsiaSolar/ 。GitHub Actions 首次采集已于 2026-11-04 18:24（北京时间）成功读取两个来源并归档 1 条相关报道。发布状态由 `.deploy/public-access.json` 管理，实际验证结果记录在 `.deploy/site-status.json`。本次云环境对 `www.pv-magazine.com` 和 `www.pv-tech.org` 返回代理 403，禁止绕过。当前 `public/data/feed.json` 已由 GitHub Actions 写入真实采集结果，不包含模拟新闻。

- 真实数据模式默认开启，显示原始 RSS 标题、摘录、发布日期、原文链接与规则分类。
- 模拟版本通过「查看界面演示」独立进入，不会自动混入真实列表。
- 市场装机、价格与预测没有可靠数据源时不显示模拟值。
- 当前没有 AI 翻译或业务影响分析，来源语言保持原样，规则标签未经人工核实。
- 个人工作台尚无登录；公开部署后任何人都可以访问，不可存入个人/企业机密。

## 推荐上线方案

使用已有 GitHub 仓库配合 GitHub Pages 与 GitHub Actions，无需单独租用应用服务器，也无需在聊天中提供密钥。是否免费取决于仓库可见性及 GitHub 账户套餐；私有仓库的 Pages 可用性和 Actions 用量需要确认，不能默认更改仓库可见性。

部署前由仓库所有者确认：

1. 同意将本项目代码（含 `.github/workflows/daily-intelligence.yml`）提交到 `NeedXu/NorthAsiaSolar` 的 `main` 分支。
2. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。如果不存在这个选项，检查仓库套餐/管理员权限，不要擅自将私有仓库改为公开。
3. 仓库策略须允许 Actions 向内容分支提交 `public/data/feed.json`。受保护的 `main` 可能阻止机器人提交；应由所有者决定采用允许的机器人权限或改造为独立数据存储。
4. 在 **Actions** 页面运行 **Daily intelligence and Pages deployment**，检查采集、构建、发布均成功。
5. 只使用 **Pages 部署结果实际给出的 URL**。在一次真实部署与采集完成前，不应把猜测的地址当作可用网址。

上线后，工作流每天 **北京时间 08:00 / UTC 00:00** 尝试采集，GitHub 调度可能延迟或暂停，不提供准点保证。网页每 5 分钟检查一次发布的数据，重新打开页面也会检查。浏览器关闭不会影响已启用的 GitHub 定时任务。任务失败时 Actions 显示失败，网页显示来源健康状态及最后成功时间，不将失败当成更新成功。

GitHub Actions 在特定情况下会停用长期无活动仓库的定时工作流；应关注 Actions 失败通知和网页更新时间。日更任务的失败状态在部署最新健康记录后上报，部分来源失败不丢弃已有归档。

## 数据范围与限制

候选源：PV magazine 全球 RSS、PV Tech RSS，仅使用公开 RSS 提供的元数据，不爬取付费全文。来源可访问性、RSS 内容格式和使用条款需要部署时复核；403 或错误须正规处理，不绕过限制。

按标题的国家关键词识别市场，主题/技术依关键词标记，政策主题优先级为规则分数，不等同于 AI 价值判断。仅接收带有效发布日期、近 90 天及 HTTPS 原文 URL 的新闻；不相关/无效条目被跳过。当前保存最多 3000 条近期去重记录，并非永久数据库。没有匹配条目不表示该市场无新闻。官方政策源和本地语言媒体尚未接入。

新闻按国家与规范 URL 去重，再按同市场标题去重。每次采集记录尝试时间、各来源健康状态与完整成功时间。来源失败会保留历史条目。每周简报由最近七个北京时间日期的已采集新闻滚动生成，可导出 Markdown 或打印/PDF；未接入历史周报快照和 AI 中文分析。

## 本地开发

要求 Node.js 22+（已在 Node.js 24 验证）与 Python 3.12+。

```bash
npm ci
npm run dev
```

只有在**运行开发服务器的同一台电脑**上，浏览器才能使用 Vite 显示的 localhost 地址。云端 localhost 不是你电脑上的网址。正式在线使用应访问 Pages 实际部署 URL，不需要用户安装 Node.js。

```bash
npm run build
npm run preview
npm test
python3 -m unittest discover -s tests -v
python3 scripts/collect.py
```

最后一条会联网并更新 `public/data/feed.json`；可通过 `FEED_OUTPUT=/tmp/probe.json` 指定临时输出。完整或部分失败返回非零退出码，健康记录仍会保存。TLS 验证和现有代理保持启用。

## 目录

```text
src/App.tsx                      默认真实数据 UI，轮询、状态、详情与周报
src/DemoApp.tsx                  明确分离的模拟演示
src/data/mock.ts                 演示模型与观察分类
src/services/live.ts             运行时数据校验、北京时间周报
src/services/intelligence.ts     筛选、演示仓库接口
scripts/collect.py              RSS 采集、去重与原子归档
public/data/feed.json            公开元数据与来源健康状态
.github/workflows/              每日采集、测试、构建与 Pages 发布
src/services/*.test.ts           前端数据逻辑测试
tests/test_collect.py            采集解析、去重与失败保护测试
```

## 后续迭代

接入核实过的日本、韩国、台湾官方及本地来源；后端 AI 翻译与带证据引用的业务分析；私有登录、数据库、永久历史与告警。任何 AI API 密钥仅存服务器或 GitHub Secrets，不写入前端或公开 JSON。

## 关闭 / 重新开放公开访问

管理入口：`https://github.com/NeedXu/NorthAsiaSolar/actions/workflows/public-access.yml`。网页顶栏也有「公开访问开关」。在工作流界面运行默认的 **close** 即撤下应用与新闻数据；选择 **open** 即重新发布应用。

**关闭模式的确切含义**：网址仍提供一个不含应用脚本和新闻的「访问已关闭」页面；不是删除域名、不是 HTTP 全站拒绝访问，也不会隐藏公开 GitHub 仓库。当前 GitHub Actions 令牌在实际测试中调用删除 Pages 站点接口返回 HTTP 403，因此不将删除站点作为默认关闭机制，也不宣称自动令牌具有站点管理权限。

关闭操作先保存 `enabled:false`，禁止日更任务重新发布应用；随后用仅含停用页的部署替换原应用，检查首页关闭标记、新闻 JSON 返回 404/410、上一版 JS/CSS 文件返回 404/410，全部通过后才保存 closed 验证记录。每日采集继续归档到 GitHub，但不再发布到网站。两个工作流共享并发锁，避免更新与关闭交错。

重新开放仍需仓库的 GitHub 登录/写入权限；浏览器不保存控制密钥。该入口是一次管理操作，而不是免登录的站内即时按钮。GitHub 工作流/部署需要等待，不能保证即时关停。无论关闭还是重新开放，失败时都不应视为成功。

关闭无法撤回第三方缓存或已下载数据。若需要私有新闻归档或严格身份验证，应迁移到私有存储及支持登录的托管方案。

### 发布状态保存的故障恢复

发布与采集任务通过 `scripts/push-main.sh` 非强制推送状态；遇到 GitHub `commit_refs` 等暂时性拒绝，会先同步远端并 rebase 后再重试（最多 4 次）。冲突或持续失败会明确停止，不丢弃他人提交。该路径已在本地临时裸仓库中测试远端并发提交与模拟拒绝。

仓库拥有者也可提交 `.deploy/access-request.json` 发起 open/close 请求，以便通过已授权的 Git 操作远程管理，无需在浏览器保存密钥。手动工作流入口仍可使用。
