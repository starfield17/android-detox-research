# 两台实机：记录、复查与恢复

本文分别标明历史 session 记录、2026-11-17 首轮 ADB 检查结果，以及 **2026-11-20 第二轮全量排查与批量减毒实操结果**。两台设备采用物理隔离分工：**moto g100 国行（无 SIM 卡）**作为海外核心与高敏资产主力机；**realme Neo7** 专门运行国内日常软件。操作方法和验收原则见[指南](guide.md)，跨设备组件见[组件](components.md)，来源见[来源](sources.md)，项目概览见[首页](../README.md)。

## realme Neo7

国行 RMX5060 / RE6022L1 的历史记录为 Android 16、RMX5060_16.0.10.500(CN01)；本轮为 **Android 17、RMX5060_17.0.0.105(CN01)**，安全补丁 2026-10-01。

| 组件 | 用户提供的历史 session | 本轮 ADB 检查 |
|---|---|---|
| `com.mobiletools.systemhelper` | 3.0.1-20250822，`/product/priv-app/SystemHelper-oppo-20250822`；用户此前已对 User 0 卸载 | 4.0.0-20260609，**`/product/priv-app/SystemHelper-release-20260609`**；User 0 和 999 均未安装，User 0 已停止，未见进程 |
| `com.coloros.regservice` | 16.0.20，`/product/app/RegService`；曾运行 DMService，User 0 卸载返回 Success | 17.0.15，同一路径；User 0 和 999 均未安装，User 0 已停止，未见进程；仅看包列表会漏掉该包 |
| `com.oplus.statistics.rom`（DCS） | 5.9.11.01，旧记录中运行 | 5.9.14.00，`/product/priv-app/DCS`；本轮对 User 0 停用，enabled 从 0 变为 3 |

系统镜像中的新版 APK 与用户卸载状态可以同时存在，本次大版本升级后两个旧卸载状态均得以保留。旧记录中的 SystemHelper 后台白名单条目仅系配置残留。

本轮 DCS 返回 `disabled-user`，仍为 installed=true，`stopped=false`，未见该包进程和服务。设置搜索 `battery` 返回多项结果，电池设置页可以正常打开。

### 后续候选与依赖

以下为本轮检出的包与服务线索（除 DCS 外均未停用）：

