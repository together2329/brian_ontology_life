# Codex 기본 용어 8개: 세미나용 요약

작성일: 2026-07-08

목적: 기존 세미나 앞부분에 넣을 수 있는 짧은 `Codex/AI 기본 사용법` 섹션. 범위는 `thread`, `plan`, `goal`, `agent`, `subagent`, `skill`, `hook`, `rule` 정도로 제한한다. 뒤쪽에 `온톨로지 기반 개발`의 기본 개념만 덧붙인다.

톤:
- Codex가 판단을 대신한다는 설명보다, 사람이 context, 검증, 리뷰, 지식화를 어떻게 설계할지에 초점을 둔다.
- RTL/Spec 업무에서는 "바로 구현"보다 "가정 분리, 검증 기준, review loop, 반복 지식화"에 연결한다.

---

## 한 장 요약

```text
Thread   = 작업의 기억 단위
Plan     = 구현 전, 가정과 순서를 먼저 정리하는 모드
Goal     = 긴 작업 동안 유지되는 완료 기준
Agent    = 특정 역할과 설정을 가진 작업 주체
Subagent = noisy/read-heavy 작업을 병렬로 분리하는 방법
Skill    = 반복 workflow를 재사용 가능한 절차로 만든 것
Hook     = agent loop 중간에 자동 검사/기록/정책을 끼우는 지점
Rule     = command 실행 권한을 prefix 기준으로 제어하는 guardrail
```

발표 문장:

> Codex 기본은 명령어를 많이 아는 것보다, thread 안에서 plan, goal, agent, skill, hook, rule을 어떻게 조합해 작업 loop를 설계할지 이해하는 데 가깝다.

---

## 1. Thread

Thread는 하나의 작업 세션이다. prompt, Codex 응답, tool call, file read/edit, command 결과가 한 흐름으로 쌓인다. 한 thread 안에서 여러 prompt를 이어갈 수 있고, 나중에 resume할 수도 있다.

RTL/Spec 관점:

```text
Thread = 한 설계/검증 task의 working memory

예:
- timer spec ambiguity 정리 thread
- failing regression triage thread
- RTL skeleton candidate thread
- review/evidence 정리 thread
```

주의:
- 여러 thread가 같은 파일을 동시에 수정하면 충돌이 날 수 있다.
- 병렬화가 필요하면 read-only 분석, subagent, worktree 같은 분리 장치를 같이 고려한다.

발표 문장:

> Thread는 채팅방이라기보다, 한 작업의 context와 evidence가 쌓이는 작업 단위로 볼 수 있다.

---

## 2. Plan

Plan은 바로 구현하기 전에 Codex가 context를 보고 작업 순서, 모호한 점, 확인해야 할 것을 먼저 정리하는 단계다. 복잡하거나 애매한 작업에서는 `/plan`으로 시작하는 편이 안전하다.

RTL/Spec 관점:

```text
/plan

Goal:
  spec draft에서 ambiguity와 owner decision을 분리한다.

Plan에서 보고 싶은 것:
  - 관련 파일
  - 먼저 읽을 spec section
  - 바꾸면 안 되는 interface
  - 사람이 판단해야 하는 behavior
  - 어떤 test/check를 돌릴지
```

좋은 사용처:
- 요구가 압축되어 있을 때
- spec과 RTL 사이에 해석 여지가 있을 때
- test/check 기준이 아직 정리되지 않았을 때
- 여러 후보를 만들기 전에 비교 기준을 세우고 싶을 때

발표 문장:

> `/plan`은 일을 늦추는 단계라기보다, AI가 조용히 가정을 품고 구현하지 않게 만드는 완충 구간으로 설명할 수 있다.

---

## 3. Goal

Goal은 긴 작업 동안 유지되는 목표와 완료 기준이다. `/goal`로 시작하며, 목표 문장이 곧 Codex가 계속 확인하는 completion criteria가 된다.

RTL/Spec 관점:

```text
/goal
이 timer block의 spec ambiguity, RTL skeleton candidate, smoke test checklist,
review risk를 정리한다. 완료 기준은 사람이 결정해야 할 항목과 자동 확인 가능한
항목이 분리되어 있는 것이다.
```

Goal에 넣으면 좋은 것:
- 구체적 산출물
- 완료 기준
- test/check 기준
- 바꾸면 안 되는 범위

Goal에 넣기 애매한 것:
- 너무 긴 배경 설명
- 중간에 바뀔 가능성이 큰 세부 지시
- 검증할 수 없는 추상 목표

발표 문장:

> Goal은 "계속 기억해야 하는 done definition"에 가깝다. 길고 여러 turn이 필요한 작업에서 특히 도움이 된다.

---

## 4. Agent

Agent는 Codex가 작업을 수행하는 주체다. 일반적으로 main agent가 사용자의 thread를 이끌고, 필요한 경우 built-in/custom agent 역할을 나눠 쓸 수 있다.

