# 两台实机：记录、复查与恢复

本文分别标明用户提供的历史 session 记录和 2026-11-17 的普通 ADB 检查结果。包版本、路径和状态只适用于所列构建；组件名、权限或服务绑定本身不能证明上传了什么。本轮没有 Root、抓包、反编译或新增卸载；新增操作只有 Neo7 DCS 和 Moto Xlog 的用户级停用。操作方法和验收原则见[指南](guide.md)，跨设备组件见[组件](components.md)，来源见[来源](sources.md)，项目概览见[首页](../README.md)。

## realme Neo7

国行 RMX5060 / RE6022L1 的历史记录为 Android 16、RMX5060_16.0.10.500(CN01)；本轮为 **Android 17、RMX5060_17.0.0.105(CN01)**，安全补丁 2026-10-01。

| 组件 | 用户提供的历史 session | 本轮 ADB 检查 |
|---|---|---|
| `com.mobiletools.systemhelper` | 3.0.1-20250822，`/product/priv-app/SystemHelper-oppo-20250822`；用户此前已对 User 0 卸载 | 4.0.0-20260609，**`/product/priv-app/SystemHelper-release-20260609`**；User 0 和 999 均未安装，User 0 已停止，未见进程 |
| `com.coloros.regservice` | 16.0.20，`/product/app/RegService`；曾运行 DMService，User 0 卸载返回 Success | 17.0.15，同一路径；User 0 和 999 均未安装，User 0 已停止，未见进程；仅看包列表会漏掉该包 |
| `com.oplus.statistics.rom`（DCS） | 5.9.11.01，旧记录中运行 | 5.9.14.00，`/product/priv-app/DCS`；本轮对 User 0 停用，enabled 从 0 变为 3 |

系统镜像中的新版 APK 与用户卸载状态可以同时存在。本次版本变化后两个旧卸载状态仍保留，不保证未来 OTA 也如此。旧记录中的 SystemHelper 后台白名单条目单独不足以证明卸载后仍在运行。

本轮 DCS 返回 `disabled-user`，仍为 installed=true，`stopped=false`，但未见该包进程和服务。设置搜索 `battery` 返回多项结果，电池设置页可以打开；这只覆盖一个搜索词和一个入口。Neo7 本轮未重启，未验证 OTA、长期使用、全部设置页或网络上传，也未证明其他组件的统计随之消失。

### 后续候选与依赖

以下是本轮包和服务发现，除 DCS 外均未新增停用；应逐项评估，不能作为批量操作清单。

| 包与当前版本 | 路径、线索及边界 |
|---|---|
| `com.oppo.ctautoregist` 17.0.5 | `/product/priv-app/CTAutoRegist`；通信相关候选，需专项回归。 |
| `com.oplus.onetrace` 1.3.49 | `/system_ext/app/OTrace`；OTraceDaemonService 的启动来源为 OBrain，共享 system UID。 |
| `com.oplus.olc` 17.0.6 | OlcService，MCS 拉起 OlcPushMessageService；不能据此断言上传内容。 |
| `com.oplus.postmanservice` 16.0.2 | `/system_ext/app/PostmanService`；检查前 stopped=true。 |
| `com.oplus.logtrial` 17.13.12 | `/system_ext/app/LogTrialCommercial`；检查前 stopped=true，未证明是旧 LogKit 改名。 |
| `com.oplus.qualityprotect` 17.0.20 | `/system_ext/app/OplusQualityProtect`；QualityProtectService，共享 system UID，并有 OBrain 调用线索。 |
| `com.oplus.powermonitor` 17.0.010 | 包含电池及电源统计服务，PowerStatsService 被 ExSystemService 绑定；处理可能影响诊断和管理。 |
| `com.oplus.audiomonitor` 17.0.2 | `/product/app/OplusAudioMonitor`；仅为发现项，未证实录音或上传。 |
| `com.heytap.openid` 5.1.6 | 标识服务线索，需考虑账号和云服务回归。 |
| `com.oplus.obrain` 17.0.21 | 含 OStatsDaemonService、OCenterDaemonService、MIDASService，与多媒体及原生 Midas 客户端有连接。 |
| `com.oplus.metis` 17.32.453、`com.oplus.deepthinker` 17.0.0、`com.oplus.gleanerservice` 17.8.0、`com.oplus.stdsp` 5.0.12_20c0875_260529 | 场景、采集、无障碍或安全服务线索；未做本机停用回归。 |
| `com.oplus.trafficmonitor` 17.3.5、`com.oplus.lfeh` 17.0.7 | 流量与诊断候选，需区分用户可见统计与后台上报。 |
| `com.coloros.activation` 17.1.4、`com.coloros.bootreg` 17.0.235 | 激活和引导链的独立包，应考虑初始化和账号功能。 |
| `com.coloros.remoteguardservice` 17.2.2、`com.coloros.familyguard` 17.3.1 | 均安装启用；涉及守护功能。 |

