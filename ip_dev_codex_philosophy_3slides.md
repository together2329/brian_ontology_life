# ip_dev/.codex Philosophy: 2-3 Slide Cut

작성일: 2026-07-08

목적: `Ontology Based IP DEV with Codex` 세미나에 넣을 수 있도록 `/Users/brian/Desktop/Project/ip_dev/.codex`의 철학을 2-3장 발표용으로 압축한다.

기반 파일:
- `/Users/brian/Desktop/Project/ip_dev/README.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/AGENTS.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/principles.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/ip-dev-agent.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/oag-mode-directive.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/decision-autonomy-policy.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/authoring-packet-policy.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/rtl-implementation.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/traceability-policy.md`
- `/Users/brian/Desktop/Project/ip_dev/.codex/oag/wavefront-policy.md`

---

## Slide 1. 철학의 중심: RTL이 truth가 아니다

### 화면 핵심

```text
User / Spec
-> Requirement
-> Obligation
-> Contract
-> Evidence
-> Validation
-> Decision
```

- `ip_dev/.codex`의 핵심은 Codex 설정 모음이 아니라 **IP 개발 운영체계**다.
- RTL은 truth가 아니라 **locked contract의 구현물**이다.
- TB는 RTL을 따라가는 보조물이 아니라 **truth를 독립적으로 관찰하는 장치**다.
- Test pass는 closure가 아니다. 완료 주장은 ROCEV trace와 decision receipt가 있어야 한다.

### 발표 멘트

`ip_dev/.codex`의 철학을 한 문장으로 말하면, "RTL이 source of truth가 아니다"입니다. OAG에서 truth는 requirement, obligation, contract, approved ontology, recorded decision history에 있습니다.

Codex나 LLM이 RTL을 만들 수는 있습니다. 하지만 생성된 RTL이 곧 설계 의도가 되면 안 됩니다. RTL agent는 locked contract를 구현하고, TB는 같은 contract에서 expected behavior를 독립적으로 예측해야 합니다.

그래서 green test만으로 끝났다고 말하지 않습니다. Requirement에서 obligation, contract, evidence, validation, decision으로 이어지는 ROCEV chain이 닫혀야 completion claim을 할 수 있습니다.

### 한 줄 메시지

> OAG는 "AI가 RTL을 만들게 하는 시스템"이 아니라, "AI가 설계 truth를 바꾸지 못하게 하면서 구현과 검증을 진행하는 시스템"이다.

---

## Slide 2. Agent에게 자유를 주되, 제품 의미는 잠근다

### 화면 핵심

| Agent가 선택 가능 | Agent가 바꾸면 안 됨 |
| --- | --- |
| internal structure | port meaning |
| signal naming | reset value / polarity |
| local implementation style | address map |
| parameterized default | protocol timing |
| measured internal tradeoff | product-visible behavior |

### 핵심 원칙

- LLM에게 engineering judgment는 허용한다.
- 그러나 behavior, timing, reset, address map, priority, protocol semantics는 invent하면 안 된다.
- 모호하면 바로 구현하지 않고 blocker로 남긴다.
- 제품 의미가 바뀌는 `external_contract` / `product_defining` decision은 human-only다.
- `reversible_internal`, `parameterizable`, `measured_tradeoff`만 제한적으로 agent가 처리할 수 있다.

### 발표 멘트

OAG는 agent를 과도하게 묶어두는 시스템은 아닙니다. 오히려 agent가 잘할 수 있는 영역에는 자유를 줍니다. 내부 구조, naming, generate option, parameterized default, bounded tradeoff는 agent가 후보를 만들거나 evidence로 비교할 수 있습니다.

하지만 제품 의미가 바뀌는 것은 다릅니다. port 의미, APB timing, reset behavior, address map, IRQ priority, CDC/RDC mitigation 같은 것은 agent가 임의로 정하면 안 됩니다. 이런 decision은 human product authority 또는 scope lock을 통해 결정되어야 합니다.

