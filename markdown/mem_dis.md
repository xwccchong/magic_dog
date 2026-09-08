# `memx` / `memsys` 项目结构梳理(核对修正 + 细化版)

> 版本说明:本文档已逐项对照代码库核实,并细化到模块/服务级别。文末附"勘误表"列出初版(基于设计文档)与代码实际实现的差异。
> 代码规模: `src/memsys` 共 535 个 Python 文件、约 15.8 万行;`tests/` 314 个测试文件。包名 `memsys`(pyproject.toml, v0.3.6, "ant memory project")。
> 关于"论文":仓库中没有独立的研究论文 PDF。最接近的是 `docs/memsys/Iterative_Design_for_MemSys_Co-Created_by_Human_Programmers_and_LLMs(_ZH).md`——一份**人机协同开发元规范**(人类当架构师、LLM 当实现者、design-as-code、`docs/` 与 `src/` 镜像)。MemSys 系统设计见 `docs/memsys/MEMSYS_ARCHITECTURE.md`(早期蓝图)与 `docs/memsys/2025-11-17 一期用户理解记忆系统(MemSys)工程系分.md`;当前分支的代码级梳理见 `docs/pipeline_v2_current_branch_design.md`。

---

## 一、项目定位

**MemSys(用户理解记忆系统)**:为应用层提供**统一记忆写入(Add)与检索(Search)接口**的记忆中台;应用层只感知这两个接口(上下文直接集成或 function-call)。同时是多种记忆方案的**实验对比平台**:内置 `mem0` / `lightmem` / `ekko` / `lingximem` / `mem0g(graph)` / `structured_graph` / `health_iot` 等可插拔抽取与检索策略,经"模板 + 实验参数 profile"组合跑 A/B 实验(locomo_ekkomem_v1 等)。

**部署形态**(代码证据):
- 本仓库同时是 **ANT oneapi 应用**(根目录 `f.yml`):`assistantiimed`(医疗助手 BizFunction,uniqueId=medical-assistant)与 `vmevalengine`(IoTDataFacade);对应生成代码在 `service/tr/oneapi/{assistantiimed,medaiothub,vmevalengine}/`。
- 宿主应用 **Memora** 多进程部署:`server.workers`(OS 进程数)× `memsys.extraction_worker.max_workers`(每进程 Worker 并发),进程 fork 后需在启动钩子调用 `EngineProcessEnv.initialize()` 才能创建 V2 Runtime。
- 关键依赖(pyproject):`redis`、`openai`、`vdb-sdk`(向量库)、`pyturso`、`langchain-neo4j`、`graphuniverse-client`(内部图库)、`layotto`/`grpcio`(RPC)、`nltk`/`jieba3k`/`rank-bm25`(BM25)、OpenTelemetry 系列。

## 二、分层架构(实际代码形态)

设计文档的"三层隔离"仍然成立,但**注册/接线机制以代码为准**:

| 层 | 职责 | 代码位置 | 实际机制 |
|---|---|---|---|
| **图引擎层** | 构图、调度执行,无业务逻辑 | `engine/` | `ExecutionEngine` 动态发现模块;`Pipeline` 递归 DAG |
| **工程控制层** | 原子模块,功能执行入口 | `modules/` | 每个模块类用 `@module` 装饰器声明元数据 |
| **算法策略层** | 开放给算法的策略 hook | `algorithm/strategy/` | 策略由节点配置 `strategies.*` 选取,随模块执行 |
| **基础服务层** | LLM/向量/图/存储等外部依赖 | `service/` | `@service_provider(类型, provider)` 注册进 `SERVICE_REGISTRY` |

接线细节(替换初版"StrategyRegistry"的说法,该类**代码中不存在**,是 ARCHITECTURE 蓝图未落地的设计):

