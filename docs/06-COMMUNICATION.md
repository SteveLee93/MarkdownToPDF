# 6단계: 통신과 이벤트

rodi-x-svc는 MQTT와 IPC를 통해 다른 서비스들과 통신합니다. 이 문서에서는 통신 패턴과 모든 이벤트 토픽을 정리합니다.

---

## 통신 채널 개요

```
┌──────────────────────────────────────────────┐
│           MQTT Broker (port 1883)             │
│            rodi-broker-svc                    │
├──────────────────────────────────────────────┤
│                                              │
│  rodi-x-svc ◄──────────►  rodi-web-svc      │
│     (rodix/*)                (UI 클라이언트)   │
│                                              │
│  rodi-x-svc ◄──────────►  rodi-control-svc  │
│     (program/*, script)      (프로그램 제어)   │
│                                              │
│  rodi-x-svc ────────────►  system/events     │
│     (시스템 이벤트 수신)                       │
│                                              │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│              IPC (Node-IPC)                   │
│                                              │
│  rodi-x-svc ◄──────────►  rodi-broker-svc   │
│     (스크립트 메타데이터 동기화)                │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 3가지 MQTT 통신 패턴

### 1. Subscribe (수신 전용)

다른 서비스가 발행한 메시지를 받아서 처리합니다.

```
rodi-web-svc  ──publish──►  MQTT Topic  ──subscribe──►  rodi-x-svc
                                                          │
                                                    sdkCommand 실행
                                                          │
                                                    finishCb(결과)
                                                          │
                                               MQTT ack로 응답 반환
```

### 2. Publish (발행 전용)

rodi-x-svc에서 다른 서비스로 단방향 메시지를 보냅니다.

```
rodi-x-svc  ──publish──►  MQTT Topic  ──subscribe──►  rodi-web-svc
(알림, 상태변경)                                        (UI 업데이트)
```

### 3. Publish with Ack (요청-응답)

다른 서비스에 요청을 보내고 응답을 기다립니다.

```
rodi-x-svc  ──publish──►  MQTT Topic  ──subscribe──►  rodi-control-svc
                                                          │
                                                    요청 처리
                                                          │
rodi-x-svc  ◄──ack────────────────────────────────────────┘
```

---

## MQTT 토픽 전체 목록

### Subscribe 토픽 (수신)

> **설정 파일**: `config/framework.json` → `eventManager.sub_list`
> **구독 등록**: `modules/interface/sdkService.js`
> **핸들러 구현**: `modules/interface/sdkCommand.js`

#### 초기화 관련

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_initialize` | `rodix/initialize` | 2 | 플러그인 서비스 활성화 시작 |
| `robot_initialize_finish` | `rodix/initialize/finish` | 2 | 초기화 완료 알림 |

#### 플러그인 정보 조회

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_get_assemblies` | `rodix/get/assemblies` | 2 | 설치된 플러그인 목록 반환 |
| `rodix_get_install_path` | `rodix/get/install/path` | 2 | 플러그인 설치 경로 반환 |
| `rodix_get_extensions` | `rodix/get/extensions` | 2 | Extension 서비스 목록 반환 |
| `rodix_get_widgets` | `rodix/get/widgets` | 2 | Widget 서비스 목록 반환 |
| `rodix_get_daemons` | `rodix/get/daemons` | 2 | Daemon 서비스 목록 반환 |
| `rodix_get_program_services` | `rodix/get/program/services` | 2 | ProgramNode 서비스 목록 반환 |

#### 프로그램 관리

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_load_program` | `rodix/load/program` | 2 | 프로그램 파일에서 X 커맨드 로드 |
| `rodix_get_program_nodes` | `rodix/get/program/nodes` | 2 | 모든 프로그램 노드 데이터 반환 |
| `rodix_new_program_node` | `rodix/new/program/node` | 2 | 새 프로그램 노드 생성 |
| `rodix_delete_program_node` | `rodix/delete/program/node` | 2 | 프로그램 노드 삭제 |
| `rodix_sync_program_nodes` | `rodix/sync/program/nodes` | 2 | 프로그램 노드 변경 동기화 |
| `rodix_undo_redo` | `rodix/undo/redo` | 2 | Undo/Redo 스택 처리 |