| 包与当前版本 | UID / 联网权限 | 路径、常驻服务、定时任务与处理边界 |
|---|---|---|
| `com.oppo.ctautoregist` 17.0.5 | `10091` / 有 `INTERNET` | `/product/priv-app/CTAutoRegist`；注册 `RegisterReceiver` 闹钟；电信自注册组件，需插电信卡专项回归。 |
| `com.oplus.onetrace` 1.3.49 | `1000` (`system`) / 共享 | `/system_ext/app/OTrace`；运行 `OTraceDaemonService`（由 OBrain 拉起）与 `StatsManagerService`。 |
| `com.oplus.olc` 17.0.6 | `1000` (`system`) / 共享 | `/system_ext/app/Olc`；运行 `OlcService`，MCS 拉起 `OlcPushMessageService`；JobScheduler 注册 `.dcs.service.UploadJobService`，含 `DcsContentProvider` 与 `TaskInfoProvider`。 |
| `com.oplus.postmanservice` 16.0.2 | `1000` (`system`) / 共享 | `/system_ext/app/PostmanService`；检查前 `stopped=true`，含远程诊断与日志抓取组件。 |
| `com.oplus.logtrial` 17.13.12 | `10460` / 有 `INTERNET` | `/system_ext/app/LogTrialCommercial`；检查前 `stopped=true`，持 `QUERY_ALL_PACKAGES` 与 `PACKAGE_USAGE_STATS`。 |
| `com.oplus.qualityprotect` 17.0.20 | `1000` (`system`) / 共享 | `/system_ext/app/OplusQualityProtect`；运行 `QualityProtectService`，与 OBrain 存在调用关联。 |
| `com.oplus.powermonitor` 17.0.010 | `1000` (`system`) / 共享 | `/system_ext/app/PowerMonitor`；运行 `FeedBackBatteryStatsService`、`OidtService`、`ChargeStatusService`、`PowerStatsService`（被 ExSystemService 绑定）。 |
| `com.oplus.audiomonitor` 17.0.2 | `10176` / **无 `INTERNET`** | `/product/app/OplusAudioMonitor`；仅持 `com.oplus.permission.safe.SETTINGS`。 |
| `com.heytap.openid` 5.1.6 | `10116` (`osec.kms`) / 有 `INTERNET` | `/product/priv-app/OpenID`；该共享 UID 下仅此一包；运行 `IdentifyService` 与 `KmsDaemonService`（User 0 与 999 均绑定）。 |
| `com.oplus.obrain` 17.0.21 | `1000` (`system`) / 共享 | `/my_stock/non_overlay/app/OBrain`；运行 `OStatsDaemonService`、`OCenterDaemonService`、`MIDASService`，JobScheduler 注册 `ConfigPullJobService`，与多媒体及原生 Midas 客户端连接。 |
| `com.oplus.metis` 17.32.453 | `10114` / 有 `INTERNET` | 更新层位于 `/data/app`，原厂 `/product/priv-app/Metis`；运行 `ContextAwareService`、`PushDataService`，JobScheduler 注册 `DcsUploadJobService` 与 `PERSONA_DAILY_ALARM`，暴露 `BehaviorCallProvider`、`UserDataCollectionProvider`。 |
| `com.oplus.deepthinker` 17.0.0 | `10208` / 有 `INTERNET` | `/system_ext/priv-app/DeepThinker`；运行 `EventHubService`、`DeepThinkerBridgeServer`，JobScheduler 注册 `TrainJobService`，含 `UserProfileProvider`、`DtNotificationListenerService`。 |
| `com.oplus.gleanerservice` 17.8.0 | `10236` / 有 `INTERNET` | 更新层位于 `/data/app`，原厂 `/product/app/Gleaner`；含 `BehaviorMonitorProvider`、`AppSwitchService`、`ObserveService`、`DataCollectService`。 |
| `com.oplus.stdsp` 5.0.12_20c0875_260529 | `10195` / 有 `INTERNET` | `/product/app/StdSP`；含 `SRPCoreService`、`KmsService` 及 NearX Track 组件。 |
| `com.oplus.dmp` 17.18.00 | `10135` / 有 `INTERNET` | 更新层位于 `/data/app`，原厂 `/product/priv-app/dmp`；监听包安装/卸载，JobScheduler 注册 `DailyTaskService`，含 `DailyEventProvider`、`SmsTodoRecordProvider`、`PvmDbInitProvider`。 |
| `com.oplus.trafficmonitor` 17.3.5、`com.oplus.lfeh` 17.0.7 | `1000` (`system`) / 共享 | 流量与诊断组件；其中 `lfeh`（`/system_ext/app/LFEHer`）注册有 `.service.UploadJobService` 与 `.service.DcsScanReceiver`。 |
| `com.heytap.htms` 2.3.2 | `10171` (`htmsenv`) / 有 `INTERNET` | 该共享 UID 下仅此一包；常驻运行 `MonitorUploadService`，JobScheduler 注册 `KitUpdateJobService`，内含 `CloudConfigReportService` 与 `com.oplus.statistic.rom.oneid.OneIdService`。 |
| `com.heytap.mcs` 5.38.4 | `1000` (`system`) / 共享 | 系统推送底座；常驻 `McsService`、`OplusNotificationAssistant`，JobScheduler 注册 `ChannelConfigService`、`CloudConfigUpdateService`。 |
| `com.opos.ads` 5.3.2 | `10143` / 有 `INTERNET` | `/product/app/ADS`；持 `QUERY_ALL_PACKAGES`，含 `AppStateProvider`。 |
| `com.coloros.activation` 17.1.4、`com.coloros.bootreg` 17.0.235 | `10182`（有网）/ `10121`（**无网**） | 激活与开机引导链独立包；`bootreg` 无 `INTERNET` 权限。 |
| `com.oplus.framework.network.drs` 1.0.25 | `10207` / 有 `INTERNET` | `/product/priv-app/DRS`；**常驻运行**，持 `QUERY_ALL_PACKAGES`、`READ_PRIVILEGED_PHONE_STATE`；JobScheduler 注册 `UploadJobService`、`DccWakeJobService`、`SelfCollectJobService`（对应各系统包内嵌的 `com.oplus.drs.rom.sdk` 埋点框架）。 |
| `com.oplus.thirdkit` 5.4.2、`com.coloros.ocs.opencapabilityservice` 17.0.6 | `10123` / `10175`（均有 `INTERNET`） | 均持 `QUERY_ALL_PACKAGES`；前者在 JobScheduler 注册 `.faulthelper.job.DataJobService`，后者注册 `com.oplus.ocs.statistics.EventTrackTimerJobService`。 |
| `com.oplus.pantanal.ums` 17.22.8、`com.coloros.assistantscreen` 17.15.40 | `10133` / `10152`（均有 `INTERNET`） | 智慧流体云与负一屏（速览），**均常驻运行**，持 `QUERY_ALL_PACKAGES`、`PACKAGE_USAGE_STATS`、`ACCESS_FINE_LOCATION`；`pantanal.ums` 在 JobScheduler 注册有短信采集服务 `SmsQueryIdleService`。 |
| `com.coloros.remoteguardservice` 17.2.2、`com.coloros.familyguard` 17.3.1 | `10124` / `10291`（均有 `INTERNET`） | 均安装启用；前者提供 `AppEventProvider`、`AppUsageProvider`，后者位于 `/my_stock/del-app/FamilyGuard` 并内嵌华为 HMS / Firebase Push 与 Drs Track。 |
| `com.android.federatedcompute.services` 17、`com.android.adservices.api` 17 | `10268` / `10262`（均有 `INTERNET`） | 位于 `/apex/`；联邦学习与广告归因模块，均持 `QUERY_ALL_PACKAGES`（后者另持 `PACKAGE_USAGE_STATS`）。 |

