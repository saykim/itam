# .agent/PLANS.md — ExecPlan(실행계획서) 규칙

이 문서는 “몇 시간 걸리는 작업”을 Codex가 끝까지 수행하기 위해 반드시 따라야 하는 표준입니다.

원칙: ExecPlan은 ‘처음 보는 사람’이 이 파일 1개만 읽고도 작업을 끝낼 수 있을 정도로
자급자족(SELF-CONTAINED) 해야 합니다.

---

## 1) ExecPlan이 꼭 필요한 경우(하나라도 해당되면 작성)

- 예상 소요가 2시간 이상
- 여러 파일/모듈/서비스를 건드림
- 요구사항이 불명확하거나 리스크가 큼
- 보안/권한/DB 마이그레이션/배포/비용에 영향
- 새 의존성 추가, 큰 리팩토링, 아키텍처 변경

---

## 2) ExecPlan 파일 위치/이름

- 위치: `.agent/execplans/`
- 파일명: `EP-YYYYMMDD-<짧은-주제>.md`
- 예: `EP-20260218-it-asset-import.md`

---

## 3) ExecPlan 템플릿(반드시 이 구조를 지킬 것)

> 새 작업을 시작할 때는 `.agent/execplans/EP_TEMPLATE.md`를 복사해서 만드세요.

## EP-YYYYMMDD-<slug>: <제목>

- Owner: PM / Dev
- Status: Draft | In-Progress | Blocked | Done
- Last updated: YYYY-MM-DD
- Related IDs: US-###, FR-###, NFR-###, UI-###, TC-###, ADR-### (가능한 한 연결)

### A. 목적(사용자 관점)

- 이 작업이 끝나면 사용자가 “무엇을 할 수 있게 되는지” 2~5문장.

### B. 완료 정의(Definition of Done)

- [ ] 사용자 확인 방법(어떻게 보면 ‘되는지’ 확인 가능한지)
- [ ] 테스트/린트 실행 및 결과(커맨드 포함)
- [ ] QA 리포트(`50_quality/TEST_REPORT.md`) 작성
- [ ] 롤백(되돌리기) 방법 문서화
- [ ] Risk 검토 + PM 최종결정 기록(ADR 포함 가능)

### C. 범위(Scope)

In scope
- …

Out of scope
- …

### D. 가정/제약(Assumptions/Constraints)

| ID | 가정/제약 | 왜 중요? | 확인 방법 | 확인됨 |
|---|---|---|---|---|
| ASM-001 | | | | ☐ |

### E. 초보자용 repo 안내(처음 보는 사람 기준)

- 핵심 폴더/파일: …
- 로컬 실행 방법: …
- 테스트 방법: …

### F. 마일스톤(순서대로 실행)

> 각 마일스톤은 “눈으로 확인 가능한 검증”으로 끝나야 합니다.

#### Milestone 1 — 조사/기준점 만들기

- 목표:
- 할 일:
  1) …
- 산출물(파일):
- 검증(기대 결과):

#### Milestone 2 — 구현(작게, 여러 번)

- 목표:
- 할 일:
- 산출물:
- 검증:

#### Milestone 3 — QA/엣지케이스/하드닝

- 목표:
- 할 일:
- 산출물:
- 검증:

#### Milestone 4 — 릴리즈 준비(필요 시)

- 목표:
- 할 일:
- 산출물:
  - `99_delivery/RELEASE.md`
  - `99_delivery/DEMO_SCRIPT.md`
- 검증:

### G. 리스크 & 완화책(꼭 작성)

| Risk | 영향 | 가능성 | 완화책 | 검증 방법 |
|---|---:|---:|---|---|
|  | H/M/L | H/M/L |  |  |

### H. 롤아웃/롤백

- 롤아웃: …
- 롤백: …
- (DB 변경이 있으면) 되돌리는 절차: …

---

## 4) 실행 중 “살아있는 섹션”(작업하면서 계속 업데이트)

ExecPlan 하단에 아래 섹션을 두고, 진행할 때마다 업데이트합니다.

### Progress

- [ ] 완료한 일
- [ ] 남은 일

### Surprises & Discoveries

- 예상치 못한 사실/문제/추가 요구사항

### Decision Log

- 언제, 무엇을, 왜 결정했는지 (ADR로 분리해도 됨)

### Outcomes & Retrospective

- 결과 요약
- 다음에 개선할 점

---

## 5) 가장 중요한 규칙(반드시 지킬 것)

- “계획만 쓰고 끝” 금지: 실행하면서 Progress/Decision을 갱신합니다.
- 큰 변경은 Milestone을 더 쪼개서 작은 PR/커밋으로 진행합니다.
- 모르겠으면 질문은 최대 3개만 하고, 나머지는 가정으로 진행하되 문서에 남깁니다.
