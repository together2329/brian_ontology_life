# SSOT -> RTL Agent Workflow Trial Lessons: Presentation 5-Slide Cut

작성일: 2026-07-07

목적: 기존 세미나 MD 자료를 바탕으로 `SSOT`, `RTL 구현`, `시행착오`, `gate/evidence`, `학습 자산화`를 발표용 5장 흐름으로 정리한다. 단정적인 성공 사례가 아니라, 로컬 실험에서 관찰된 시행착오를 통해 어떤 운영 방향을 검토하게 됐는지 설명한다.

권장 발표 시간: 8-12분

전체 흐름:

```text
1. AI RTL 생성보다 어려웠던 것은 기준을 지키는 구현이었다.
2. 그래서 SSOT가 필요해졌다.
3. 하지만 SSOT가 있어도 RTL 구현 중 결정은 계속 나온다.
4. 구현 handoff, test pass, closure는 구분해야 했다.
5. 결론적으로 SSOT -> RTL -> Evidence -> Decision -> Learning loop가 필요해 보였다.
```

---

## Slide 1. 문제 정의: AI RTL 생성보다 어려운 것은 "기준을 지키는 구현"이었다

### 화면 핵심
- 처음 관심: AI가 RTL을 얼마나 빨리 만들어주는가
- 실제로 더 크게 보인 문제:
  - 어떤 requirement를 기준으로 구현했는가
  - interface / protocol / PPA intent가 보존됐는가
  - test pass가 정말 의도 충족을 의미하는가
  - 같은 실수와 질문이 다음 실행에서 반복되지 않는가
- 중심축: `SSOT -> RTL 구현 -> Evidence -> Decision -> Learning`

### 발표 대본
처음에는 저도 자연스럽게 "AI가 RTL을 얼마나 빨리 만들어줄 수 있나"에 관심이 갔습니다. 그런데 직접 workflow를 만들어보니, 더 큰 문제는 생성 속도보다 기준을 지키는 구현이었습니다.

예를 들어 "APB register block을 만들어줘"라고 하면 결과는 나옵니다. 하지만 그 다음에 바로 질문이 생깁니다. APB write side effect는 write 시점에 발생하는가, readback 때 확인되는가. reset/default 값은 spec에 있었는가, agent가 추정했는가. bvalid나 handshake timing은 어떤 contract를 따른 것인가. counter clear priority와 status read side effect는 무엇이 우선인가.

이런 문제는 RTL line 하나하나의 문제가 아니라, 구현의 기준 정보가 무엇이었는가의 문제에 가깝습니다. 그래서 세미나의 중심을 "AI RTL generator"가 아니라, SSOT를 기준으로 RTL 구현을 통제하고 evidence와 decision을 남기는 workflow로 잡는 편이 좋아 보였습니다.

### 시각화 제안
```text
Before: Prompt -> RTL

After:
SSOT -> RTL Implementation -> Evidence -> Decision -> Learning
```

### 전환 멘트
그래서 첫 번째 시행착오는 "의도만 전달했을 때 agent가 빈칸을 어떻게 채우는가"였습니다.

---

## Slide 2. 시행착오 1: 의도만 주면 agent가 빈칸을 채운다

### 화면 핵심
| 시도 | 관찰된 현상 | 왜 문제가 되는가 |
| --- | --- | --- |
| 자연어 의도 전달 | Agent가 빠르게 RTL 후보 생성 | 모호한 부분을 임의 해석할 수 있음 |
| RTL부터 구현 | hidden assumption이 뒤늦게 드러남 | review 시점에 기준이 흔들림 |
| 오류 발생 후 수정 | fix가 반복됨 | 원인이 spec/contract인지 구현인지 흐려짐 |

### 발표 대본
처음에는 의도를 전달하면 agent가 알아서 잘 채워줄 것이라고 기대했습니다. 실제로 결과는 빠르게 나옵니다. 문제는 그 결과가 그럴듯해 보이지만, 비어 있던 부분을 agent가 자기 방식으로 채웠을 수 있다는 점입니다.

예를 들어 SSOT에 아래 내용이 분리되어 있지 않으면, agent는 구현 중에 임의 선택을 할 수 있습니다.

```text
Requirement:
- APB CSR register를 통해 config/status를 제어한다.

구현 전에 더 명확해야 할 수 있는 부분:
- write side effect 우선순위
- read-clear 여부
- illegal/protected access 처리
- reset/default value
- CDC-visible status의 안정성 조건
- timeout / mismatch / error case의 expected behavior
```

