# AI Verification-First Seminar Focus Cut: Trial-And-Error

작성일: 2026-07-06

목적: 내일 발표용으로 바로 옮길 수 있는 집중본. 넓은 AI 기능 소개보다, 현재 회사에서 현실적으로 집중하고 있는 검증 업무를 중심에 둔다. Spec 작성과 RTL 생성은 아직 회사 업무에 agent가 본격 적용된 영역이 아니며, 난도가 높고 조심스럽게 확장해야 하는 future frontier로 설명한다. Brian의 로컬 AI agent workflow와 IP 개발 workflow 시행착오는 "왜 검증/evidence loop부터 시작하는가"를 설명하는 배경 사례로만 사용한다.

회사 공유 전 점검:
- local repo path, 내부 프로젝트명, private raw log는 제거하거나 추상화한다.
- git commit hash는 발표에서 직접 보여주기보다 "history evidence"로만 사용한다.
- 메시지는 "AI가 RTL 설계자를 대신한다"가 아니다.
- 현재 적용 포인트는 검증 log triage, evidence 정리, review planning, 반복 질문의 guide/skill화다.
- Spec/RTL agent 개발은 아직 어렵고, 검증에서 나온 evidence와 ambiguity를 바탕으로 나중에 연결할 수 있는 확장 방향으로 둔다.

---

## One-Liner

현재 회사 적용의 현실적인 시작점은 Spec/RTL 자동 개발보다 검증 업무 쪽으로 보인다. AI는 lint/compile/simulation/formal log를 분류하고, evidence와 next check를 정리하고, 사람이 판단할 지점을 드러내는 데 먼저 써볼 수 있다. 이 검증 loop에서 쌓인 evidence와 ambiguity가 나중에 Spec/RTL 개선으로 돌아갈 수 있다.

## Core Message

Spec/RTL 개발에 agent를 바로 붙이는 것은 쉽지 않다. design intent, interface contract, timing/PPA, ownership, 검증 책임이 얽혀 있어서 agent가 조용히 잘못된 결정을 내리면 위험하다.

그래서 첫 적용 지점은 검증 쪽으로 잡아볼 수 있다. 검증 업무는 input과 output이 비교적 명확하다. log, failing command, test result, waveform/evidence path, known rule, review comment가 있고, agent가 "무엇을 고쳐야 한다"보다 "무엇이 관찰됐고, 다음에 무엇을 확인해야 하는가"를 정리하기 좋은 편이다.

> 지금의 메시지는 "AI가 Spec/RTL을 작성한다"가 아니라, "검증 가능한 업무 loop를 먼저 안정화하고, 거기서 얻은 근거를 Spec/RTL 개선으로 되돌린다"에 가깝다.

현재 세미나의 중심 loop는 다음처럼 잡는 편이 안전하다.

```text
검증 input 수집
-> log/failure/evidence 분류
-> 관련 spec/RTL/test/context 조사
-> safe next check와 human decision 분리
-> rerun/checklist/review plan 작성
-> 검증 evidence와 unresolved assumption 기록
-> 반복 패턴을 Rule / Skill / LLM Wiki / Ontology로 저장
-> 다음 검증, Spec review, RTL review에 반영
```

이 방향은 네 번의 시행착오에서 나왔다.

```text
1차: 의도만 전달했다.
-> Agent가 빈칸을 자기 방식으로 채우고 마음대로 만들었다.

2차: 모호한 부분은 묻게 했다.
-> 너무 많은 질문이 쏟아져서 사람이 모두 판단해야 하는 부담이 생겼다.

3차: 정말 의도한 대로 구현한 것이 맞는지 보려 했다.
-> test pass만으로는 부족할 수 있었고, intent-conformance를 확인하는 장치가 필요해 보였다.

4차: 이전 결과로 배운 것을 토대로 계속 개선하려 했다.
-> 같은 실수를 줄이기 위해 rule, skill, wiki, ontology로 되돌리는 시스템이 도움이 될 수 있어 보였다.
```

## Recommended Seminar Flow

발표 순서는 "무엇을 만들었는가"보다 "무엇을 겪었고 어떤 고민이 생겼는가"를 먼저 보여주는 편이 자연스럽다.

```text
1. Reality: 회사의 현재 AI 적용 초점은 검증 쪽이다.
2. Constraint: Spec/RTL agent 적용은 어렵고 아직 조심스럽다.
3. Thesis: 검증 업무는 log -> evidence -> next check -> decision loop로 agent를 붙여보기 좋은 후보다.
4. Evidence: local agent/IP workflow history는 왜 gate/evidence/review가 중요한지 보여준다.
5. Pain: 생성 속도, 질문 증가, review bottleneck, silent-pass 문제가 있었다.
6. Method: 검증 task를 read-heavy triage부터 시작하고, same gate와 evidence 기준으로 닫는다.
7. Memory: 결과를 ontology/wiki/rule/skill로 남기면 다음 검증과 Spec/RTL review에 도움이 될 수 있다.
8. Action: 작은 verification task 하나를 세미나 demo와 첫 action으로 잡는다.
```

세미나의 중심 문장:

> AI는 지금 당장 RTL 설계자를 대체하는 도구라기보다, 검증 loop에서 관찰, 근거, 다음 확인 지점을 정리하는 도구로 시작해볼 수 있다.

## Why Ontology And LLM Wiki