Codex manual 기준으로 built-in agent 예시는 다음과 같다.

| Agent | 발표용 설명 |
| --- | --- |
| `default` | 일반 작업 fallback |
| `worker` | 구현과 수정 중심 |
| `explorer` | read-heavy codebase 탐색 중심 |

RTL/Spec 관점:

```text
main agent:
  요구, 결정, 최종 산출물을 관리

explorer-like agent:
  spec/RTL/TB 구조를 읽고 관련 파일을 찾음

worker-like agent:
  제한된 candidate 수정이나 checklist 작성
```

주의:
- 역할을 너무 많이 나누면 coordination cost가 생긴다.
- product-defining decision은 agent 역할로 넘기기보다 사람이 판단할 항목으로 남기는 편이 좋다.

발표 문장:

> Agent를 역할로 나누면 "누가 구현하나"보다 "누가 읽고, 누가 비교하고, 누가 검증하나"를 설계할 수 있다.

---

## 5. Subagent

Subagent는 main thread 밖에서 별도 agent를 병렬로 돌리는 방식이다. Codex가 여러 specialized agent를 띄우고, 결과를 모아 하나의 응답으로 정리할 수 있다.

좋은 사용처:
- 큰 repo에서 관련 파일 찾기
- failure log triage
- spec section별 요약
- review 관점 분리: correctness / test gap / maintainability
- 여러 후보의 장단점 비교

조심할 사용처:
- 여러 subagent가 같은 RTL 파일을 동시에 수정
- owner decision이 필요한 interface 변경
- raw log를 main thread에 그대로 많이 붙이는 방식
- 너무 깊은 recursive delegation

추천 prompt:

```text
이 branch를 read-only subagent로 나눠서 분석해줘.

spawn 3 agents:
1. spec/requirement trace 관점
2. RTL reset/handshake correctness 관점
3. test/evidence gap 관점

각 agent는 raw log를 길게 붙이지 말고,
file reference / risk / next check만 요약해줘.
모든 agent가 끝난 뒤 하나의 action table로 합쳐줘.
```

발표 문장:

> Subagent는 사람 review를 없애기 위한 장치라기보다, main thread의 context를 깨끗하게 유지하면서 noisy exploration을 분리하는 방법으로 볼 수 있다.

---

## 6. Skill

Skill은 반복 workflow를 재사용 가능한 절차로 만든 것이다. `SKILL.md`에 언제 쓰는지, 어떤 순서로 할지, 어떤 reference나 script를 볼지 적는다.

RTL/Spec 관점에서 skill로 만들 만한 것:

| 반복 업무 | Skill 후보 |
| --- | --- |
| simulation log triage | failure grouping / first evidence / next check |
| RTL review | reset, handshake, width, missing test checklist |
| spec review | requirement, assumption, ambiguity, owner decision 분리 |
| release checklist | lint, compile, regression, report packaging |

좋은 skill의 특징:
- 한 가지 일을 좁게 다룬다.
- input과 output이 명확하다.
- 반복되는 review feedback을 절차로 내린다.
- 필요할 때만 자세한 instruction을 읽게 한다.

작은 예시:

```md
---
name: rtl-review
description: Use when reviewing RTL changes for reset, handshake, width, and missing test risk.
---

1. Identify changed RTL and related tests.
2. Check reset behavior, handshake timing, width mismatch, and interface changes.
3. Report only actionable risks with file references.
4. Separate confirmed issues from questions.
```

발표 문장:

> Skill은 "잘 된 prompt를 저장"하는 수준을 넘어, 반복 업무를 팀의 검증 절차로 만드는 방법이다.

---

## 7. Hook

Hook은 Codex의 agent loop 중간에 사용자가 만든 script를 끼우는 확장 지점이다. 예를 들어 prompt 제출, tool 실행 전후, permission request, subagent start/stop, turn stop 같은 지점에서 자동 검사나 기록을 실행할 수 있다.

RTL/Spec 관점에서 hook으로 생각해볼 수 있는 것:

| Hook 사용처 | 예시 |
| --- | --- |
| prompt 제출 전 | private path, secret, raw IP 이름이 prompt에 들어갔는지 검사 |
| command 실행 전 | 위험한 shell command 차단 |
| command 실행 후 | lint/sim 결과 요약 저장 |
| turn 종료 시 | evidence summary나 TODO를 wiki 후보로 남김 |
| subagent 종료 시 | subagent raw output을 요약 형태로 강제 |

주의:
- hook은 자동화이므로 너무 빨리 복잡하게 만들면 디버깅 비용이 생긴다.
- non-managed command hook은 review/trust가 필요하다.
- 처음에는 기록/검사 위주로 작게 시작하는 편이 좋다.

발표 문장:

> Hook은 agent가 일하는 중간중간에 팀의 안전장치나 기록 장치를 끼워 넣는 방법으로 설명할 수 있다.

---

## 8. Rule

Rule은 Codex가 sandbox 밖에서 어떤 command를 실행할 수 있는지 prefix 기준으로 제어하는 guardrail이다. `.rules` 파일로 만들고, `allow`, `prompt`, `forbidden` 같은 decision을 줄 수 있다.

RTL/Spec 관점에서 rule로 생각해볼 수 있는 것:

| Rule 예시 | 의도 |
| --- | --- |
| `rm -rf` 계열 forbidden | 실수 방지 |
| `git push` prompt | 외부 side effect 전 확인 |
| 특정 regression command allow | 반복 check의 approval fatigue 감소 |
| private path 접근 forbidden | 민감 자료 보호 |

개념 예시:

```python
prefix_rule(
    pattern = ["git", "push"],
    decision = "prompt",
    justification = "Pushing changes should be confirmed by the user",
)
```

발표 문장:

> Rule은 agent에게 일을 못 하게 만드는 장치라기보다, 반복되는 안전 판단을 명시해서 사람이 중요한 승인에 집중하게 하는 장치로 볼 수 있다.

---

## 온톨로지 기반 개발 기본 개념

여기서 말하는 온톨로지는 거창한 지식 그래프라기보다, AI가 만든 산출물과 사람이 내린 판단을 다음 작업에서 다시 쓸 수 있게 연결해 두는 구조다.

발표용 한 문장:

> AI 기반 개발에서 온톨로지는 "이번 실험에서 무엇을 배웠는지"를 requirement, contract, evidence, decision으로 남겨 다음 loop의 입력으로 만드는 장치에 가깝다.

### 핵심 흐름

```text
요구 문장
-> 요구 원자
-> 의무
-> 계약
-> 근거
-> 검증
-> 결정
-> rule / skill / wiki 업데이트
```

각 단계의 의미:

| 단계 | 발표용 설명 |
| --- | --- |
| 요구 문장 | 사용자가 처음 말한 요구나 기존 spec 문장 |
| 요구 원자 | 하나의 trigger, condition, response, timing으로 나눈 작은 요구 |
| 의무 | 설계나 검증이 책임져야 하는 항목 |
| 계약 | RTL/TB/review가 공유할 관찰 가능한 동작 약속 |
| 근거 | simulation, lint, waveform, assertion, review note 같은 확인 자료 |
| 검증 | 근거가 현재 요구와 계약을 실제로 확인하는지 보는 단계 |
| 결정 | 사람이 선택한 architecture, trade-off, 예외, open/close 판단 |
| rule/skill/wiki | 반복된 시행착오를 다음 agent loop에서 재사용할 형태로 정리 |

### 왜 필요한가

Spec을 쓰는 단계에서도 모호함은 꽤 많이 드러난다. 다만 AI로 구현 후보, test 후보, review 후보를 빠르게 많이 만들기 시작하면 같은 질문이 반복해서 돌아오는 경우가 생긴다.

온톨로지 기반 개발은 그 반복을 줄이기 위한 방식으로 설명할 수 있다.

```text
이번 turn에서 나온 질문:
  reset 우선순위가 write보다 높은가?

그냥 지나가면:
  다음 RTL 후보에서도 같은 가정이 다시 생길 수 있음

온톨로지에 남기면:
  requirement atom / contract / decision으로 연결되어
  다음 plan, review, test checklist의 입력이 됨
```

### RTL/Spec 업무에 맞춘 최소 단위

처음부터 모든 것을 모델링할 필요는 없다. 세미나에서는 아래 정도만 보여줘도 충분하다.

| 최소 단위 | 예시 질문 |
| --- | --- |
| Requirement Atom | 이 요구는 어떤 event, condition, response, timing을 말하는가? |
| Open Decision | 사람이 정해야 하는 behavior나 trade-off는 무엇인가? |
| Contract Candidate | RTL과 TB가 공유할 관찰 가능한 약속은 무엇인가? |
| Evidence | 이 약속을 확인한 command, log, waveform, assertion은 무엇인가? |
| Validation | 이 evidence가 현재 요구를 확인한다고 볼 수 있는가? |
| Rule/Skill Update | 같은 실수를 줄이기 위해 다음 loop에 남길 절차는 무엇인가? |

### AI loop와 연결하기

```text
/plan
  요구 문장을 requirement atom 후보와 open decision으로 나눈다.

/goal
  완료 기준에 contract candidate, evidence, validation note를 포함한다.

subagent
  spec trace, RTL risk, test gap을 병렬로 읽게 하되
  raw log보다 "어떤 atom/contract/evidence와 연결되는지"를 요약하게 한다.

skill
  반복되는 review나 log triage를 절차로 만든다.

hook
  turn 종료 시 evidence summary나 open decision 후보를 남긴다.

rule
  위험 command와 외부 side effect를 명시적으로 제어한다.
```