#### 페이지(UI) 관리

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_open_page` | `rodix/open/page` | 1 | 플러그인 페이지 열기 |
| `rodix_close_page` | `rodix/close/page` | 1 | 플러그인 페이지 닫기 |
| `rodix_event_page` | `rodix/event/page` | 1 | 페이지 UI 이벤트 (click, change 등) |
| `rodix_page_info` | `rodix/page/info` | 1 | 페이지 정보 조회 |

#### 스크립트 생성

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_generate_script` | `rodix/generate/script` | 1 | 전체 스크립트 코드 생성 |
| `rodix_generate_script_program` | `rodix/generate/script/program` | 1 | 프로그램 스크립트만 생성 |
| `rodix_generate_script_extension` | `rodix/generate/script/extension` | 1 | Extension 스크립트만 생성 |

#### 시스템/기타

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_event_daemon` | `rodix/event/daemon` | 1 | 데몬 서비스 이벤트 |
| `system_events` | `system/events` | 1 | 시스템 레벨 이벤트 |
| `event_status_program` | `event/status/program` | 1 | 프로그램 상태 이벤트 |
| `robot_simulation_mode` | `robot/simulation/mode` | 2 | 시뮬레이션 모드 전환 |
| `rodix_user_info_change` | `rodix/user/info/change` | 1 | 로그인 사용자 정보 변경 |

---

### Publish 토픽 (발행)

> **설정 파일**: `config/framework.json` → `eventManager.pub_list`

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_update_page` | `rodix/update/page` | 2 | 페이지 UI 업데이트 알림 |
| `rodix_sync_script_variables` | `rodix/sync/script/variables` | 1 | 스크립트 변수 동기화 |
| `rodix_sync_script_functions` | `rodix/sync/script/functions` | 1 | 스크립트 함수 동기화 |
| `rodix_datamodel_changed` | `rodix/datamodel/changed` | 1 | 데이터 모델 변경 알림 |
| `rodix_variables_changed` | `rodix/variables/changed` | 1 | 변수 변경 알림 |
| `rodix_show_spinner` | `rodix/show/spinner` | 1 | 로딩 스피너 표시 |
| `rodix_show_notification` | `rodix/show/notification` | 1 | 알림 메시지 표시 |
| `program_comment` | `program/comment` | 1 | 프로그램 코멘트 |
| `event_close_collision` | `event/close/collision` | 1 | 충돌 이벤트 닫기 |
| `rodix_showhide_window` | `rodix/showhide/window` | 1 | 윈도우 표시/숨김 |

---

### Publish with Ack 토픽 (요청-응답)

> **설정 파일**: `config/framework.json` → `eventManager.pub_with_ack_list`

#### 프로그램 제어

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `program_list` | `program/list` | 2 | 프로그램 목록 요청 |
| `program_plan_by_rds` | `program/plan/by/rds` | 2 | RDS 기반 프로그램 계획 요청 |
| `program_play` | `program/play` | 2 | 프로그램 실행 |
| `program_pause` | `program/pause` | 2 | 프로그램 일시정지 |
| `program_resume` | `program/resume` | 2 | 프로그램 재개 |
| `program_stop` | `program/stop` | 2 | 프로그램 정지 |
| `program_set_repeat` | `program/set/repeat` | 2 | 반복 횟수 설정 |
| `program_clear` | `program/clear` | 2 | 프로그램 초기화 |
| `program_delete` | `program/delete` | 2 | 프로그램 삭제 |
| `program_script_compile` | `program/script/compile` | 2 | 스크립트 컴파일 |
| `program_script_command` | `program/script/command` | 2 | 스크립트 명령 실행 |