AI로 검증 log, review comment, 실패 사례를 더 많이 다루게 되면 결과가 흩어지기 쉽다. 흩어진 결과가 다음 검증이나 Spec/RTL review로 이어지려면 구조가 필요하다.

- AI: 검증 log triage, root-cause 후보 정리, next check 제안 속도를 올릴 수 있다.
- Test / Gate / Review: "봤다"와 "검증됐다"를 분리하는 기준이 된다.
- Worktree / Wavefront: 나중에 수정 후보나 실험 후보가 생길 때 안전하게 분리할 수 있다.
- Architecture/PPA 탐색: 현재 주제가 아니라, 검증 evidence가 쌓인 뒤 확장할 수 있는 고난도 영역이다.
- Ontology: Requirement, Assumption, RTLBlock, TestCase, Failure, Evidence, Decision, Rule을 연결해볼 수 있다.
- LLM Wiki: 사람이 읽고 LLM이 다시 context로 쓸 수 있는 지식 표면으로 둘 수 있다.

짧은 표현:

```text
AI = 더 빠른 검증 triage
Gate = 검증과 추정을 나누는 필터
Evidence = 사람이 판단할 근거
Ontology = 배움의 구조
LLM Wiki = 다음 AI-assisted turn의 기억 표면
```

---

## Evidence From Git History

주의: 아래 history는 Brian의 로컬 실험과 workflow prototype에서 나온 근거다. 회사에서 Spec/RTL agent 개발이 이미 적용됐다는 의미가 아니다. 발표에서는 "왜 검증, gate, evidence, review를 먼저 잡아야 하는가"를 설명하는 배경 evidence로만 쓴다.

분석 대상:
- local development history HEAD: 4,657 commits, `--all`: 5,027 commits
- AI agent workflow prototype path: 3,342 commits
- IP workflow pack: 86 commits

local development history 월별 commit 분포:

| Month | Commits | 해석 |
| --- | ---: | --- |
| 2025-10 | 10 | AXI write/read generator 실험 시작 |
| 2025-11 | 64 | packet/header/error/mismatch 직접 구현 시행착오, zero-dependency ReAct agent 시작 |
| 2025-12 | 105 | memory, Graph Lite, Verilog analysis, RAG, sub-agent, Plan mode 실험 |
| 2026-03 | 245 | agent workflow prototype, spec navigation, skill routing, plan/todo 정리 |
| 2026-04 | 1,229 | TUI, tool/parser/streaming 안정화, generation/evidence 실험 확대 |
| 2026-05 | 1,929 | Atlas UI, SSOT->RTL, todo/gate/evidence pipeline 확대 |
| 2026-06 | 1,072 | 설계 수렴 루프, locked design intent, silent-pass hardening, ontology/evidence 기반 완료 판단 정리 |

local development history commit subject keyword counts:

| Keyword | Count | 의미 |
| --- | ---: | --- |
| todo | 1,650 | 작업을 작은 turn 단위로 쪼개려는 시도 |
| fix | 1,050 | 한 번에 맞힌 것이 아니라 반복 수정으로 수렴 |
| rtl | 809 | RTL 생성 실험과 검증 workflow 비중이 커짐 |
| ssot | 773 | 단순 코드 생성보다 기준 정보를 두려는 시도 |
| gate | 410 | 사람이 모든 것을 리뷰하기 어려워 gate가 도움이 됨 |
| atlas | 397 | UI/운영 surface 실험 |
| test | 334 | 실험을 검증 가능한 loop로 만들려는 시도 |
| evidence | 176 | 통과 결과와 완료 판단을 구분하려는 evidence 구조 |
| ontology | 161 | 시행착오를 구조화된 지식으로 남기려는 방향 |
| req/spec | 287 | Spec/requirement를 구현 전후로 계속 정제 |

IP workflow pack commit flow:

| Date | Main Movement | 해석 |
| --- | --- | --- |
| 2026-06-20 | clean design-completion pack, native subagent, fallback block, scope lock, receipt | 무작정 구현을 줄이는 최소 operating system |
| 2026-06-21 | requirement atom, lock readiness, deep intake, verification strategy | 질문을 많이 받기보다 lock-blocking 주요 req를 분해 |
| 2026-06-22 | wavefront scheduler, review guide, barrier, stale path guard | 병렬 실험을 안전하게 열기 시작 |
| 2026-06-23 | lifecycle, baseline, stale propagation, version steward | 실험 결과와 artifact lifecycle 관리 |
| 2026-06-24 | pack resolver, migration, mixed-layout reject, run loop + wavefront | pack 구조 정리와 run loop 안정화 |
| 2026-06-25~27 | bounded loop, schema validation, handoff decisions, review workflow | 많은 turn을 통제된 loop와 review로 묶음 |
| 2026-06-29 | recovery, deep interview ranking, IP git flow, run control | 멈춤/복구/질문 우선순위/개별 IP history 관리 |
| 2026-07-04~05 | RTL/TB role split, decision autonomy, evidence handoff, web review | 병렬 역할 분리와 decision automation의 경계 정리 |

분석에 사용한 evidence command:

```bash
git -C <local-development-history> rev-list --count HEAD
git -C <local-development-history> rev-list --all --count
git -C <local-development-history> log --date=format:%Y-%m --format='%ad' | sort | uniq -c
git -C <local-development-history> log --date=short --format='%ad%x09%h%x09%s'
git -C <local-development-history> log --numstat --format='--COMMIT--%H%x09%ad%x09%s' --date=short
git -C <ip-workflow-pack> rev-list --count HEAD
git -C <ip-workflow-pack> log --reverse --date=short --format='%ad%x09%h%x09%s'
```

회사 발표용 redaction:
- local path는 "Brian's local development history"로 바꾼다.
- commit hash는 숨기고 timeline/keyword/phase 위주로 보여줄 수 있다.
- internal project/package names are replaced with "AI agent workflow prototype" and "IP workflow pack".
- private IP 이름이나 raw design detail은 demo에서 쓰지 않는다.

---

## 시행착오 1: 검증 loop에서 요구의 빈틈이 먼저 드러날 수 있다

Evidence:
- 2025-11 초기 log: `bad header version`, `add multiple error case`, `Fix AXI handshake timing issues`, `resolve issue - bvalid`, `size mismatch error`, `fix mismatch`

겪은 문제:
- 예전 직접 구현 방식에서는 header format, packet size, bvalid timing, queue allocation, interrupt/error behavior가 구현 중에 계속 보였음.
- 구현 자체가 비싸던 시절에는 이 시행착오의 부담이 컸다.
- 회사 적용 관점에서는 바로 RTL을 만들게 하기보다, 검증 log와 failing case에서 ambiguity, open decision, assumption, testable contract를 먼저 뽑는 편이 안전하다.
- 검증 결과는 Spec과 RTL의 가정이 어디서 충돌하는지 보여주는 evidence가 될 수 있다.
- 이 evidence가 쌓이면 나중에 Spec review와 RTL review를 더 구조화할 수 있다.

발표 메시지:

> AI는 검증 log와 failing case를 읽으며 요구의 빈틈과 결정 지점을 먼저 드러내는 데 도움이 될 수 있다.

---

## 시행착오 2: AI workflow에서는 생성 속도와 운영 복잡도가 같이 늘어날 수 있다

Evidence:
- 2025-11-28: lightweight ReAct-style agent 추가
- 2025-11-30: `Add error recovery system to prevent infinite loops`
- 2025-12-02: `Prevent agent from hallucinating Observations and breaking the loop`
- 2025-12-03~07: Memory, Graph Lite, Verilog analysis, RAG, sub-agent 추가
- 2025-12-22: Plan Mode 추가

겪은 문제:
- agent loop, parser, tool call, streaming, RAG, memory, subagent가 늘어나면서 각각의 failure mode도 함께 생길 수 있었다.
- 구현 속도는 올라갔지만, context pollution, hallucinated observation, infinite loop, stale state, tool parsing 문제가 생겼다.
- "AI가 많이 한다"와 "품질이 쌓인다"는 다른 문제로 보였다.

발표 메시지:

> AI로 검증 triage 속도를 높이면 loop control, context, verification, memory 같은 운영 이슈도 함께 살펴볼 수 있었다.

시행착오 1과 2의 차이:

| 구분 | 시행착오 1 | 시행착오 2 |
| --- | --- | --- |
| 문제의 위치 | 검증 evidence / 설계 계약 | AI 실행 workflow |
| 드러난 것 | 요구의 모호함, open decision, hidden assumption | loop, context, tool, memory failure mode |
| 도움이 된 접근 | 검증 결과에서 ambiguity와 contract를 먼저 분리 | AI workflow를 evidence/guard/review로 운영 |

---

## 시행착오 3: 마음대로 만들게 해도, 전부 묻게 해도 문제가 생길 수 있다

Brian reflection:
- 처음에는 의도를 전달했더니 agent가 빈칸을 자기 방식으로 채우고 마음대로 만들었다.
- 너무 질문을 다 받아서 Brian이 전부 정하려고 한 것도 시행착오였다.
- 세 번째로는 정말 의도한 대로 구현한 것이 맞는지 확인하는 장치가 필요해 보였다.
- 네 번째로는 이전 결과에서 배운 것을 토대로 개선하고, 같은 실수를 줄이는 시스템이 도움이 될 수 있어 보였다.
- 최소한 PPA spec과 interface 구조처럼 product-defining contract가 맞다면, 모든 세부 질문을 사람에게 던지기보다 parameterized generation으로 열어두는 방식도 검토해볼 수 있었다.
- 더 좋은 아키텍처를 열어두고 탐색하되, 주요 requirement는 지키는 방식이 도움이 되는 경우가 있었다.
- parameter화 / generated-option 기반으로 두었으면 더 좋았을 결정들이 있었다.

문제:
- 의도만 전달하면 agent가 hidden assumption을 임의로 채울 수 있었다.
- 모든 질문을 사람에게 묻는 방식은 사람의 판단 부담을 줄이기 어려웠다.
- 반대로 agent가 모든 결정을 해버리면 product-defining decision을 조용히 바꿀 여지가 있었다.
- 회사 검증 적용에서는 agent가 "수정 결정"을 내리는 것보다, human decision needed를 정확히 표시하는 쪽에서 시작하는 편이 안전해 보인다.
- test pass만으로는 정말 의도한 대로 구현됐는지 충분히 설명되지 않는 경우가 있었다.
- 실패와 판단을 남기지 않으면 다음 실행에서 같은 질문과 같은 실수가 반복될 수 있었다.