이런 부분이 명확하지 않은 상태에서 RTL부터 나오면, 나중에 "왜 이렇게 구현됐는가"를 설명하기 어려워집니다. 이때 SSOT는 단순히 spec 문서를 예쁘게 정리하는 것이 아니라, agent가 마음대로 해석하기 쉬운 빈칸을 줄이는 기준 정보 역할을 합니다.

### 시각화 제안
```text
Natural intent
  -> hidden assumptions
  -> RTL choices
  -> review confusion

Structured SSOT
  -> requirement / assumption / interface / PPA intent / open decision
  -> controlled RTL projection
```

### 전환 멘트
그 다음에는 "그럼 모호한 부분을 모두 질문하게 하면 되지 않을까"라는 방향을 시도하게 됩니다. 그런데 여기서 두 번째 문제가 생겼습니다.

---

## Slide 3. 시행착오 2: 모호함을 전부 질문으로 올리면 사람이 병목이 된다

### 화면 핵심
- 첫 보정: "모호하면 물어봐"
- 관찰: 질문이 너무 많아질 수 있음
- 보인 방향: 모든 질문을 올리는 대신 decision type을 나눈다

```text
Human locks:
PPA intent / interface / protocol / product behavior

Agent can keep as options:
internal choice / generated option / parameter default
```

### 발표 대본
의도만 전달했을 때 agent가 마음대로 채우는 문제가 있었기 때문에, 다음에는 모호한 부분을 묻게 하는 방식이 자연스럽게 떠오릅니다. 하지만 RTL 구현 중에 물을 수 있는 질문은 생각보다 많습니다.

예를 들면 이런 질문들이 계속 나올 수 있습니다.

```text
- 이 register field는 read-only인가 write-one-clear인가?
- error bit는 clear 우선인가 set 우선인가?
- FIFO empty/full status는 어느 clock 기준인가?
- APB read latency는 0-cycle인가 1-cycle인가?
- reset은 sync인가 async인가?
- counter width는 고정인가 parameter인가?
- timeout value는 spec fixed인가 generated default인가?
```

이 질문을 모두 사람에게 올리면 workflow가 멈춥니다. 그래서 질문을 줄이기 위해서는 "무엇을 사람에게 물어야 하는가"를 정해야 했습니다.

제가 보기에는 PPA intent, external interface structure, protocol, product-defining behavior처럼 바뀌면 제품 의미가 달라지는 것은 사람이 먼저 잡는 편이 좋습니다. 반면 reversible internal choice, local implementation detail, generated option, parameter default 같은 것은 매번 질문으로 올리기보다 option으로 열어둘 수 있습니다.

예를 들어 interface 구조와 PPA intent가 맞다면, 내부 counter width나 pipeline boundary 후보는 parameterized option으로 두고 evidence로 비교해볼 수 있습니다. 반대로 APB-visible behavior나 protocol contract는 사람이 확인해야 합니다.

### 시각화 제안
2-column table:

| Ask human | Keep as option |
| --- | --- |
| PPA intent/spec | internal structure |
| interface structure | parameter default |
| protocol behavior | naming/layout |
| product behavior | generated variant |

### 전환 멘트
그런데 contract와 option을 잘 나눠도, RTL이 만들어진 뒤에 또 다른 문제가 남습니다. "이게 정말 의도대로 구현됐는가"입니다.

---

## Slide 4. 시행착오 3: RTL handoff, test pass, closure는 서로 다르다

### 화면 핵심
- `RTL_HANDOFF_PASS`: RTL 산출물이 넘겨질 수 있다는 의미
- `Validation evidence`: 특정 contract를 현재 RTL delta가 만족한다는 근거
- `Gate / closure`: evidence가 fresh하고 scope가 맞으며 completion claim이 가능한지 보는 판단
- 이 셋을 섞으면 과도한 완료 주장이 생길 수 있음

### 발표 대본
세 번째 시행착오는 "RTL이 나왔고 test가 통과했으니 끝인가"였습니다. 로컬 MCTP/IP loop에서 특히 이 구분이 중요하게 보였습니다.

한 상황에서는 RTL handoff receipt가 있었습니다. 그런데 관련 closure evidence는 handoff 이전 timestamp였습니다. handoff 이후의 RTL delta에 대해 fresh validation/gate record가 없는 상태였습니다. 이 경우 `RTL_HANDOFF_PASS`는 구현 산출물이 넘겨질 수 있다는 의미로 볼 수 있지만, closure/signoff-ready라고 말하려면 새 evidence가 필요합니다.