1. **模块发现**:`@module(name, input_type, output_type, services)`(`engine/base_module.py:123`)给类打上 `_module_name/_module_input_type/_module_output_type/_module_services`;构造函数被包装,自动从 `ServiceManager` 注入声明式依赖服务(DI)。`ExecutionEngine._discover_modules_and_strategies()` 遍历 `memsys.modules` 与 `memsys.algorithm.strategy` 两个包,按属性收集模块类到 `module_metas`。
2. **服务注册**:`@service_provider(service_type, provider)`(`engine/service/registry.py`)把实现类按 `(service_type, provider)` 二元组登记进 `SERVICE_REGISTRY`;`ServiceManager.initialize()` 解析 `conf/service/*.yaml`,按 provider 实例化并缓存(进程级单例)。
3. **策略选择**:pipeline 配置里每个节点携带 `strategies.{NAME}`(strategy_name + default_enabled + config);策略类的选择与版本切换发生在配置层,而非全局注册中心。少数算法域另有独立工厂单例(`ExtractionStrategyFactory`、benchmark 的 `AdapterFactory`/`EvaluatorFactory`、lightmem 的 `PreCompressor/TopicSegmenter/TextEmbedder` 工厂等)。
4. **模块间依赖**:节点声明 `dependencies: {字段: 来源节点.字段 | '@.根输入字段'}` 显式映射;`PipelineConfig`(会话期只读,模块不可写)/`PipelineContext`(引擎内部状态,不暴露给模块)分离——对应系分文档"避免 rtb AdContextDTO"的约束。
5. **策略并发**:`BaseModule` 支持 `COROUTINE/THREAD` 两种调度、`FAIL_FAST/COLLECT_ALL` 失败模式、`StrategyTask/StrategyResult` 批量结构(`engine/base_module.py`)。

## 三、配置体系(三级资源 + 实验参数)

**入口**:`Memx._load_pipeline_config()` 优先级:① 请求 `config["pipeline_config"]` 直传 → ② `config["memory_template"]` 命中模板 → ③ fallback `conf/pipeline/v2/output/{instance_id}/{template}.yaml` → ④ `v2/output/default_{add,search}.yaml`。

**`MemoryTemplateManager.TEMPLATES`**(`common/memory_template_manager.py`)——`memory_template` 直接选整套链路,共 21 个:

- mem0 系:`mem0`、`mem0_enhance`、`mem0_k300`、`mem0_hybrid`、`mem0_lingxi`、`mem0g`(图存储)
- lightmem 系:`lightmem`、`lightmem_0526`、`lightmem_lingxi`
- 工作记忆 V1 系:`work_memory`、`work_memory_create`(手动创建)、`work_memory_batch`(批量导入)、`work_memory_afu_groupchat`(阿福群聊)、`ekko_memory_lite_search`
- V2 系:`v2`、`v2_max`、`v2_lite`、`v2_xdy`(信贷员)、`health_iot`
- 其他:`gam`(deepresearch)、`insurance`(保险,月度/实时双路召回)

**V2 三层资源**(`conf/pipeline/v2/`):
1. `templates/add|search/*.yaml` —— 节点模板(声明模块、输入输出 schema、默认策略配置)。
2. `templates/unified_{add,search}_pipeline.yaml` —— Pipeline 编排模板(节点顺序与默认依赖)。
3. `output/*.yaml` —— **编译产物**(flat 可执行格式,运行时直接消费;`default_add.yaml` 根模块为 `conditional_async_pipeline`)。
另有 `profiles/*.yaml` —— **实验参数 override**(键形如 `memx:default_search:RECALL.strategies.BM25_RECALL_STRATEGY.config.top_k`,逐键覆盖与默认值的差异;由 `tools/generate_v2_profiles.py` 生成、`scripts/gen_exp_params.py` 产出合法键清单)。当前 profiles:`ekko_v5_max`/`ekko_v5_lite`(locomo_ekkomem_v1 实验,补开 BM25 双路/time_filter/rerank 对齐旧 work_memory 行为)、`medical_personal_v2`(医疗个人搜索,六阶段全 Medical Strategy)、`health_iot`、`v2_huaxiaobei`、`v2_xdy`、`v2_graph_question_only`。

编译工具:`tools/pipeline_v2_builder.py`(`PipelineConfigBuilder`:加载节点模板+Pipeline 模板,按 `hook_node_name` 分组合并策略,每个 hook 至多启用一个 strategy)。

## 四、两条核心流水线(V2 实际形态)

**Add(默认产物 `output/default_add.yaml`)**:根模块 `conditional_async_pipeline`,当前产物默认 `enable_conditional_async: false`(同步;条件异步经请求覆盖开启)。

```
同步前置: ADD_INPUT_VALIDATION → CONTEXT_PACKAGE
异步阶段(extractor, Worker 执行): LOAD_UNITS → STRATEGY_REFINE
  → MEMORY_MODELING → SIMILAR_RECALL → MEMORY_DECISION → POSTPROCESS
```

