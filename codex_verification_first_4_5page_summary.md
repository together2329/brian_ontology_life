# AI Verification-First Seminar: 4-5 Page Summary

작성일: 2026-07-07

목적: 회사 공유용 짧은 handout 또는 4-5장짜리 압축 발표본. 현재 회사의 AI 적용 초점이 검증 업무라는 전제를 중심에 둔다. Spec/RTL agent 적용은 아직 어렵고 조심스러운 다음 단계로 둔다.

---

## Page 1. 현재 현실: Spec/RTL 자동화보다 검증부터 시작해볼 수 있다

현재 회사에서 AI agent를 바로 적용하기 좋은 지점은 Spec 작성이나 RTL 생성보다 검증 업무다.

Spec/RTL 개발에는 design intent, interface contract, timing/PPA, ownership, 검증 책임이 같이 얽혀 있다. Agent가 이 영역에서 조용히 잘못된 결정을 내리면 설계 의도나 product contract가 바뀔 수 있다. 그래서 "AI가 RTL 설계자를 대체한다"는 식의 메시지는 현재 상황에서는 조심스럽게 다루는 편이 좋아 보인다.

반면 검증 업무는 agent를 붙여보기 상대적으로 수월한 후보로 보인다. Input과 output이 비교적 명확하기 때문이다.

- lint / compile / simulation / formal log
- failing command
- first failing line 또는 first meaningful evidence
- 관련 spec, test, RTL context
- rerun command
- pass/fail marker
- review comment

따라서 세미나 메시지는 다음 한 문장 정도로 잡아볼 수 있다.

> 지금은 AI를 검증 loop의 triage, evidence 정리, next check 제안에 먼저 써보고, 그 결과를 나중에 Spec/RTL 개선으로 되돌리는 구조를 검토해볼 수 있다.

---

## Page 2. 검증 업무에서 Agent가 먼저 할 수 있는 일

검증 agent의 첫 역할은 "고쳐주는 것"보다 "정리해주는 것"에 가깝게 잡아볼 수 있다.

이 관점은 네 가지 시행착오에서 나왔다.

```text
1차 시도: 의도만 전달했다.
-> Agent가 빈칸을 자기 방식으로 채우고 마음대로 만들었다.

2차 시도: 모호한 부분은 묻게 했다.
-> 너무 많은 질문이 쏟아져서 사람이 모두 판단해야 하는 부담이 생겼다.

3차 시도: 의도한 대로 구현됐는지 확인하려 했다.
-> test pass만으로는 부족할 수 있었고, 의도 충족을 확인하는 장치가 필요해 보였다.

4차 시도: 이전 결과에서 배워 개선해나가려 했다.
-> 같은 실수를 줄이기 위해 기록, rule, skill, wiki, ontology가 도움이 될 수 있어 보였다.

정리된 방향:
-> Agent가 모든 것을 만들지도, 모든 것을 묻지도 않게 한다.
-> Evidence로 판단 가능한 것과 사람이 결정할 부분을 나눠본다.
-> "동작했다"와 "의도대로 구현됐다"를 구분한다.
-> 실패와 판단을 다음 실행의 context로 되돌린다.
```

가장 안전한 시작점은 read-heavy triage다.

```text
failing command / log
-> failure group
-> first meaningful evidence
-> suspected area
-> related spec/test/RTL context
-> safe next check
-> human decision needed
-> evidence summary
```

예를 들어 compile error라면 agent가 바로 코드를 수정하기보다 다음을 정리한다.

- 첫 번째 의미 있는 실패 지점은 어디인가
- 같은 root cause로 보이는 error가 몇 개인가
- generated file, missing dependency, include path, syntax, interface mismatch 중 어디에 가까운가
- 관련 파일이나 test 후보는 무엇인가
- rerun하면 확인할 수 있는 command는 무엇인가
- 사람이 결정할 ownership/design intent 항목은 무엇인가

