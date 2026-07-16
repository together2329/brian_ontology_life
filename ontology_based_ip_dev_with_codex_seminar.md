# Ontology Based IP DEV with Codex

작성일: 2026-07-08

목적: 기존 Codex 세미나 자료를 `Ontology Based IP DEV with Codex`라는 하나의 주제로 재정렬한다. Codex 기능 소개에 머물지 않고, HW/IP 개발에서 requirement, interface, decision, verification evidence, learning asset을 ontology로 연결하는 운영 모델을 설명한다.

---

## 세미나 주제 확정

**Main Title**

```text
Ontology Based IP DEV with Codex
```

**Korean Subtitle 후보**

```text
Codex로 IP 개발을 자동화하기 전에, 기준 정보와 evidence를 연결하는 방법
```

**Executive Subtitle 후보**

```text
From prompt-driven coding to ontology-guided IP development workflow
```

---

## 한 문장 메시지

> 이 세미나는 Codex가 RTL을 자동으로 작성한다는 이야기가 아니라, IP 개발에 필요한 requirement, interface, design decision, verification evidence를 ontology로 연결하고 Codex가 그 기준 안에서 설계/검증/리뷰 loop를 돌게 하는 방법을 설명한다.

---

## 왜 이 주제가 좋은가

### 기존 "Codex 전반"보다 좋은 점

| 관점 | Codex 전반 세미나 | Ontology Based IP DEV with Codex |
| --- | --- | --- |
| 메시지 | 기능이 많아 보일 수 있음 | HW/IP 업무 문제로 바로 연결됨 |
| 청중 | Codex 초보자 전체 | RTL/IP/검증 엔지니어 중심 |
| 차별성 | 일반 사용법과 겹칠 수 있음 | Brian의 SSOT/ontology/IP 경험이 드러남 |
| 설득력 | "좋은 도구" 설명 | "IP 개발 품질 체계" 설명 |
| 다음 액션 | Codex 써보기 | 작은 IP slice를 ontology/evidence로 모델링 |

### 핵심 포지셔닝

```text
Codex = 작업을 실행하는 agent workspace
Ontology = IP 지식과 판단 기준의 semantic source
Evidence = 완료 주장과 검증 결과를 연결하는 근거
Skill/Rule = 반복 시행착오를 다음 실행에 반영하는 자산
```

---

## 발표 구조: 30분 버전

### 1. Opening: 왜 IP DEV에는 단순 coding agent가 부족한가

화면 핵심:
- IP 개발은 코드 생성보다 기준 유지가 어렵다.
- Requirement, interface, protocol, PPA intent, verification evidence가 연결되어야 한다.
- Codex는 실행을 돕지만, 기준 정보가 없으면 빈칸을 임의로 채울 수 있다.

발표 메시지:
```text
AI가 RTL을 빨리 만들어주는 것보다 중요한 문제는,
그 RTL이 어떤 requirement와 decision을 기준으로 만들어졌는지 설명 가능한가이다.
```

### 2. Codex 기본: Thread, Context, Plan, Review

화면 핵심:
- Thread는 작업 단위와 evidence trail이다.
- Prompt는 `Goal / Context / Constraints / Done when` 형태의 작업 계약이다.
- Plan mode는 모호함과 risk를 먼저 나누는 장치다.
- Review는 사람이 봐야 할 decision point를 좁히는 과정이다.

발표 메시지:
```text
Codex를 잘 쓰는 출발점은 긴 prompt가 아니라,
작업 단위와 완료 기준을 명확히 잡는 것이다.
```

### 3. 시행착오: 의도만 주면 만들고, 다 묻게 하면 멈춘다

화면 핵심:
- 의도만 주면 agent가 hidden assumption을 만든다.
- 모호하면 모두 질문하게 하면 사람이 병목이 된다.
- 따라서 contract와 option을 나눠야 한다.

구분 예:
| Human locks | Agent options |
| --- | --- |
| interface structure | internal structure |
| protocol visible behavior | parameter default |
| PPA intent | generated variant |
| product behavior | naming/layout |

발표 메시지:
```text
사람이 모든 detail을 결정할 필요는 없지만,
제품 의미가 바뀌는 contract는 사람이 잠가야 한다.
```

### 4. Ontology: IP 개발 기준을 연결한다

화면 핵심:
```text
SoC
-> Subsystem
-> IPBlock
-> Interface
-> Requirement
-> Constraint
-> DesignDecision
-> ImplementationTask
-> VerificationCase
-> Evidence
-> Owner / ReviewState
```

발표 메시지:
```text
Ontology는 지식 그래프를 예쁘게 그리는 도구가 아니라,
Codex가 무엇을 기준으로 설계하고 검증해야 하는지 알려주는 구조다.
```

### 5. Verification-first 적용: 지금 당장 가능한 시작점