바뀐 원칙:

```text
Product-defining / external contract -> 사람 결정
Repo-local fact -> local evidence cite 후 agent 결정 가능
Reversible internal choice -> parameterize / generated option으로 유지
Architecture/PPA tradeoff -> 현재 세미나의 직접 적용 범위 밖. 나중에 worktree/DSE + metric + verification cost로 후보 비교
Measured tradeoff -> metric + selection rule + decision receipt
Unknown direct-impact decision -> needs_user
```

질문 폭주를 줄이는 기준:

```text
Ask human:
- PPA intent/spec
- external interface structure
- protocol/contract
- product-defining behavior

Do not ask every detail:
- reversible internal choice
- local implementation detail
- generated option
- parameter default
```

발표 메시지:

> 검증 agent는 마음대로 만들거나 질문을 쏟아내는 방향보다, evidence로 판단 가능한 것, 사람이 결정해야 할 것, intent-conformance를 확인해야 할 것을 나누는 방향이 좋아 보인다. 배운 것을 다음 실행으로 되돌리는 구조도 함께 검토해볼 수 있다.

---

## 시행착오 4: 후보가 많아지면 리뷰 방식도 나눠볼 수 있었다

Evidence:
- `todo` 1,650회, `fix` 1,050회, `test` 334회, `gate` 410회
- 2026-05~06에 `silent-pass`, `gate`, `evidence`, `review`, `completion` 관련 commit이 반복됨
- 2026-06-08~10: silent-pass gate hardening, vacuous completion, fabricated coverage, comment-only traces, survivor evidence 관련 fix

겪은 문제:
- AI가 후보를 많이 만들 수 있어도, 사람이 모두 깊게 review하면 많은 test를 돌리기 어려웠다.
- test pass가 의미 있는 통과인지, silent pass인지, vacuous pass인지 구분해볼 수 있었다.
- evidence가 있어도 freshness, traceability, independent oracle을 함께 보는 편이 좋았다.
- 특히 "동작했다"와 "의도한 대로 구현됐다"를 구분하는 장치가 필요해 보였다.

도움이 된 구조:

```text
많은 후보 생성
-> compile/lint/test/checklist 자동 필터
-> AI self-review / gate-reviewer
-> 비교표와 risk 요약
-> intent-conformance check
-> 상위 후보만 사람 review
-> decision receipt
-> ontology/wiki 반영
```

발표 메시지:

> 사람은 모든 후보를 깊게 보기보다, 자동 검증과 AI 리뷰를 통과한 후보를 중심으로 보되, 마지막에는 의도 충족 여부를 확인하는 흐름을 둘 수 있다.

---

## 시행착오 5: 구현 결과를 다음 시도에 연결해보는 구조를 만들고 다듬었다

Evidence:
- 2026-05: SSOT-driven IP generation, per-IP git, workflow guide, SSOT preview, gates
- 2026-06: 설계 수렴 루프, locked design intent, requirement/obligation/contract/evidence/validation/decision
- IP workflow pack README: ROCEV path

```text
Requirement -> Obligation -> Contract -> Evidence -> Validation -> Decision
```

겪은 문제:
- 구현 결과만 남으면 "왜 그렇게 했는가"가 흐려지기 쉬웠다.
- test 결과만 남으면 "다음에는 무엇을 바꿔야 하는가"가 흐려지기 쉬웠다.
- review comment만 남으면 다음 AI-assisted turn의 context로 잘 재사용되지 않는 경우가 있었다.

도움이 된 구조:

```text
Failure
-> Cause
-> Affected requirement/spec/assumption
-> Fix
-> Validation evidence
-> Decision
-> Rule / Checklist / Skill
-> LLM Wiki page
-> Next AI context
```

발표 메시지:

> 실험이 많아질수록, 원인과 선택 이유를 남기는 방식이 다음 시도와 더 잘 연결되는 경우가 있었다.

재발 방지 관점:

| 반복되는 것 | 남길 자산 |
| --- | --- |
| 같은 log pattern | triage FAQ / known issue |
| 같은 실수 | rule / do-not-do checklist |
| 같은 확인 절차 | skill / workflow recipe |
| 같은 decision boundary | reviewer guide |
| 같은 evidence 부족 | validation checklist |
| 같은 개념 설명 | LLM Wiki page |

---

## 시행착오 6: 후보를 여러 개 볼 때는 작업 공간 분리가 도움이 될 수 있었다

Evidence:
- IP workflow pack wavefront policy: dependency-ready parallel execution, ownership lock, receipt, review_pending, handoff_pass
- IP workflow pack DSE worktree policy: candidate worktrees under isolated worktrees, product RTL/TB write-back 금지, copy-back은 exploration knowledge만 허용
- local development history 2026-05~06: per-IP git, branch/workflow/session isolation, worker/session scope fixes 반복

겪은 문제:
- 한 workspace에서 여러 시도를 섞으면 path, session, owner, filelist, evidence가 엉키기 쉬웠다.
- 병렬 실험은 좋지만, product artifact에 바로 섞이면 설계 기준이 흐려질 수 있다.

도움이 된 구조:

```text
main line
  -> worktree candidate A
  -> worktree candidate B
  -> worktree candidate C
  -> compare by same gate
  -> promote selected decision
  -> product RTL/TB update
```

발표 메시지:

> AI는 병렬 구현의 비용을 낮춰줄 수 있고, worktree는 병렬 실험을 분리해서 비교하는 데 도움이 될 수 있었다.

---

## 시행착오 7: 디테일 구현에 집중하다 보면 Architecture/PPA 질문이 늦어질 수 있다

IP workflow pack PPA principle:

```text
PPA is easier to reason about when architectural intent is visible early.
Synthesis works with the structure it receives.
```

IP workflow pack architecture option policy:

```text
Architecture exploration is derived evidence, not product decision by itself.
Tier-1 metrics are ranking proxies.
Product-defining decisions are human-only.
```

겪은 문제:
- AI에게 디테일 구현만 많이 시키면 빠른 코딩 도구처럼 쓰이기 쉬웠다.
- local bugfix loop가 빨라질수록 더 큰 구조적 질문을 놓치기 쉬웠다.
- 한 줄의 RTL을 어떻게 고칠지보다, critical path, pipeline boundary, resource sharing, state encoding, fanout, toggle, verification cost를 먼저 살펴보는 편이 도움이 되는 경우가 있었다.
- PPA를 synthesis 후처리로만 보면 앞단 architecture decision으로 돌아가는 경우가 있었다.
- 다만 회사의 현재 적용 범위에서는 이 영역을 demo 중심에 두지 않는다. 검증 evidence가 충분히 쌓인 뒤 연결할 확장 주제로 둔다.

도움이 된 구조:

```text
Core contract 정리
-> PPA intent 분리
-> architecture option A/B/C
-> cheap prototype / bench / worktree
-> metric + verification cost 비교
-> decision receipt
-> reversible option은 parameterize/generated form으로 유지
-> product RTL/TB implementation
```

질문 프레임:

| 질문 | 왜 architecture/PPA 질문인가 |
| --- | --- |
| critical path가 어디인가 | 한 cycle에 compare/mux/adder/decode가 쌓이는지 결정 |
| pipeline/register boundary가 도움이 되는가 | performance와 latency contract를 함께 바꿈 |
| resource를 공유할 것인가 복제할 것인가 | area와 timing을 tradeoff |
| high-fanout enable/reset/select가 있는가 | timing, power, reset strategy에 영향 |
| toggle이 큰 datapath는 언제 isolate할 것인가 | power intent가 RTL 구조에 들어감 |
| state encoding을 어떻게 할 것인가 | area/timing/debug/verification cost를 함께 바꿈 |

발표 메시지:

> Architecture/PPA 후보 비교는 매력적이지만 난도가 높다. 현재 세미나에서는 검증 loop를 먼저 안정화하고, 이 영역은 다음 단계로 둔다.

---

## 시행착오 8: 설계 수렴 루프를 둘 수 있었던 이유

IP workflow pack design-completion principle:

```text
RTL is one implementation of design intent.
Evidence helps; validation and decision complete the loop.
```

설계 수렴 루프에서 정리해본 관점:

| Layer | 역할 |
| --- | --- |
| Intake / Draft | 사용자의 압축된 요구를 바로 구현하지 않고 의미와 ambiguity로 보존 |
| Ontology / Design Intent | 요구/가정/계약/구조/검증 의도를 기준 정보로 정리 |
| Projection / Compile | worker가 original prose를 재해석하지 않게 generated packet 제공 |
| Readiness / Gates | 구현 전에 schema/quality/contract strength 확인 |
| Run / Orchestration | 긴 작업의 next action, stop/resume, active obligation 유지 |
| Wavefront | dependency-ready parallel work만 열기 |
| Dispatch / Receipt | subagent write authority와 결과를 경계 안에 묶기 |
| Evidence / Decision | test pass와 완료 판단을 구분 |

발표 메시지:

> 설계 수렴 루프는 RTL을 빨리 만들기 위한 장치라기보다, 검증 evidence와 설계 의도, 생성 산출물을 함께 관리하는 운영 구조로 볼 수 있었다.

---

## Slide Deck: 16-Slide Version

### Slide 1. Title

화면:
- AI 기반 검증 업무에서 고민해볼 지점들
- Verification first, Spec/RTL은 다음 단계

노트:
오늘 말하려는 것은 특정 도구 기능 소개라기보다, 검증 업무에 AI agent를 어떻게 안전하게 붙일지에 대한 이야기다. Spec 작성과 RTL 생성은 중요하지만 아직 회사에서 바로 agent 적용하기 어려운 영역이므로, 오늘은 검증 loop에서 시작해 그 결과가 나중에 Spec/RTL review로 어떻게 돌아갈 수 있는지에 초점을 둔다.

### Slide 2. Current Reality

화면:

| 구분 | 현재 현실 | 세미나 메시지 |
| --- | --- | --- |
| Verification | log, test, evidence 중심 | 바로 시작하기 좋음 |
| Spec | contract와 ambiguity가 중요 | agent가 결정하지 말고 드러내야 함 |
| RTL | agent 직접 적용은 아직 어려움 | 수정보다 review/근거 정리부터 |
| Learning | 실패가 흩어지기 쉬움 | rule/wiki/ontology로 남겨야 함 |

