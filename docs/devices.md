# 两台实机：记录、复查与恢复

本文分别标明历史 session 记录和 2026-11-17 的普通 ADB 检查结果。本轮新增操作为 Neo7 DCS 和 Moto Xlog 的用户级停用。操作方法和验收原则见[指南](guide.md)，跨设备组件见[组件](components.md)，来源见[来源](sources.md)，项目概览见[首页](../README.md)。

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
| `com.coloros.remoteguardservice` 17.2.2、`com.coloros.familyguard` 17.3.1 | `10124` / `10291`（均有 `INTERNET`） | 均安装启用；前者提供 `AppEventProvider`、`AppUsageProvider`，后者内嵌华为 HMS / Firebase Push 与 Drs Track。 |
| `com.android.federatedcompute.services` 17 | `10268` / 有 `INTERNET` | `/apex/com.android.ondevicepersonalization/`；Android OnDevicePersonalization 联邦计算模块，持 `QUERY_ALL_PACKAGES`。 |

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

历史记录中的 `fraud_app_observer_switch=1`、`install_app_detail_safeguard_state=0`、`oplus_customize_cta_user_experience=0` 本轮仍可读取，未修改。

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
| `com.motorola.aiservices` 1.5.239.7 | `10169` / 有 `INTERNET` | `/product/priv-app/AiServices`；持 `ACCESS_FINE_LOCATION`、`PACKAGE_USAGE_STATS`、`ACCESS_CHECKIN`；常驻 `MayaManagerService`、`ContextEngineService`、`SemanticLocationService`（语义位置）、`SleepPatternService`，JobScheduler 注册 `.analytics.AnalyticsJob` 与 `.modeltrainer.ModelTrainerJob`。 |
| `com.motorola.appforecast` 06.01.0494-release | `10186` / 有 `INTERNET` | `/product/priv-app/MotoAppForecast`；持 `QUERY_ALL_PACKAGES`、`ACCESS_CHECKIN`，在 JobScheduler 有后台任务。 |
| `com.lenovo.lsf` V4.6.0.0117p | `10179` / 有 `INTERNET` | `/product/priv-app/LSF-User-Phone`；`lsf.device`（UID `10122`）虽已停用，但本包仍为 `enabled=0`。 |
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
| `com.google.android.federatedcompute` 16 | `10318` / 有 `INTERNET` | `/apex/com.android.ondevicepersonalization/`；联邦学习模块，当前 `enabled=0`。 |
| `com.motorola.ccc.ota` 36.00.043 | `10246` / 有 `INTERNET` | `/system_ext/priv-app/3c_ota`；独立系统更新包，本轮保留。 |

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