当前固件未见旧清单中的 `com.oplus.logkit`、`com.oplus.crashbox`。`com.heytap.tas` 的实际路径是 `/product/app/TasWallet`（钱包组件）。

### ColorOS 17 反诈、风控与埋点子组件拓扑

从本机 Resolver Table 与 JobScheduler 提取出四层风控与埋点实现：

1. **国家反诈解析与号码识别（`com.ted.number` 17.15.5，独立 UID `10115`，有 `INTERNET`）**：
   - JobScheduler 除调度泰迪熊词典更新（`TedJobScheduler`、`LocalDicUpdateJob`）外，还注册了 **`com.oplus.nationalantifraud.parse.ParseJobService`**，并包含 `com.oplus.harassdetec.OpushService` 与 `ServerMarkProvider`。
2. **AI 通话防诈、AI 换脸检测、安天查杀与灰产管控（`com.coloros.phonemanager` 17.6.8，独立 UID `10128`，有 `INTERNET`）**：
   - **AI 通话防诈（`aivoicecalldetect`）**：含 `AiVoiceDetectForegroundService`、`SimCallDetectTriggerService`（普通电话触发）、`VoipCallDetectTriggerReceiver`（VoIP 通话触发）、`AiVoiceDetectProvider`、`FeedbackFileLogProvider` 及 `FraudDetectRuleFilePipeProvider`。
   - **AI 换脸视频检测（`deepfakedetect`）**：含 `DeepfakeForegroundService`、`DeepfakeFaceGuideActionReceiver`、`DeepfakeFaceDetectSettingsActivity`。
   - **安天（AVL）查杀与实时应用切换监控（`virusdetect` / `grayproduct` / `adidentify`）**：内嵌 `com.avl.engine.security.AVLProvider`，包含 `RemoteAppScanService`、`RemoteVirusService`、`AutoTestScanApksService`、`RealTimeMonitorReceiver`、`AppSwitchNotifyReceiver`、`AppRiskPackageProvider`、`GrayProductProvider`（灰产/单应用封禁）及 `LayoutExtractService`（界面布局提取）。
3. **本地应用切换与安全事件采集（`com.coloros.securityguard` 17.5.2，独立 UID `10189`，无 `INTERNET`）**：
   - 本身不申请联网权限，作为本地采集层暴露 `com.oplus.securityguard.antifraud.data.collection.AppSwitchNotifyProvider`、`SecurityEventProvider`、`SecurityGuardProvider`、`PvmContentProvider` 与 `InstructionReceiver`，通过 Epona/Tingle IPC 供上层风控调用。