当前未找到旧清单中的 `com.oplus.logkit`、`com.oplus.crashbox`，这不代表没有其他日志能力。`com.heytap.tas` 的实际路径是 TasWallet，不应仅按外部清理记录归为纯遥测。多个日志包共享 system UID，不能按单个包名直接封锁共享 UID。

安装和权限链本轮保留：`com.android.packageinstaller` 17.0.1（`/system_ext/priv-app/OppoPackageInstaller`）；`com.oplus.appdetail` 当前更新层 5.27.0，原厂 `/product/priv-app/KeKeAppDetail` 为 5.17.62_os17；`com.coloros.phonemanager` 17.6.8；`com.oplus.securitypermission` 17.00.003；`com.oplus.safecenter` 17.2.1；`com.coloros.securityguard` 17.5.2；以及 APEX 权限模块 `com.android.permissioncontroller` 17.00.002。`com.coloros.securepay` 17.5.0、`com.ted.number` 17.15.5 和 `com.oplus.blacklistapp` 17.20.0 属于不同功能环节，可先检查对应设置。

历史记录中的 `fraud_app_observer_switch=1`、`install_app_detail_safeguard_state=0`、`oplus_customize_cta_user_experience=0` 本轮仍可读取，未修改；这些值既不能证明全链路关闭，也不能证明数据已发送。

## moto g100 国行

XT2533-4 / portov，Android 16、MYUI 8、W1VT36H.1-51-8；本轮与历史记录固件相同，安全补丁 2026-04-01。本轮无 SIM。

| 组件 | 用户提供的历史 session | 本轮 ADB 检查（含重启后） |
|---|---|---|
| `com.mobiletools.systemhelper` | 当次未发现 | 全量包状态也未发现，不能外推所有 Moto |
| `com.motorola.regservice` | 2.0.001.0014，`/system/priv-app/RegService`；原已停用，User 0 卸载返回 Success | 仍未安装、已停止；共享 phone UID |
| `com.motorola.deviceshield.engine` | 1.0.0，`/system_ext/priv-app/PrcDeviceShieldEngine`；用户级停用 | enabled=3 保留，重启后未见进程 |
| `com.lenovo.lsf.device` | 原已 enabled=3 | 仍停用；更新层 V5.1.0.0330pg，系统副本 V5.0.2.0290pg |
| `com.zui.xlog` | — | 1.1.0062，`/system/priv-app/ZuiXlog`；本轮对 User 0 停用并重启 |

历史上在无网、无 SIM 条件下，通过 `com.android.packageinstaller` 界面侧载 Hiddify 一次成功；记录显示引擎包未找到并直接显示安装按钮。仍有 DeviceGuard 的 IllegalAppProvider 查询和备案、商店匹配逻辑，另有一次 Play Protect SAFE 结果。该记录只支持跳过该引擎的一次界面侧载成功，不能说明所有安装审查已关闭。本轮没有重新安装。

Xlog 原为 persistent，主进程及 usage 子进程运行；停用后子进程退出，补做 force-stop 后主进程仍在。Moto 重启后停用状态保留，主、子进程以及 UsageCollectorService、DeamonService 均未出现，设置页面可启动。启动阶段有两次服务未找到记录，约 15 分钟采样未见持续循环重试。启动阶段仍有 `init` 原生 SIGABRT，操作前已有同类记录，本轮未归因；没有新增 Java FATAL EXCEPTION，不能据此保证整机无异常。未验证电话、短信、IMS、OTA 或长期待机。

### 后续候选与依赖

以下均未在本轮新增停用；服务存在或绑定不等于已证明上传。