발표 메시지:

> 구현 비용이 낮아질수록 더 많이 실험할 수 있다. 다만 실험 결과가 다음 spec, review, rule, skill로 연결되지 않으면 학습이 쌓이기 어렵다. 온톨로지는 그 연결을 가볍게 만드는 방법으로 소개할 수 있다.

---

## 세미나 삽입용 5-slide 구성

### Slide A. Codex 기본은 작업 loop다

```text
Thread -> Plan -> Goal
-> Agent/Subagent
-> Skill/Hook/Rule
-> Review / Evidence / Next turn
```

말할 포인트:
- AI는 한 번 답을 주는 도구보다, 여러 turn에서 작업을 진행하는 agent로 보는 편이 자연스럽다.
- 중요한 것은 사람이 context와 done definition을 어떻게 설계하느냐이다.

### Slide B. Plan과 Goal

```text
Plan = 모호함과 순서 정리
Goal = 긴 작업의 완료 기준
```

RTL/Spec 연결:
- 바로 RTL 생성보다 ambiguity, assumption, owner decision을 먼저 나눈다.
- Goal에는 test/check/review 기준을 넣는다.

### Slide C. Agent와 Subagent

```text
Main agent = 요구와 decision 관리
Subagent = noisy exploration 병렬 처리
```

RTL/Spec 연결:
- explorer는 관련 spec/RTL/TB를 찾는다.
- reviewer는 reset/handshake/test gap을 본다.
- worker는 제한된 candidate를 만든다.

### Slide D. Skill, Hook, Rule

```text
Skill = 반복 workflow
Hook  = 자동 검사/기록 지점
Rule  = command permission guardrail
```

RTL/Spec 연결:
- 반복 triage는 skill로 내린다.
- evidence 기록은 hook으로 보조할 수 있다.
- 위험 command는 rule로 제어한다.

### Slide E. 온톨로지 기반 개발

```text
Requirement Atom
-> Contract Candidate
-> Evidence
-> Validation
-> Decision
-> Rule / Skill / Wiki
```

RTL/Spec 연결:
- Spec 단계에서 ambiguity와 owner decision을 먼저 줄인다.
- 구현/test/review에서 나온 질문은 다음 loop의 입력으로 남긴다.
- 반복되는 판단은 rule, skill, wiki로 옮겨 team memory에 가깝게 만든다.

---

## RTL/Spec demo 흐름

```text
1. Thread 시작
   Toy spec 또는 failing log를 context로 제공

2. /plan
   requirement atom / assumption / open question / owner decision 분리

3. /goal
   완료 기준 설정: contract candidate, skeleton candidate, test checklist, review risk

4. Agent 역할 분리
   main agent는 decision table 관리
   subagent는 read-only로 spec trace / RTL risk / test gap 분석

5. Skill 사용
   repeated flow를 rtl-review 또는 log-triage skill로 설명

6. Evidence / Validation 정리
   실행한 check, log, waveform, assertion, review note를 contract 후보와 연결

7. Hook/Rule 소개
   hook: evidence summary 자동 저장
   rule: git push, rm, secret path 같은 command guardrail

8. 마무리
   산출물은 RTL 후보뿐 아니라
   사람이 판단할 decision과 검증 가능한 next check
```

발표 메시지:

> Codex 기본을 이해한다는 것은 slash command를 많이 외우는 것이 아니라, thread 안에서 plan, goal, agent, skill, hook, rule을 조합해 검증 가능한 개발 loop를 만드는 감각에 가깝다.

---

## Sources

Codex manual helper로 확인한 최신 manual 기준. Manual status: `local manual was already current`.

| Topic | Official manual section / URL | Line range used |
| --- | --- | --- |
| Thread, context, goal | Codex Manual > Prompting, `https://developers.openai.com/codex/prompting.md` | lines 478-550 |
| Plan mode | Codex Manual > Best practices, `https://developers.openai.com/codex/learn/best-practices.md`; Slash commands, `https://developers.openai.com/codex/cli/slash-commands.md` | lines 197-207, 6522-6532 |
| Skills | Codex Manual > Agent Skills, `https://developers.openai.com/codex/skills.md` | lines 7335-7360, 7478-7484 |
| Agents and subagents | Codex Manual > Subagents, `https://developers.openai.com/codex/subagents.md`; concepts, `https://developers.openai.com/codex/concepts/subagents.md` | lines 12275-12386, 10567-10593 |
| Hooks | Codex Manual > Hooks, `https://developers.openai.com/codex/hooks.md` | lines 11052-11139, 11263-11284 |
| Rules | Codex Manual > Rules, `https://developers.openai.com/codex/rules.md` | lines 8094-8158, 8162-8228 |