또 다른 상황에서는 evidence lifecycle 문제가 있었습니다. formal run이 의도치 않게 먼저 실행되어 output이 바뀌었고, dispatch/receipt가 생기기 전에 evidence가 생겼습니다. 이후 app run과 CLI fallback이 중복 실행되어 duplicate artifact도 생겼습니다.

여기서 중요한 점은 pass log 자체가 쓸모없다는 것이 아닙니다. 다만 어떤 evidence를 canonical로 볼지 정리하지 않으면 proof strength를 과대평가할 수 있습니다. duplicate evidence는 additive proof가 아니라 audit trail로 분류해야 할 수 있습니다.

그래서 gate는 단순 pass/fail이 아니라 다음을 함께 봐야 했습니다.

- evidence freshness
- evidence scope
- dispatch/receipt ownership
- out-of-scope artifact 여부
- `may_claim_complete`
- bounded development gate인지, release/signoff claim인지

### 시각화 제안
```text
RTL handoff
  != validation evidence
  != closure / signoff

Pass log
  -> check freshness
  -> check scope
  -> check canonical evidence
  -> check claim boundary
```

### 전환 멘트
결국 RTL 구현 workflow는 생성과 검증을 한 번 통과하는 문제가 아니라, 기준 정보와 evidence, decision이 계속 돌아가는 loop로 보는 편이 좋아 보였습니다.

---

## Slide 5. 운영 방향: SSOT를 RTL 구현의 입력이 아니라 loop의 기준으로 둔다

### 화면 핵심
```text
SSOT
  Requirement
  Assumption
  Interface
  PPA intent
  Parameter
  Open decision

-> RTL Implementation
-> Evidence
-> Validation
-> Decision
-> Rule / Skill / Wiki / Ontology
```

### 발표 대본
정리하면, SSOT는 한 번 만들고 끝나는 입력 문서가 아니라 RTL 구현과 검증 결과가 다시 돌아오는 기준점으로 보는 편이 좋아 보였습니다.

첫째, SSOT에서 contract와 option을 분리합니다. Interface, protocol, PPA intent, product behavior는 contract에 가깝습니다. Internal structure, parameter default, reversible detail은 option으로 둘 수 있습니다.

둘째, RTL 구현은 SSOT의 projection으로 봅니다. Agent가 original prose를 매번 재해석하지 않게 하고, generated packet이나 implementation packet처럼 구현용 context를 주는 방식입니다.

셋째, evidence는 "통과 로그"가 아니라 claim과 연결합니다. 어떤 requirement를 검증했는지, 어떤 RTL delta 이후 evidence인지, stale/duplicate/out-of-scope 여부는 없는지 봅니다.

넷째, gate는 완료 선언이 아니라 claim boundary를 정합니다. Bounded development gate인지, closure/signoff claim이 가능한지, `may_claim_complete`가 true인지 구분합니다.

다섯째, 반복된 시행착오는 자산으로 내립니다. 같은 RTL 해석 실수는 SSOT rule로, 같은 질문은 reviewer guide나 FAQ로, 같은 검증 누락은 validation checklist로, 같은 evidence 혼선은 gate/evidence policy로 남길 수 있습니다.

### 재사용 자산화 예
| 반복되는 것 | 남길 자산 |
| --- | --- |
| 같은 RTL 해석 실수 | SSOT rule / do-not-do checklist |
| 같은 질문 | reviewer guide / FAQ |
| 같은 검증 누락 | validation checklist |
| 같은 evidence 혼선 | gate/evidence policy |
| 같은 구현 절차 | skill / workflow recipe |

### 최종 메시지
> 세미나의 핵심은 "AI가 RTL을 자동 생성한다"가 아니라, SSOT를 기준으로 RTL 구현을 통제하고 evidence와 decision을 남겨 다음 구현 품질을 높이는 loop로 설명하는 편이 좋아 보인다.

### 마무리 멘트
이 관점으로 보면 AI agent 도입의 성공 기준도 "RTL을 몇 줄 만들었는가"가 아니라, "기준 정보가 남았는가, 구현 claim이 evidence와 연결됐는가, 다음 실행에서 같은 실수를 줄일 수 있는가"로 바뀝니다.