화면 핵심:
- 현재 실무 적용은 Spec/RTL 자동 구현보다 검증 쪽이 현실적이다.
- lint/compile/simulation/formal log triage
- evidence freshness, scope, claim boundary 확인
- handoff, test pass, closure를 분리

발표 메시지:
```text
첫 demo는 RTL 자동 수정이 아니라,
실패 log를 구조화하고 evidence 기반 next check를 정하는 workflow가 더 안전하다.
```

### 6. Closing: IP DEV loop

화면 핵심:
```text
Ontology / SSOT
-> Codex Thread
-> Plan / Implementation Candidate
-> Verification Evidence
-> Gate / Decision
-> Rule / Skill / Ontology Patch
```

마무리 메시지:
```text
Ontology Based IP DEV with Codex의 목표는
AI가 마음대로 IP를 만드는 것이 아니라,
사람이 정한 기준과 검증 evidence 안에서 IP 개발 loop를 더 빠르고 일관되게 돌리는 것이다.
```

---

## 발표 구조: 45-60분 버전

| 구간 | 주제 | 핵심 질문 |
| --- | --- | --- |
| 0-5분 | Why now | 왜 Codex를 단순 coding tool로 보면 부족한가 |
| 5-12분 | Codex operating basics | thread/context/plan/review를 어떻게 설명할까 |
| 12-20분 | Agent 시행착오 | 의도 전달, 질문 폭주, 검증 장치 문제 |
| 20-30분 | Ontology for IP DEV | IP 지식을 어떤 object와 edge로 모델링할까 |
| 30-40분 | Verification-first demo | 지금 당장 가능한 안전한 workflow는 무엇인가 |
| 40-50분 | SSOT to RTL path | 나중에 RTL candidate 생성으로 어떻게 확장할까 |
| 50-60분 | Asset program | rule/skill/wiki/ontology로 무엇을 남길까 |

---

## 핵심 슬라이드 제목 후보

1. Ontology Based IP DEV with Codex
2. AI RTL 생성보다 어려운 것은 기준을 지키는 구현이었다
3. Codex Thread는 작업 단위이자 evidence trail이다
4. Prompt는 명령이 아니라 작업 계약이다
5. 의도만 주면 agent가 빈칸을 채운다
6. 모호함을 모두 질문하면 사람이 병목이 된다
7. Contract는 잠그고, reversible detail은 option으로 둔다
8. IP Ontology: Requirement부터 Evidence까지 연결한다
9. Verification-first: 안전한 첫 적용 지점
10. Handoff, test pass, closure는 서로 다르다
11. SSOT -> RTL Candidate -> Evidence -> Decision
12. 반복 시행착오는 Rule, Skill, Ontology Patch로 남긴다
13. 2개월의 성공 기준은 사용량이 아니라 IP Knowledge asset이다

---

## Demo 후보

### Demo A. Verification-first log triage

가장 안전한 첫 demo.

```text
Input:
  failing log excerpt
  related file names
  expected command

Codex output:
  failure group
  first evidence
  suspected area
  safe next check
  human decision needed
  evidence table
```

### Demo B. Toy APB IP ontology slice

제품 IP를 노출하지 않는 구조 demo.

```text
IPBlock: toy_apb_timer
Interface: APB slave
Requirement: counter enable / compare interrupt / clear policy
Decision: interrupt clear priority
VerificationCase: smoke / clear / reset
Evidence: sim pass log
```

### Demo C. SSOT to RTL candidate

후속 세미나용.

```text
SSOT object
-> implementation packet
-> RTL skeleton candidate
-> ambiguity/open decision table
-> validation checklist
```

---

## 청중별 메시지

| 청중 | 가져가야 할 메시지 |
| --- | --- |
| RTL/Design engineer | Codex는 RTL을 바로 맡기는 도구가 아니라 requirement와 검증 기준 안에서 후보를 만들고 리뷰하는 도구다. |
| Verification engineer | 지금 가장 현실적인 시작점은 log triage, evidence 정리, missing check 탐색이다. |
| Tech lead | 성공 기준은 사용량이 아니라 반복 가능한 workflow package와 reviewable evidence다. |
| 임원/조직 관점 | 2개월 window는 Codex 사용 확산보다 SoC/IP Knowledge asset을 남기는 기간으로 봐야 한다. |

---

## 다음 작업

1. 기존 `codex_overall_seminar.html`의 제목과 첫 화면을 이 주제로 맞춘다.
2. 메인 발표용으로 12-15장 slide cut을 만든다.
3. demo는 우선 `Verification-first log triage`로 잡는다.
4. 후속 확장으로 `Toy APB IP ontology slice`를 준비한다.
5. 마지막 장은 `SSOT -> Codex -> Evidence -> Decision -> Learning` loop로 닫는다.