#### 로봇 제어

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `robot_set_operation` | `set/operation` | 2 | 작동 모드 설정 |
| `robot_direct_teaching_start` | `directTeaching/start` | 2 | 직접 교시 시작 |
| `robot_direct_teaching_stop` | `directTeaching/stop` | 2 | 직접 교시 종료 |
| `robot_set_velocity` | `set/velocity` | 2 | 속도 설정 |
| `robot_move_stop` | `move/stop` | 2 | 이동 정지 |
| `robot_jog_start` | `jog/start` | 2 | 조그(카테시안) 시작 |
| `robot_jog_rotation_start` | `jog/rotation/start` | 2 | 조그(회전) 시작 |
| `robot_jog_joint_start` | `jogJoint/start` | 2 | 조그(조인트) 시작 |
| `robot_jog_joint_stop` | `jogJoint/stop` | 2 | 조그(조인트) 정지 |
| `robot_move_joint_home` | `move/joint/home` | 2 | 홈 위치로 이동 |
| `robot_move_joint_here` | `move/joint/here` | 2 | 현재 조인트 위치로 이동 |
| `robot_move_flange_here` | `move/flange/here` | 2 | 현재 플랜지 위치로 이동 |
| `robot_event_collision_clear` | `event/collision/clear` | 2 | 충돌 해제 |
| `robot_event_collision_clear_resume` | `event/collision/clear/resume` | 2 | 충돌 해제 후 재개 |

#### UI 다이얼로그

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_show_msg` | `rodix/show/msg` | 2 | 메시지 다이얼로그 표시 |
| `rodix_show_browser` | `rodix/show/browser` | 2 | 브라우저 다이얼로그 표시 |
| `rodix_show_dialog` | `rodix/show/dialog` | 2 | 범용 다이얼로그 표시 |
| `rodix_show_robot_position_panel` | `rodix/show/robot/position/panel` | 2 | 로봇 위치 패널 표시 |

#### 프로그램 노드 반환

| 이벤트명 | MQTT 토픽 | QoS | 설명 |
|---------|----------|-----|------|
| `rodix_return_get_program_node` | `rodix/return/get/program/node` | 2 | 프로그램 노드 데이터 반환 |
| `rodix_return_update_program_node` | `rodix/return/update/program/node` | 2 | 업데이트된 노드 데이터 반환 |
| `rodix_login_info` | `rodix/login/info` | 2 | 로그인 정보 |

---

## 내부 이벤트 (EventAggregator)

MQTT가 아닌 **서비스 내부** 모듈 간 통신용 이벤트:

| 이벤트명 | 발행 위치 | 설명 |
|---------|----------|------|
| `system.start` | `index.js` | 시스템 시작 완료 |
| `system.exit` | `index.js` | 시스템 종료 시작 |
| `assembly.load` | `applicationContext` | 어셈블리 로딩 완료 |
| `assembly.datamodel.save` | `applicationContext` | 데이터 모델 저장 요청 |
| `assembly.datamodel.changed` | `applicationContext` | 데이터 모델 변경 |
| `script.variables.changed` | `applicationContext` | 스크립트 변수 변경 |
| `script.function.changed` | `applicationContext` | 스크립트 함수 변경 |
| `user.info.change` | `sdkCommand` | 사용자 정보 변경 |

---

## QoS 레벨 가이드

| QoS | 의미 | 사용 대상 |
|-----|------|----------|
| **1** | At least once | 페이지 이벤트, 알림, 상태 변경 등 (손실 허용 가능) |
| **2** | Exactly once | 프로그램 제어, 로봇 동작, 초기화 등 (정확히 1회 실행 보장 필요) |

> 로봇 제어 관련 토픽은 모두 QoS 2입니다. 안전에 직결되는 동작이므로 메시지 중복/누락이 발생하면 안 됩니다.

---

## 토폴로지 관리

**Heartbeat 매커니즘**:
- 토픽: `heartbeat`
- 주기: 1000ms (1초)
- 목적: 서비스 생존 확인
- 타임아웃: 5000ms (5초 무응답 시 disconnected 판단)

```
rodi-x-svc ──heartbeat──► MQTT Broker ──► 다른 서비스들
            매 1초                        (토폴로지 모니터링)
```

---

## 이벤트 추가 방법 요약

새 이벤트를 추가할 때 수정해야 하는 파일:

```
1. config/framework.json
   └─ sub_list 또는 pub_list에 토픽 정의 추가

2. modules/interface/sdkCommand.js
   └─ commands.새_이벤트명 = function(data, finishCb) { ... }

3. modules/interface/sdkService.js
   └─ self.$eventManager.subscribe('새_이벤트명', subscribeEvent);
```

---

## 다음 단계

통신 패턴을 이해했으면, [7단계: 개발/유지보수 가이드](./07-DEVELOPMENT-GUIDE.md)에서 실제 코드를 수정할 때의 주의사항과 팁을 확인합니다.