- **同步模式**:按依赖顺序跑完所有节点。
- **条件异步模式**(`enable_conditional_async=true`,与 `enable_async` 互斥):请求只执行 pre_nodes,CONTEXT_PACKAGE 判定 trigger_status;满足时经 TBase MEM 命令写 STM 并立即返回 `task_id`(accepted),后续由 Worker 抽取。mem_id 格式 `{instance_id}:{user_id}:{run_id}:{agent_id}`;`MEM.CREATE` 下发 threshold/idle_hours/ttl_hours 触发规则给 MEM **服务端**(非客户端判断)。
- **Worker 链路**(`service/queue/extraction_worker_v2.py`, 2414 行;由进程级单例 `UnifiedWorkerManager` 启动,`EngineProcessEnv` 负责生命周期):
  1. 只轮询 `WorkMemoryInstanceRegistry.list_runtimes(use_pipeline_v2=True)` 的各 runtime;
  2. 公平轮询 `MEM.TAKESUMM(owner, count=1)` 领任务,本地 `instance_id:mem_id` 去重;
  3. `RANGEBYINDEX` 读取当批前 10 条 STM 消息;
  4. `MemMessage.resolve_add_data()` hydrate(优先 `meta.add_data_raw`,失败降级最小 AddData);
  5. 组装 `entry_data`,复制 runtime 的 `pipeline_config` 注入 `_async_stage="extractor"`;
  6. 复用同一个 `ExecutionEngine.execute_pipeline()` 派生内层 pipeline(LOAD_UNITS→POSTPROCESS);
  7. **只有执行成功且写库 action 全部成功**才 `MEM.ARCHIVESTM`(STM 剪切到 backup_stm)+ `ACKSUMM OK`;否则保留 STM、`ACKSUMM FAILED_RETRY`(MEM 不存在/校验错则 `FAILED_DROP`)——保证失败不静默丢数据。
- 异步任务查询:`engine/async_task/`(FastAPI 路由 `/async-tasks`,依赖可选;state_store 查询任务状态)。

**Search(默认产物 `output/default_search.yaml`,普通六阶段 DAG)**:

```
SEARCH_INPUT_VALIDATION → QUERY_PROCESS → ROUTER_PLAN → RECALL → RERANK → POST_PROCESS
```

默认开启的策略:`SEARCH_INPUT_VALIDATION_STRATEGY`、`QUERY_PROCESS_STRATEGY`(`analyze_mode=llm`, prompt=query_understanding_zh_v1.1)、`VECTOR_RECALL_STRATEGY`(top_k=60)、`POST_PROCESS_STRATEGY`;BM25/时间/图/DeepResearch/Rerank/CE 保留候选但默认关闭,由 profile 或请求配置启用。加入医疗 profile 后各阶段切 Medical, Strategy,RECALL 关 vector 走 IoT 实时召回。

## 五、目录结构(细化为服务级)