SDC나 lint warning도 비슷하다. Agent가 constraint 의미를 임의로 바꾸는 것은 조심하는 편이 좋다. 대신 warning을 분류하고, 위험도와 reviewer 판단이 필요한 지점을 표시하고, evidence와 rerun plan을 남기는 쪽이 안전한 시작점으로 보인다.

핵심은 다음 경계다.

```text
Agent can:
- classify
- summarize evidence
- suggest safe next check
- prepare review material

Agent should not silently:
- infer design intent
- change constraint rationale
- decide product contract
- accept warning without owner judgment
```

---

## Page 3. Decision Boundary: 무엇은 agent가 하고, 무엇은 사람이 봐야 하나

검증 업무에서도 모든 질문을 사람에게 올리면 agent workflow가 느려질 수 있다. 반대로 agent가 모든 결정을 내리면 위험해질 수 있다. 그래서 decision type을 나누는 표가 도움이 된다.

핵심 lesson은 질문의 양을 늘리는 것이 아니라 질문의 질을 높이는 것이다.

- Agent가 마음대로 만든다: design intent가 조용히 바뀔 수 있다.
- Agent가 전부 물어본다: 사람의 판단 부담이 폭증한다.
- Agent가 test pass만 보여준다: 정말 의도한 대로 구현됐는지 알기 어렵다.
- Agent가 이전 실패를 잊는다: 같은 실수와 같은 질문이 반복된다.
- Agent가 잘 나눈다: evidence check는 진행하고, product-defining decision과 intent-conformance 판단만 사람에게 올리며, 배운 것은 다음 실행에 재사용한다.

질문 폭주를 줄이는 practical rule은 다음처럼 둘 수 있다.

```text
사람이 먼저 잠그는 편이 좋아 보이는 것:
- PPA intent/spec
- external interface structure
- protocol/contract
- product-defining behavior

질문 대신 열어둘 수 있는 것:
- reversible internal choice
- local implementation detail
- generated option
- parameter default
```

즉 최소한의 PPA spec과 interface 구조가 맞다면, 모든 세부 질문을 사람에게 던지기보다 parameterized generation으로 후보를 열어두는 방식을 검토해볼 수 있다.

| Decision Type | Handling | 이유 |
| --- | --- | --- |
| Product-defining / external contract | 사람에게 질문 | contract가 조용히 바뀌면 안 됨 |
| Repo-local fact | local evidence 인용 후 agent 정리 가능 | 파일, log, command로 확인 가능 |
| Verification next check | evidence와 함께 제안 | rerun/check는 비교적 안전 |
| Reversible internal choice | parameterize 또는 generated option으로 유지 | 질문 폭주를 줄이고 나중에 되돌릴 수 있음 |
| Architecture/PPA tradeoff | future topic, human-led | 현재 세미나 demo 범위 밖 |
| Measured tradeoff | metric + selection rule + decision receipt | 판단 기준이 남아야 함 |
| Unknown direct-impact decision | human decision needed | 추정으로 진행 금지 |

이 표를 쓰면 "AI가 어디까지 할 수 있나"라는 질문에 안정적으로 답할 수 있다.

세미나에서는 특히 다음 문장을 반복해볼 수 있다.

> Agent의 좋은 답은 확신하는 답이라기보다, evidence로 판단 가능한 것과 사람이 결정할 것을 잘 나눈 답에 가까워 보인다.

---

## Page 4. Evidence를 남겨야 다음 검증과 Spec/RTL review로 돌아간다

검증 실패는 단순한 bug report가 아니다. 반복해서 쌓이면 Spec과 RTL의 가정이 어디서 충돌하는지 보여주는 evidence가 된다.

따라서 test pass만 보고 끝내면 부족할 수 있다. 특히 AI가 만든 결과는 "무언가 동작한다"와 "처음 의도한 대로 구현됐다"를 분리해서 보는 편이 좋다. 최소한 다음 구조를 남겨볼 수 있다.

