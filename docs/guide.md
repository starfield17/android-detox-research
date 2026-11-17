# 操作与验收指南

按具体型号、构建和用户逐项核对，候选组件及品牌差异见[组件表](components.md)，设备专项结果见[实机记录](devices.md)。

## 操作方式、恢复与验收口径

### 先区分三种结论

| 标记 | 用于什么 | 能据此做什么 |
|---|---|---|
| **实操支持** | 具体设备操作记录或公开机型反馈 | 采用相同路径前仍核对固件；写明只核验了包状态还是做过功能测试 |
| **试验候选** | 别的固件有处理依据，当前目标未验证；或只在组件数据库有说明 | 从单包可逆停用开始；不称为“已证明安全卸载” |
| **发现项** | 只发现包、权限、服务、SDK 或功能 | 先用设置/网络限制；没有处理依据时不给整包删除结论 |

`QUERY_ALL_PACKAGES` 是能力，服务运行是运行态，数据库有记录是本地采集，网络请求成功是传输结果。本文只在来源实际支持时使用“采集”“上传”等表述，不把这几者混写。UAD/UAD-ng/Canta 的分级可辅助筛选，不能替代固件回归；Canta 使用相同生态的组件资料，不是独立的第二次安全验证。[UAD 数据快照](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json)、[Canta 文档](https://github.com/samolego/Canta/blob/master/README.md)

### 多台手机、多用户与完整检查

本指南的通用 `adb` 命令适用于**只连接一台目标手机**的情况。两台同时连接时，先 `adb devices -l`，将命令改为 `adb -t 当前transport_id …` 或 `adb -s 自己的序列号 …`。**重启后 transport_id 可能变化**，不能把当前 ID 固化成以后脚本的设备身份。

```bash
adb shell getprop ro.product.model
adb shell getprop ro.product.device
adb shell getprop ro.build.display.id
adb shell getprop ro.build.version.release
adb shell am get-current-user
adb shell pm list users
```

前台用户不一定是 0；分身、工作资料和三星安全文件夹可能是另一用户。明确写 User 0 的操作，只影响那个用户，不自动覆盖其他空间。

已知包名至少同时查状态、路径、进程和服务。以下是一个包的检查模板；只将 `P` 改为表中确切包名：

```bash
P=com.mobiletools.systemhelper
adb shell pm list packages -u --user 0 "$P"
adb shell pm path "$P"
adb shell dumpsys package "$P"
adb shell ps -A
adb shell dumpsys activity services "$P"
```

输出保存本地后用电脑的 `rg -F` 查包名。进程名可能是自定义名或 `包名:子进程`，不能只用 `pidof 完整包名` 判断没有运行。两台设备的全量检查与包列表曾有差集，具体见[实机记录](devices.md)。 不将“包列表没有”直接判成“手机没有”。

必要时补查一次全量包状态：

```bash
adb shell dumpsys package packages > package-state-private.txt
```

不建议扫描器反复执行 `pm dump`。特定三星 One UI 9 报告显示它会连带执行 ActivityManager 全量 dump 并触发 Watchdog；`dumpsys package` 与 `pm dump` 不是同一条调用路径。[三星故障定位](https://github.com/Eynnzerr/TelemetryCleaner/issues/5)

### 停用、卸载、挂起的命令各自对应什么恢复

先保存该包完整 `dumpsys package`。重点记录**当前 Packages 段**的版本、路径和 `User 0`；更新系统应用的输出还可能有 `Hidden system packages` 原厂副本，不能把副本状态当成当前状态。

```bash
# 示例：一次只处理一个包；这一行请按目标表选择
P=com.oplus.statistics.rom

# 停用，保留数据和系统 APK
adb shell pm disable-user --user 0 "$P"

# 恢复“停用”：显式启用
adb shell pm enable --user 0 "$P"

# 如果操作前 enabled=0，要精确恢复原“默认状态”，用这一条
adb shell pm default-state --user 0 "$P"
```

`enabled=0` 为默认，`1` 为显式启用，`2` 为 disabled，`3` 为 disabled-user；`stopped` 是另一属性，**`stopped=false` 不等于进程正在运行**。持久进程还可能在停用后暂留内存，[Moto Xlog](devices.md) 是一个实例。

用户级卸载与恢复：

```bash
P=com.coloros.regservice

# 只对指定用户卸载；通常会删除该用户的数据
adb shell pm uninstall --user 0 "$P"

# 确实需要保留原数据时，才使用 -k，而不是与上面一条连续执行
# adb shell pm uninstall -k --user 0 "$P"

# 恢复已卸载的系统包：前提是原包仍被系统识别/保留
adb shell cmd package install-existing --user 0 "$P"
adb shell pm enable --user 0 "$P"
```

**只写 `pm enable` 不能恢复 `installed=false` 的包。** 若固件支持，也可用 `pm install-existing --user 0`。`install-existing` 不会找回已被卸载清除的私有数据；已被 Root 模块遮蔽的原包应先解除遮蔽，真正删除的 APK 则需恢复同版镜像/原文件。不要拿其他版本、其他签名的同名 APK 作为系统包恢复物。[ADB 官方命令说明](https://developer.android.com/tools/adb#pm)

挂起不是停用的等价替代：

```bash
P=com.opos.ads
adb shell pm suspend --user 0 "$P"
adb shell pm unsuspend --user 0 "$P"
```

它主要限制应用交互等行为，不保证所有后台服务停止。若本机返回 `new state: default`、`suspended state: false`、`DELETE_FAILED_USER_RESTRICTED` 或 SecurityException，应按实际状态判失败；不连续堆叠不明绕过命令。

[组件表](components.md)恢复栏简写：**E = `pm enable`（或按原值 `default-state`）；R = `install-existing` 后再启用；S = `pm unsuspend`；UI = 重新打开对应设置。** 均明确指定原用户。

## 核心耦合时怎么继续处理

### 安装干预按环节做，不把安装器与扫描器合并

| 环节 | 处理方式 | 验收与退路 |
|---|---|---|
| 每个安装来源的许可、纯净/增强模式、三星 Auto Blocker | UI 关闭不要的额外限制；对文件管理器/浏览器分别授予需要的安装来源权限 | 用实际来源点 APK，保留系统签名与包完整性校验 |
| 独立扫描引擎 | 已验证的 Moto Engine 可保持停用；其他型号先单包试停 | 安装器应能结束，分别测首次安装和覆盖更新；E |
| 安装辅助/收尾页 | AppDetail 等先看固件依赖，不能因旧版成功就照搬 | 卡“正在安装”、卸载不收尾，马上 enable；曾 suspend 则先 unsuspend |
| 安全中心 Provider/策略查询 | 先确认完整组件名和调用失败是否能容错；可以组件级试验，但目前两机未做 | 安装器可能等待结果或崩溃；组件 E；不提供猜测的 Provider 禁用清单 |
| Android 包管理、权限控制器 | 保留系统安装与授权基本链 | 换一个安装器 App 不会自动绕过系统包管理或厂商验证器 |

`verifier_verify_adb_installs=0` 只针对 ADB 安装验证相关设置；`package_verifier_enable=0` 也不能保证厂商全部扫描关闭。两台设备的原有状态见[实机记录](devices.md)。不把 `adb install` 成功当作文件管理器 UI 侧载成功，也不以关闭校验设置代替独立引擎验证。

### 子组件级停用：小范围可逆，但并非什么方法都能禁掉

先在目标包 dump 中找到完整 Service/Receiver/Provider 名称。下面的示例只针对 **GuardProvider 的 AiGuardService**，不是 SecurityCenter/electricrisk 的停用命令，也不能据此关闭 SecurityCenter 的本地画像记录。manifest 组件可以尝试：

```bash
# 以下为小米 Gist 中出现的服务，仅在本机确实存在时试验；目标固件未验证
adb shell pm disable-user --user 0 com.miui.guardprovider/com.miui.guardprovider.aiguard.AiGuardService

# 对同一个组件恢复
adb shell pm default-state --user 0 com.miui.guardprovider/com.miui.guardprovider.aiguard.AiGuardService
```

需核对操作前组件是否已有 enabled/disabled 覆盖，按原值恢复。普通 Java 方法、内部 SDK 或已经合并到进程里的逻辑不能靠猜一个 `包名/类名` 来禁；组件停用也不保证同包其他路径不再进行本地记录。小米行为库的进一步关闭需要匹配版本的 Hook 或修改方案，现有资料不足以给出一个已验证的统一方法。[服务出处](https://gist.github.com/std-microblock/c38cacab22bf0fffb94b247e09a4d948)

### 网络隔离与 AppOps 的实际边界

1. **厂商自带联网控制**：若能分别关闭 WLAN、移动数据、后台网络，按目标包处理并复查。某些系统包被豁免；界面允许点击不等于流量一定被拦。
2. **无 Root VPN 防火墙**：可作为不能停用时的退路，但 Android 每个用户同一时间通常只有一个活动 VPN。正在使用 Hiddify VPN 时，不能再假定另一 VPN 防火墙能同时工作；应在同一网络方案内整合规则，或使用路由器/Root 路线。[Android 官方 VPN 约束](https://developer.android.com/develop/connectivity/vpn)
3. **DNS/路由器阻断**：只加入来源已确认的目标域名，观察失败是否会卡住必要功能。硬编码 IP、HTTPDNS、其他网络和共享域名可能绕过或造成连带影响；不直接导入来历不明的“反诈域名大全”。
4. **Root 防火墙**：先确认当前用户的实际 UID 及共享包。Moto RegService 的 phone UID、Neo7 多个包的 system UID、Moto NativeDropBox 的 log UID 都不适合按包名直觉封整个 UID。规则必须覆盖 IPv4/IPv6 和目标接口，不能以一条 IPv4 DROP 宣布全断。
5. **AppOps 后台/用量限制**：是补充，不能等同卸载，也不保证特权组件所有采集入口都受其控制。记录原模式；恢复原 allow/default/ignore 等值，不用全局 reset 清空其他偏好。

证书固定会影响中间人解密，**不阻止防火墙丢包**。相反，阻断上传也不保证不再本地采集；若数据先缓存在本地，解除网络阻断后可能补发。短信型 AutoReg 不在 IP 防火墙覆盖范围内。

### Root、系统遮蔽和换固件

Root 可以让受限的 `pm` 操作以 UID 0 执行，但仍优先用用户级状态处理。必要时采用按实机路径设计的 systemless 遮蔽模块，先记录 APK 所在分区、更新层及可恢复方式；不要把某个小米模块硬编码的路径套到 Neo7 的 `SystemHelper-release-20260609`。

删系统文件与 `pm uninstall --user 0` 不同，可能涉及 AVB、动态分区及 OTA 增量条件。本文不提供把分区 remount 后批量 `rm` APK 的命令。恢复遮蔽需禁用/移除模块并重启；原包物理缺失时 `install-existing` 无法凭空恢复文件。

换海外官版或第三方 ROM 是独立路线：先确认**具体型号、硬件区域、Bootloader 状态、反回滚和固件支持**，不预设小米/OPPO/vivo/华为/三星/Moto 当前均可解锁或互刷。也要验收本地 IMS、NFC/钱包、相机、完整性与 OTA。海外 ROM 不是没有厂商组件的保证，改版 ROM 不属于本稿国行主结论。

## 云控、预装恢复与更新后的复查

### 区分更新功能，不为了阻止一个包回归就删除全部更新体系

| 链路 | Neo7 当前组件 / 其他品牌线索 | 可做的较小处理 | 代价与事实边界 |
|---|---|---|---|
| RUS/运行配置 | Neo7 `com.oplus.romupdate` 17.0.8 | 先关相关功能的云配置/体验项；缺 UI 时考虑确认后的通信限制 | 可能影响兼容性/网络策略；尚无证据证明它恢复了卸载包 |
| 系统应用更新 | Neo7 `com.oplus.sau` 17.0.23、`com.oplus.sauhelper` 1.17.0；荣耀 `com.hihonor.systemappsupdater` | 系统应用更新页、商店自动更新逐项关闭，保留手动入口 | 组件修复时效降低；拒绝 disable 就记录真实失败，不连续删除依赖 |
| 定制资源/配置 | Neo7 `com.oplus.cota` 2.2.4，CotaService 实际运行 | 无明确恢复行为前先保留、观察 | 定制和配置更新能力减少；EnterprisePushService 这个名字本身不证明设备受企业管理 |
| 已卸载预装恢复 | Neo7 `com.oplus.apprecover` 17.0.10，`/product/priv-app/MDSService` | 不使用恢复预装功能时可列后续试停：`adb shell pm disable-user --user 0 com.oplus.apprecover`；E | 恢复入口失效；当前**未证明**该包会自动重装 SystemHelper/RegService |
| 推送/云底座 | Neo7 `com.heytap.mcs` 5.38.4、`com.heytap.htms` 2.3.2 更新层 | 先切具体订阅、体验或联网；整包后置 | 可能影响厂商消息、账号、云功能；不能只把它们当“云控恶意包” |
| OS OTA | Neo7 `com.oplus.ota`、Moto `com.motorola.ccc.ota`、荣耀 `com.hihonor.ouc` | UI 关闭自动下载/夜间安装，升级前后人工复查 | 不等于永久停更新 |

Reno9 / ColorOS 15 的记录还显示 `sauhelper` 可以停，而部分包会拒绝 disable；版本差异应保留。[公开操作记录](https://github.com/byteharbor-k2/Secure-3C-Device/blob/main/docs/03-app-management/Chapter_1/1_debloat-main-system.md) “包有自更新能力”“云端可下发配置”“已发生用户卸载状态恢复”是三个事实，不能互相替代。

### 发生哪些事件后要复查

普通重启、插拔/换 SIM、联网恢复、系统应用更新、OTA、分身/工作资料创建、云备份恢复、恢复预装、恢复出厂设置后，都检查既有处理清单。不同事件触发不同变化，不推断每次都会恢复。

记录：型号、构建、用户、包名、当前/系统副本版本、codePath、installed/enabled/suspended、服务/进程、功能测试。没有 `Success` 或状态没变，不能记成已完成；包路径存在不自动等于当前用户安装。

```bash
# 每次只查一个此前已处理的包
P=com.coloros.regservice
adb shell dumpsys package "$P" > package-after-private.txt
adb shell pm path "$P"
adb shell ps -A > processes-after-private.txt
adb shell dumpsys activity services "$P"
adb shell logcat -b crash -d -t 200 > crash-after-private.txt
```

同时查 `pm list users`，对每个**实际存在并有授权处理范围的用户**读取 package 状态。User 999、10、95、150 等只是样本，不能照着数字删除不存在/未授权的空间。

若被恢复，先看是包变名、原更新层被回退、用户安装位重新打开，还是仅设置开关重置。核对新版本后，**只重放该包原先验证过的动作**；保留旧/新差异，不执行全品牌的一键清理列表。不能对目标作用域以外用户直接批量操作。

### 自动清理应有的边界

优先人工复查；若以后确实需要自动执行，只允许自己的“已验证清单”，校验机型/固件变化，保存原状态，失败停止并报告，不扫描到一个可疑名字就新增删除目标。Shizuku 重启后可能需重启服务，Root 模块/脚本也可能因 OTA 失效；自动器自己不是永久在线的保证。[项目自动清理说明](https://github.com/Eynnzerr/TelemetryCleaner/blob/0b2cbc303cec7d3af79d528f947025300d6819a5/README.md)


## 验收清单

### 每处理一个包，至少留下这些结果

| 处理目标 | 当场检查 | 后续实际功能检查 | 出现问题怎样回退 |
|---|---|---|---|
| DM/自注册 | 各用户 installed/enabled、进程/服务、包路径 | 拨出/接听、短信收发、主副卡数据、VoLTE/VoWiFi、飞行模式恢复、换卡；只测实际使用的业务 | 先 E；卸载过先 R。恢复后重启并重测 |
| 扫描引擎/安装辅助 | 停用状态、扫描日志、安装器是否返回完成 | 文件管理器/浏览器的 UI 侧载、覆盖安装、卸载收尾、常用商店更新；ADB 单独测 | E；如果是挂起则 S；不要首先清安装器或权限数据 |
| 统计/日志 | 状态、persistent 主/子进程、服务、客户端重试频率 | 设置搜索、电池/耗电页、常用智能功能；重启后观察一段时间 | 按原 enabled 状态恢复；诊断功能必要时临时启用 |
| 网络阻断 | 对应网络上的实际请求/流量是否被拒绝 | 移动数据和 WLAN 分别测；必要功能不应卡死 | 删除新增的具体规则，别 reset 全机防火墙偏好 |
| 云控/更新 | 先证明自动下载/配置或恢复行为是什么 | 系统应用更新和 OTA 分别测试，不用一个结果包办 | UI 开关恢复；按包 E/R，别从第三方随便补系统 APK |

电话、短信等测试会影响通信或费用，后续执行 agent 应在用户明确指定测试方式/号码后实施；不自动拨号、发消息或拨紧急号码做测试。两台设备均未做这类外发测试。

各机型的未完成验证与已观察结果见 [实机记录](devices.md)。