```
src/memsys/                       # 535 py 文件 / ~15.8 万行
├── main.py            (3456行)   # Memx 门面类: add/add_async/search/summary_work_memory/
│                                  #   clear_work_memory/delete_work_memory/get_sessions + CRUD 兼容层;
│                                  #   release_id→ServiceManager 池(切流换 SM 不重建);
│                                  #   V1(Work Memory)/V2(conditional-async) 双 Runtime 家族,uint32 由
│                                  #   实例原始配置 use_pipeline_v2 冻结,运行时禁止跨家族切换;
│                                  #   Request/Message Build 状态登记(registration→ACK SUCCESS/DROP)
├── engine/            (5.3k, 32文件)
│   ├── execution_engine.py        # 执行流引擎: 模块发现/节点构造/SM 选择器/trace hooks
│   ├── base_module.py             # BaseModule/BaseStrategy/@module 装饰器/并行策略执行
│   ├── service_manager.py         # 进程级服务管理: 解析 conf/service 创建并缓存各服务
│   ├── service/registry.py        # SERVICE_REGISTRY + @service_provider 二元组注册
│   ├── service/config/*.py        # 各服务 pydantic 配置(按 provider 判别联合)
│   ├── pipeline/                  # Pipeline(递归DAG)/PipelineConfig/PipelineContext
│   ├── pipeline_v2/               # ConditionalAsyncPipeline 条件异步根模块
│   └── async_task/                # FastAPI 异步任务查询 API(可选依赖 + mock 兼容)
├── modules/           (19k, 58文件) # 工程控制层原子模块
│   ├── add/                       # add_input_validation/context_package/load_units/
│   │                              # strategy_refine/memory_modeling/similar_recall/
│   │                              # unified_memory_decision/postprocess
│   ├── search/                    # search_input_validation/query_process/router_plan/
│   │                              # recall/rerank/post_process(+medical 观测)
│   ├── work_memory_*              # work_mem_extractor/create/stm_recall + wm_* 检索族
│   └── …                          # lightmem_extraction、双路/混合召回、graph_recall/update、
│                                  # judge、render、rerank、pre_compressor、text/cluster_chunk 等
├── algorithm/         (48k, 146文件) # 算法策略层
│   ├── strategy/add/              # memory_decision(direct/ekko/llm/health_iot_lifecycle)…
│   │   ├── memory_modeling/        # ★ 抽取策略矩阵: mem0 / lightmem(unified) / ekko(zh/群聊/
│   │   │                          #   多模态/华夏小贝/xdy_dense) / afu / dp / structured_graph /
│   │   │                          #   health_iot / lingximem(经 module) 
│   │   ├── strategy_refine/        # topic_detection/merge、memory_value_judge、pre_compressor、
│   │   │                          #   multimodal_enrichment、ekko_turn_merge
│   │   ├── similar_recall/          # bm25/vector 相似召回(写路径去重用)
│   │   └── postprocess/            # graph/structured/unified/health_iot 写库策略
│   ├── strategy/search/           # query_process(医疗contracts)/recall(9种)/rerank(分阶段)/
│   │                              # router_plan(医疗/通用)/post_process(睡眠计算/医疗指标)
│   ├── strategy/health_iot/domain/ # 指标注册/canonical/投影/校验等领域模型
│   └── strategy/prompts/          # ★ 全部 Prompt 以 yaml 外置(add/memory_modeling、
│                                  #   search/query_process|recall|rerank,zh/en 双语多版本)
├── service/           (59k, 220文件) # 基础服务层
│   ├── llm/                       # openai_service(provider="openai", 兼容openai协议)
│   ├── emb/                       # embedding: tbase/deepfuse/openai/random/local
│   ├── vector/                    # ★ 向量库: tbase.py(TbaseService+WorkMemoryService, 2559行起)/
│   │                              #   oceanbase(.py&_afu)/vectordb(v1)/vectordb_v2(vdb-sdk)/
│   │                              #   turso_vector/turso/ + graph_vector + 过滤方言/字段映射
│   ├── graph/                     # ★ 图存储: adapter(graphuniverse: direct+gustudio/tinygraph)/
│   │                              #   blueprint(embedding_cache/entity_feature/mem0g_knowledge_graph/
│   │                              #   structured_evidence_graph/user_centric_memory/…)/
│   │                              #   core(graph_service)/memory(neo4j_memory/factory)
│   ├── lightmem/                  # lightmem 全家桶: configs+factory(pre_compressor/llmlingua2/
│   │                              #   entropy, text_embedder, topic_segmenter)+memory_buffer(感觉/
│   │                              #   短时记忆)+lightmem_service
│   ├── lingximem/                 # 灵犀记忆服务
│   ├── structured_graph/          # DeepFuse 结构化图(算法/engine_executor/udf_shell/tinygraph)
│   ├── reranker/                  # openai(1/v2)+aq_memory_v2
│   ├── queue/                     # extraction_worker(v1)/extraction_worker_v2(2414行)/
│   │                              # unified_worker_manager/persistent_task_queue
│   ├── memory_store/              # memory_crud_store(CRUD 门面)/vector_memory_store
│   ├── tr/                        # ★ 中台对接: iot(健康IoT contracts/服务/睡眠聚合/
│   │                              #   指标映射/校验)、normalization、oneapi(assistantiimed/
│   │                              #   medaiothub/vmevalengine 生成代码)、arecpyproxy
│   ├── cache/ checkpoint/ trace/  # 检查点管理、turso/graph trace 服务
│   ├── db/                        # work_memory_store/request_build_status_store/
│   │                              # project_storage_binding
│   └── rpc/ loop_local/ process_env.py …
├── common/            (15k, 46文件)
│   ├── protocol.py               # AddData/AddRequest/AddResponse/SearchData/SearchRequest/
│   │                             # SearchResponse/MedicalSearchResponse/BuildStatus/删除条件
│   ├── base.py                   # MemoryItem/ActionDict/过滤条件
│   ├── mem_work_memory_client.py # ★ TBase redis-mem 客户端(MEM.* 命令;+async 版)
│   ├── work_memory_instance_registry.py  # Runtime 注册表(activation_lock/stm_write_transaction)
│   ├── work_memory_*.py          # manager/types/config/visibility/alias_map/identity…
│   ├── stm_mem_identity.py       # mem_id 编码(codec/AutoV2 群聊/非群聊 profile)
│   ├── tracer/                   # OTel tracer/metrics/span_registry/memory_trace/trace_collector
│   └── …                         # feature_flags/model_config/prompt_safety/async_completion 等
├── provenance/        (6.3k, 13文件) # 记忆溯源: ledger/trace/schema(redaction/sidecar/
│                                  #   projection/scope)+sql 建表; contracts 见 docs/contracts/
├── benchmark/                     # 评测框架: dataset(AdapterFactory, 内置 demo_adapter)/
│                                  #   evaluation(EvaluatorFactory, 内置 locomo10+llm_judge)
├── conf/                          # pipeline(v1 模板+v2 三级资源)/service(默认、work_memory、
│                                  #   medical_personal 示例)/feature_flags/iot(metric_registry)
├── data/                          # locomo10.json/insurance uid*.json/insx_sample_test_v1/
│                                  #   vocab 词表(jieba/BM25/弱约束关键词)
└── util/                          # const/rerank_score

├── tools/                         # pipeline_v2_builder(编译)、generate_v2_profiles/defaults、
│                                  # gen_exp_params、tr_oneapi_codegen/tr_facade_runner(oneapi)、
│                                  # vectordb_tool(_v2)、health_iot_*、export_provenance_*
├── scripts/                       # query_vectordb.py
├── group_chat_biz/                # 医疗群聊评测业务: bench 147 条样本、AFU 群聊抽取/检索/
│                                  #   评测/回填/清数脚本(shell+py)
├── tests/            (314文件)    # mirror src: memsys/{engine,modules,algorithm,service,common,
│                                  #   provenance,benchmark,conf,runtime,util,tracer}+boundary+
│                                  # group_chat_biz+tools+fixtures
├── docs/                          # ① API/设计: mem-redis.md(TBase redis-mem 协议)、work-mem.md、
│                                  #   work_memory_{design,pipeline,scope,batch_import,v2_migration}、
│                                  #   ADD_PIPELINE(_V2_DESIGN)、pipeline_v2_current_branch_design、
│                                  #   hybrid_recall_rerank_pushdown、stm_mem_id_format、
│                                  #   iot_*(两个算法交接) ② 规范: coding-standards/、
│                                  #   contracts/(provenance-trace-v1.schema.json)、spec-kit/、
│                                  #   superpowers/ ③ memsys/(架构+人机协同规范+DeepFuse指南)
├── designs/                       # 按日期归档的增量设计决策(2026-07~09: stm-mem-id 格式、
│                                  #   群消息粒度、统一模型调用、v2 并行执行/共享TBase隔离/
│                                  #   异步失败丢弃/worker生命周期、PR范围收敛、手动创建状态…)
├── f.yml                          # oneapi 应用声明(assistantiimed + vmevalengine)
└── pyproject.toml .aci.yml .pre-commit-config.yaml .flake8 setup.sh OWNERS LEGAL.md
```