노트:
지금 회사에서 자연스러운 시작점은 Spec/RTL 자동 생성보다 검증 쪽으로 보인다. 검증 업무는 관찰 가능한 input과 evidence가 있고, 사람이 판단할 지점도 비교적 분리하기 쉽다. 그래서 메시지는 "AI가 RTL을 작성한다"보다 "검증 가능한 loop를 먼저 안정화해본다"로 잡는 편이 안전해 보인다.

### Slide 3. Thesis

화면:

```text
Verification input
-> Triage
-> Evidence
-> Next check
-> Human decision boundary
-> Ontology / LLM Wiki
-> Better next turn
```

노트:
검증 업무에 agent를 붙일 때 핵심은 답을 바로 내는 것이 아니라, 관찰된 실패를 분류하고, 근거를 연결하고, 다음 확인 지점과 사람이 판단할 지점을 나누는 것이다. 이 loop가 쌓이면 나중에 Spec/RTL review에도 돌아갈 수 있다.

### Slide 4. Evidence: Iteration History

화면:
- Brian local experiment, not company rollout evidence
- local development history: 4,657 commits
- AI agent workflow prototype path: 3,342 commits
- IP workflow pack: 86 commits

| Month | Commits | Movement |
| --- | ---: | --- |
| 2025-10 | 10 | AXI write/read generator 실험 시작 |
| 2025-11 | 64 | packet/header/error/mismatch 직접 구현 시행착오 |
| 2025-12 | 105 | memory, Verilog analysis, RAG, sub-agent, Plan mode 실험 |
| 2026-03 | 245 | spec navigation, skill routing, plan/todo 정리 |
| 2026-04 | 1,229 | tool/parser/streaming 안정화, generation/evidence 실험 확대 |
| 2026-05 | 1,929 | SSOT->RTL, todo/gate/evidence pipeline 확대 |
| 2026-06 | 1,072 | locked design intent, silent-pass hardening, ontology/evidence 기반 완료 판단 정리 |

노트:
이 history는 회사에서 Spec/RTL agent가 이미 적용됐다는 증거가 아니다. 많은 turn과 실패를 거치며 gate, evidence, review, memory가 왜 필요한지 드러난 로컬 시행착오 evidence로만 사용한다.

### Slide 5. Pain 1: Verification Can Surface Requirement Gaps

화면:
- failing log
- mismatch
- timing/handshake symptom
- missing assumption
- unclear acceptance condition

노트:
검증 실패는 단순히 bug report가 아니라 요구와 가정의 빈틈을 보여줄 수 있다. Agent가 여기서 할 일은 design intent를 추측해 고치는 것보다, 어떤 요구가 불명확한지, 어떤 evidence가 있는지, 어떤 decision이 필요한지 분리하는 쪽에 가까워 보인다.

### Slide 6. Pain 2: AI Workflow Can Add Speed And Failure Modes

화면:
- ReAct loop
- parser/tool call
- RAG/memory
- subagent
- context/compression
- stale state / hallucinated observation

노트:
이건 Spec/RTL 자체보다 AI 실행 환경 쪽 이슈에 가깝다. 검증 triage 속도를 높이더라도 loop control, context, evidence, stale state 문제를 함께 봐야 한다.

### Slide 7. Pain 3: Make Everything / Ask Everything 둘 다 문제가 있다

화면:

```text
1차: 의도만 전달 -> Agent가 빈칸을 마음대로 채움
2차: 모호하면 질문 -> 질문 폭주
3차: test pass 확인 -> 의도 충족 장치가 필요해 보임
4차: 같은 실수 반복 -> rule / skill / wiki / ontology가 도움
```

노트:
돌아보면 "의도만 전달한 것"도, "질문을 너무 다 받은 것"도 시행착오였다. 검증 agent는 모든 것을 만들거나 모든 것을 묻는 도구라기보다, evidence로 판단 가능한 것, 사람이 결정해야 할 것, intent-conformance를 확인해야 할 것을 나누고 배운 것을 다음 실행으로 되돌리는 도구로 다듬어볼 수 있다.

### Slide 8. Decision Boundary

화면:

| Decision Type | Handling |
| --- | --- |
| Product-defining / external contract | ask human |
| Repo-local fact | cite local evidence |
| Reversible internal choice | parameterize |
| Verification next check | propose with evidence |
| Architecture/PPA tradeoff | future topic, human-led |
| Measured tradeoff | selection rule + decision receipt |

노트:
이 표는 중간 정리로 쓸 수 있다. 사람에게 모든 질문을 던지지 않되, product contract가 조용히 바뀌지 않게 경계를 둔다.

### Slide 9. Practical Loop: Verification Evidence

화면:

```text
failing command / log
-> first evidence line
-> suspected area
-> related spec/test/RTL context
-> safe next check
-> human decision needed
```

노트:
세미나의 중심 demo는 이 정도가 적당해 보인다. Agent가 RTL을 고치는 장면보다, 검증 실패를 구조화하고 다음 확인을 제안하고 사람이 봐야 할 결정을 표시하는 장면이 더 현실에 맞을 수 있다.

### Slide 10. Use AI As A Verification Triage Assistant

화면:

```text
Input: lint / compile / sim / formal log
-> group failures
-> identify first meaningful evidence
-> link context
-> propose next check
-> write evidence summary
```

노트:
AI에게 "고쳐줘"라고 바로 시키면 위험하다. 먼저 "분류해줘, 근거를 찾아줘, 다음 확인을 제안해줘, 불확실한 결정은 표시해줘"라고 쓰는 편이 검증 업무에 맞다.

