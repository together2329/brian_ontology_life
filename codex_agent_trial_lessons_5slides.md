# Agent Workflow Trial Lessons: Executive 5-Slide Cut

작성일: 2026-07-07

목적: 임원 보고용 5장 압축본. 세부 구현보다 "AI agent를 실무에 붙일 때 어떤 운영 장치가 필요한가"를 빠르게 파악할 수 있게 구성한다.

---

## Slide 1. 핵심 메시지

### 화면 핵심
- AI agent 활용의 병목은 단순 생성 능력보다 운영 통제에 있었다.
- 시행착오를 통해 네 가지 관리 포인트가 보였다.
  - 의도 해석
  - 질문 범위
  - 의도 충족 검증
  - 재발 방지 학습
- 결론: Agent에게 모두 맡기거나 모두 묻게 하기보다, contract / evidence / option / learning loop로 운영하는 방향을 검토할 수 있다.

### 보고 멘트
이번 경험의 핵심은 "AI가 할 수 있느냐"보다 "어떻게 통제 가능한 업무 흐름으로 만들 것인가"에 가깝다. Agent는 빠르게 결과를 만들 수 있지만, 의도 해석, 질문량, 검증 기준, 학습 구조가 없으면 사람의 부담이나 품질 리스크가 커질 수 있었다.

---

## Slide 2. 시행착오 1-2: 맡기면 과해지고, 묻게 하면 많아진다

### 화면 핵심
| 시도 | 관찰된 현상 | 의미 |
| --- | --- | --- |
| 의도만 전달 | Agent가 빈칸을 자기 방식으로 채움 | 의도와 다른 결과가 나올 수 있음 |
| 모호하면 질문 | 질문이 과도하게 증가 | 사람이 병목이 될 수 있음 |

### 보고 멘트
처음에는 의도를 주면 agent가 알아서 채워줄 것이라 기대했다. 하지만 모호한 부분을 agent가 임의로 해석할 수 있었다. 반대로 모호한 것을 모두 질문하게 하면 안전해 보이지만, 사람이 모든 세부 판단을 떠안게 된다.

### 핵심 시사점
> 필요한 것은 더 많은 자율성이나 더 많은 질문이 아니라, 어떤 것은 agent가 진행하고 어떤 것은 사람이 판단할지 나누는 decision boundary다.

---

## Slide 3. 시행착오 3: Test pass와 의도 충족은 다를 수 있다

### 화면 핵심
- 결과가 생성되고 test가 통과해도, 의도대로 구현됐다고 단정하기는 어렵다.
- 확인해야 할 것은 pass/fail뿐 아니라 intent-conformance다.
- 필요한 evidence:
  - 어떤 intent를 만족하려 했는가
  - 그 intent가 어떤 check로 검증됐는가
  - 바뀌면 안 되는 동작은 유지됐는가
  - silent/vacuous pass 가능성은 없는가

### 보고 멘트
Agent 결과는 "동작한다"와 "의도대로 동작한다"를 구분해서 봐야 했다. 단순 test pass는 중요한 evidence지만, product intent를 만족했다는 충분한 설명은 아닐 수 있다. 그래서 requirement, test, evidence, decision이 연결된 검증 장치가 필요해 보였다.

### 핵심 시사점
> AI agent 결과의 품질 관리는 test 통과 여부보다, 의도와 evidence가 연결되는지까지 봐야 한다.

---

## Slide 4. 시행착오 4: 같은 실수를 줄이는 학습 구조가 필요하다

### 화면 핵심
- 한 번의 실행이 끝나도 배운 점이 남지 않으면 같은 실수가 반복될 수 있다.
- 실패와 판단을 재사용 가능한 자산으로 남기는 구조가 필요해 보였다.

| 반복되는 것 | 남길 자산 |
| --- | --- |
| 같은 실수 | Rule / do-not-do checklist |
| 같은 확인 절차 | Skill / workflow recipe |
| 같은 질문 | FAQ / reviewer guide |
| 같은 evidence 부족 | Validation checklist |
| 같은 개념 설명 | LLM Wiki / ontology link |

### 보고 멘트
Agent workflow는 한 번 성공시키는 것보다 반복 품질을 높이는 것이 중요해 보였다. 실패 원인, 판단 기준, 검증 evidence가 다음 실행에 재사용되지 않으면 같은 질문과 같은 실수가 반복될 수 있다.

### 핵심 시사점
> AI agent 도입은 prompt 사용이 아니라, 실패를 자산화하고 다음 실행에 반영하는 운영 체계로 봐야 한다.

---

## Slide 5. 권장 운영 방향: Contract는 잠그고, 나머지는 option으로 둔다

### 화면 핵심
| 사람이 먼저 잡는 편이 좋은 것 | Agent가 option으로 열어볼 수 있는 것 |
| --- | --- |
| PPA intent / spec | Reversible internal choice |
| Interface structure | Local implementation detail |
| Protocol / external contract | Generated option |
| Product-defining behavior | Parameter default |

### 보고 멘트
모든 세부사항을 질문으로 올리면 사람이 병목이 된다. 반대로 agent에게 모두 맡기면 의도와 다른 결정을 할 수 있다. 따라서 PPA spec, interface 구조, protocol처럼 product-defining contract는 사람이 먼저 잡고, 내부 구현 선택지는 parameterized generation으로 열어두는 방식이 현실적인 중간 지점으로 보였다.

### 최종 메시지
> Agent 운영의 핵심은 "얼마나 많이 자동화할 것인가"보다, 무엇을 contract로 잠그고 무엇을 option으로 열어둘지 정하는 것이다.

### 다음 액션 후보
- 작은 검증 task에서 이 운영 원칙을 먼저 적용해본다.
- 결과를 evidence summary, rule, skill 후보로 남긴다.
- 반복되는 판단 지점을 reviewer guide로 정리한다.