## 六、服务提供者矩阵(`@service_provider` 注册表)

| service_type | 已注册 provider | 实现位置 |
|---|---|---|
| vector_service | **tbase**(含 WorkMemoryService)、**vectordb**、**vectordb_v2**、**oceanbase**、**turso** | `service/vector/*` |
| llm_service | openai(单一;`light_llm_service`/`multimodal_service` 复用同一 provider,不同实例) | `service/llm/openai_service.py` |
| embedding_service | tbase、deepfuse、openai、random(mock)、local(hf) | `service/emb/*` |
| reranker_service | openai、aq_memory | `service/reranker/*` |
| trace_service | turso、deepfuse(graph) | `service/trace/*` |
| stm_store_service / ltm_store_service | (TBase redis-mem 后端,WorkMemory 存储) | `service/vector/tbase.py:WorkMemoryService` + `MemWorkMemoryClient` |

`ServiceManager` 另管理:`request_build_status_store_service`、`project_storage_binding_service`、`lightmem_service`、`iot_sleep_detail_aggregate_service` 等业务侧服务。

## 七、存储与外部依赖的真实拓扑

- **STM(短期/工作记忆)**:TBase **redis-mem** 模块 —— Redis 兼容协议 + `MEM.*` 命令集(CREATE/ADD/GET/RANGEBYINDEX/MARKSUMM/TAKESUMM/ACKSUMM/ARCHIVESTM/DELMSG/DELBYTIME);协议文档即 `docs/mem-redis.md`;客户端封装 `common/mem_work_memory_client.py`(同步/异步)。**触发队列也在 MEM 服务端**,客户端只下发规则 —— "蓄水池"就是 STM 本身。
- **LTM/长期记忆**:向量库(默认 TBase 的 vector 能力;亦可 OceanBase/vectordb/vectordb_v2/Turso)+ 图库(GraphUniverse/Gustudio/TinyGraph/Neo4j,经 blueprint 模式编排 schema 与转换)。
- **mem_id(STM 分片键)**:`{instance_id}:{user_id}:{run_id}:{agent_id}`,由 `common/stm_mem_identity.py` 的 codec/AutoV2 群聊 profile 编码;群聊 run 物理分片固定 default_user_id。
- **RPC/中台**:`service/rpc/`(arec、custom)、`service/tr/iot`(健康 IoT 数据:指标注册表 `conf/iot/metric_registry_v1.yaml`、oneapi contracts、睡眠明细/聚合)、`layotto` 运行时。

