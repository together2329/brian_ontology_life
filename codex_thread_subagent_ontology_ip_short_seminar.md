# Codex Thread/Subagent + Ontology-Based IP Design: Short Seminar Draft

작성일: 2026-07-08

목적: `Codex 기본 개념(thread, context, subagent)`을 짧게 설명한 뒤, 이를 `ontology 기반 IP 설계/검증 workflow`로 연결하는 간략 세미나안이다. 실제 product IP를 직접 공개하기보다 toy/generic IP 예시로 설명한다.

권장 발표 시간: 12-18분

톤:
- Codex가 RTL을 자동으로 완성한다는 식으로 말하지 않는다.
- 현재 실무 적용은 검증, 리뷰, evidence 정리, 지식화부터 시작하는 편이 현실적이라고 설명한다.
- Spec/RTL 구현 agent는 가능성이 있지만, interface/PPA/protocol/ownership/evidence 문제가 있어 단계적으로 접근한다고 설명한다.

---

## 전체 메시지

```text
Codex는 "한 번 물어보는 코드 생성기"보다
"thread 안에서 context, 변경, 검증, evidence를 같이 관리하는 작업 agent"에 가깝다.

Hardware IP에서는 이 thread를 잘 쓰는 것만으로는 부족하고,
IP/Interface/Requirement/Decision/Evidence를 연결하는 ontology가 있어야
agent가 같은 기준으로 설계, 리뷰, 검증, 학습을 반복할 수 있다.
```

---

## Slide 1. 왜 Codex 기본 개념부터 설명해야 하나

### 화면 핵심
- AI agent 도입의 첫 오해: "프롬프트를 잘 쓰면 RTL을 만들어준다"
- 실제로 중요한 것:
  - 어떤 context를 줬는가
  - 어떤 thread에서 작업을 이어갔는가
  - 어떤 검증 evidence로 완료를 주장하는가
  - 반복된 실수를 어디에 남기는가
- 세미나 흐름:

```text
Codex thread
-> subagent로 탐색/검토 분리
-> ontology로 IP 지식 구조화
-> evidence 기반 설계/검증 loop
```

### 발표 대본
처음 Codex를 소개할 때 바로 "RTL을 만들어준다"로 들어가면 기대치가 너무 앞서갈 수 있습니다. 실제로는 Codex가 잘 동작하려면 작업 단위, context, 검증 기준, 반복 지식이 같이 잡혀야 합니다.

그래서 이 세미나는 먼저 Codex의 기본 작업 단위인 thread와, 병렬 탐색에 쓰는 subagent를 짧게 설명합니다. 그 다음 Hardware IP 업무에서는 왜 단순 파일 검색이나 TODO list보다 ontology가 필요한지로 넘어가겠습니다.

핵심은 자동화 자체가 아니라, 사람이 정한 기준이 agent workflow 안에서 유지되는 구조입니다.

---

## Slide 2. Thread: Codex의 기본 작업 단위

### 화면 핵심
```text
Thread =
  prompt
  + model outputs
  + file read/edit
  + command/tool calls
  + follow-up turns
  + evidence trail
```

### 설명
Thread는 하나의 작업 세션이다. 첫 요청, Codex의 응답, 파일 읽기/수정, command 실행, tool call, follow-up이 한 흐름으로 쌓인다. 같은 thread에서 이어서 질문하거나, 나중에 resume할 수도 있다.

### Hardware IP 예시
```text
Thread A: Toy APB timer spec review
Thread B: interface ambiguity 정리
Thread C: RTL skeleton candidate 생성
Thread D: validation checklist / evidence 정리
```

### 발표 대본
Thread는 단순 채팅방이라기보다, 하나의 작업 단위와 그 작업의 흔적입니다. 예를 들어 "APB timer spec을 검토해줘"라고 시작하면, 그 thread 안에는 spec 요약, ambiguity, RTL 후보, test checklist, 실행한 command, 남은 issue가 이어서 쌓입니다.

다만 thread가 길어질수록 context가 섞일 수 있습니다. 그래서 중요한 결정과 evidence는 thread 안에만 두지 않고, 파일이나 ontology object로 남기는 것이 좋습니다.

### 전환 멘트
그런데 한 thread에 모든 탐색 로그, test log, code search 결과를 다 넣으면 main thread가 금방 지저분해집니다. 이때 subagent 개념이 도움이 됩니다.

---

## Slide 3. Subagent: main thread를 깨끗하게 유지하는 병렬 탐색

### 화면 핵심
```text
Main thread:
  requirement / decision / final action

Subagents:
  spec scan
  RTL scan
  test/evidence scan
  log triage
```