4. **安装收尾云检与无障碍风控（`com.oplus.appdetail` 5.27.0 / `com.oplus.safecenter` 17.2.1）**：
   - `com.oplus.appdetail` 拥有独立 UID `10105`（有 `INTERNET`），其安装收尾 UI（`InstallFinishActivity`、`UninstallPackageActivity`）与云端校验同处一包；**按 UID `10105` 阻断联网**可在保留本地安装收尾界面的前提下切断安装云检。
   - `com.oplus.safecenter`（共享 `system` UID `1000`）包含 `.accessibility.provider.FraudRiskProvider`、`.stealth.VoipReceiver` 与 `.privacy.control.DeepProtectReceiver`。
5. **跨包内嵌的 NearX / DRS / HLog 埋点组件**：
   - 即使停用主统计包 `com.oplus.statistics.rom`（UID `10096`），`phonemanager`、`appdetail`、`htms`、`mcs`、`obrain`、`stdsp`、`blacklistapp`、`tas`、`deepthinker`、`familyguard`、`ota` 内部仍各自声明了 `com.oplus.nearx.track.internal.storage.*`（`TrackEventProvider`、`EventContentProvider`）、`com.oplus.drs.rom.sdk.comm.provider.StandaloneTrackProvider` 或 `com.heytap.log.kit.server.HLogSdkProvider`。

历史记录中的 `fraud_app_observer_switch=1`、`install_app_detail_safeguard_state=0`、`oplus_customize_cta_user_experience=0` 在 2026-11-17 仍可读取；在 **2026-11-20 实操**中，已将检出的 3 项开启状态反诈/骚扰开关全部置 `0` 并完成回读确认：

| Settings 命名空间 | 键名 | 2026-11-20 操作前 → 操作后 |
|---|---|---|
| `system` | `fraud_app_observer_switch` | `1` → **`0`** |
| `system` | `oplus_ai_fraud_guide_trigger_mask` | `11` → **`0`** |
| `global` | `oplus_customize_harass_intercept_mark_number_fraud` | `3` → **`0`** |

### 2026-11-20 Neo7 第二轮批量停用与 AppOps 剥权实操

1. **成功停用（`pm disable-user --user 0` 均变为 `enabled=3`，并执行 `force-stop` 清退进程，共 33 个包）**：
   - **遥测、日志、故障上报与联邦计算（10 项）**：`com.oplus.framework.network.drs`（中央 DRS 遥测守护进程）、`com.oplus.onetrace`、`com.oplus.lfeh`、`com.oplus.logtrial`、`com.oplus.postmanservice`、`com.oplus.qualityprotect`、`com.oplus.thirdkit`、`com.coloros.ocs.opencapabilityservice`、`com.android.federatedcompute.services`、`com.android.adservices.api`。
   - **行为画像、AI 记忆、小布语音与识屏（11 项）**：`com.oplus.metis`、`com.oplus.dmp`、`com.oplus.deepthinker`、`com.coloros.sceneservice`、`com.coloros.colordirectservice`、`com.oplus.aimemory`、`com.oplus.aiwriter`、`com.heytap.speechassist`、`com.oplus.ovoicemanager`、`com.oplus.ovoicemanager.wakeup`、`com.oppo.instant.local.service`。
   - **家庭/远程守护、车联、预装恢复与冗余功能（12 项）**：`com.coloros.familyguard`、`com.coloros.remoteguardservice`、`com.coloros.childrenspace`、`com.oplus.riderMode`、`com.oplus.ocar`、`com.heytap.opluscarlink`、`com.oplus.ohome`、`com.oplus.travelengine`、`com.coloros.karaoke`、`com.coloros.operationManual`、`com.oplus.upgradeguide`、`com.oplus.apprecover`。