## 八、工作记忆子系统(V1 与 V2 双轨)

- **数据模型**(`docs/work-mem.md` + `common/work_memory_types.py`):`PersonWorkRecord`(个人交互记录,含 git remote/branch/log 的 `AddInfo`,promotion_status=waiting/promoted/rejected)→ LLM 提炼 → `ProjectWorkMemory`(团队共享经验)。
- **V1 链路**(`memory_template='work_memory*'`):`work_memory_add.yaml` 等 5 个模板;后台 `extraction_worker` + `persistent_task_queue` 消费;STM 实时写入、阈值触发同步 drain(`summary_work_memory` 执行模式=sync)。
- **V2 链路**(`use_pipeline_v2=true`):context_package 条件异步 + `ExtractionWorkerV2` 轮询 MEM 服务端触发;`summary_work_memory` 执行模式=async(MARKSUMM 受理)。V1/V2 由**实例原始 service_config**冻结,请求级 pipeline 不可切换家族(跨家族替换会抛错)。
- **实例生命周期**:`WorkMemoryInstanceRegistry` 提供 `activation_lock`(实例级注册事务)与 `stm_write_transaction`(写事务内冻结 generation);Runtime 发布前必须 worker 就绪;`Memx._register_static_stm_runtime()` 延迟注册,失败不残留半初始化 entry。

## 九、可观测性 / 溯源 / 评测

- **可观测**:`common/tracer/` 全家桶(OTel tracer、span_registry 的 SpanName/MetricsKey、httpx+threading 自动埋点、LogExporter);`main.py` 每个入口包 span + metrics_reset/snapshot;`TraceCollector`/`MemoryTraceCollector` 收集请求与记忆变更轨迹;`service/trace` 落 turso/deepfuse(graph trace)。
- **溯源(provenance)**:每条记忆变更的 ledger + trace schema(`docs/contracts/provenance-trace-v1.schema.json`)+ 脱敏/投影;`tools/export_provenance_*` 导出 bundle。
- **评测**:`benchmark/` 框架很小(demo_adapter + locomo10 evaluator + llm_judge,数据 `data/locomo10.json`)。实际业务评测主要在:① `tools/gen_exp_params.py`+`profiles/` 的参数化实验;② `group_chat_biz/` 医疗群聊 bench(147 样本,AFU 群聊策略抽取→检索→eval JSONL 全流程脚本);③ `tests/` 场景级测试(`work_mem_scenario.py`、314 文件)。注意:**MemGallery 数据集不在库内**,仅以 prompt 名(`lightmem_memgallery_extraction`)出现——目录 `mem_gallery_data`(本仓库所在)即对应外部数据集。

## 十、勘误表(初版 ↔ 代码核实)

| # | 初版说法 | 代码核实结果 |
|---|---|---|
| 1 | "策略经 `StrategyRegistry` 中心化注册,支持版本管理与运行时路由" | ❌ StrategyRegistry 不存在(仅 ARCHITECTURE 蓝图)。实际:`@module` 装饰器 + `ExecutionEngine` 属性动态发现;服务按 `@service_provider(type, provider)` 注册;策略选择在 pipeline 配置层 |
| 2 | "底层 STM 用 Redis/TBase" | ⚠️ 精确化:STM = TBase 的 **redis-mem** 模块(Redis 兼容协议 + MEM.* 命令集),触发队列同样在 MEM 服务端(MEM.TAKESUMM),非独立 Redis List |
| 3 | "在 LoCoMo、MemGallery 等基准上跑评测" | ⚠️ 修正:benchmark 框架仅内置 demo/locomo10;MemGallery 数据不在库内(仅 prompt 命名);群聊评测在 group_chat_biz(147 条医疗 bench) |
| 4 | Add 流水"支持条件异步...(默认)入蓄水池" | ⚠️ 补充:机制正确,但当前 `default_add.yaml` 默认 `enable_conditional_async: false`(同步);设计文中"默认 true"是分支演进差异。Worker=ExtractionWorkerV2,归档语义为"全部写库成功才 ARCHIVESTM,否则 FAILED_RETRY 重试" |
| 5 | main.py "~3457 行" | 实际 3456 行(无关紧要,顺手修正) |
| 6 | —(遗漏) | 补充:本仓库是 oneapi 应用(f.yml:assistantiimed 医疗 + vmevalengine IoT);宿主 Memora 多进程部署(engine ProcessEnv 钩子);21 个 memory_template;V2 profiles 实验参数体系;`@service_provider` 矩阵;`tr/iot` 健康 IoT 中台对接 |