### 좋은 사용처
| 사용처 | 예시 |
| --- | --- |
| Read-heavy exploration | 관련 module, spec section, test 위치 찾기 |
| 관점별 review | spec trace / RTL correctness / test gap |
| log triage | failure group, first evidence, suspected area |
| 큰 자료 요약 | 긴 문서나 report를 나눠 읽고 요약 |

### 조심할 사용처
| 조심할 일 | 이유 |
| --- | --- |
| 여러 subagent가 같은 RTL 수정 | merge conflict, 의도 충돌 가능 |
| interface/protocol 임의 변경 | product contract가 바뀔 수 있음 |
| raw log를 그대로 main thread에 합류 | context pollution 가능 |

### 발표 대본
Subagent는 여러 agent를 병렬로 돌려서 main thread가 최종 판단에 집중하게 하는 방식입니다. 예를 들어 한 agent는 spec trace만 보고, 한 agent는 RTL reset/handshake만 보고, 한 agent는 test gap만 보는 식입니다.

중요한 점은 subagent를 "사람을 빼는 장치"로 보면 위험하다는 것입니다. 더 적절한 관점은 noisy exploration을 분리하고, main thread에는 요약된 근거와 decision 후보만 올리는 장치입니다.

RTL/IP에서는 특히 read-heavy 분석에 먼저 쓰는 편이 좋아 보입니다. 여러 agent가 동시에 product RTL을 수정하는 것은 coordination cost가 크기 때문에 조심해야 합니다.

### 예시 prompt
```text
Spawn 3 read-only subagents:
1. spec/requirement trace 관점
2. RTL reset/handshake/interface 관점
3. test/evidence gap 관점

각 agent는 raw log를 붙이지 말고,
file reference / risk / next check만 요약해줘.
모든 결과를 main thread에서 하나의 action table로 합쳐줘.
```

### 전환 멘트
이제 질문은 이것입니다. thread와 subagent를 잘 쓰더라도, HW/IP에서 agent가 무엇을 기준으로 판단하게 할 것인가. 여기서 ontology가 필요해집니다.

---

## Slide 4. 왜 IP 설계에는 ontology가 필요한가

### 화면 핵심
```text
File search:
  "어디에 무엇이 있는가"

TODO list:
  "무엇을 해야 하는가"

Ontology:
  "무엇이 무엇과 연결되어 있고,
   어떤 evidence로 어떤 claim을 할 수 있는가"
```

### Hardware IP에서 필요한 연결
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

### 발표 대본
Hardware IP 업무는 파일 몇 개를 찾는 문제로 끝나지 않습니다. 어떤 requirement가 어떤 interface와 연결되는지, 어떤 constraint 때문에 design decision이 생겼는지, 어떤 verification case가 어떤 requirement를 검증하는지, 현재 evidence가 최신 RTL delta 이후의 것인지가 중요합니다.

그래서 ontology는 지식 그래프를 예쁘게 그리는 장식이라기보다, agent가 설계와 검증을 같은 기준으로 이어가기 위한 semantic substrate로 볼 수 있습니다.

예를 들어 "이 interrupt clear behavior가 맞는가"라는 질문은 RTL line만 봐서는 답하기 어렵습니다. 연결된 requirement, register field policy, APB-visible behavior, test case, pass log, owner decision을 같이 봐야 합니다.

### 전환 멘트
그러면 ontology 기반 IP 설계는 처음부터 거대한 SoC 모델을 만드는 것이 아니라, 작은 IP slice에서 시작하는 편이 현실적입니다.

---

## Slide 5. Ontology 기반 IP 설계: 작은 slice부터 시작

### 화면 핵심
```text
First slice:
  one IP block
  + one interface
  + 3-5 requirements
  + key decisions
  + validation evidence
  + owner/review state
```

### Toy IP 예시
```yaml
IPBlock:
  id: ip_toy_apb_timer
  interface_refs:
    - if_apb_slave
  requirement_refs:
    - req_counter_enable
    - req_compare_interrupt
    - req_clear_policy
  decision_refs:
    - dec_interrupt_clear_priority
  verification_refs:
    - vcase_counter_smoke
    - vcase_interrupt_clear
  evidence_refs:
    - ev_sim_counter_smoke_pass
  review_state: draft
```

### 설계 흐름
```text
1. IPBlock / Interface / Requirement를 먼저 만든다.
2. 모호한 부분은 DesignDecision 또는 OpenDecision으로 분리한다.
3. RTL candidate는 ontology의 projection으로 생성한다.
4. 검증 결과는 Evidence object로 연결한다.
5. 반복 실수는 Lesson / Rule / Skill 후보로 내린다.
```