### Slide 11. Worktree Is For Later, Not The First Demo

화면:

```text
read-only triage
  -> plan-only
  -> small reviewed change
  -> validation evidence
  -> optional worktree for risky experiments
```

노트:
Worktree는 중요하지만 첫 메시지로 앞세우지 않는 편이 나아 보인다. 처음에는 read-only triage와 plan-only가 더 안전할 수 있다. 수정 후보가 생기거나 병렬 실험이 필요해질 때 worktree를 꺼내볼 수 있다.

### Slide 12. Review Can Also Be Layered

화면:

```text
Many findings
-> auto compile/lint/test
-> AI review
-> risk/evidence table
-> human reviews key decisions
```

노트:
검증에서는 review 비용이 여전히 중요하다. 사람은 모든 log line을 깊게 보기보다, agent가 정리한 evidence와 decision point를 중심으로 판단하는 흐름을 둘 수 있다.

### Slide 13. Learning Can Be Captured

화면:

```text
Failure
-> Cause
-> Affected requirement / assumption
-> Fix
-> Evidence
-> Decision
-> Rule / Skill
-> Ontology / LLM Wiki
```

노트:
검증 실패와 해결 과정을 남기면 다음 비슷한 실패를 더 빨리 다룰 수 있다. Ontology는 구조이고, LLM Wiki는 사람이 읽고 LLM이 다시 쓰는 기억 표면으로 볼 수 있다.

### Slide 14. Spec/RTL로 돌아가는 길

화면:

```text
Verification evidence
-> unclear requirement
-> missing assumption
-> test expectation
-> owner decision
-> Spec/RTL review item
```

노트:
Spec/RTL agent 적용은 어렵지만, 검증 evidence는 Spec/RTL 개선으로 돌아갈 수 있다. 이 연결을 만들면 검증 업무가 단순 후처리가 아니라 설계 품질을 높이는 feedback loop가 된다.

### Slide 15. Demo / Tomorrow's Action

화면:
1. 작은 verification task 하나를 고른다.
2. log, failing command, 관련 spec/test context를 준다.
3. Codex에게 failure group, first evidence, suspected area를 정리하게 한다.
4. safe next check와 human decision needed를 분리한다.
5. evidence summary와 unresolved assumption을 LLM Wiki/Ontology 후보로 남긴다.

노트:
처음부터 Spec/RTL 자동화로 가기보다, 작은 검증 task 하나를 닫아보고, 반복되면 rule/skill/FAQ로 내리는 방식이 좋아 보인다.

### Slide 16. Closing

화면:

```text
AI 적용의 첫 현실적 후보는 검증으로 보인다.
검증 loop에서 evidence와 decision boundary를 안정화하면,
그 결과가 나중에 Spec/RTL review로 돌아갈 수 있다.
```

노트:
AI는 검증 triage 속도를 올리고, gate는 추정과 검증을 나누고, ontology/wiki는 실패와 판단 기록을 다음 turn으로 되돌리는 데 도움이 될 수 있다. Spec/RTL 생성은 오늘의 현재 적용 사례가 아니라, 이 기반 위에서 조심스럽게 봐야 할 다음 단계다.

---

## 5-Minute Opening Script

오늘은 AI가 Spec과 RTL을 바로 만들어준다는 이야기를 하려는 것이 아닙니다. 오히려 회사 현실에서는 그 영역이 아직 쉽지 않습니다. Spec과 RTL에는 design intent, interface contract, timing, ownership, 검증 책임이 같이 얽혀 있기 때문에 agent가 조용히 잘못된 결정을 내리면 위험합니다.

그래서 현재 회사에서 더 현실적인 시작점은 검증 쪽이라고 볼 수 있습니다. 검증 업무에는 log, failing command, test result, waveform이나 report path, review comment처럼 agent가 읽고 정리할 수 있는 evidence가 있습니다. 그리고 agent가 직접 설계 결정을 내리기보다, 관찰된 실패를 분류하고, 첫 evidence line을 찾고, 다음 확인 지점을 제안하고, 사람이 판단할 지점을 표시하는 방식으로 시작해볼 수 있습니다.

제가 로컬에서 agent와 IP workflow를 만들며 겪은 시행착오도 이 방향으로 이어졌습니다. 처음에는 생성 자체에 관심이 갔지만, 많이 만들어내는 것만으로는 충분하지 않았습니다. 실제로는 loop control, stale state, hallucinated observation, silent pass, evidence freshness, review boundary 같은 운영 문제가 계속 보였습니다.

그 시행착오에서 얻은 메시지는 이 정도로 정리해볼 수 있습니다. AI를 먼저 자동 설계자로 놓기보다, 검증 가능한 업무 loop를 안정화하는 데 써보는 편이 안전해 보입니다. 검증 실패에서 요구의 모호함, assumption, owner decision, 추가 test 필요성을 분리하고, 그 결과를 wiki, rule, skill, ontology 같은 형태로 남기면 다음 검증과 Spec/RTL review에 다시 쓸 수 있습니다.

오늘 볼 흐름도 이 관점입니다. 첫째, 왜 Spec/RTL agent 적용은 조심스러운지 봅니다. 둘째, 검증 업무에서 agent가 할 수 있는 작은 역할을 봅니다. 셋째, log triage, evidence, next check, human decision boundary를 어떻게 남길지 봅니다. 마지막으로 이 기록이 나중에 Spec/RTL review와 설계 수렴으로 어떻게 이어질 수 있는지 이야기하겠습니다.