---

# 附录:多模态记忆优化方向切入门通俗版）

> 背景:研究方向为"多模态记忆优化"(多模态、或纯记忆方向均可)。以下用大白话把这个项目里可改进的点捋一遍,再挑四个最值得做的详细展开。
> 一句话现状:**图片相关的记忆功能,写入这条路只修了一半而且没通车(默认关闭),检索那条路压根没动工。**

## 一、这个项目里值得改的小点,全部列出来

**和多模态直接相关的(8 个)**

| 编号 | 一句话说明 | 在哪里 | 现状 |
|---|---|---|---|
| M1 | 搜索结果排序时,模型只能"看字",看不到图片本身 | `search/rerank/stages/scoring/llm.py` | 检索完全不多模态 |
| M2 | 用户提问时可以带图片,但系统直接忽略了 | `common/protocol.py:144` 的 `SearchData.media` | 字段存在,无人使用 |
| M3 | 给图片起名字(图注)时,不看聊天上下文,凭空描述 | `multimodal_enrichment_strategy.py:72` | 零上下文一次性生成 |
| M4 | 判断"这张图片是不是重复记忆",只靠图注文字像不像 | `ekko_multimodal:79` + `similar_recall.py` | 没有视觉层面的对比 |
| M5 | 图片记忆的"可信度"是拍脑袋写死的(0.8/1.0),一张图压成一条记忆 | `ekko_multimodal:96` | 硬编码,粒度单一 |
| M6 | 图片记忆的两个核心策略**写好了但没启用**——纯"暗代码" | `strategy_refine.yaml:178`、`memory_modeling.yaml:224` | 全部默认关闭,谁也没测过 |
| M7 | 图片理解功能和"价值判断"功能挂在了同一个钩子上,一开就互相顶掉 | `strategy_refine.yaml:178` | 位置冲突,需挪窝 |
| M8 | 协议说支持视频,代码里只要不是图片就直接跳过 | `multimodal_enrichment_strategy.py:47` | 视频是摆设 |

**和"记忆"相关但不是多模态的**
- 后台抽取工人每批固定只取 10 条消息,超过批量的行为没验证过;
- 新检索链路相比旧链路少了三样东西:短期记忆召回、业务场景分流、意图加分;
- 默认检索配置偏"通用",BM25/时间过滤/重排都关着,和旧行为对齐要手工补;
- 图片记忆的决策只有"加/不加",没有"更新/删除"——像从不打扫的仓库。

**顺手要处理的工程问题**:`conf/service/default.yaml:47` 有一个**明文写在配置里的 API key**,这部分代码若要对外,必须先删掉。

## 二、哪些点属于你的方向

按"多模态记忆优化"的口径,有四个地带是你的地盘:
1. **写入侧多模态**——怎么给图片起好名字、怎么建模成记忆(M3、M5);
2. **读取侧多模态**——搜的时候怎么用上图片(M1、M2,目前完全空白);
3. **记忆的生命周期**——重复了怎么办、可信度怎么用、怎么更新(M4 + 通用记忆问题);
4. **评测闭环**——先让一切可测量(M6,其他三个点都靠它)。

## 三、四个详细讲解

### ① 检索排序时"看一眼图":Cross-modal rerank

**现在是什么样**:搜索回来的候选要重新排序,其中一种方式是让大模型打分。打分时模型拿到的只有文字(图注),图片本体根本没参与——相当于请人给照片打分,但只递给他照片的文字说明。

**问题在哪**:图注是有损压缩。两张内容不同的图,图注写得差不多,模型分不清;一张内容和提问强相关的图,图注写得很平淡,就被排到了后面。写入时图片记忆明明带了原图链接,排序时却视而不见。

