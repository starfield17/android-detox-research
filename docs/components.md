# 品牌与组件对照

研究范围为中国大陆国行 Android/AOSP 固件，包括 EMUI 和仍支持 Android 包管理与 APK 的 HarmonyOS 2/3/4.x；不包括 HarmonyOS NEXT 和后续非 Android 固件。先阅读[操作指南](guide.md)，了解三种证据等级、用户范围、恢复与验收。E、R、S、UI 分别表示启用或恢复默认状态、恢复用户级卸载、解除挂起、恢复设置；具体命令见指南。实际设备结果见[实机记录](devices.md)。

## 跨品牌 SystemHelper / RegService / DM 对照

以下是候选发现表，**不是要连续执行的卸载清单**。已有本机历史完成项只复查，不再次执行。列出的路径是样本路径，不是所有设备的固定路径。

纳入这组候选有具体行为依据：公开 realme GT5 Pro 的 SystemHelper 本地缓存中有设备/SIM 标识、使用统计、基站和位置，不能简单等同“完整安装清单”；该样本 HTTP 请求的业务正文有加密封装，不能写成所有内容明文裸传。一加 PJA110 的 RegService 报告则记录了应用清单/用量、网络环境等本地数据和上报流程。两份资料的分析对象不是当前 Neo7 新版 APK，本文不把字段逐项外推。[SystemHelper 样本](https://github.com/DreamingCats/com.mobiletools.systemhelper_analysis/blob/main/docs/analysis.md)、[RegService 样本](https://github.com/poppis-xin/coloros-regservice-telemetry/blob/main/README.md)

| 系统/组件 | 包名、路径或内部线索 | 适用记录与处理依据 | 动作、权限与恢复 | 功能损失与边界 |
|---|---|---|---|---|
| 跨品牌联通 SystemHelper | `com.mobiletools.systemhelper`；小米可在 `/system/priv-app/SystemHelper`，Neo7 当前在 `/product/priv-app/SystemHelper-release-20260609` | 小米 15 Ultra：HyperOS 3.0.314.0.WOACNXM / Android 16，4.0.0-20260610，User 0/10 卸载成功；Neo7 见[实机记录](devices.md)；realme GT5 Pro 有独立分析和用户重启反馈。[操作](https://github.com/LING71671/systemhelper-privapp-audit/blob/main/docs/mitigation.md#6-推荐用户级卸载免-root)、[realme 样本](https://github.com/DreamingCats/com.mobiletools.systemhelper_analysis/blob/main/docs/analysis.md) | ADB：`adb shell pm uninstall --user 0 com.mobiletools.systemhelper`；R。未处理目标可先 disable | 丧失运营商 DM/统计功能；已有结果没有完整覆盖所有 SIM、VoLTE/VoWiFi。勿与 `com.qualcomm.qti.services.systemhelper` 混同 |
| OPPO/一加/realme 移动 DM | `com.coloros.regservice`；`/product/app/RegService`；`cn.richinfo.dm`、`com.dmyk.android.telephony` | 一加 PJA110 / ColorOS 16.0.2.400 / Android 16 / RegService 16.0.1 有数据库、通信及移除记录；Neo7 两版本见[实机记录](devices.md)。[分析](https://github.com/poppis-xin/coloros-regservice-telemetry/blob/main/README.md) | ADB：`adb shell pm uninstall --user 0 com.coloros.regservice`；R；Neo7 已完成 | 失去对应 DM；仅数据库或 SDK 相同不能保证各版本上报字段相同 |
| OPPO/一加/realme 电信 | `com.oppo.ctautoregist`；Neo7 当前 `/product/priv-app/CTAutoRegist` | Reno9 / ColorOS 15 有停用结果；TelemetryCleaner 有 OPPO 处理反馈。[记录](https://github.com/byteharbor-k2/Secure-3C-Device/blob/main/docs/03-app-management/Chapter_1/1_debloat-main-system.md)、[项目](https://github.com/Eynnzerr/TelemetryCleaner/blob/0b2cbc303cec7d3af79d528f947025300d6819a5/README.md) | 试验：`adb shell pm disable-user --user 0 com.oppo.ctautoregist`；E；目标机未验证 | 失去电信终端自注册/相应短信流程；应插相应卡验证，不等于停掉 IMS 栈 |
| 小米移动 | `com.miui.dmregservice`；旧资料还见 `com.miui.regservice` | 小米 14 Ultra / HyperOS OS3.0.306.0，Shizuku v1.3 卸载成功，日常暂正常。[具体反馈](https://github.com/Eynnzerr/TelemetryCleaner/issues/18) | ADB 或 Shizuku：`adb shell pm uninstall --user 0 com.miui.dmregservice`；R | 不能用“日常正常”代替换卡、5G 消息、IMS 专项测试；旧包名只在实际存在时考虑 |
| 小米电信 | `com.xiaomi.registration` | 同一小米 14 Ultra 记录。[反馈](https://github.com/Eynnzerr/TelemetryCleaner/issues/18) | `adb shell pm uninstall --user 0 com.xiaomi.registration`；R | 失去电信自注册；VoLTE 风险须机型验证 |
| vivo/iQOO 移动+电信复合包 | `com.vivo.devicereg`，`/system/app/DeviceReg`；`cn.richinfo.dm`，也含独立 IMS/自注册分支 | X200 Ultra V2454DA / PD2454C_A_16.1.17.2.W10 / 5.4.0.0；免 Root 拒绝，Root 用户级卸载成功且报告录音正常。iQOO 13、Neo9 Pro 等有明确无 Root 失败日志。[X200](https://github.com/Eynnzerr/TelemetryCleaner/issues/7)、[iQOO 13 失败](https://github.com/Eynnzerr/TelemetryCleaner/issues/10) | 无 Root 先查保护状态；出现拒绝即转设置/网络方案。Root 命令见 vivo / iQOO 小节；R。可选 LSPosed RegBlocker | 不将“卸载必坏录音”当定论，也不把一台录音正常外推所有 IMS/卫星业务。Hook 是另一条已报告成功的路径 |
| 华为 Android 移动 | `com.huawei.regservice` / `HwCmccDm.apk`，`cn.richinfo.dm` | HarmonyOS 4.2.0.196(C00E182R8P6) 的公开 User 0 卸载反馈；作者未公布具体机型，未验证私有目录是否仍被访问。[记录](https://github.com/Eynnzerr/TelemetryCleaner/issues/4) | 有限实操支持，目标先 `adb shell pm disable-user --user 0 com.huawei.regservice`；E；卸载用 R | 该样本与下两包共享 `android.uid.phone`，勿按 UID 封网；不套到 NEXT |
| 华为/旧荣耀电信及联通注册 | `com.huawei.android.UEInfoCheck` / `UEInfoCheck.apk`；`com.huawei.android.AutoRegSms` / `ChnTelecomAutoReg.apk` | 同一 HarmonyOS 4.2 记录；UEInfoCheck 有双运营商实现，不应永远只标成电信。[记录](https://github.com/Eynnzerr/TelemetryCleaner/issues/4) | 逐项 `disable-user`，E；若用户级卸载则 R | AutoRegSms 可走短信而非 IP；仅封 INTERNET 不处理短信注册 |
| 新荣耀移动 | `com.hihonor.regservice` / `HnCmccDm` | honor-debloat 清单记为“已卸载”，但未给具体构建与通信回归。[原始清单](https://github.com/bruceCzK/honor-debloat/blob/33823962cb71ff9c36d2d3b58f38e03dbfd10302/references/package-list.md) | 试验：`adb shell pm disable-user --user 0 com.hihonor.regservice`；E/R | 公开记录缺少具体构建和通信回归，不能宣称当前所有 MagicOS 可安全删 |
| 新荣耀电信 | `com.hihonor.android.UEInfoCheck`、`com.hihonor.android.AutoRegSms` | 上述清单有 UEInfoCheck 停用；TelemetryCleaner 目录也收录，部分条目状态与文末“本人未验证”声明不完全一致。[清单](https://github.com/bruceCzK/honor-debloat/blob/33823962cb71ff9c36d2d3b58f38e03dbfd10302/references/package-list.md)、[目录](https://github.com/Eynnzerr/TelemetryCleaner/blob/0b2cbc303cec7d3af79d528f947025300d6819a5/README.md) | 先逐包核对、试停；E/R | 不把目录表的“已实测”升级成特定机型完整测试 |
| 魅族 Flyme | `com.meizu.regservice` | TelemetryCleaner 当前目录有此包，但缺可复核型号/构建/通信回归。[目录](https://github.com/Eynnzerr/TelemetryCleaner/blob/0b2cbc303cec7d3af79d528f947025300d6819a5/README.md) | 试验：`adb shell pm disable-user --user 0 com.meizu.regservice`；E | 归属和副作用按本机再确认；不给通用安全卸载保证 |
| 初代红魔线索 | `cn.nubia.register` | 项目收录、标未验证。[目录](https://github.com/Eynnzerr/TelemetryCleaner/blob/0b2cbc303cec7d3af79d528f947025300d6819a5/README.md) | 发现项；先查存在和职责，不提供默认删除动作 | 不外推到新红魔、MyOS 或所有努比亚 |
| Moto 国行 | `com.motorola.regservice`，`/system/priv-app/RegService/RegService.apk`；`cn.richinfo.dm`、`com.motorola.ctdm.SmsAutoRegistrationService` | XT2533-4 / W1VT36H.1-51-8 / 2.0.001.0014，用户级卸载及重启后复查记录见[实机记录](devices.md) | **历史完成**；R | 同包共享 phone UID；通信尚未插卡测试 |
| 三星国行特定样本 | `com.mobiletools.systemhelper` | SM-F9710 / One UI 9.0 / Android 17 / F9710ZCU3AZJ8 的公开冻结和多空间记录。[具体 issue](https://github.com/Eynnzerr/TelemetryCleaner/issues/5) | 按用户分别核查，优先单包 ADB；E/R/S 对应原动作 | 安全文件夹 150 可能仍安装；不可照搬用户编号；该 issue 的工具扫描故障也需避开 |

运营商模块既可能进行终端注册，也可能包含周期统计；**它们不等于电话进程、IMS 栈、APN 提供器或 CarrierConfig**。本报告不将 `com.android.phone`、`com.android.providers.telephony`、芯片 IMS 实现与上述包并排删除。不同年份的样本也不能互相替代。WiSec 2023 测的是 Redmi Note 11、OnePlus 9R、realme Q3 Pro 国行样本，不能证明华为或三星的具体行为。[论文](https://homepages.inf.ed.ac.uk/ppatras/pub/wisec23.pdf)

## 按品牌的组件与操作表

### 小米 / Redmi：MIUI、HyperOS

先在“手机管家 → 隐私与安全 → 安全 → 电诈防护”关闭不需要的 AI 通话预警、屏幕防护、短信/电话防护；按当前 UI 实际存在的选项操作。Gist 正文和评论覆盖不同设备/APK：正文称 GuardProvider 2.x，评论另分析 **3.0.7-20260708.0**；普通电话和 QQ/微信纯语音是音频路径，特定视频场景才录屏，不能合成“所有电话都录屏”。本地 `fraud_detection_data.db` 又是另一条记录链，关 AI 开关不能保证不写入。[原始核验与分开的评论](https://gist.github.com/std-microblock/c38cacab22bf0fffb94b247e09a4d948)

| 包/功能 | 理由、适用边界 | 建议动作和权限 | 代价、核验及恢复 |
|---|---|---|---|
| `com.mobiletools.systemhelper` / 两种运营商注册包 | 优先级高；见跨品牌具体固件 | 按跨品牌表逐包 ADB 处理 | E/R；通信测试 |
| `com.miui.analytics` | 统计候选；UAD 收录，历史实现资料不能证明当前仍有全部旧能力 | 试验：`adb shell pm disable-user --user 0 com.miui.analytics` | E；检查设置、商店、反馈，未知目标构建不得标“实测安全” |
| `com.miui.daemon` | 统计候选；实际存在再处理 | 试验：`adb shell pm disable-user --user 0 com.miui.daemon` | E；观察耗电/性能及系统功能。[数据库](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json) |
| `com.miui.systemAdSolution`；部分 ROM 的 `com.miui.msa.global` | 广告/推荐候选，名称不同不要自行替换 | 先关个性化推荐；需要时只对实际存在的一个包试停 | E；失去推荐广告服务，不等于停止所有遥测。[数据库](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json) |
| `com.xiaomi.security.onetrack`、`com.miui.misightservice` | 当前 TelemetryCleaner 新增检测对象；具体机型卸载回归不足 | **发现项**：记录版本、服务、依赖，暂不把新收录等于新验证 | 无改动无需恢复。[新增代码 PR](https://github.com/Eynnzerr/TelemetryCleaner/pull/20) |
| `com.miui.guardprovider` | 独立扫描/AI 服务，但参与安装授权；HyperOS 有停用后 ADB 安装失败反馈 | UI 关闭优先；若要整包试验：`adb shell pm disable-user --user 0 com.miui.guardprovider`，须预备马上恢复 | E；至少分别测 UI 侧载、ADB、商店安装/更新；不是所有入口都一定同时失效。[安装故障 issue](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/issues/557) |
| `com.miui.securitycenter`，内含 `com.miui.electricrisk` | 总安全中心与本地画像记录相关；数据库归属和提醒开关不同 | 不推荐默认整包删除。需另确认本包具体入口与依赖；[指南](guide.md)中的 GuardProvider 示例属于另一包，不能用于关闭本包画像逻辑 | 更改服务仅影响该入口，不保证内部非组件代码不再执行；整包可能损失多项管理功能 |
| `com.xiaomi.joyose`、`com.xiaomi.aicr` | 不是“遥测包就安全删”的例子 | 后置；没有与目标行为匹配的依据就不动 | 前者涉及游戏性能；后者有壁纸功能故障反馈。[aicr 具体 issue](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/issues/1110) |

不把未经核对的域名列表一股脑封掉。Gist 对 `flash.sec.miui.com` 与 `detection-aigc.engine.miui.com` 给出不同用途；`fraud-detection.engine.miui.com` 在该分析中用于 NFC 配置，紧急报警辅助地址也不应作为默认“反诈上报”黑名单。本文不复述完整接口与录制参数，因为操作选择需要的是功能链和版本边界。[核验来源](https://gist.github.com/std-microblock/c38cacab22bf0fffb94b247e09a4d948)

### OPPO / 一加 / realme：ColorOS、realme UI

这里至少有安装器、AppDetail、安全事件/管家、权限服务、独立安全支付与号码识别等层。旧版 `com.coloros.safecenter`、`com.oppo.safe` 与新版 `com.oplus.safecenter` 不能只因显示名类似就看成同一个实现。

| 包/组 | 处理理由和公开适用记录 | 建议动作 / 权限 | 损失、结果边界与恢复 |
|---|---|---|---|
| `com.oplus.statistics.rom`；旧 `com.nearme.statistics.rom` | 统计。OnePlus 9RT 有移除和 Settings 搜索故障记录；Reno9 / ColorOS 15 有停用结果；Neo7 验证见[实机记录](devices.md) | `adb shell pm disable-user --user 0 com.oplus.statistics.rom`；ADB | E；Neo7 搜索正常，不能消除旧版故障记录。[9RT](https://github.com/0x192/universal-android-debloater/issues/306)、[Reno9](https://github.com/byteharbor-k2/Secure-3C-Device/blob/main/docs/03-app-management/Chapter_1/1_debloat-main-system.md) |
| `com.oplus.onetrace` | 日志；Reno9 / ColorOS 15 有停用记录，Neo7 当前同包存在 | 试验：`adb shell pm disable-user --user 0 com.oplus.onetrace` | E；影响日志诊断；新 Neo7 未操作，不能写成已实测停止整套原生日志 |
| `com.oplus.postmanservice` | 诊断/校准相关；旧记录停用成功 | 试验：`adb shell pm disable-user --user 0 com.oplus.postmanservice` | E；可能损失工程/售后诊断；Neo7 检查前已 stopped，收益有限 |
| `com.oplus.logkit`、`com.oplus.crashbox` | 其他 ColorOS 日志候选 | 对确实存在的包逐项试停，不用一个旧包名补另一个 | E；**Neo7 未发现这两个包**，不得报告已停用它们。[旧版记录](https://github.com/byteharbor-k2/Secure-3C-Device/blob/main/docs/03-app-management/Chapter_1/1_debloat-main-system.md) |
| `com.oplus.metis`、`com.coloros.activation` | 行为/激活链候选；Reno9 有停用结果 | 试验，分别 `disable-user`，不要一次全停 | E；智能建议、激活及相关服务可能受影响；Neo7 Android 17 未验证 |
| `com.heytap.openid` | 标识服务候选；Neo7 可见 IdentifyService | 可试单包停用，但放在日志之后 | E；可能影响云盘/账号生态，需验证；不因 OAID 存在就说已上传全部应用清单。[数据库](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json) |
| `com.oplus.obrain`、`com.oplus.olc` | 日志链；Neo7 同时牵涉 MIDAS/多媒体与推送，见[实机记录](devices.md) | 先处理独立日志入口；整包停用为目标机未验证试验 | E；不能仅凭“日志”二字忽略调用方 |
| `com.coloros.remoteguardservice`、`com.coloros.familyguard` | 用户不用家庭/远程守护时值得处理 | 先从 UI 解除守护关系/撤销授权，再分别试停；前者有 Reno9 停用记录 | E/UI；远程协助、定位或守护提醒失效；并不说明当前有人远程控制 |
| `com.oplus.appdetail` | 安装安全与收尾 UI；Reno9 / ColorOS 15 停用有结果，但 RMX3700 / ColorOS 16 有挂起卡住安装/卸载反馈 | **Neo7 当前不作为本轮默认动作。** 在目标安装回归准备好后再试停，别先挂起 | E；若曾挂起，先 `adb shell pm unsuspend --user 0 com.oplus.appdetail`。Neo7 未改此包。[故障](https://github.com/rddmwmddr/android-ad-cleaner/blob/main/AGENTS.md) |
| `com.coloros.phonemanager`、`com.coloros.securityguard` | 有旧版独立停用/移除经验，不是“绝对不能动”；当前含多项安全、AI、事件功能 | 先关目标 UI；整包停用需要目标构建的安装、权限、锁屏回归；不能直接照搬旧三包批量脚本 | E/R；不同版本职责迁移明显 |
| `com.oplus.safecenter`、`com.oplus.securitypermission` | 当前权限/隐私、锁屏等功能；公开有具体故障 | 不默认整包删除；优先设置或最小子组件 | OnePlus Android 14 的 safecenter 移除影响锁屏、悬浮窗；不是“被系统绑定所以一定会变砖”。[具体修订](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/pull/439/files) |
| `com.oplus.romupdate`、`com.oplus.sau`、`com.oplus.sauhelper`、`com.oplus.cota`、`com.oplus.apprecover` | 云控、资源或系统应用更新、预装恢复候选 | 见[操作指南](guide.md)；逐层关闭自动项，不整批删除 | E/UI；没有证明它们必然恢复本机 SystemHelper/RegService |

Reno9 来源中的“将 Athena 叫作安装扫描器”“把 heytap.tas 叫作遥测”等功能概括不直接继承。Neo7 的 **`com.heytap.tas` 实际 codePath 为 `/product/app/TasWallet`，5.51.1**；它不能只凭 `tas` 缩写就列入纯统计清理。`com.oplus.athena` 也有后台管理等职责，不能因出现在清理脚本就当成独立反诈引擎。

### vivo / iQOO：OriginOS

先关闭“电话 → 电话设置 → AI 识别诈骗电话”，或“设置 → 安全 → 防骗中心”的对应选项，并单独关闭“保存诈骗电话通话内容”。官方材料区分离线服务包与其他保护功能；不能把需要离线包的识别直接写成云端上传。[vivo 官方操作入口](https://bbs.vivo.com.cn/newbbs/thread/38499336)

| 包/功能 | 适用资料 | 可执行路径、权限 | 已知代价与恢复 |
|---|---|---|---|
| `com.vivo.devicereg` 5.4.0.0 | X200 Ultra V2454DA / Android 16 / PD2454C_A_16.1.17.2.W10；本地采集与模块分析、Root 卸载记录 | **Root** 用户级卸载见下；无 Root 拒绝后不再反复撞；R | 公开反馈中通话、录音正常；不代表所有网络/卫星功能已穷尽测试。[原始记录](https://github.com/Eynnzerr/TelemetryCleaner/issues/7) |
| 同包的选择性拦截 | iQOO 13 V2408A / Android 16 / DeviceReg 5.4.0.0 | Root + LSPosed，RegBlocker 仅作用于该包；检查命中日志及数据库不再增长 | 作者报告采集/落库阻止、双卡 IMS 正常；未覆盖所有机型。恢复：关闭模块并重启目标进程/手机。[模块说明](https://github.com/Greatday2233/regblock/blob/main/README.md) |
| `com.bbk.iqoo.logsystem` | 上述 X200 Ultra 来源有采集、persistent 及处理记录 | 试验：`adb shell pm disable-user --user 0 com.bbk.iqoo.logsystem`；必要时重启复查 | E；诊断、试用版升级等功能需回归。不要以停用返回成功代替查进程 |
| `com.vivo.networkimprove` | 同机版本 16.0.1；作者报告基站与前台包名采样 | 试验：`adb shell pm disable-user --user 0 com.vivo.networkimprove` | E；网络诊断能力减少；未在实机记录中的两台设备验证 |
| `com.vivo.nps`、`com.vivo.epm` | 同一来源列为体验调查、异常策略候选 | 先查本机版本、服务与系统拒绝情况，再逐包试停 | E；不能将来源写的“安全”直接作为所有 OriginOS 保证 |
| `com.vivo.aiengine`、`com.vivo.abe`、`com.vivo.vms` | 同机来源显示场景、配置、标识链；不能使用数据库里“ABE 只是均衡器”等笼统注释定性当前包 | 先关智能场景、改进计划和 ID 个性化项；确需进一步减少通信时按端点/功能做隔离 | 这些实现可能共享 system UID；禁止为封一个包直接封 UID 1000。整包停用须专门回归，不给基础删除指令 |
| `com.iqoo.secure` / i 管家 | 与安全设置和管理入口相关 | UI 关闭安装扫描、风险提醒中可关闭的项目；整包试验后置 | E/R；目前不提供适用于 OriginOS 6 全部机型的“删管家即可自由安装”保证 |

上表后五行来源集中在一个 X200 Ultra 用户报告，本文仅据此建立处理候选和重启要求，不复述其中所有“安全”评级或端点列表。[报告与回帖](https://github.com/Eynnzerr/TelemetryCleaner/issues/7)

Root 用户级卸载的可复制形式如下；**这仍不删除系统分区 APK**，应先确认 `su -c id` 确实返回 UID 0，并保存原状态：

```bash
adb shell su -c 'pm uninstall --user 0 com.vivo.devicereg'

# 恢复（需该手机仍保留原包）
adb shell su -c 'cmd package install-existing --user 0 com.vivo.devicereg'
adb shell su -c 'pm enable --user 0 com.vivo.devicereg'
```

无 Root 的 `Cannot disable … no root permission` 是已记录的实际限制；ADB 启动的 Shizuku通常仍是 shell 权限。Binder 绕过可能只绕过部分命令入口检查，绕不过包管理服务内部的同一保护规则。[iQOO 13 失败日志](https://github.com/Eynnzerr/TelemetryCleaner/issues/10)、[Neo9 Pro 失败日志](https://github.com/Eynnzerr/TelemetryCleaner/issues/13)

RegBlocker 的验收重点是 `probe`、实际安装的 Hook 数，以及对应事件后库是否不再新增。**仅 force-stop DeviceReg 不是关闭 Hook 的方法**：模块仍启用时，进程下次启动还会重新注入。模块说明里对此写得不够清楚，执行者应先在 LSPosed 停用模块，再重启进程或手机。[源码项目说明](https://github.com/Greatday2233/regblock/blob/main/README.md)

### 华为 EMUI 与 Android 兼容阶段 HarmonyOS

| 固件类别 | 安装干预的处理入口 | 包级候选与回归重点 |
|---|---|---|
| EMUI Android 固件 | 在当前安全/应用安装界面关闭能关闭的检测；旧版菜单不套用新 HarmonyOS 路径 | `com.huawei.regservice`、`com.huawei.android.UEInfoCheck`、`com.huawei.android.AutoRegSms` 按实机确认；`com.huawei.bd`、`com.huawei.hiview` 可作为统计/诊断试验候选，但当前国行具体构建回归缺口仍在 |
| HarmonyOS 2.x、确认仍为 Android 兼容架构 | 若界面提供“退出纯净模式”，走其 UI 流程，不修改猜测的数据库键 | 与同机实际包名对应，不从显示名补包 |
| HarmonyOS 3/4.x、确认仍为 Android 兼容架构 | “设置 → 系统和更新 → 纯净模式 → 关闭增强防护”；安装页可能仍需勾选风险确认、输入锁屏密码 | 基础扫描仍可能存在；HarmonyOS 4.2.0.196 的三个运营商包有公开 User 0 卸载反馈 |
| HarmonyOS NEXT 及后续非 Android 架构 | **不在本报告范围内** | 不提供 Android `pm`/APK 操作；不能混用 HDC/bm 包表 |

华为官方对 3.0/3.1/4.0/4.2/4.3 的安装说明支持上述增强防护关闭流程，但这是安装限制的 UI 处理，不代表停掉所有扫描。[官方安装步骤](https://consumer.huawei.com/cn/support/content/zh-cn01089223/)、[官方应用检测说明](https://consumer.huawei.com/cn/support/content/zh-cn15897865/)

统计包试验命令分别为：

```bash
adb shell pm disable-user --user 0 com.huawei.bd
# 回归并决定是否保留后，再单独考虑另一项
adb shell pm disable-user --user 0 com.huawei.hiview
```

这些是**目标机未验证的试验命令**，恢复 E；不要把日志诊断关掉后仍可开机写成整机无副作用。`com.huawei.systemmanager` 不只是清理器，`com.huawei.coauthservice`、`com.huawei.security.privacycenter` 等也有安装/权限依赖。Mate 20 X HarmonyOS 4 / Mate 10 EMUI 12 的公开反馈记录了这些具体损失，但地区未明确，本文只把它用于依赖警示，不冒充当前国行验证。[依赖与重启反馈](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/issues/410)

`com.huawei.trustagent` 是智能解锁相关名称，不因含 `trust` 就等同远控。`com.huawei.bd` 也不能与蜂窝、北斗等包名按缩写类推。[组件数据](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json)

### 荣耀 Magic UI / MagicOS Android 固件

先关闭当前 UI 中“不需要的反诈防护”：AI 换脸/变声、AI 诈骗话术、相应通话/会议/视频图片场景。荣耀官方说明明确区分系统拨号语音、第三方语音、视频等路径，按实际支持应用处理。[反诈设置](https://www.honor.com/cn/support/content/zh-cn15887690/)、[另一版本说明](https://www.honor.com/cn/support/content/zh-cn15886207/)

| 包/组 | 处理理由与版本边界 | 动作和权限 | 损失与恢复 |
|---|---|---|---|
| `com.hihonor.regservice`、两个 `com.hihonor.android.*Reg* / UEInfoCheck` 包 | 运营商候选；具体包名以跨品牌表为准 | 逐包 ADB 试停；不运行整个外部清理脚本 | E/R；公开清单未给足够通信回归 |
| `com.hihonor.sceneservice`、`com.hihonor.awareness`、`com.hihonor.brain` | 场景感知和 AI 调度；公开清单记载停用，未附目标构建 | 先 UI 关相应建议/感知；确实不要能力时逐项 `disable-user` | E；场景卡片、助手/AI 功能会减少，不能只当遥测 |
| `com.hihonor.collectcenter` | YOYO 记忆/全局收藏候选 | 先取消记忆/收藏授权，再决定是否试停 | E/UI；全局收藏等能力失去 |
| `com.hihonor.ouc`、`com.hihonor.systemappsupdater` | OTA 和系统应用更新通道 | 先 UI 关闭自动下载、夜间安装；仅关闭通知不能停止下载/更新 | UI/E；自动修复和应用更新时效下降 |
| `com.hihonor.systemmanager` | 广泛安全、权限管理 | 先 UI/子功能，不默认整包删 | 保留当前权限链；不存在“所有荣耀都不能动”的保证，只有当前缺少充分回归 |

以上场景包来源为 [honor-debloat 的固定提交组件清单](https://github.com/bruceCzK/honor-debloat/blob/33823962cb71ff9c36d2d3b58f38e03dbfd10302/references/package-list.md)，它可提供包名和代价线索，但没有具体机型就不写成跨 MagicOS 实测。旧荣耀可能仍用 `com.huawei.*`；新荣耀的 `com.hihonor.phoneservice` 是“我的荣耀”一类服务，不能仅因权限多就当成整个反诈内核。

### 三星国行 One UI

三星的直接操作入口比“删整个智能管理器”更明确：

| 功能/包 | 适用边界与理由 | 操作 | 代价与恢复 |
|---|---|---|---|
| 自动拦截程序 / Auto Blocker，含最大限制 | One UI 对未授权来源安装、USB 命令等有限制；官方列有开关，6.1.1 起功能增加 | 设置 → 安全与隐私 → 自动拦截程序，关闭不要的功能；先处理它再启用 ADB | 恢复 UI；这不等同关闭其他安全扫描。[中国官方说明](https://www.samsung.com.cn/support/mobile-devices/protect-your-galaxy-device-with-the-new-auto-blocker-feature/) |
| 应用程序保护 / App protection | 官方说明中国使用 Tencent，其他地区可用 McAfee | 设备维护 → 应用程序保护，关闭相应扫描；若最大限制强制开启，先关最大限制 | UI；失去对应恶意软件扫描。[官方支持说明](https://support-cacyber.samsung.com/cacyber/popup/iframe/pop_troubleshooting_fr.jsp?idx=903542&lang=ca) |
| `com.samsung.android.sm.devicesecurity` | 可作为独立安全包候选，但同名包在不同地区引擎/职责未必相同 | **国行当前未验证的试验**：核对后才考虑 `adb shell pm disable-user --user 0 com.samsung.android.sm.devicesecurity` | E；必须测各安装入口，不照搬海外 McAfee 清理经验 |
| `com.samsung.android.sm_cn` | 国行智能管理器主体，含多项设置 | UI/子功能优先，整包后置 | E/R；不默认删整包。[组件项](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json) |
| `com.sec.android.diagmonagent` | 诊断候选 | 先 UI 关闭发送诊断；包级试验需观察重试 | 数据库记录某 9.0.11 样本停用后重拉、发热，地区未明，不当成所有国行结论。[组件记录](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json) |
| `com.samsung.android.sm.policy` / SCPM | 策略配置候选 | 不默认停止整个策略通道，先查目标功能 | 改策略可能影响其他系统能力 |
| `com.mobiletools.systemhelper` | 已有特定 SM-F9710 国行多空间报告 | 见跨品牌表，按用户检查 | E/R/S；不能漏掉 Knox 安全文件夹 |

不把 `com.samsung.android.kgclient`（Knox Guard/支付或设备限制相关）作为普通遥测包处理；其变更可能触发锁定。是否存在企业管理应另查 `dumpsys device_policy`、设置中的设备管理员/管理资料，不按包名认定。[数据库风险记录](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json)

### 摩托罗拉 / 联想：MYUI、ZUI

具体设备的证据见[实机记录](devices.md)。跨型号仅采用以下方向：

| 目标 | 可执行建议 | 适用边界与恢复 |
|---|---|---|
| 国行 `com.motorola.regservice` | 已存在、确认职责后先试停或用户级卸载 | XT2533-4 有用户实操与复查；其他型号试验；E/R |
| 国行 `com.motorola.deviceshield.engine` | 优先于整个安全中心；单包 `disable-user` 后真实 UI 安装回归 | XT2533-4 的 1.0.0 有一次安装验证；E |
| `com.zui.xlog` | 日志/应用用量，单包停用并检查 persistent | XT2533-4 有有限验证；E。ZUI 平板条目只能辅助包名核对，不证明 Moto 副作用相同 |
| `com.zui.sdac`、`com.zui.deviceidservice` | 后置的激活/推送、标识候选 | 先检查实际客户端和功能；E；目标机未处理 |
| `com.motorola.motocare`、`com.motorola.help.extlog`、`com.motorola.android.nativedropboxagent` | 诊断与反馈候选 | 设备检查发现，未停用；尤其 log 共享 UID 不按 UID 封网 |
| `com.motorola.ccc.devicemanagement`、`com.motorola.dciservice` | 不是因为被绑定就绝对不能动，但须先缩小到具体采集/签入入口 | 整包处理后置；电话、系统服务、OTA 需回归；E |

公开清理脚本往往覆盖海外 Moto，不能把它们的成功/警告直接搬到中国版 MYUI 8。UAD 对 CCC 的一般化 MDM 描述也不足以证明这台机的实际远控行为。[数据库](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json)

### 魅族、中兴、努比亚、红魔等

| 组件 | 纳入理由、资料边界 | 后续操作与恢复 |
|---|---|---|
| 魅族 `com.meizu.regservice` | 运营商候选，公开目录收录 | `pm path`、`dumpsys package` 确认后试停；E。无当前 Flyme 详细功能回归 |
| 魅族 `com.flyme.telecom.usagedata.service` | UAD 收录的用量类线索，职责说明不够确定 | **发现项**；先查电话耦合，暂不给默认删除命令 |
| 魅族 `com.meizu.cloud` / `com.meizu.safe` | 云/推送与安全总包候选 | 不需要云推送时可试前者；后者先 UI，不凭清理标签整包删 |
| 努比亚 `cn.nubia.identity`、`cn.nubia.neopush`、`cn.nubia.woodpecker`、`cn.nubia.persist` | 数据库收录，可用于发现标识、推送或日志线索；缺当前国行构建回归 | `dumpsys` 核对后逐包试停；E；推送、售后等能力可能损失，不一键套清单 |
| 中兴 `com.zte.zdmdaemon`、`com.zte.zdmdaemon.install` | 数据库收录的采集/日志候选；现代 MyOS 的确切职责仍须目标机核对 | 试验候选；不把旧包名自动外推到同品牌所有新机 |
| 努比亚 `cn.nubia.security2`；中兴可能的 `com.zte.heartyservice` | 多功能安全/管理线索 | 先设置和内部功能，不默认删除；E/R |

这些仅是 [公开数据库](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/31e3dea4546c9b05eb975474d30ea7c88fd0b930/resources/assets/uad_lists.json) 的发现入口，尚无足够当前国行操作结果。红魔 10/10S Pro 的 RedMagicOS 10.5.9 **EU** 清理帖明确是海外固件，本文不拿它证明国行可删；也不抄其中删除设置向导、支付组件等整批动作。[EU 对照原帖](https://www.reddit.com/r/RedMagic/comments/1n6itot/debloat/) 未找到记录不等于该品牌没有相关组件。