| 包与当前版本 | 路径、线索及边界 |
|---|---|
| `com.zui.sdac` 1.1.1270 | SDACService、CNSClientService 运行，曾绑定 Xlog；可能涉及厂商消息。 |
| `com.zui.deviceidservice` 16 | 客户端包括 smartplugins、smartservice 和 trip；涉及设备标识与智能场景。 |
| `com.motorola.motocare` 4.16.06 | MotoCareService 运行，有用量及设备信息能力线索；处理可能影响售后诊断。 |
| `com.motorola.help.extlog` 6.00.0000 | `/product/priv-app/MotoFeedbackAssistant`；本轮未见对应运行服务，不等于永不运行。 |
| `com.motorola.android.nativedropboxagent` 6.0 | `/system_ext/priv-app/com.motorola.android.nativedropboxagent`；服务运行、persistent，共享 log UID 1007，不应按 UID 一刀封网。 |
| `com.motorola.cn.smartservice` 2.0.2.029 | `/product/priv-app/Smartservice`；PersistService 被 Motorola systemserver 客户端绑定，另有场景服务。 |
| `com.motorola.cn.trip` 03.0.0.05.0 | `/product/priv-app/TravelInfoServices`；TripService 运行并使用 DeviceidService，停用可能影响行程卡片。 |
| `com.motorola.dciservice` 1.0 | DciStatsService 被 `com.android.phone` 绑定；无卡环境不足以回归电话和网络。 |
| `com.motorola.ccc.devicemanagement` 16.00.0011 | 有 Checkin 和系统服务连接及 OTA 关联线索；本轮设备管理输出未显示 Device Owner，不排除其他管理能力。 |
| `com.motorola.deviceguard` 7.0.0_20251128011556 | 涉及黑名单、安全、屏幕时间、电池、自启和权限等链；本轮保留整包。 |
| `com.ted.number` 34.L.4.52.4 | 未见常驻进程；同名 Neo7 包的实现和权限不同。 |
| `com.motorola.prcaisafety` 1.0.0.09.0 | 水印和 AI 服务名称线索；未证实是扫描引擎。 |
| `com.motorola.bach.modemstats` 2.16.02 | 基带和网络诊断服务；无卡条件不足以完整测试。 |
| `com.motorola.ccc.ota` 36.00.043 | 独立系统更新包，本轮保留。 |

## 恢复

验证器设置的补充记录：本轮两机读到的 global `verifier_verify_adb_installs` 均为 `0`，没有修改。没有完整记录 `package_verifier_enable` 的有效原值，不据此补出该值。前者为 0 不代表厂商所有安装扫描已关闭。

先确认目标设备；多台连接时，对每条 `adb` 命令加入正确的设备选择参数（例如 `adb -s <设备序列号>`），或只连接目标手机。以下命令针对 User 0。恢复前先核实当前包及状态；系统更新后路径和状态可能改变。

本轮仅停用的 DCS 和 Xlog 原本为默认启用状态（enabled=0），可分别恢复默认状态：

```bash
adb shell pm default-state --user 0 com.oplus.statistics.rom
adb shell pm default-state --user 0 com.zui.xlog
```

分别在对应手机执行。`pm enable --user 0 <包名>` 也可显式启用，但设置的是 enabled=1。Xlog 恢复后可正常重启以重建常驻服务；若出现持续发热、卡顿或功能问题，可先恢复并在相同条件下对照。

历史停用的 Moto 引擎可在 Moto 上执行：

```bash
adb shell pm enable --user 0 com.motorola.deviceshield.engine
```

历史用户级卸载的包需要系统仍保留并识别原包，不能只用 enable。分别在对应设备上恢复所需包：

```bash
# Neo7
adb shell cmd package install-existing --user 0 com.mobiletools.systemhelper
adb shell pm enable --user 0 com.mobiletools.systemhelper
adb shell cmd package install-existing --user 0 com.coloros.regservice
adb shell pm enable --user 0 com.coloros.regservice

# Moto
adb shell cmd package install-existing --user 0 com.motorola.regservice
adb shell pm enable --user 0 com.motorola.regservice
```

恢复 Neo7 时使用当前系统中的版本，不会强制降回历史版本。用户级卸载可能已删除该用户的数据，重新安装不保证恢复数据。