**怎么改**:打分消息里把候选的图片链接带上(消息格式项目中已有现成写法,在 `multimodal_enrichment_strategy.py:74-82` 直接照抄);更省钱的方案是把图片挂在"提问"那一侧,所有文档仍是文字,一次调用搞定,成本不变。

**值不值得做**:需要注意的点是——给每张图单独调视觉模型比一次性文字打分贵;可以设计成"粗排后排到前 N 名的图片才做视觉精排"——这个成本与效果的权衡本身就是论文曲线。

### ② 起图注时"看看聊天记录再开口":Context-aware caption

**现在是什么样**:图片缺描述时,系统会把图丢给视觉模型,让它"客观描述图片内容"。prompt 里没有任何变量(`variables: []`)——同一张白板照片,不管出现在"预算讨论"还是"团建复盘"里,得到的图注一模一样。

**问题在哪**:图注是图片记忆**唯一**被存进向量库的文字(`normalized_content/abstract/keywords` 三个字段全都直接塞图注)。而用户搜的时候问的是"我们上次讨论的预算方案吧"这类对话式的问题——"三个人站在白板前"对上"预算方案"是天堑。**写入侧改一个方法,检索侧全局受益**,是杠杆最高的点。

**怎么改**:给 prompt 加一个上下文变量,把这段对话的主题(管线里现成有话题检测的产出)一起喂给视觉模型,让它写出"白板上写着 Q3 预算分配"这种带语境的图注。改动就在 `_generate_caption` 一个方法内。

**怎么验证**:图注单独评(实体保留、别瞎编),检索端到端评(图相关问题召回率)。

### ③ 别让记忆库变成图片垃圾堆:判重、置信度、粒度

**现在是什么样(三个环节连起来看)**:
1. 每张图生成一条记忆,可信度拍脑袋定(用户自带描述 1.0,模型写得 0.8),类别统一填 "other";
2. 判重靠"新记忆的图注"去向量库里搜相似旧记忆;
3. 决策规则简单粗暴:相似度超过阈值就算重复、不存;否则存。全程只有"存/不存"两种操作。

**问题在哪**:判重完全由"图注文字的措辞"决定。同一块白板拍两次两次角度、两次措辞 → 相似度不够 → 存了两份(垃圾堆积);反过来两张不同的图,图注都写"两个人在户外" → 误判重复 → 真记忆被丢弃。另外"可信度"字段下游根本没人用;一张内容丰富的图(表格+多人+事件)被压扁成**一条**记忆,以后想更新局部都不行。项目的存储里图片有唯一 ID,但只在同一条消息内去重,跨消息、跨会话的图没有视觉指纹。

**怎么改**:在写路径的召回环节加一路"图片指纹召回"(图像哈希或视觉向量),文本相似度和视觉相似度加权判重——加一路召回的流程在模块注释里写得明明白白,照抄即可;再让判重阈值跟着可信度浮动。

**为什么这个点最"记忆"**:记忆系统的灵魂是增量、冲突、遗忘管理;当前图片记忆是"只进不出的文字替代品"。这个话题落在记忆系统研究,而不是多模态应用炒作区。

### ④ 先把灯点亮:多模态评测与 A/B 实验闭环

**现在是什么样**:两个多模态策略默认全关,翻遍所有编译后的运行配置,没有一个启用过——功能写完了、没上链、没测过,纯属"暗代码"。而实验基建三件套现成:profile 参数逐键覆盖、参数合法键生成脚本、评测框架(locomo10 + llm_judge),另有 147 条医疗群聊评测脚本可作为范式照抄。MemGallery 数据集就在本项目所在目录(有对应 prompt 为证)。

**问题在哪**:没有一个可跑的 baseline,前面三个点做出来的任何改进都无法横向比较,也就变不成结果。

**怎么改**:
1. 解决 ⑦ 的钩子冲突(把图片理解挪到独立节点);
2. 写一个 profile 覆盖,把两个策略的开关打开,编译出实验用的运行配置;
3. 从 MemGallery 造一批"图相关问题",用现成 llm_judge 打分,主指标 recall@k;
4. 实验组天然有梯度:不开图注(只用用户描述)→ 开图注 → 图注入上下文 → 排序加图——每一档都是一个参数差异键,各省一个 profile 文件。

## 四、这四点怎么串成一条线

**④ 先点亮灯**建立 baseline → **② 磨刀**(把图注写好)→ **① 检索时看图** → **③ 啃硬骨头**(记忆生命周期)。

①② 是两周边的工作量,③ 是研究级,④ 是地基。做的时候可以把每一个改进都做成一个 profile 文件,仓库的实验机制天生支持这种逐键 A/B。