### 발표 대본
처음부터 전체 SoC를 ontology로 만들려고 하면 부담이 큽니다. 작은 slice가 좋습니다. 예를 들어 toy APB timer 하나를 잡고, IP block, APB interface, counter enable requirement, compare interrupt requirement, clear policy decision, smoke test evidence를 연결합니다.

이 구조가 있으면 Codex thread에서 "이 requirement를 기준으로 RTL skeleton을 만들어줘", "이 evidence가 어떤 requirement를 커버하는지 확인해줘", "이 decision이 바뀌면 어떤 test가 영향을 받는지 찾아줘" 같은 요청이 가능해집니다.

여기서 RTL은 agent가 마음대로 상상한 결과가 아니라, ontology에 있는 requirement/interface/decision을 구현 후보로 투영한 결과가 됩니다.

### 전환 멘트
마지막으로 이 구조를 실제 운영 loop로 보면, Codex 기본 기능과 ontology가 어떻게 만나는지 정리할 수 있습니다.

---

## Slide 6. 운영 loop: Thread/Subagent/Ontology/Evidence

### 화면 핵심
```text
Thread:
  goal / context / constraints / done-when

Subagent:
  spec scan / RTL scan / test scan / log triage

Ontology:
  IP / interface / requirement / decision / evidence / owner

Gate:
  evidence freshness / scope / claim boundary

Learning:
  AGENTS.md / rule / skill / wiki / ontology patch
```

### 발표 대본
정리하면 Codex 기본 사용법과 ontology 기반 IP 설계는 별도 주제가 아니라 연결된 구조입니다.

Thread는 작업을 진행하는 표면입니다. Subagent는 탐색과 로그 분석을 병렬로 분리하는 방식입니다. Ontology는 agent가 무엇을 기준으로 판단해야 하는지 알려주는 구조입니다. Evidence는 claim을 뒷받침하는 근거이고, gate는 어디까지 완료라고 말할 수 있는지 정하는 장치입니다.

현재 단계에서는 Spec/RTL 자동 구현을 크게 주장하기보다, 검증 triage, review, evidence 정리, requirement trace, 반복 실수 지식화부터 시작하는 편이 현실적입니다. 그렇게 작은 workflow가 안정되면, 그 다음에 RTL skeleton 생성이나 parameterized implementation candidate로 확장할 수 있습니다.

### 마지막 메시지
> Codex를 잘 쓰는 것은 좋은 prompt 하나를 찾는 문제가 아니라, thread와 subagent로 작업을 나누고 ontology와 evidence로 판단 기준을 남기는 운영 구조를 만드는 문제에 가깝다.

---

## 10분 압축 버전

1. Codex는 코드 생성기보다 작업 thread agent로 설명한다.
2. Thread는 prompt, context, tool call, evidence가 쌓이는 작업 단위다.
3. Subagent는 noisy exploration을 분리해 main thread를 깨끗하게 유지한다.
4. HW/IP에서는 file search보다 IP/Requirement/Interface/Evidence 관계가 중요하다.
5. Ontology는 이 관계를 agent가 읽을 수 있는 구조로 만든다.
6. 시작점은 전체 SoC가 아니라 작은 IP slice다.
7. 회사 적용은 검증, review, evidence, 지식화부터 시작하는 편이 현실적이다.

---

## 발표 직전 한 장 Cheat Sheet

```text
Prompt = Goal + Context + Constraints + Done when
Thread = 작업 흐름 + evidence trail
Subagent = read-heavy 탐색/리뷰를 병렬 분리
Ontology = IP 지식의 연결 구조
Evidence = 어떤 claim을 뒷받침하는 근거
Gate = 어디까지 완료라고 말할 수 있는지의 경계
Learning = 반복 실수를 rule/skill/wiki/ontology로 저장
```

---

## Sources

- Codex manual helper 확인일: 2026-07-08. Manual status: `local manual was already current`.
- Codex thread/context: Codex Manual > Prompting, `https://developers.openai.com/codex/prompting.md`, local manual lines 478-505.
- Codex subagent concepts: Codex Manual > Subagent concepts, `https://developers.openai.com/codex/concepts/subagents.md`, local manual lines 10558-10620.
- Codex subagent workflow/config: Codex Manual > Subagents, `https://developers.openai.com/codex/subagents.md`, local manual lines 12275-12390.
- Local seminar basis: `codex_basic_usage_for_seminar.md`, `codex_ssot_rtl_trial_lessons_5slides.md`.
- Ontology/IP basis: `life/knowledge/agent_architecture_thoughts.yaml`, `life/knowledge/soc_knowledge_db_design.yaml`.