오늘의 메시지는 이 정도로 정리할 수 있습니다.

> 지금은 AI를 검증 loop의 triage, evidence 정리, next check 제안에 먼저 써보고, 그 결과를 나중에 Spec/RTL 개선으로 되돌리는 구조를 검토해볼 수 있습니다.

---

## Demo Candidate

작은 demo 하나를 보여줄 수 있다.

Demo setup:
- 작은 lint/compile/simulation failure log를 준비한다.
- 관련 spec/test/RTL context는 민감 정보 없이 추상화하거나 toy example로 둔다.
- AI에게 바로 RTL을 고치게 하지 않고, failure grouping, first evidence, suspected area, next check, human decision needed를 분리하게 한다.

Demo flow:

```text
Turn 1: log + failing command + context boundary 제공
Turn 2: failure group과 first evidence line 추출
Turn 3: suspected area와 관련 파일/테스트 후보 정리
Turn 4: safe next check와 rerun command 제안
Turn 5: human decision needed / do-not-infer 항목 표시
Turn 6: evidence summary 작성
Turn 7: 반복 가능하면 rule/skill/FAQ 후보로 분류
Turn 8: Ontology/LLM Wiki에 Failure/Evidence/Decision 후보 반영
```

보여줄 포인트:
- AI가 한 번에 고치는 장면보다, "관찰 -> 근거 -> 다음 확인 -> 사람 판단"으로 정리하는 장면이 더 안전하다.
- 검증 업무는 agent 적용의 첫 실전 영역 후보로 설명하기 좋다.
- Spec/RTL 수정은 demo의 중심이 아니라 follow-up decision으로 둔다.

---

## Q&A Short Answers

Q. 그러면 Spec/RTL 개발에도 바로 agent를 쓰자는 뜻인가?

A. 아니다. 현재 회사 적용의 중심은 검증 쪽이다. Spec/RTL은 design intent와 ownership이 커서 바로 자동화하기 어렵다. 대신 검증 evidence를 통해 Spec/RTL review item을 더 잘 만들 수 있다.

Q. 검증 업무에서 AI가 제일 먼저 할 수 있는 일은 무엇인가?

A. log triage, first evidence line 찾기, failure grouping, 관련 context 후보 찾기, safe next check 제안, human decision needed 표시가 현실적인 시작점으로 보인다.

Q. 사람 review는 어떻게 남겨야 하나?

A. 사람 review를 없애기보다는, agent가 evidence와 risk를 정리하고 사람이 product-defining decision과 owner judgment에 집중하는 방식으로 본다.

Q. PPA/architecture 후보 비교는 빼야 하나?

A. 완전히 빼기보다 "다음 단계"로 둔다. 현재 발표 중심은 검증이다. PPA/architecture는 검증 evidence와 decision boundary가 어느 정도 안정화된 뒤에 조심스럽게 연결할 주제다.

Q. 왜 Ontology도 같이 고민했나?

A. 검증 실패가 많아질수록 기록이 흩어진다. Failure, Cause, Evidence, Decision, Rule을 연결해두면 다음 비슷한 실패를 다룰 때 재사용하기 쉽다.

Q. LLM Wiki는 Ontology와 뭐가 다른가?

A. Ontology는 지식 구조이고, LLM Wiki는 사람이 읽고 LLM이 context로 쓰는 문서 표면이다. 둘이 같이 있으면 기록이 다음 AI-assisted turn으로 돌아오기 쉬워진다.

Q. Worktree는 왜 같이 보나?

A. 첫 demo의 중심은 아니다. 다만 수정 후보나 병렬 실험으로 넘어갈 때 main workspace와 product artifact를 보호하는 장치로 설명할 수 있다.

---

## Final Takeaways

1. 현재 회사 적용의 현실적인 시작점은 Spec/RTL 자동 개발보다 검증 업무로 볼 수 있다.
2. Spec/RTL agent 적용은 어렵고, design intent와 ownership 때문에 조심스럽게 다루는 편이 좋다.
3. 검증 log와 failing case는 요구의 빈틈과 assumption을 드러낼 수 있다.
4. AI는 log triage, first evidence, suspected area, next check 정리에 먼저 써볼 수 있다.
5. Agent가 수정 결정을 내리기보다 human decision needed를 잘 표시하는 것이 도움이 될 수 있다.
6. Review와 완료 판단은 evidence, freshness, traceability 기준으로 계층화해볼 수 있다.
7. Test pass만으로 끝내기보다 validation evidence와 decision을 함께 남기는 편이 좋아 보인다.
8. 반복 검증 패턴은 rule, skill, FAQ로 내릴 수 있다.
9. Ontology는 Failure, Cause, Evidence, Decision, Rule을 연결하는 데 도움이 될 수 있다.
10. LLM Wiki는 이 지식을 다음 AI-assisted turn의 context로 되돌리는 표면이다.
11. Worktree와 Architecture/PPA 탐색은 첫 demo보다 후속 확장 주제로 두는 편이 안전하다.
12. 검증 loop가 안정화되면 그 evidence가 Spec/RTL review와 설계 수렴으로 돌아갈 수 있다.