2. **ColorOS 17 包管理同时拦截 `disable-user` 与免 Root `uninstall --user 0` 的 9 个受保护包**：
   - 目标：`com.opos.ads`、`com.oplus.olc`、`com.coloros.assistantscreen`、`com.heytap.quicksearchbox`、`com.heytap.pictorial`、`com.nearme.instant.platform`、`com.heytap.browser`、`com.oplus.gleanerservice`、`com.oplus.pantanal.ums`。
   - **实测保护边界**：在 `RMX5060_17.0.0.105(CN01)` 上，这 9 个包对 `pm disable-user --user 0` 均返回码 0 但状态保持 `default (enabled=0)`；进一步测试 `pm uninstall --user 0` 时，系统均明确拒绝并返回 **`Failure [only root can delete system app for a particular user]`**。
   - **AppOps 剥权与 `force-stop` 实效**：对这 9 个包继续执行 `cmd appops set --user 0 <pkg> <OP> ignore` 后，**全部 9 个包的 `RUN_IN_BACKGROUND` 与 `RUN_ANY_IN_BACKGROUND` 均回读确认为 `ignore`**，6 个声明了用量权限的包（`olc`、`assistantscreen`、`quicksearchbox`、`instant.platform`、`browser`、`pantanal.ums`）的 `GET_USAGE_STATS` 亦全部确认为 `ignore`。配合 `am force-stop --user 0` 后，**其中 6 个包（`opos.ads`、`quicksearchbox`、`pictorial`、`instant.platform`、`browser`、`gleanerservice`）的后台进程与服务彻底清零且未再自启**；仅 `olc`（UID `1000`）、`assistantscreen`（UID `10152`，被桌面绑定，可在桌面设置关闭“速览”）与 `pantanal.ums`（UID `10133`）仍有进程留存，后两者具备独立 UID，可直接交由 Hiddify (Sing-box) 按包/UID 阻断联网。
3. **其余核心耦合包的 AppOps 持久化剥权（11 项）**：
   - 对 `com.coloros.phonemanager`、`com.coloros.securityguard`、`com.oplus.safecenter`、`com.oplus.appdetail`、`com.ted.number`、`com.oplus.blacklistapp`、`com.oplus.romupdate`、`com.oplus.cota`、`com.heytap.htms`、`com.heytap.mcs`、`com.heytap.openid` 执行 `cmd appops set --user 0 <pkg> <OP> ignore`：全部 11 个包的 `RUN_IN_BACKGROUND` 与 `RUN_ANY_IN_BACKGROUND` 均确认为 `ignore`；声明了使用情况统计权限的 `phonemanager`、`safecenter`、`mcs` 的 `GET_USAGE_STATS` 亦确认为 `ignore`（Neo7 合计共 **20 个包**完成 AppOps 剥权）。
   - 回归验证：系统设置首页正常拉起；崩溃缓冲无新增异常。

## moto g100 国行

XT2533-4 / portov，Android 16、MYUI 8、W1VT36H.1-51-8；本轮与历史记录固件相同，安全补丁 2026-04-01。本轮无 SIM。

| 组件 | 用户提供的历史 session | 本轮 ADB 检查（含重启后） |
|---|---|---|
| `com.mobiletools.systemhelper` | 当次未发现 | 全量包状态未见此包 |
| `com.motorola.regservice` | 2.0.001.0014，`/system/priv-app/RegService`；原已停用，User 0 卸载返回 Success | 仍未安装、已停止；共享 phone UID |
| `com.motorola.deviceshield.engine` | 1.0.0，`/system_ext/priv-app/PrcDeviceShieldEngine`；用户级停用 | enabled=3 保留，重启后未见进程 |
| `com.lenovo.lsf.device` | 原已 enabled=3 | 仍停用；更新层 V5.1.0.0330pg，系统副本 V5.0.2.0290pg |
| `com.zui.xlog` | — | 1.1.0062，`/system/priv-app/ZuiXlog`；本轮对 User 0 停用并重启 |

历史上在无网、无 SIM 条件下，通过 `com.android.packageinstaller` 界面侧载 Hiddify 一次成功；记录显示引擎包未找到并直接显示安装按钮，同时仍触发 DeviceGuard 的 IllegalAppProvider 查询与备案/商店匹配逻辑，另有一次 Play Protect SAFE 结果。

Xlog 原为 persistent，主进程及 usage 子进程运行；停用后子进程退出，补做 force-stop 后主进程仍在。Moto 重启后停用状态保留，主、子进程以及 UsageCollectorService、DeamonService 均未出现，设置页面可启动。启动阶段有两次服务未找到记录，约 15 分钟采样未见持续循环重试。启动阶段仍有操作前已存在的 `init` 原生 SIGABRT，未出现新增 Java FATAL EXCEPTION。

### 后续候选与依赖

以下为本机检出的相关组件与服务依赖（尚未停用）：

