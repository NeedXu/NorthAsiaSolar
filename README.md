# North Asia Solar Intelligence

个人北亚光伏情报工作台，覆盖日本、韩国、台湾。React 19 + TypeScript + Vite，中文 UI，深浅主题与移动端布局。

## 当前状态

代码已具备「公开 RSS → 每日采集 → JSON 归档 → GitHub Pages → 浏览器读取」流程，并增加受 GitHub 权限保护的公开访问开关。**尚未部署，未取得可公开访问的网址，远程关闭开关权限仍待验证**。GitHub Actions 首次采集已于 2026-11-04 18:24（北京时间）成功读取两个来源并归档 1 条相关报道。初始发布状态为关闭。本次云环境对 `www.pv-magazine.com` 和 `www.pv-tech.org` 返回代理 403，禁止绕过。当前 `public/data/feed.json` 已由 GitHub Actions 写入真实采集结果，不包含模拟新闻。

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

管理入口：`https://github.com/NeedXu/NorthAsiaSolar/actions/workflows/public-access.yml`。网页顶栏也提供「公开访问开关」入口。

- 关闭：在该工作流页面点击 **Run workflow**，保持默认 **close**，再点运行。只有任务成功且 GitHub 返回下线确认，才算关闭完成。
- 重新开放：运行相同工作流，选择 **open**；确认 Pages 权限后重新构建发布。
- 该开关通过仓库管理员的 GitHub 登录和工作流权限保护，浏览器不存放任何控制密钥。它不是免登录的网页内单击开关。
- 关闭时先提交 `.deploy/public-access.json` 的 `enabled:false`，随后调用 GitHub 官方删除 Pages 站点接口；每日采集继续，但不再发布。两个工作流共享并发锁，避免更新任务与关闭任务交错。
- 初始文件为 `false`，因此单纯提交代码不会自动开放网站。只有 open 工作流获得权限且成功执行后才会发布。
- GitHub 返回 403/404 等不能证明已下线：工作流必须报错，不能显示关闭成功。若工作流令牌不能管理 Pages，仓库所有者需在 **Settings → Pages → Unpublish site** 手动下线；在验证自动关闭权限前不应将其宣称为可用的一键关闭。
- 分支保护可能阻止开关提交，失败时不得声称访问已关闭。必须确认任务结果。
- 下线不保证立即清空 CDN、搜索引擎或访客缓存，也不能收回已下载的 HTML/数据。
- 此开关仅控制网站，**不会改变仓库可见性或删除仓库中的代码与新闻归档**。公开仓库的文件仍可通过 GitHub 读取；如需将归档也限制为个人访问，应先采用私有仓库及支持身份认证的托管方案，不能把网页下线等同于数据私有化。

当前关闭逻辑通过本地测试，但尚未使用真实 GitHub 管理权限验证，不应在此之前承诺关停时效。

### 发布状态保存的故障恢复

发布与采集任务通过 `scripts/push-main.sh` 非强制推送状态；遇到 GitHub `commit_refs` 等暂时性拒绝，会先同步远端并 rebase 后再重试（最多 4 次）。冲突或持续失败会明确停止，不丢弃他人提交。该路径已在本地临时裸仓库中测试远端并发提交与模拟拒绝。

仓库拥有者也可提交 `.deploy/access-request.json` 发起 open/close 请求，以便通过已授权的 Git 操作远程管理，无需在浏览器保存密钥。手动工作流入口仍可使用。