이 철학은 "질문을 안 하게 하자"가 아니라, "무엇을 물어야 하는지 구분하자"에 가깝습니다. 모든 detail을 질문으로 올리면 workflow가 멈추고, 모든 detail을 agent가 정하면 spec drift가 생깁니다.

### 한 줄 메시지

> OAG의 자율성은 무제한 자동화가 아니라, 제품 contract를 잠근 상태에서 reversible/internal choice를 agent가 다루게 하는 방식이다.

---

## Slide 3. 운영 장치: Packet, Wavefront, Gate가 claim boundary를 만든다

### 화면 핵심

```text
Ontology Truth
-> Compile / Authoring Packet
-> Dispatch / Wavefront
-> Subagent Receipt
-> Evidence Validation
-> Gate Decision
```

### 핵심 원칙

- Generated authoring packet은 hand-authored truth가 아니라 read-only worker input이다.
- RTL/TB worker는 original prose를 재해석하지 않고 같은 contract graph에서 나온 packet을 소비한다.
- Wavefront는 parallel execution layer일 뿐, requirement나 locked truth를 만들지 않는다.
- Write-capable subagent는 dispatch scope, allowed paths, receipt로 경계를 가진다.
- Worker는 `HANDOFF_PASS`를 말할 수 있지만 final closure를 claim하면 안 된다.
- Closure는 fresh evidence, traceability, validation, gate decision이 있을 때만 가능하다.

### 발표 멘트

OAG는 철학만 있는 문서가 아니라 실제 운영 장치를 갖고 있습니다. Ontology가 truth를 갖고, compile이 RTL/TB authoring packet을 만들고, subagent는 packet과 dispatch scope 안에서만 일합니다.

Parallel work도 마찬가지입니다. Wavefront는 "여러 agent를 많이 띄우자"가 아니라 dependency, ownership, evidence boundary가 만족된 task만 여는 장치입니다. Read-only triage는 넓게 fan out할 수 있지만, write task는 allowed path가 겹치면 안 됩니다.

가장 중요한 점은 claim boundary입니다. RTL worker가 `RTL_HANDOFF_PASS`를 낼 수는 있지만, 그것은 closure가 아닙니다. Evidence validator와 gate reviewer가 fresh evidence, trace graph, checked artifact hash를 확인한 뒤에야 completion decision으로 갈 수 있습니다.

### 한 줄 메시지

> OAG는 agent 실행을 빠르게 만들지만, 완료 주장은 evidence와 gate가 허용할 때만 가능하게 만든다.

---

## 2장으로 줄일 때

### Option A. Slide 1 + 2를 합치기

**Slide 1. RTL은 truth가 아니고, agent는 contract 안에서만 자유롭다**

- ROCEV chain 소개
- RTL/TB/Validator 역할 분리
- agent freedom vs forbidden freedom 표
- product-defining decision은 human-only

**Slide 2. Packet/Wavefront/Gate로 구현과 완료 주장을 분리한다**

- Ontology -> Packet -> Dispatch -> Receipt -> Evidence -> Gate
- worker handoff와 closure의 차이
- test pass != completion
- 반복 시행착오는 rules/skills/ontology patch로 환류

### Option B. 더 임원 보고용 2장

**Slide 1. 핵심 철학**

> Codex로 IP를 개발하되, 설계 truth는 RTL이 아니라 ontology/contract/evidence chain에 둔다.

**Slide 2. 운영 방식**

> Agent는 bounded worker로 쓰고, 완료 주장은 traceable evidence와 gate decision으로만 허용한다.

---

## 세미나 연결 문장

`Ontology Based IP DEV with Codex`에서 `ip_dev/.codex`는 단순한 Codex 설정 예시가 아니라, ontology-first IP 개발을 위한 reference operating model로 소개할 수 있다. 핵심은 agent를 더 많이 쓰는 것이 아니라, agent가 product intent를 바꾸지 못하게 하면서 구현, 검증, evidence, closure를 분리하는 것이다.