| 包与当前版本 | UID / 联网权限 | 路径、常驻服务、定时任务与处理边界 |
|---|---|---|
| `com.zui.sdac` 1.1.1270 | `10142` / 有 `INTERNET` | `/system/priv-app/ZuiSdac`；运行 `SDACService`、`CNSClientService`，注册 `com.zui.sdac.cns.hard.repeat.ALARM`，曾绑定 Xlog；涉及设备激活与 ZUI 推送。 |
| `com.zui.deviceidservice` 16 | `10115` / 有 `INTERNET` | `/system/priv-app/DeviceidService`；运行 `DeviceidService`，客户端包括 `smartplugins`、`smartservice` 和 `trip`。 |
| `com.lenovo.leos.cloud.sync` 7.0.42.99 | `10144` / 有 `INTERNET` | `/system/priv-app/XuiEasySync`；**常驻运行**，持 `QUERY_ALL_PACKAGES`、`CAMERA`、`READ_PRIVILEGED_PHONE_STATE`，在 JobScheduler 注册 `.common.service.BgJobService`。 |
| `com.zui.antitheft` 12.0.0.0.033 | `10251` / 有 `INTERNET` | `/system_ext/priv-app/FindMyPhone`；**常驻运行**，持 `QUERY_ALL_PACKAGES`、`ACCESS_FINE_LOCATION`、`CAMERA`、`READ_PRIVILEGED_PHONE_STATE`（联想国行防盗模块）。 |
| `com.motorola.cn.searchintelligence` 2.0.0.040、`com.motorola.cn.contentassistant` 1.0.0.034 | `10280` / `10247`（均有 `INTERNET`） | **均常驻运行**；前者持 `QUERY_ALL_PACKAGES`、`ACCESS_CHECKIN`，后者运行 `.appurl.GetAppUrlService`。 |
| `com.lenovo.levoice_agent` 1.12.7-moto、`com.lenovo.xiaotian.trigger` 1.0.251203 | `10253`（**无网**）/ `10140`（有 `INTERNET`） | 联想“小天”语音代理（**常驻**）与语音唤醒触发器（持 `RECORD_AUDIO`、`ACCESS_CHECKIN`）。 |
| `com.motorola.aiservices` 1.5.239.7 | `10169` / 有 `INTERNET` | `/product/priv-app/AiServices`；持 `ACCESS_FINE_LOCATION`、`PACKAGE_USAGE_STATS`、`ACCESS_CHECKIN`；常驻 `MayaManagerService`、`ContextEngineService`、`SemanticLocationService`（语义位置）、`SleepPatternService`，JobScheduler 注册 `.analytics.AnalyticsJob` 与 `.modeltrainer.ModelTrainerJob`。 |
| `com.motorola.appforecast` 06.01.0494-release、`com.motorola.cn.pkbservice` 1.0.0.44 | `10186` / `10274`（均有 `INTERNET`） | `appforecast` **常驻运行**，持 `QUERY_ALL_PACKAGES`、`ACCESS_CHECKIN`；`pkbservice` 为国行个人知识库服务（`PRCPKBService`）。 |
| `com.lenovo.lsf` V4.6.0.0117p | `10179` / 有 `INTERNET` | `/product/priv-app/LSF-User-Phone`；`lsf.device`（UID `10122`）虽已停用，但本包仍为 `enabled=0` 且持 `QUERY_ALL_PACKAGES`。 |
| `com.motorola.coresettingsext` 16、`com.motorola.msimsettings` 36.0.00.0000、`com.motorola.wifi.motowifimetrics` 16 | `10250`（有网）/ `10256`（有网）/ `10267`（**无网**） | **均常驻运行**且持 `ACCESS_CHECKIN`；分别注册有 `.core.checkin.CheckinBroadcastReceiver` 闹钟、`SmartSimCheckinJobService` 与 `.MotoWifiMetricsService` 任务。 |
| `com.motorola.cn.calendar` 9.0.9.007、`com.motorola.wallpaper.cn` 01.0.2.74、`com.motorola.wallpaperphotoshuffle` 1.0.98 | `10358` / `10139` / `10285`（均有 `INTERNET`） | 国行日历（`lecalendar`，**常驻**，持 `QUERY_ALL_PACKAGES`、`LOC`、`ACCESS_CHECKIN` 并跑 `.sms.RegularSmsJobService`）与国行壁纸组件（本机已使用 Google Calendar，可停用国行日历）。 |
| `com.google.android.federatedcompute` 16、`com.google.android.adservices.api` 16 | `10318` / `10325`（均有 `INTERNET`） | 位于 `/apex/`；联邦学习与广告归因模块，均持 `QUERY_ALL_PACKAGES`，当前 `enabled=0`。 |
| `com.motorola.motocare` 4.16.06 | `10259` / **无 `INTERNET`** | `/system_ext/priv-app/MotoCare`；运行 `MotoCareService`，持 `QUERY_ALL_PACKAGES`、`PACKAGE_USAGE_STATS`、`ACCESS_CHECKIN`，将相机、锁屏与设置事件写入 `.data.MotoCareProvider` 供 Checkin 链路读取。 |
| `com.motorola.help.extlog` 6.00.0000 | `10188` / **无 `INTERNET`** | `/product/priv-app/MotoFeedbackAssistant`；检查时无运行服务（主反馈应用为 `com.motorola.help` 6.00.0219，有 `INTERNET`）。 |
| `com.motorola.android.nativedropboxagent` 6.0 | `1007` (`log`) / **无 `INTERNET`** | `/system_ext/priv-app/com.motorola.android.nativedropboxagent`；`NativeDropBoxAgent` 常驻（persistent），本身无联网权限。 |
| `com.motorola.cn.smartservice` 2.0.2.029 | `10215` / 有 `INTERNET` | `/product/priv-app/Smartservice`；持 `ACCESS_FINE_LOCATION`、`QUERY_ALL_PACKAGES`；运行 `MyScreenExtService`、`AITripWidgetService`、`PersistService`（被 `com.motorola.systemserver` 绑定），JobScheduler 注册 `.CheckInSchedulerService`。 |
| `com.motorola.cn.smartplugins` 1.0.0.010 | `10212` / 有 `INTERNET` | `/product/priv-app/SmartPlugins`；持 `ACCESS_CHECKIN`，运行 `SmartPluginsService` 及计步 `PersistService` / `SensorService`。 |
| `com.motorola.cn.trip` 03.0.0.05.0 | `10214` / 有 `INTERNET` | `/product/priv-app/TravelInfoServices`；`TripService` 运行并绑定 `DeviceidService`，停用影响行程卡片。 |
| `com.motorola.dciservice` 1.0 | `10292` / **无 `INTERNET`** | `/system_ext/app/DciStatsService`；`DciStatsService` 被 `com.android.phone` 绑定，无联网权限。 |
| `com.motorola.ccc.devicemanagement` 16.00.0011 | `10245` / 有 `INTERNET` | `/system_ext/priv-app/3c_devicemanagement-binary`；持 `QUERY_ALL_PACKAGES`、`PACKAGE_USAGE_STATS`、`ACCESS_CHECKIN`；运行 `BlurServiceMother`、`CheckinService`、`SystemServerBindService`，JobScheduler 注册 `JobSchedulerService`。因具独立 UID `10245`，**按 UID 防火墙断网**可阻断 `CheckinService` 外连而不影响 `SystemServerBindService` 本地绑定。 |
| `com.motorola.deviceguard` 7.0.0_20251128011556 | `10279` / 有 `INTERNET` | `/system_ext/priv-app/PrcSecurityCenter`；涵盖 `IllegalAppProvider`、`PolicySyncService`、`SecurityScoreJobService`、`TrainAndPredictJobService`、联想 `upspushsdk`、电池与屏幕时间服务。因具独立 UID `10279`，**按 UID 阻断联网**可切断策略同步与推送，同时保留 `PackageInstaller` 对 `IllegalAppProvider` 的本地 IPC 查询及系统设置入口。 |
| `com.ted.number` 34.L.4.52.4 | `10135` / 有 `INTERNET` | `/system/priv-app/TdxIdentifyUnknownNumbers`；未见常驻进程，仅含 `NumberService`、`IdentifyProvider`、`YellowPageProvider`（无 Neo7 同名包中的 `nationalantifraud` 任务）。 |
| `com.motorola.prcaisafety` 1.0.0.09.0 | `10273` / 有 `INTERNET` | `/system_ext/priv-app/PRCAISafety`；含 `.AISafetyService` 与 `.AISafetyWaterMarkService`。 |
| `com.motorola.bach.modemstats` 2.16.02 | `10255` / 有 `INTERNET` | `/system_ext/priv-app/ModemStatsService`；持 `ACCESS_FINE_LOCATION`、`PACKAGE_USAGE_STATS`、`ACCESS_CHECKIN`；运行 `ModemStatsService`、`DataStallDetectService`、`NRCheckinService`、`NVProgrammerService` 及 4 项基带统计闹钟。 |
| `com.motorola.aicore` 1.1.127.4、`com.motorola.smarteye` 2.0.0.093、`com.motorola.enterprise.adapter.service` 16.01.0.038 | `10172` / `10282` / `10248`（均有 `INTERNET`） | 本机当前已处于停用状态（前两者 `enabled=3`，后者 `enabled=2`）。 |
| `com.motorola.ccc.ota` 36.00.043 | `10246` / 有 `INTERNET` | `/system_ext/priv-app/3c_ota`；独立系统更新包，本轮保留。 |