```text
Failure
-> Cause
-> Affected requirement / assumption
-> Fix or next check
-> Evidence
-> Validation
-> Decision
-> Intent conformance note
-> Rule / Skill / FAQ
-> LLM Wiki / Ontology
```

의도 충족을 확인하는 장치는 다음 질문으로 만들 수 있다.

- 어떤 requirement 또는 intent를 만족하려 했나
- 그 intent가 어떤 observable check로 바뀌었나
- 이 evidence가 정말 그 intent를 검증하나, 아니면 단순히 실행만 된 것인가
- silent pass, vacuous pass, fabricated coverage 가능성은 없는가
- 바뀐 동작과 바뀌지 말아야 할 동작이 각각 확인됐나
- 사람이 판단할 product-defining decision이 남아 있나

이 구조가 있으면 같은 실패가 다시 나왔을 때 agent가 과거 기록을 context로 쓸 수 있다. 또한 단순 log 요약을 넘어 다음 개선으로 이어진다.

- 반복 warning -> lint triage guide
- 반복 compile failure -> setup/checklist 개선
- 반복 simulation mismatch -> test expectation 정리
- 반복 ambiguity -> Spec review item
- 반복 human decision -> owner/reviewer boundary 정리

재발 방지를 위한 asset화 기준은 간단하다.

| 반복되는 것 | 남길 자산 |
| --- | --- |
| 같은 log pattern | triage FAQ / known issue |
| 같은 실수 | rule / do-not-do checklist |
| 같은 확인 절차 | skill / workflow recipe |
| 같은 decision boundary | reviewer guide |
| 같은 evidence 부족 | validation checklist |
| 같은 개념 설명 | LLM Wiki page |

Ontology와 LLM Wiki의 역할은 다르게 설명하면 이해가 쉬워진다.

- LLM Wiki: 사람이 읽고 agent가 context로 다시 쓰는 문서 표면
- Ontology: Failure, Cause, Evidence, Decision, Rule, Owner, TestCase를 연결하는 구조

짧게 말하면:

```text
LLM Wiki = 읽는 기억
Ontology = 연결되는 기억
Evidence = 다시 쓸 수 있는 근거
```

---

## Page 5. Demo와 세미나 후 첫 Action

첫 demo는 작아야 한다. Spec/RTL 자동 생성 demo보다 검증 중심 demo가 안전하고 메시지도 분명하다.

권장 demo:

```text
Input:
- 작은 lint/compile/simulation failure log
- failing command
- 민감 정보 제거된 관련 context

Agent task:
1. failure group 정리
2. first evidence line 찾기
3. suspected area 정리
4. safe next check 제안
5. human decision needed 표시
6. evidence summary 작성
7. 반복 가능하면 rule/skill/FAQ 후보로 분류
```

세미나 후 참석자에게 줄 첫 action도 작게 잡는다.

1. 본인 repo/project에서 작은 verification task 하나를 고른다.
2. log, failing command, 관련 spec/test context를 준비한다.
3. Codex에게 바로 수정시키지 말고 triage와 evidence summary를 시킨다.
4. safe next check와 human decision needed를 분리하게 한다.
5. 결과를 shared FAQ, rule, skill 후보로 남긴다.

마무리 메시지:

> AI 적용의 첫 현실적 후보는 검증으로 볼 수 있다. 검증 loop에서 evidence와 decision boundary를 안정화하면, 그 결과가 나중에 Spec/RTL review와 설계 수렴으로 돌아갈 수 있다.

---

## 4-Page Version으로 줄일 때

4페이지로 줄여야 하면 Page 4와 Page 5를 합친다.

권장 4페이지 구성:

1. 현재 현실: Spec/RTL 자동화보다 검증부터 시작해볼 수 있다.
2. 검증 업무에서 Agent가 먼저 할 수 있는 일.
3. Decision Boundary: 무엇은 agent가 하고, 무엇은 사람이 봐야 하나.
4. Evidence loop와 demo/first action.