### 2026-11-20 Moto 第二轮全量隐藏威胁停用与 AppOps 剥权实操

1. **成功停用（`pm disable-user --user 0` 全部 26 个目标均变为 `enabled=3`，并执行 `force-stop`）**：
   - **联想云、国行防盗、搜索与语音唤醒（7 项）**：`com.lenovo.leos.cloud.sync`（`XuiEasySync`）、`com.zui.antitheft`（`FindMyPhone`）、`com.motorola.cn.searchintelligence`、`com.motorola.cn.contentassistant`、`com.lenovo.levoice_agent`、`com.lenovo.xiaotian.trigger`、`com.lenovo.lsf`（`LSF-User-Phone`）。
   - **Moto AI 位置/分析、应用预测与智慧场景链（8 项）**：`com.motorola.aiservices`（含 `SemanticLocationService` 与 `.analytics.AnalyticsJob`）、`com.motorola.appforecast`、`com.motorola.cn.pkbservice`、`com.motorola.cn.smartservice`（含 `.CheckInSchedulerService`）、`com.motorola.cn.smartplugins`、`com.motorola.cn.smartscene`、`com.motorola.cn.trip`、`com.motorola.myscreen`。
   - **ZUI 激活/标识、诊断、国行日历/壁纸与联邦学习（11 项）**：`com.zui.sdac`、`com.zui.deviceidservice`、`com.motorola.motocare`、`com.motorola.help.extlog`、`com.motorola.prcaisafety`、`com.ted.number`、`com.motorola.cn.calendar`（`lecalendar`，已确认 Google Calendar 在用；保留 `com.motorola.cn.deskclock` 以维持系统闹钟）、`com.motorola.wallpaper.cn`、`com.motorola.wallpaperphotoshuffle`、`com.google.android.federatedcompute`、`com.google.android.adservices.api`。
   - **进程清退结果**：26 个包中有 23 个包的进程与服务在 `force-stop` 后当场清零；仅 `com.zui.antitheft`、`com.lenovo.levoice_agent`、`com.zui.sdac` 因 manifest 声明 `PERSISTENT` 暂留内存（与首轮 `com.zui.xlog` 机制相同，待下次正常重启后彻底不再拉起）。
2. **耦合 Checkin / 安全组件的 AppOps 持久化剥权（7 项）**：
   - 对 `com.motorola.ccc.devicemanagement`、`com.motorola.deviceguard`、`com.motorola.coresettingsext`、`com.motorola.msimsettings`、`com.motorola.bach.modemstats`、`com.motorola.wifi.motowifimetrics`、`com.motorola.cn.deskclock` 执行 `cmd appops set --user 0 <pkg> <OP> ignore`：全部 7 个包的 `RUN_IN_BACKGROUND` 与 `RUN_ANY_IN_BACKGROUND` 均确认为 `ignore`；声明了使用情况统计权限的 `ccc.devicemanagement`、`deviceguard`、`bach.modemstats` 的 `GET_USAGE_STATS` 均确认为 `ignore`。
   - **回归验证**：系统设置首页正常拉起并恢复前台，崩溃缓冲 **0 条新增 Java FATAL EXCEPTION**。

## 恢复

验证器设置记录：本轮两机读取到的 global `verifier_verify_adb_installs` 均为 `0`，未作修改（该项仅控制 ADB 安装验证，独立于厂商安全组件扫描）。

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
