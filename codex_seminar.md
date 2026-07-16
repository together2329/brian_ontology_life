# Codex Seminar Deck Draft

목적: 이 문서는 PowerPoint로 옮기기 위한 Codex 세미나 원고다. 각 슬라이드는 제목, 화면에 넣을 핵심 bullet, 발표자 노트, 추천 시각화로 구성한다.

작성 기준:
- 로컬 research note에서 확인한 세미나 준비 맥락, 회사 도입 지원 흐름, 2개월 asset capture 운영 아이디어를 회사 공유용 표현으로 추상화한다.
- 공식 Codex manual 확인 항목: Codex app/CLI, Plan mode, AGENTS.md, skills, worktrees, app-server, subagents, open-source 범위
- 웹 리서치 보강 항목: OpenAI Codex/Agent improvement loop, Google OKF, Obsidian Bases, Palantir Ontology/AIP/Foundry/Apollo, Anthropic Agent Skills/Artifacts, Microsoft Copilot PowerPoint, LazyCodex
- 회사 공유 전에는 내부 프로젝트명, DRM 자료, repo path, 개인 기록을 반드시 검토하고 제거한다.

웹 리서치 결론:
- Codex 운영법은 OpenAI 공식 문서 기준으로 설명한다. 특히 prompt는 Goal/Context/Constraints/Done when 구조, 어려운 task는 Plan mode, 반복 규칙은 AGENTS.md, 반복 workflow는 Skills로 정리한다.
- OKF는 "새 플랫폼"이 아니라 markdown + YAML frontmatter 기반의 open knowledge format이다. 세미나에서는 회사 지식을 큰 DB로 바로 밀어 넣기보다 OKF-style 파일과 Obsidian/Base view로 시작하는 것이 현실적이다.
- Palantir 자료는 ontology를 단순 semantic layer가 아니라 data, logic, action, security를 통합한 decision/operation system으로 설명한다. 이 관점은 SoC-on-ontology 메시지와 잘 맞는다.
- Microsoft Copilot과 Anthropic 자료는 문서/발표자료 생성이 단순 prompt가 아니라 app-native action, source structure, template/style, review/iteration workflow로 이동하고 있음을 보여준다.
- LazyCodex는 공식 Codex 기능 설명이 아니라 complex codebase harness 참고 사례다. 세미나에서는 공식 Codex primitive로 재해석해서 소개한다.

리서치 보강 원칙:
- 본문 슬라이드는 live deck으로 바로 설명할 수 있게 만들고, Appendix는 source map, template, backup/Q&A 용도로 둔다.
- 공식 Codex claim은 OpenAI Codex manual과 developers.openai.com 문서 기준으로만 말한다.
- OKF/Obsidian/Palantir/Microsoft/Anthropic/LazyCodex는 "비교 참고"로만 쓰고, 회사가 해당 제품을 도입해야 한다는 주장으로 말하지 않는다.
- RTL/IP 예시는 private repo path, DRM raw text, unreleased design detail 없이 log type, evidence type, workflow shape만 보여준다.
- 현재 회사 적용 초점은 검증 업무다. Spec/RTL agent 개발은 아직 본격 적용 전이고 난도가 높으므로, 본문 demo와 첫 action은 lint/compile/simulation/formal log triage, evidence 정리, review planning 중심으로 둔다.

발표 narrative spine:
1. 문제 인식: AI가 코드를 "대신 써주는" 시대가 아니라, 검증 가능한 작업 loop를 빠르게 돌리는 시대로 넘어간다.
2. 철학: Codex adoption의 본질은 prompt trick이 아니라 operating model이다. Context, rule, permission, plan, validation, review, artifact, feedback이 연결되어야 한다.
3. 기본기: 처음에는 app/CLI/IDE surface, `/status`, `/plan`, prompt contract, AGENTS.md, review를 익힌다.
4. 안전한 첫 적용: RTL/IP에서는 read-heavy triage, SDC/lint/compile/sim log 분석, evidence checklist부터 시작한다.
5. 고급 운영: worktree, subagent, custom agent, app-server, MCP, skill/plugin은 "많이 쓰는 기능"이 아니라 복잡도가 올라갈 때 쓰는 운영 장치다.
6. 실제 연동: 개인 prompt를 팀 자산으로 바꾸려면 guide, rule, skill, demo, FAQ, knowledge object, evidence pattern으로 남긴다.
7. 최종 메시지: 2개월 Codex window의 성공 기준은 사용량이 아니라 재사용 가능한 workflow package와 SoC Knowledge asset이다.

발표자 운영 원칙:
- 각 파트가 끝날 때마다 "그래서 내일 무엇을 하면 되는가"를 한 문장으로 연결한다.
- 기능명은 목적 뒤에 소개한다. 예: "위험을 줄이기 위해 Plan mode를 쓴다", "병렬 실험을 격리하기 위해 worktree를 쓴다".
- live demo는 작은 성공을 보여주고, 깊은 기능은 Appendix/Q&A로 보낸다.

60분 live deck cut:
| 구간 | 사용할 슬라이드 | 청중이 느껴야 할 것 | 연결 멘트 |
|---|---|---|---|
| Opening | 1-5 | "이건 도구 소개가 아니라 업무 방식 전환이다" | Codex adoption은 prompt 모음이 아니라 operating model이다. |
| Basic operation | 6-12 | "오늘 바로 켜고 안전하게 시작할 수 있다" | surface와 command를 알았으면, 이제 반복 규칙을 팀 문서로 내려야 한다. |
| Team operating model | 13-18 | "좋은 결과는 재현 가능한 규칙과 handoff에서 나온다" | workflow가 반복되면 skill이 되고, 일이 커지면 worktree와 handoff가 필요해진다. |
| Advanced orchestration | 19-23 | "고급 기능은 복잡도가 올라갈 때 쓰는 운영 장치다" | subagent/app-server/open-source 이야기는 도구 자랑이 아니라 확장 경계 설명이다. |
| Practical RTL/IP use | 24-26 | "내 업무에서는 검증 중심 read-heavy triage부터 시작하면 된다" | 작은 verification demo가 성공하면 다음 질문은 이 결과를 어떻게 지식 자산으로 남길 것인가다. |
| Knowledge and integration | 27-34 | "Codex output은 사라지면 안 되고, 지식 구조로 승격되어야 한다" | 지식 구조가 생기면 2개월 rollout은 사용량이 아니라 asset capture program이 된다. |
| Rollout close | 35-43 | "내일 할 첫 행동과 2개월 후 남길 자산이 보인다" | 오늘의 첫 action은 작은 read-only task, 첫 자산은 FAQ와 guide다. |

Appendix로 보낼 것:
- App Server JSON-RPC 상세, custom agent TOML 세부 필드, Palantir 제품별 상세 비교, OKF spec 세부 항목, LazyCodex command 목록은 Q&A나 후속 세션에서 다룬다.
- 60분 발표에서는 "왜 필요한가"와 "언제 꺼내는가"만 말한다.

---

## Slide 1. Codex를 왜 지금 봐야 하는가

### 화면 핵심
- Codex는 단순 채팅 도구가 아니라, 코드와 문서를 읽고 수정하고 검증하는 agent workflow 도구다.
- 회사에 Codex가 들어오면 개인 사용법보다 더 중요한 것은 팀이 반복 가능한 workflow를 만드는 것이다.
- 이번 세미나의 목표는 "한 번 써보기"가 아니라 "실제 RTL/IP 업무에 안전하게 붙이는 방법"을 잡는 것이다.
- 오늘의 관점: "AI가 대신한다"가 아니라 "사람이 검증 가능한 loop를 더 빨리 돈다".

### 발표자 노트
이번 세미나는 Codex 기능 나열이 아니다. 핵심은 Codex를 어떻게 실무 workflow에 넣을지다. AI 도구는 처음에는 신기해서 이것저것 시도하게 되지만, 회사 업무에서는 결국 재현성, 검증, 보안, 책임, 산출물이 중요하다. 그래서 오늘의 관점은 "Codex에게 뭘 시키면 잘하나"가 아니라 "Codex가 실제 업무 품질에 도달하게 만들려면 어떤 운영 장치가 필요한가"다.

몰입용 연결 멘트:
처음 5분 동안은 기능을 잠깐 잊고, 우리가 왜 이 도구를 업무 시스템으로 봐야 하는지부터 잡는다. Codex를 잘 쓰는 사람은 prompt를 많이 아는 사람이 아니라, context를 주고, 위험을 분리하고, evidence를 확인하고, 결과를 다음 workflow 자산으로 남기는 사람이다.

### 추천 시각화
- 왼쪽: "Chat / one-shot prompt"
- 오른쪽: "Workflow / context / rules / validation / assets"
- 가운데 화살표: "도구 사용 -> 업무 시스템"

---

## Slide 2. 오늘의 결론

### 화면 핵심
- AI Agent 도입은 prompt skill 문제가 아니라 quality system 문제다.
- 먼저 원하는 품질 threshold를 정하고, 그 다음 token, tool call, 시간, attempt를 줄인다.
- LLM Wiki는 설명을 잘하고, Ontology는 일을 굴린다.
- 좋은 skill은 작은 실제 task를 성공시킨 뒤 workflow를 정제해서 만든다.
- 2개월 Codex window는 사용량을 태우는 기간이 아니라 자산을 남기는 기간이다.
- 오늘 한 문장: Codex adoption = 검증 가능한 작업 loop를 팀 자산으로 만드는 일

### 발표자 노트
이 문장을 오늘 전체 세미나의 기억 포인트로 가져가면 된다. 많은 사람이 AI를 "프롬프트를 잘 쓰면 되는 것"으로 이해한다. 하지만 실제 엔지니어링에서는 프롬프트보다 더 중요한 것이 있다. 결과가 맞는지 확인하는 방법, 실패했을 때 무엇을 기록할지, 반복 작업을 어떻게 skill로 만들지, 여러 사람이 쓸 수 있게 어떻게 guide와 rule을 남길지다.

연결 멘트:
이 결론을 먼저 말하고 시작하면 뒤의 기능들이 흩어지지 않는다. `/plan`, AGENTS.md, skill, worktree, subagent, MCP는 각각 따로 외울 기능이 아니라 이 한 문장을 실행하기 위한 부품이다.

### 추천 시각화
- 5개 메시지를 카드가 아니라 가로 bar로 배치
- 각 bar에 작은 icon: 품질, 비용, 지식, skill, 자산

---

## Slide 3. 현재 상황과 세미나 배경

### 화면 핵심
- 2026-06-12 Cursor 세미나를 성공적으로 진행했다.
- 다음 단계로 Codex 세미나가 예정되어 있다.
- 예상 audience: RTL/design engineers, AI Transformation 활동가, engineering lead
- 회사 전체로는 약 70~80명의 개발자가 Codex를 사용할 수 있는 상황을 고려해야 한다.
- planned package: rule, skill, demo, guide document

### 발표자 노트
Cursor 세미나는 이미 좋은 신뢰 자산이다. "Brian이 AI를 잘 쓴다"는 인식이 생긴 상태에서, Codex 세미나는 더 실무적인 전환점이 되어야 한다. 단순히 "이 명령어를 쓰세요"가 아니라, RTL/IP 엔지니어가 실제로 겪는 SDC 정리, lint triage, compile/simulation 실패 분석, 문서화, evidence 정리 같은 업무에 어떻게 연결할지 보여줘야 한다.

### 추천 시각화
- Timeline: Cursor seminar success -> Codex rollout -> 2-month asset window -> SoC Knowledge

---

## Slide 4. 세미나 범위: 한 번의 강의인가, 프로그램인가

### 화면 핵심
- 압축판: 1~3회, setup과 core demo 중심
- 현실적인 세미나 시리즈: 10~12회, 실무 적용과 Q&A 포함
- full asset backlog: 15~18회, guide/rule/skill/demo/FAQ/knowledge graph까지 자산화

### 발표자 노트
우리가 다루고 싶은 주제는 매우 많다. Codex setup, Plan mode, AGENTS.md, rules, skills, hooks, MCP, worktree, subagent, LLM/RAG, OKF, Obsidian, Interactive HTML, SoC Knowledge Graph, waveform/MCP, UVM/Verilator까지 한 시간에 담기 어렵다. 그래서 첫 세미나는 압축해서 신뢰와 방향을 만들고, 이후에는 시리즈와 자산화 backlog로 분리하는 것이 현실적이다.

### 추천 시각화
- 3단 피라미드: compressed intro / seminar series / asset backlog

---

## Slide 5. 첫 세미나의 권장 구성

### 화면 핵심
1. 왜 Codex인가
2. 철학: prompt가 아니라 operating model
3. Basic: app/CLI, `/status`, prompt contract, Plan mode
4. Team rule: AGENTS.md, review, permission boundary
5. Practice: 작은 검증 중심 RTL/IP task demo
6. Advanced: worktree, subagent, skill/plugin, app-server/MCP
7. Integration: issue -> evidence -> knowledge asset
8. 2개월 asset capture 방식

### 발표자 노트
첫 세미나에서는 욕심을 줄여야 한다. 모든 것을 설명하려고 하면 핵심이 흐려진다. 참석자가 당장 가져가야 할 것은 네 가지다. 첫째, Codex는 어디에서 어떻게 쓰는가. 둘째, 위험한 변경을 막으려면 plan과 review를 어떻게 거치는가. 셋째, RTL/IP 업무에서 어떤 작은 task부터 붙일 수 있는가. 넷째, 개인 시행착오를 팀 자산으로 어떻게 남길 것인가.

발표 흐름:
기본 조작을 먼저 보여주되, 기능 리스트처럼 흘러가면 안 된다. 각 기능은 한 문장으로 연결한다. "위험한 변경을 막기 위해 Plan mode", "반복 규칙을 잊지 않기 위해 AGENTS.md", "후보 접근을 분리하기 위해 worktree", "반복 성공을 팀에 나누기 위해 skill"이라는 식으로 목적이 먼저 나오게 한다.

### 추천 시각화
- 8-step flow diagram

---

## Transition. Basic에서 Operating Model로

### 발표자 노트
여기부터는 "Codex를 켜는 법"이 아니라 "Codex가 우리 방식으로 일하게 만드는 법"이다. 먼저 surface와 command를 잡고, 바로 이어서 prompt, Plan mode, AGENTS.md로 넘어간다. 이 순서를 지키면 참석자는 기능을 외우는 것이 아니라 작업을 안전하게 만드는 구조를 이해하게 된다.

---

## Slide 6. Codex surface map

### 화면 핵심
- CLI: terminal-first local repository workflow
- IDE extension: editor context와 함께 코드 이해/수정
- Codex app: thread, worktree, diff, terminal, automation, artifact workflow를 다루는 desktop surface
- Cloud thread: GitHub 기반 remote/parallel work
- App Server / SDK: 제품 통합이나 자동화가 필요한 경우
- 선택 기준: "어디서 쓰는가"보다 "검증과 review evidence가 어디에 남는가"로 판단한다.

### 발표자 노트
Codex를 하나의 화면으로만 이해하면 활용 폭이 줄어든다. CLI는 terminal workflow에 강하고, IDE extension은 editor context에 강하다. Codex app은 여러 thread와 worktree를 관리하면서 planning, review, artifact 확인을 하기 좋다. 회사 rollout에서는 개인 취향보다 업무 종류에 맞는 surface 선택이 중요하다.

리서치 보강:
- OpenAI 공식 문서 기준 surface map은 app, CLI, IDE extension, cloud/web, app-server/SDK, GitHub review/action으로 나눌 수 있다.
- app은 parallel thread, worktree, diff/review, terminal, automation을 묶는 local orchestration surface로 설명한다.
- CLI는 terminal-first local repo 작업과 automation에, IDE extension은 open file/editor context가 중요한 작업에, cloud는 isolated parallel work에 맞다.
- App Server와 SDK는 일반 세미나의 시작점이 아니라 thread/turn primitive를 제품이나 내부 tool에 붙일 때의 고급 통합 옵션이다.

### 추천 시각화
- Surface별 표: 사용 장면 / 장점 / 주의점

---

## Slide 7. Codex app의 핵심 가치

### 화면 핵심
- 여러 project와 thread를 한 곳에서 관리
- Local / Worktree / Cloud mode 선택
- diff panel과 built-in Git tool로 변경 검토
- integrated terminal로 test, lint, build 확인
- in-app browser, document/PPT preview, skills, automation 연결
- 핵심 framing: "chatbot"이 아니라 reviewable agent workspace

### 발표자 노트
Codex app은 단순 채팅창이 아니다. 한 프로젝트에서 여러 thread를 관리하고, worktree로 변경을 분리하고, diff를 보며 review하고, terminal output을 agent가 다시 참고하게 할 수 있다. 특히 RTL/IP 업무에서는 build, lint, simulation log가 중요하므로 terminal과 diff를 같은 workflow 안에서 보는 것이 크다.

리서치 보강:
- RTL/IP 업무에서는 답변 텍스트보다 evidence loop가 중요하다. app에서 thread, worktree, diff, terminal output을 한 workflow로 묶으면 "무엇을 바꿨고, 무엇으로 확인했는가"를 추적하기 쉽다.
- Worktree mode는 여러 후보 approach를 나눠 실험할 때 유용하지만, 같은 파일을 여러 thread가 동시에 수정하는 구조는 피해야 한다.

### 추천 시각화
- App surface mock: Thread list / diff / terminal / task sidebar

---

## Slide 8. CLI slash command 기본 세트

### 화면 핵심
- `/status`: model, approval, writable root, context 상태 확인
- `/plan`: 구현 전 계획 모드
- `/review`: 변경 사항 review
- `/diff`: 현재 변경 확인
- `/compact`: 긴 대화를 요약해 context 확보
- `/resume`, `/fork`, `/clear`: session continuity 관리
- `/permissions`: 승인/권한 정책 조정
- `/skills`: task-specific skill 사용

### 발표자 노트
처음부터 모든 slash command를 외울 필요는 없다. 세미나에서는 "운영에 필요한 최소 command"만 잡으면 된다. 특히 `/status`, `/plan`, `/review`, `/diff`, `/compact`는 엔지니어링 안전성과 직결된다. `/resume`, `/fork`는 thread continuity를 설명할 때 중요하고, `/permissions`는 sandbox와 approval을 잘못 풀지 않게 하는 안전 장치다.

### 추천 시각화
- "기본 조작", "안전/검증", "연속성" 세 그룹으로 command 분류

---

## Slide 9. 좋은 prompt의 기본 구조

### 화면 핵심
- Goal: 무엇을 바꿀 것인가
- Context: 어떤 파일, 로그, 문서, 예시가 중요한가
- Constraints: 지켜야 할 convention, 안전 규칙, 금지 사항
- Done when: 완료 조건, test, review 기준
- Output format: 사람이 review할 수 있는 evidence 형식

### 발표자 노트
공식 best practice에서도 prompt에 goal, context, constraints, done condition을 넣는 것이 효과적이라고 설명한다. 특히 회사 업무에서는 "대충 해줘"가 아니라 "무엇이 끝난 상태인지"를 명확히 해야 한다. Codex가 검증할 수 있는 작업일수록 품질이 올라간다.

웹 리서치 보강:
- OpenAI Codex best practice는 큰/복잡한 repo에서 "right task context"와 clear structure가 가장 큰 unlock이라고 설명한다.
- 이 구조는 RTL/IP 업무에 그대로 맞는다. 로그, spec, guide, failing command, expected evidence가 prompt context로 들어가야 한다.
- prompt는 긴 설명문이 아니라 실행 계약서다. `Goal / Context / Constraints / Output / Validation`을 고정하면 Codex output이 review 가능한 형태로 안정화된다.
- RTL/IP prompt에는 "design intent를 추정하지 말고, 불확실하면 human decision needed로 표시하라"를 명시해야 한다.

### 화면 예시
```text
Goal: example block의 SDC warning triage open issue를 정리해줘.
Context: docs/sdc_notes.md, logs/dc_latest.log, current failing check.
Constraints: 기존 constraint 의도를 임의로 바꾸지 말고, 모르는 것은 질문해.
Output: Issue / Evidence / Risk / Human decision needed / Next check 형식.
Done when: 변경 파일 목록, risk, rerun command, evidence를 요약해줘.
```

### 추천 시각화
- Prompt input template 화면

---

## Slide 10. Plan mode를 먼저 써야 하는 순간

### 화면 핵심
- task가 크거나 애매할 때
- 어떤 파일을 건드릴지 모를 때
- 실패 비용이 큰 업무일 때
- 여러 접근법을 비교해야 할 때
- demo 전 risk와 fallback을 정해야 할 때
- Plan output은 implementation 전 review checklist가 되어야 한다.

### 발표자 노트
Plan mode는 "느리게 가기"가 아니라 "잘못 빨리 가는 것을 막기" 위한 장치다. RTL/IP 업무에서는 작은 변경도 의미가 크다. 설계 의도, interface contract, 검증 기준, owner 판단이 필요한 영역은 agent가 추측해서 고치면 위험하다. 먼저 계획을 만들고, 파일 범위와 검증 방법을 정한 뒤 실행해야 한다.

웹 리서치 보강:
- OpenAI 문서는 복잡하거나 애매하거나 설명하기 어려운 task에서는 Codex에게 먼저 plan을 요청하라고 권장한다.
- Plan mode는 Codex가 context를 모으고, 질문하고, 구현 전 더 강한 계획을 만드는 단계다.
- 좋은 plan은 likely files, assumptions, validation command, fallback path, human decision point를 포함해야 한다.
- Goal mode와 Plan mode를 혼동하지 않는다. 불명확한 문제는 먼저 `/plan`으로 모양을 잡고, 오래 지속할 objective가 생겼을 때 goal로 전환한다.

### 화면 예시
```text
/plan
이 repo에서 example technical guide를 보강하려고 한다.
먼저 관련 파일, 누락 가능성, 검증 방법, risk를 정리하고,
수정은 아직 하지 말아줘.

Return:
- likely files
- assumptions / unknowns
- validation commands
- fallback path
- human decision needed
```

### 추천 시각화
- "Plan -> Execute -> Validate -> Review" loop

---

## Slide 11. one-shot / two-shot prompt pattern

### 화면 핵심
- one-shot: 원하는 출력 예시 하나를 준다.
- two-shot: 좋은 예시와 나쁜 예시, 또는 두 스타일의 차이를 준다.
- format, review style, summary depth, evidence format을 안정화하는 데 유용하다.

### 발표자 노트
Codex에게 "요약해줘"라고 하면 매번 다른 형태가 나올 수 있다. 하지만 "이런 형식으로 해줘"라는 예시를 하나 주면 훨씬 안정적이다. 두 개의 예시는 contrast를 알려줄 때 유용하다. 예를 들어 "좋은 issue summary"와 "나쁜 issue summary"를 같이 주면 Codex가 품질 기준을 더 잘 잡는다.

### 화면 예시
```text
아래 형식으로 SDC issue를 정리해줘.

Example:
- Issue:
- Evidence:
- Risk:
- Owner / reviewer:
- Next action:
- Confidence:
```

### 추천 시각화
- "Instruction only" vs "Instruction + example" 비교

---

## Transition. 개인 조작에서 팀 규칙으로

### 발표자 노트
지금까지는 한 사람이 Codex에게 일을 잘 시키는 방법이었다. 다음부터는 팀이 같은 품질을 반복하는 방법이다. 개인 prompt에 계속 적는 규칙은 오래가지 않는다. 팀의 build command, review 기준, 보안 경계, done criteria는 AGENTS.md와 skill로 내려가야 한다.

---

## Slide 12. AGENTS.md는 agent용 README다

### 화면 핵심
- repo layout, build/test command, convention, done criteria를 저장
- Codex가 작업 전에 읽는 durable instruction
- global, project, nested directory scope로 나눌 수 있음
- 가까운 디렉토리의 instruction이 더 구체적인 규칙을 제공
- 짧고 정확한 AGENTS.md가 긴 추상 규칙보다 낫다

### 발표자 노트
반복해서 말하는 규칙은 prompt에 매번 쓰지 말고 AGENTS.md로 내려야 한다. 예를 들어 "RTL 수정 후 어떤 lint를 돌릴지", "DRM 자료는 raw copy하지 말 것", "검증 로그를 evidence로 남길 것", "문서 변경 시 reviewer를 명시할 것" 같은 규칙은 repo instruction으로 남기는 것이 좋다.

### 화면 예시
```md
# AGENTS.md

## Verification
- RTL 변경 후 `make lint`를 실행한다.
- 실패하면 log path와 첫 번째 root cause 후보를 요약한다.

## Safety
- 회사 DRM 문서는 raw text로 복사하지 않는다.
- 불확실한 design intent는 추측하지 않고 질문한다.
```

### 추천 시각화
- instruction chain: global -> repo -> subdir

---

## Slide 13. Rule, Skill, Plugin의 차이

### 화면 핵심
- Rule: command 실행 권한과 안전 경계를 제어
- Skill: 반복 workflow를 instructions + references + scripts로 패키징
- Plugin: skill, MCP, app mapping, asset 등을 묶어 배포하는 단위
- 처음에는 skill보다 작은 실제 task를 안정화하는 것이 먼저다.
- 배포 판단: workflow 작성은 Skill, 여러 사람이 설치할 단위는 Plugin

### 발표자 노트
세미나에서 rule과 skill을 배포한다고 했을 때, 둘의 목적을 명확히 해야 한다. Rule은 주로 "무엇을 허용/차단/확인할지"에 가깝다. Skill은 "어떤 일을 어떤 순서와 검증으로 할지"에 가깝다. Plugin은 여러 사람이 설치할 수 있는 배포 단위다. 처음부터 완성형 skill pack을 만들려고 하기보다, 작은 업무 하나를 안정화하고 그 결과를 skill로 내리는 순서가 좋다.

웹 리서치 보강:
- OpenAI Codex Skills는 reusable workflow authoring format이며, plugin은 skill과 app integration 등을 묶어 배포하는 installable unit이다.
- Anthropic Agent Skills도 비슷하게 domain-specific workflow, context, scripts, templates를 패키징하고 progressive disclosure 방식으로 필요한 내용만 로드한다.
- 따라서 "skill"은 prompt 모음이 아니라 반복 업무의 절차, 예시, reference, validation을 담는 operational package로 설명하는 것이 좋다.
- Skill의 재료는 `SKILL.md`, 예시, reference, script, template, validation check다. 이 중 script는 deterministic하게 반복해야 하는 부분에만 넣는다.
- Plugin은 skill 자체보다 배포 경계다. 팀 공통 workflow, MCP 설정, app mapping, shared asset을 함께 전달해야 할 때 고려한다.

### 추천 시각화
- 3-column table: Rule / Skill / Plugin

---

## Slide 14. Skill은 언제 만드는가

### 화면 핵심
1. 작은 실제 task를 고른다.
2. Codex와 수동으로 몇 번 수행한다.
3. prompt, context, 수정, 실패, 검증을 기록한다.
4. quality threshold에 반복적으로 도달하는지 본다.
5. workflow를 `SKILL.md`로 정제한다.
6. team에 배포할 때 plugin화를 고려한다.
7. 실패 사례와 correction을 skill의 failure mode로 남긴다.

### 발표자 노트
좋은 skill은 책상 위에서 상상해서 나오지 않는다. 실제 task를 수행하면서 어디서 실패하는지, 어떤 context가 반드시 필요한지, 어떤 검증이 의미 있는지 알아야 한다. 예를 들어 "SDC cleanup skill"을 만들고 싶다면 먼저 한 개의 SDC cleanup task를 제대로 끝내야 한다. 그 과정에서 필요한 source, check, stop condition을 뽑아 skill로 만든다.

리서치 보강:
- Skill로 승격하기 전에는 같은 task class에서 2~3회 이상 반복 성공했는지 확인한다.
- 실패도 자산이다. 같은 실수가 반복되면 prompt 예시, AGENTS.md rule, skill instruction, validation check 중 어디로 내려야 할지 결정한다.
- RTL/IP 후보 skill은 `rtl-log-triage`, `sdc-cleanup-planner`, `evidence-reviewer`, `handoff-writer`처럼 read-heavy하고 검증 가능한 것부터 시작한다.

### 추천 시각화
- Funnel: task -> repeated success -> skill -> plugin

---

## Slide 15. 평가와 모니터링: quality threshold first

### 화면 핵심
- 첫 번째 질문: 원하는 품질에 도달했는가?
- 두 번째 질문: 도달했다면 비용은 얼마였는가?
- 비용 항목: token, tool call, command, attempt, wall time, failure count
- 개선 방향: 같은 품질을 더 낮은 비용으로 재현
- 개선 loop: trace -> feedback -> eval -> repair -> validate

### 발표자 노트
AI workflow를 평가할 때 "빠른가"부터 보면 안 된다. 틀린 결과를 빠르게 내는 것은 의미가 없다. 먼저 결과가 필요한 품질에 도달했는지 확인해야 한다. 그 다음에 token 수, tool call 수, 시도 횟수, 걸린 시간, 실패율을 줄인다. 이것이 agent 운영에서 evaluation과 monitoring이 필요한 이유다.

웹 리서치 보강:
- OpenAI cookbook의 Agent Improvement Loop는 trace, human/model feedback, eval, Codex-ready handoff를 하나의 개선 loop로 묶는다.
- Codex iterative repair loop 패턴은 Review -> Repair -> Validate 구조를 사용한다. 즉 "검증 가능한 feedback이 다음 repair input이 된다"는 점이 핵심이다.
- 세미나 scorecard는 결과 품질뿐 아니라 재시도 횟수, validation failure, handoff 품질까지 포함해야 한다.
- 세미나 후 질문/실패 log는 FAQ, rule, skill, eval case 중 하나로 분류해야 한다. 답변만 하고 끝내면 asset이 남지 않는다.

### 추천 시각화
- Gate 1: Quality reached?
- Gate 2: Resource efficient?
- Gate 3: Reusable?

---

## Slide 16. Codex review workflow

### 화면 핵심
- 변경 후 바로 merge하지 말고 diff와 review를 본다.
- `/review`로 uncommitted changes, base branch, commit 단위 review 가능
- review 기준은 prompt나 AGENTS.md에 저장한다.
- bug, regression, missing test, risky assumption을 우선 확인한다.
- Review output은 다음 repair prompt의 input이 된다.

### 발표자 노트
Codex가 만든 결과를 사람이 보지 않고 받아들이면 안 된다. Codex는 구현뿐 아니라 review에도 쓸 수 있다. 중요한 것은 review 기준을 명시하는 것이다. RTL/IP에서는 functional risk, spec mismatch, missing evidence, unchecked assumption이 중요하다. 코드 스타일보다 behavior risk를 먼저 봐야 한다.

리서치 보강:
- review는 스타일 지적보다 behavior risk와 evidence gap을 먼저 봐야 한다.
- repair prompt에는 review finding, affected file, expected evidence, rerun command를 넣는다.
- validation이 실패하면 "다시 해줘"가 아니라 실패 log와 첫 root-cause 후보를 다음 입력으로 넘긴다.

### 화면 예시
```text
/review
Focus on functional regression, missing validation,
unsafe assumptions about design intent, and incomplete evidence.
```

### 추천 시각화
- "Generate -> Test -> Review -> Accept" quality loop

---

## Transition. 반복 workflow에서 병렬 운영으로

### 발표자 노트
AGENTS.md와 skill은 같은 workflow를 안정화하는 장치다. 하지만 실제 업무가 커지면 한 thread 안에서 모든 것을 처리하기 어렵다. 여기서 worktree, handoff, subagent가 나온다. 핵심은 "더 많은 agent"가 아니라 "작업 단위를 분리하고 evidence를 모으는 coordinator 방식"이다.

---

## Slide 17. Worktree는 병렬 실험의 안전장치다

### 화면 핵심
- Local: 현재 checkout에서 직접 작업
- Worktree: Git worktree로 격리된 checkout에서 작업
- 여러 candidate를 병렬로 만들고 비교 가능
- 현재 foreground 업무를 깨지 않고 background 작업 가능
- branch/worktree handoff와 cleanup 규칙이 필요

### 발표자 노트
Codex를 쓰면 동시에 여러 접근법을 시도하고 싶어진다. 같은 checkout에서 여러 thread가 같은 파일을 수정하면 충돌과 혼란이 생긴다. 그래서 Codex app의 Worktree mode가 중요하다. 한 thread는 SDC cleanup approach A, 다른 thread는 approach B를 시도하게 하고, 나중에 diff와 validation으로 비교하면 된다.

### 화면 예시
```text
Create a separate background thread in a worktree.
Try a minimal SDC cleanup approach.
Return: worktree path, branch, changed files, validation, blockers, next action.
```

### 추천 시각화
- main checkout에서 두 개의 worktree branch가 갈라지는 그림

---

## Slide 18. Thread continuity: 끊기지 않는 작업 만들기

### 화면 핵심
- thread는 하나의 작업 맥락이다.
- long task는 resume, fork, compact, handoff가 중요하다.
- handoff에는 objective, repo, branch/worktree, changed files, evidence, blockers, next action이 들어가야 한다.
- ontology ID나 task ID를 붙이면 세션을 넘어 이어가기 쉽다.

### 발표자 노트
AI 작업에서 흔한 문제는 "어제 어디까지 했지?"다. thread continuity를 운영 규칙으로 만들면 이 문제가 줄어든다. 특히 한 사람이 여러 업무와 thread를 관리할 때는 handoff template이 필요하다. 이 template은 사람에게도 유용하고, subagent나 다음 Codex session에게도 유용하다.

### 화면 예시
```md
## Handoff
- Objective:
- Repo / cwd:
- Branch / worktree:
- Related task ref:
- Changed files:
- Validation:
- Decisions:
- Blockers:
- Next action:
```

### 추천 시각화
- Thread A -> Handoff -> Thread B

---

## Slide 19. Subagent는 병렬 작업을 위한 운영 장치다

### 화면 핵심
- Codex는 명시적으로 요청할 때 subagent를 spawn한다.
- subagent는 token과 tool work를 추가로 사용한다.
- 기본 agent: default, worker, explorer
- custom agent TOML로 reviewer, explorer, RTL checker, doc writer 등을 정의 가능
- 먼저 read-heavy 역할부터 시작하는 것이 안전하다.
- 좋은 subagent 설계는 "많이"가 아니라 "역할이 겹치지 않게"다.

### 발표자 노트
Subagent는 "많을수록 좋은 기능"이 아니다. 병렬화할 수 있는 작업에만 써야 한다. 예를 들어 PR review에서 security, bug, test flakiness, maintainability를 나눠 보는 것은 좋다. 하지만 같은 RTL 파일을 여러 subagent가 동시에 수정하게 하는 것은 위험하다. 처음에는 explorer, reviewer, evidence reviewer처럼 읽기 중심 역할이 적합하다.

리서치 보강:
- RTL/IP 후보 역할: `log triager`, `constraint reviewer`, `doc drafter`, `evidence checker`.
- subagent는 각자 model/tool work를 하므로 token과 wall time이 늘어난다. 병렬 가치가 있는 exploration, review, QA에 먼저 쓴다.
- write-heavy 작업을 병렬화할 때는 write scope를 분리하고, 같은 파일을 여러 agent가 수정하지 않게 한다.

### 추천 시각화
- Coordinator thread가 여러 specialist agent를 spawn하고 결과를 collect하는 그림

---

## Slide 20. Custom agent TOML 예시

### 화면 핵심
- 위치: `~/.codex/agents/` 또는 `.codex/agents/`
- 필수 필드: `name`, `description`, `developer_instructions`
- 선택 필드: model, reasoning, sandbox, MCP, skills, nickname
- global limit: `[agents]`의 max_threads, max_depth, runtime

### 화면 예시
```toml
name = "rtl_lint_checker"
description = "Read-heavy RTL lint and compile triage agent."
developer_instructions = """
Focus on lint, compile, and evidence triage.
Do not change RTL intent without explicit approval.
Return root-cause candidates, evidence paths, and next checks.
"""
sandbox_mode = "read-only"
```

### 발표자 노트
Custom agent는 역할을 좁게 잡아야 한다. "똑똑한 agent"보다 "검증 로그를 읽고 root cause 후보를 정리하는 agent"가 낫다. 그리고 sandbox를 read-only로 두는 것도 좋은 시작이다. 여러 subagent를 쓰면 token 비용과 latency가 늘어나므로, global limit를 보수적으로 둬야 한다.

### 추천 시각화
- TOML snippet을 코드 카드로 표시

---

## Slide 21. Codex manages Codex: coordinator pattern

### 화면 핵심
- coordinator thread가 active thread를 정리한다.
- 관련 thread 검색, pin/archive, resume/fork 후보를 제안한다.
- 독립 작업은 worktree-backed worker thread로 보낸다.
- worker는 branch, changed files, validation, blockers, next action을 반환한다.

### 발표자 노트
thread가 많아지면 사람의 인지 부하가 커진다. 이때 Codex 자체를 coordinator로 쓸 수 있다. "현재 project에서 관련 thread를 찾아라", "계속할 thread와 archive할 thread를 분리해라", "독립 작업은 별도 worktree thread로 보내라" 같은 운영 방식이다. 단, 자동화가 커질수록 handoff와 evidence 규칙이 더 중요해진다.

### 추천 시각화
- Coordinator -> Thread inventory -> Worker dispatch -> Consolidated report

---

## Transition. 고급 기능은 언제 꺼내는가

### 발표자 노트
이제부터는 첫날 모든 사람이 쓸 기능이 아니라, 복잡도가 올라갈 때 꺼내는 도구다. App Server, open-source 경계, MCP, 외부 tool 연동은 매력적이지만 첫 demo의 중심이 되면 메시지가 흐려진다. 세미나에서는 "어떤 문제를 만나면 이 기능이 필요해지는가"로만 연결한다.

---

## Slide 22. App Server는 고급 통합용이다

### 화면 핵심
- Codex app-server는 rich client나 제품 통합을 위한 JSON-RPC interface다.
- thread/start, thread/resume, thread/fork, turn/start 같은 primitive가 있다.
- 일반 사용자 세미나의 기본 흐름은 아니다.
- thread inventory나 사내 tool 연동 proof에만 제한적으로 다룬다.

### 발표자 노트
App Server는 강력하지만 첫 세미나의 핵심은 아니다. 다만 고급 사용자가 "thread를 programmatic하게 관리할 수 있나?"라고 물을 수 있다. 이때 app-server가 있다는 것, thread와 turn primitive가 있다는 것 정도를 소개하면 충분하다. 실제 운영 자동화는 보안과 인증, 로그, 권한 정책이 붙어야 한다.

### 추천 시각화
- Codex App / IDE / Custom client -> App Server -> Thread/Turn APIs

---

## Slide 23. Codex open-source 범위는 정확히 말해야 한다

### 화면 핵심
- 공개 component: Codex CLI, Codex SDK, Codex App Server, Skills, Universal cloud environment
- 공개되지 않은 component: IDE extension, Codex web
- "Codex 전체가 오픈소스"라고 말하면 부정확하다.
- issue와 discussion은 openai/codex GitHub repo에서 추적 가능

### 발표자 노트
참석자들이 Codex가 오픈소스인지 관심을 가질 수 있다. 이때 정확하게 말해야 한다. CLI, SDK, App Server, Skills, codex-universal 등 주요 구성요소는 공개되어 있지만, IDE extension과 Codex web은 open source가 아니다. 공개 repo는 학습과 issue tracking, feature request를 보는 데 유용하다.

### 추천 시각화
- Open source / Not open source 비교 표

---

## Transition. 기능에서 실제 RTL/IP 업무로

### 발표자 노트
여기서부터가 참석자가 가장 중요하게 느낄 부분이다. "좋은 기능이 많다"에서 끝나면 도입이 안 된다. 실제로 내일 할 수 있는 일은 작은 log triage, SDC warning 분류, compile 실패 원인 후보 정리, evidence checklist 만들기다. 첫 적용은 code generation이 아니라 read-heavy triage와 validation planning이어야 한다.

---

## Slide 24. RTL/IP 업무에 Codex를 붙이는 첫 task 후보

### 화면 핵심
- 현재 우선순위: verification first
- SDC cleanup
- lint triage
- compile error analysis
- simulation smoke check
- guide document draft
- spec/requirement summary
- evidence checklist generation
- issue -> resolution -> validation 기록 정리
- 우선순위: read-heavy triage -> plan -> small change -> validation -> evidence

### 발표자 노트
처음부터 RTL generator나 SoC cockpit을 만들려고 하면 위험하다. 지금 회사의 현실적인 시작점은 검증 중심이어야 한다. 예를 들어 SDC cleanup에서 "현재 warning 목록을 분류하고, 수정 후보와 risk를 정리하고, rerun command를 제안"하는 정도가 좋다. 혹은 compile log를 읽고 root cause 후보를 분류하는 것부터 시작할 수 있다.

리서치 보강: RTL/IP operating loop
1. Input: SDC/lint/compile/simulation log와 failing command를 준다.
2. Classify: error group, suspected subsystem, first evidence line을 분리한다.
3. Inspect: 관련 RTL, constraint, spec, guide, previous issue를 찾되 design intent는 추정하지 않는다.
4. Decide: safe next check와 human decision needed를 분리한다.
5. Validate: rerun command, expected artifact, pass/fail threshold를 명시한다.
6. Record: evidence path, changed files, unresolved assumption, owner/reviewer, next action을 남긴다.

RTL/IP 금지선:
- technical intent, exception rationale, ownership boundary를 추측해서 고치지 않는다.
- constraint 의미를 조용히 바꾸지 않는다.
- private log/raw DRM text를 company-shareable asset에 복사하지 않는다.

### 추천 시각화
- Task 후보를 risk/impact 2x2 matrix로 표시

---

## Slide 25. 데모 후보: SDC cleanup workflow

### 화면 핵심
1. failing log 또는 warning list 제공
2. Codex가 관련 파일과 context 조사
3. Plan mode로 수정 범위와 risk 정리
4. 작은 변경 또는 문서화 먼저 수행
5. lint/build/synthesis check 실행
6. evidence와 next action 기록
- fallback: live run 실패 시 prepared log와 static evidence로 같은 workflow를 보여준다.

### 발표자 노트
SDC cleanup은 실무적이고, 검증 흐름을 설명하기 좋다. 단, design intent를 agent가 임의로 바꾸면 안 된다. 그래서 첫 데모는 "자동 수정"보다 "분류, 원인 후보, risk, 필요한 human decision"을 보여주는 것이 안전하다. 실제 수정은 fallback 없이 live로 무리하지 말고, static log와 prepared repo를 같이 준비한다.

리서치 보강: demo verification matrix
| Task type | Input | Success evidence | Human review point |
|---|---|---|---|
| SDC cleanup | warning list, representative snippet | rerun check log, proposed diff summary, risk note | exception rationale |
| Lint triage | lint log segment | grouped root-cause candidates, safe next check | whether warning is acceptable |
| Compile analysis | failing command/output | first failing file/symbol, minimal repro command | design dependency or generated file policy |
| Simulation smoke | sim command/log/waveform ref | pass/fail marker, artifact path, runtime | scenario coverage and acceptance |

### 추천 시각화
- Input log -> Codex analysis -> plan -> change -> validation -> evidence

---

## Slide 26. 데모 후보: Issue to Evidence

### 화면 핵심
- Issue: 어떤 문제가 있는가
- Context: 어떤 spec/log/file과 연결되는가
- Attempt: 무엇을 시도했는가
- Resolution: 무엇이 해결책인가
- Evidence: 어떤 test/log/artifact가 증명하는가
- Reusable pattern: 다음에 무엇을 재사용할 수 있는가

### 발표자 노트
이 구조는 Solution RAG와 ontology 구축에도 그대로 연결된다. 회사 지식은 단순 문서 모음이 아니라 "문제와 해결의 구조"로 남아야 한다. Codex가 과거 issue를 찾고, 해결 과정을 요약하고, evidence가 부족한 항목을 표시할 수 있으면 실무 가치가 크다.

### 추천 시각화
- Issue -> Attempt -> Resolution -> Evidence graph

---

## Transition. 개별 task에서 지식 시스템으로

### 발표자 노트
작은 RTL/IP task가 한 번 성공하면 그 다음 질문은 "이걸 어떻게 남길 것인가"다. 여기서 LLM Wiki, OKF, Obsidian, Ontology 이야기가 나온다. 이 파트의 목적은 새로운 지식 도구를 소개하는 것이 아니라, Codex output이 사라지지 않게 만드는 구조를 보여주는 것이다.

---

## Slide 27. LLM Wiki와 Ontology의 차이

### 화면 핵심
- LLM Wiki: 사람이 읽고 agent가 참고하는 설명/문서 layer
- Ontology: object, relation, action, state, evidence layer
- Wiki는 "무엇을 설명하는가"에 강하다.
- Ontology는 "무엇을 할 수 있고, 무엇이 연결되어 있는가"에 강하다.

### 발표자 노트
LLM Wiki와 Ontology를 같은 것으로 보면 안 된다. LLM Wiki는 markdown과 YAML frontmatter처럼 사람이 읽기 좋은 설명 구조다. Ontology는 task, issue, requirement, IP, interface, evidence, owner, decision 같은 객체와 관계를 명시한다. Agent가 실제 업무를 굴리려면 ontology가 필요하다.

### 추천 시각화
- Explanation layer와 Operational layer를 층으로 표현

---

## Slide 28. OKF, Obsidian, Interactive HTML의 역할

### 화면 핵심
- OKF: AI와 도구가 읽기 쉬운 markdown/YAML 지식 포맷
- Obsidian: 사람이 보는 local knowledge UI
- Bases: task, issue, evidence를 filterable table/card로 보기
- Interactive HTML: 복잡한 관계를 self-contained graph로 설명
- Word/PPT skill: 구조화된 지식을 문서와 발표자료로 변환

### 발표자 노트
지식은 하나의 UI에 갇히면 안 된다. Canonical source는 ontology나 reviewed knowledge object로 두고, OKF는 portable view, Obsidian은 사람용 UI, Interactive HTML은 설명용 artifact, Word/PPT는 보고와 전파용 output으로 볼 수 있다. 같은 지식을 여러 view로 보여주는 것이 핵심이다.

웹 리서치 보강:
- Google OKF v0.1은 markdown file + YAML frontmatter 기반이며, 필수 frontmatter는 `type` 하나로 매우 작다. `title`, `description`, `resource`, `tags`, `timestamp`는 권장 필드다.
- OKF는 `index.md`를 progressive disclosure용 directory listing으로, `log.md`를 update history로 쓸 수 있게 정의한다.
- OKF blog는 static HTML visualizer가 OKF bundle을 self-contained graph view로 보여줄 수 있다고 설명한다. 이 점은 세미나의 Interactive HTML demo와 직접 연결된다.
- Obsidian Bases는 local markdown 파일과 properties를 database-like view로 보여주며, `.base` 파일은 YAML syntax로 filters, views, formulas를 정의한다.
- 세미나 메시지는 "OKF를 도입하자"가 아니라 "agent-readable file format과 human-readable view를 분리하자"다.
- SoC Knowledge에서는 canonical object를 먼저 안정화하고, OKF/Obsidian/HTML/PPT는 같은 지식을 목적별로 보여주는 view로 둔다.

### 추천 시각화
- Canonical knowledge -> OKF -> Obsidian / HTML / Word / PPT

---

## Slide 29. SoC Knowledge Graph로 가는 이유

### 화면 핵심
- Codex 사용 경험을 개인 prompt 모음으로 끝내면 사라진다.
- 팀 자산이 되려면 format, review, owner, evidence가 필요하다.
- SoC Knowledge는 subsystem, IP, interface, requirement, issue, evidence, decision을 연결한다.
- reference package로 format을 안정화하고, pilot workflow로 적용 범위를 넓힌다.

### 발표자 노트
2개월 동안 Codex를 많이 쓰는 것 자체는 목적이 아니다. 중요한 것은 무엇이 남는가다. guide, rule, skill, FAQ, workflow cookbook, issue case, evidence pattern이 남아야 한다. 더 나아가 이것들이 SoC Knowledge Graph로 연결되면 새 사람이 들어오거나 유사 문제가 생겼을 때 재사용할 수 있다.

### 추천 시각화
- Scattered prompts -> Reviewed SoC Knowledge graph

---

## Slide 30. Sub System Level Ontology

### 화면 핵심
- File/task 단위만으로는 SoC 맥락을 이해하기 어렵다.
- Subsystem level에서는 IP, interface, requirement, integration point, verification, evidence, owner가 연결된다.
- Codex demo는 최소 한 개의 subsystem slice를 보여주는 것이 좋다.

### 발표자 노트
RTL/IP 업무에서 중요한 것은 개별 파일보다 연결 관계다. 어떤 requirement가 어떤 interface에 영향을 주고, 어떤 IP block과 verification case에 연결되며, 현재 evidence가 충분한지 보는 것이 실무 가치다. 그래서 Sub System Level Ontology가 중요하다. 이것이 SoC-on-ontology로 가는 브리지다.

### 추천 시각화
- SoC -> Subsystem -> IP -> Interface -> Requirement -> Verification -> Evidence

---

## Slide 31. Palantir analogy: Foundry, AIP, Apollo, Gotham

### 화면 핵심
- Foundry-like: local engineering data와 ontology substrate
- AIP-like: Codex, Solution RAG, LLM Wiki agent layer
- Apollo-like: workflow packaging, deployment, validation, monitoring
- Gotham-like: 나중에 만들 수 있는 SoC debug/signoff cockpit
- 먼저 cockpit이 아니라 operational ontology loop가 필요하다.

### 발표자 노트
Palantir analogy는 설명 도구로만 쓴다. 핵심은 "AI chatbot이 먼저가 아니라, 현실 업무 객체와 의사결정 loop가 먼저"라는 점이다. SoC 개발에서도 처음부터 멋진 dashboard를 만들기보다, task, issue, evidence, decision, action, state가 제대로 남는 구조가 먼저다.

웹 리서치 보강:
- Palantir 공식 문서는 Foundry를 data operations platform, AIP를 generative AI platform, Apollo를 continuous delivery platform으로 설명한다.
- Palantir Ontology 설명에서 중요한 포인트는 ontology가 단순 data model이 아니라 enterprise decision을 표현하고, data/logic/action/security를 통합한다는 점이다.
- 특히 semantic concepts인 objects/properties/links만으로는 부족하고, actions라는 "verbs"가 붙어야 decision을 모델링할 수 있다고 설명한다. Brian의 semantic/kinetic/dynamic 설명과 잘 맞는다.
- 세미나에서는 Palantir를 제품 비교가 아니라 architecture analogy로만 쓴다. SoC ontology도 block/property/link에서 멈추면 부족하고 issue triage, review, validation, signoff action까지 연결되어야 한다.
- 안전하게 표현할 문장: "우리가 만들려는 것은 Palantir 복제가 아니라, SoC 업무에 맞는 object/action/evidence loop다."

### 추천 시각화
- 4-layer platform stack

---

## Slide 32. Operational decision loop

### 화면 핵심
1. Raw engineering data
2. Real-world objects
3. Current state and decision context
4. Human/agent-assisted judgment
5. Action or writeback
6. Evidence and audit
7. Feedback to next decision

### 발표자 노트
AI agent의 가치는 답변 자체가 아니라 결정과 실행을 개선하는 데 있다. 예를 들어 log를 보고 issue를 만들고, owner를 정하고, fix를 시도하고, validation evidence를 남기고, 그 결과를 다음 의사결정에 반영하는 loop가 중요하다. 이 loop가 없으면 AI output은 휘발된다.

### 추천 시각화
- Closed loop diagram

---

## Slide 33. AI 정보 과부하와 cognitive bandwidth

### 화면 핵심
- 예전 병목: 정보 부족
- 현재 병목: AI가 너무 많이 말함
- 사용자는 소화하지 못하면 기억하지 못하고 실행하지 못한다.
- 좋은 AI assistant는 "많이 설명"보다 "지금 판단할 3개 + 다음 액션 1개"를 준다.
- Ontology는 AI output을 소화 가능한 지식으로 바꾼다.

### 발표자 노트
AI가 좋아질수록 정보는 더 많이 나온다. 그런데 사람이 소화하지 못하면 업무는 좋아지지 않는다. 그래서 세미나에서도 설명을 줄이고 구조를 줘야 한다. 지금 알아야 할 것, 나중에 저장할 것, 버려도 되는 것을 구분하는 습관이 필요하다.

### 추천 시각화
- AI output flood -> ontology filter -> 3 key points + 1 action

---

## Slide 34. PPT/Word generation도 workflow다

### 화면 핵심
- 나쁜 prompt: "PPT 만들어줘"
- 좋은 workflow:
  1. source knowledge 정리
  2. audience와 objective 정의
  3. outline 작성
  4. slide intent 지정
  5. reference design 검토
  6. artifact 생성
  7. visual review와 iteration

### 발표자 노트
Codex로 문서와 발표자료를 만들 때도 workflow가 필요하다. source knowledge 없이 PPT를 만들면 내용이 얕아진다. reference design 없이 만들면 시각 품질이 낮다. 그래서 ontology/OKF에서 source를 가져오고, slide intent를 정하고, reference style을 분석하고, 생성 후 시각적으로 검토하는 loop가 필요하다.

웹 리서치 보강:
- Microsoft Copilot PowerPoint 문서는 presentation 생성 과정에서 target audience, style 같은 clarifying questions를 거쳐 outline을 만들고, 사용자가 refine한 뒤 slide를 생성하는 흐름을 설명한다.
- Microsoft 365 Copilot blog는 agentic 기능의 가치를 "앱 안에서 multi-step action을 수행하되 사용자가 control을 유지하는 것"으로 설명한다.
- Claude Artifacts는 standalone content를 main conversation과 분리된 window에서 만들고 수정/재사용하는 방식이다. Codex 세미나에서는 이를 "artifact workflow" 트렌드로만 참고하고, 실제 산출물은 local file/PPT/Word/HTML로 관리한다.
- 이 `codex_seminar.md` 자체를 example로 보여줄 수 있다. source -> outline -> slide intent -> speaker note -> reference appendix -> review loop가 한 파일 안에 남는다.
- 문서 생성 prompt도 Goal/Context/Constraints/Done when 구조를 쓴다. 특히 audience, slide count, tone, visual reference, source boundary, review checklist를 넣어야 한다.

### 추천 시각화
- Source -> Outline -> Design reference -> PPT -> Review

---

## Transition. 세미나 이벤트에서 2개월 프로그램으로

### 발표자 노트
여기까지가 "어떻게 쓸 것인가"였다면, 이제는 "어떻게 남길 것인가"다. Codex가 70~80명에게 열리는 상황에서는 Brian이 질문을 계속 받아주는 방식으로는 확장되지 않는다. 세미나 이후 2개월은 사용량을 늘리는 기간이 아니라, 반복 가능한 workflow package를 만드는 기간으로 설계해야 한다.

---

## Slide 35. 2개월 Codex asset capture program

### 화면 핵심
- Week 1: setup, first task, onboarding guide
- Week 2: verification-centered RTL/IP task adoption
- Week 3~4: repeated questions -> FAQ/rules/skills
- Week 5~6: workflow cookbook와 case study
- Week 7~8: SoC Knowledge object와 review loop
- 매주 금요일: 무엇이 자산이 되었는지 review

### 발표자 노트
무제한 사용 기간은 "많이 써보자"가 아니라 "남기자"로 설계해야 한다. 매주 어떤 guide, rule, skill, demo, FAQ, case가 생겼는지 점검해야 한다. 특히 70~80명이 사용할 수 있다면 Brian이 모든 질문에 직접 답하는 구조는 지속 불가능하다. self-serve material이 필요하다.

### 추천 시각화
- 8-week roadmap

---

## Slide 36. Week-one asset list

### 화면 핵심
- Codex setup checklist
- first prompt template
- Plan mode quick guide
- AGENTS.md starter template
- review checklist
- one reliable demo script
- fallback screenshot/static demo
- repeated question log
- starter kit index: 어디서 시작하고, 무엇을 남길지 한 장으로 안내

### 발표자 노트
첫 주에는 완벽한 skill pack보다 시작 장벽을 낮추는 자산이 중요하다. 사람들이 Codex를 열고, 올바른 workspace에서, 안전한 permission으로, 작은 task를 시도하고, 결과를 review하는 흐름을 잡아야 한다. 질문이 반복되면 바로 FAQ나 guide로 전환한다.

첫 주 운영 흐름:
1. Setup: Codex app/CLI/IDE 중 본인 surface를 고르고 `/status`로 권한과 workspace를 확인한다.
2. Read-only task: module 설명, log 분류, 관련 파일 찾기처럼 변경 없는 task를 수행한다.
3. Plan-only task: 실제 수정 전에 Plan mode로 파일 범위, risk, validation을 받는다.
4. Review: 결과를 사람이 확인하고 shared FAQ에 질문/실패/성공을 남긴다.
5. Asset capture: 반복되는 질문은 guide, rule, skill 후보로 분류한다.

### 추천 시각화
- Checklist style slide

---

## Slide 37. 첫 demo는 작아야 한다

### 화면 핵심
- broad product demo는 실패 위험이 크다.
- reliable small slice를 먼저 보여준다.
- live demo + fallback demo를 같이 준비한다.
- "AI가 다 해줌"보다 "AI가 engineering workflow를 가속하고 기록함"을 보여준다.

### 발표자 노트
이전 demo 경험에서 얻을 수 있는 lesson은, stakeholder 앞에서는 작은 reliable slice가 중요하다는 것이다. Codex가 모든 것을 하는 것처럼 보이게 만드는 것보다, 실제 engineering workflow에서 어느 지점을 줄여주는지 보여주는 것이 더 신뢰를 만든다.

### 추천 시각화
- Large risky demo vs Small reliable slice

---

## Slide 38. Demo fallback 계획

### 화면 핵심
- live repo가 안 되면 prepared log로 전환
- tool이 없으면 static output으로 전환
- network가 막히면 local docs와 screenshots 사용
- simulation이 오래 걸리면 precomputed evidence 사용
- 질문이 깊어지면 appendix slide로 이동

### 발표자 노트
세미나는 실패할 수 있다. 중요한 것은 실패하지 않는 척하는 것이 아니라 fallback을 준비하는 것이다. hardware demo는 toolchain, license, path, environment에 의존한다. 그래서 live path와 static path를 둘 다 준비해야 한다.

### 추천 시각화
- Failure condition -> fallback response table

---

## Slide 39. Company-shareable boundary

### 화면 핵심
- 공유 가능: generic workflow, prompt template, public docs link, reviewed guide
- 검토 필요: pilot IP 예시, internal log, design decision, owner 정보
- 공유 금지/주의: DRM raw content, private life ontology, unreleased design details, credential/path
- SoC Knowledge는 permission-preserving ingest가 전제다.
- 애매하면 "review required" metadata를 붙이고 공유하지 않는다.

### 발표자 노트
회사 rollout에서 가장 조심할 것은 좋은 의도로 민감 정보를 섞는 것이다. 특히 개인 ontology와 회사 shareable asset을 분리해야 한다. DRM 자료는 우회하거나 해제하려고 하면 안 된다. metadata stub, human-reviewed distilled knowledge, authorized path를 써야 한다.

리서치 보강:
- Raw internal log를 복사하는 대신 log type, command class, error category, evidence path shape만 남긴다.
- 내부 design decision은 reviewer가 확인한 요약으로 승격하고, 원문/owner/path/credential은 shared deck에서 제거한다.
- SoC Knowledge pilot에서도 permission-preserving ingest가 먼저다. 사람이 볼 권한이 없는 자료를 agent context로 우회해서 넣지 않는다.

### 추천 시각화
- Green / Yellow / Red data boundary

---

## Slide 40. 세미나 후 남겨야 할 것

### 화면 핵심
- 참석자용 setup guide
- first task checklist
- prompt examples
- rule pack 초안
- skill pack 초안
- demo script와 fallback
- FAQ
- asset index
- next session backlog

### 발표자 노트
좋은 세미나는 끝난 뒤 산출물이 남는다. 참석자가 다음 날 다시 보고 쓸 수 있는 guide가 있어야 하고, Brian은 반복 질문을 줄일 수 있어야 한다. 또한 이번 세미나에서 나온 질문과 실패를 다음 asset backlog에 반영해야 한다.

### 추천 시각화
- Seminar event -> reusable assets

---

## Slide 41. 권장 첫 60분 진행안

### 화면 핵심
- 0~5분: 왜 Codex인가
- 5~12분: 철학 - prompt가 아니라 operating model
- 12~22분: Basic - app/CLI surface, `/status`, prompt contract, Plan mode
- 22~30분: Team rule - AGENTS.md, permission, review
- 30~42분: Practice - 작은 검증 중심 RTL/IP demo
- 42~50분: Advanced - worktree, subagent, skill/plugin, app-server/MCP는 언제 쓰는가
- 50~57분: Integration - issue/evidence/knowledge asset과 2개월 asset capture
- 57~60분: Q&A와 다음 action

### 발표자 노트
첫 60분은 모든 주제를 얕게 훑는 시간이 아니다. 참석자가 최소 한 번 따라할 수 있는 흐름을 잡는 것이 목표다. demo가 길어지면 뒤쪽 asset capture 설명이 사라지므로, demo는 15분 안에 끝나는 prepared slice로 제한하는 것이 좋다.

진행 팁:
각 구간 마지막에 bridge sentence를 넣는다. 예를 들어 Basic 끝에서는 "이제 개인 조작은 됐고, 팀 규칙으로 내려가야 합니다"라고 말한다. Practice 끝에서는 "이 demo가 한 번 성공하면, 다음 질문은 이걸 어떻게 skill과 knowledge asset으로 남길 것인가입니다"라고 연결한다.

### 추천 시각화
- Timeboxed agenda

---

## Slide 42. 참석자에게 줄 첫 action

### 화면 핵심
오늘 세미나 후 각자 할 일:
1. Codex에서 본인 repo/project를 연다.
2. `/status` 또는 app 설정으로 현재 권한과 context를 확인한다.
3. 작은 read-only task 하나를 시도한다.
4. Plan mode로 다음 변경 task의 계획만 받아본다.
5. 결과와 질문을 shared FAQ에 남긴다.
6. 성공/실패 사례를 rule, skill, guide, FAQ 후보로 분류한다.

### 발표자 노트
첫 action이 너무 크면 아무도 실행하지 않는다. "작은 read-only task"부터 시작하면 안전하다. 예를 들어 "이 module이 어떤 역할인지 설명하고 관련 file을 찾아줘" 또는 "최근 failing log를 분류해줘" 정도다. 실제 수정은 그 다음 단계다.

리서치 보강:
- 첫날 목표는 code change가 아니라 operating model 체험이다. context, rule, plan, permission, validation, review, artifact, feedback이 어떻게 이어지는지 보는 것이 중요하다.
- 각자 하나의 read-only task를 수행하고, 그 결과가 팀 FAQ나 starter guide에 들어갈 수 있는지 확인한다.

### 추천 시각화
- First-day checklist

---

## Slide 43. 발표 마무리 메시지

### 화면 핵심
- Codex는 사람을 대체하는 도구가 아니라 engineering loop를 강화하는 도구다.
- 좋은 결과는 prompt 하나가 아니라 context, rules, validation, review, assets에서 나온다.
- 작은 task를 안정화하고 skill로 만들면 팀 전체의 반복 비용이 줄어든다.
- 이번 rollout의 성공 기준은 "많이 썼다"가 아니라 "무엇이 팀 자산으로 남았는가"다.
- 한 문장: prompt collection이 아니라 operating model과 reusable workflow package를 만든다.

### 발표자 노트
마지막에는 기술보다 운영 메시지를 남긴다. AI 도입은 개인 productivity hack으로 끝나면 사라진다. 팀의 knowledge, workflow, review, evidence 구조에 붙어야 지속된다. 이 세미나는 그 출발점이다.

리서치 보강:
- Operating model = context, rule, plan, permission, validation, review, artifact, feedback.
- 2개월 window의 산출물은 성공 prompt가 아니라 반복 가능한 workflow package, 검증된 guide, evidence pattern, review checklist다.

### 추천 시각화
- "Usage -> Workflow -> Asset -> Team leverage"

---

# Appendix A. 10~12회 세미나 시리즈 상세안

## Session 1. Why Codex now
- LLM, RAG, coding agent trend
- Cursor seminar에서 Codex로 넘어가는 이유
- AI가 실제 engineering workflow에 들어올 때 생기는 변화
- 산출물: opening story와 adoption frame

## Session 2. Codex setup and operating surfaces
- Codex app, CLI, IDE extension, cloud thread
- permissions, sandbox, `/status`, app settings
- AGENTS.md, config.toml, MCP overview
- 산출물: setup guide 초안

## Session 3. Agent loop that behaves as intended
- prompt, context, plan, tool call, file edit, validation, review
- one-shot/two-shot examples
- stop condition과 done criteria
- 산출물: agent loop diagram과 rule pack 초안

## Session 4. Workflow to skill distillation
- 작은 실제 task 선택
- 반복 수행과 failure capture
- `SKILL.md` 구조
- skill과 plugin 배포 차이
- 산출물: task-to-skill recipe

## Session 5. Evaluation and monitoring
- quality threshold first
- resource efficiency: token, tool call, attempt, wall time, failure
- scorecard 설계
- 산출물: AI workflow scorecard

## Session 6. Hardware/IP practical demo
- SDC cleanup, lint triage, compile error analysis
- validation log와 evidence capture
- demo fallback 운영
- 산출물: reliable verification demo script

## Session 7. LLM Wiki, OKF, Ontology
- LLM Wiki vs Ontology
- OKF-style markdown/YAML
- ontology object/relation/action/state/evidence
- 산출물: OKF layering example

## Session 8. Obsidian graph and Bases
- OKF-style notes를 Obsidian에 넣기
- graph view와 Bases filter
- raw note -> reviewed object promotion
- 산출물: Obsidian demo vault slice

## Session 9. Interactive HTML knowledge viewer
- task/issue/evidence/owner graph
- self-contained HTML artifact
- stakeholder explanation용 view
- 산출물: HTML graph viewer demo

## Session 10. Document and deck generation
- Word/PPT 생성 workflow
- source knowledge -> outline -> slide intent -> artifact -> review
- reference design guided generation
- 산출물: guide/PPT generation demo

## Session 11. SoC Knowledge Graph and 2-month asset program
- reference package first, pilot workflow expansion
- canonical object format과 DB representation
- weekly asset review
- 산출물: two-month asset capture plan

## Session 12. Subagents, thread/worktree orchestration
- custom agent TOML
- coordinator thread
- worktree-backed worker thread
- handoff skill과 skill-making skill
- 산출물: subagent/worktree operating guide

---

# Appendix B. Prompt templates

## Template 1. Plan mode for risky engineering task
```text
/plan
Goal:
Context:
Constraints:
Risk:
Done when:

Before editing, identify:
1. likely files
2. assumptions
3. validation commands
4. rollback/fallback path
5. questions that require human decision
```

## Template 2. RTL/IP log triage
```text
Read the attached/following log and classify issues.
Do not assume design intent.

Return:
- Error group:
- Likely root cause:
- Evidence lines:
- Related files to inspect:
- Safe next check:
- Human decision needed:
- Confidence:
```

## Template 3. Worktree worker request
```text
Create a separate background thread in a worktree for this project.
Task:
Constraints:
Do not touch:
Validation:

Return:
- worktree:
- branch:
- changed files:
- validation result:
- blockers:
- next action:
```

## Template 4. Thread handoff
```md
## Handoff
- Objective:
- Repo / cwd:
- Thread:
- Branch / worktree:
- Related task refs:
- Files inspected:
- Files changed:
- Decisions made:
- Evidence:
- Validation:
- Blockers:
- Next action:
```

## Template 5. Skill extraction
```text
We have repeated this workflow successfully.
Turn it into a skill draft.

Extract:
1. trigger condition
2. required input
3. workflow steps
4. examples
5. validation checks
6. stop conditions
7. known failure modes
8. what the skill must not do
```

---

# Appendix C. Minimal rule/skill package proposal

## Rule package v0
- Do not run destructive Git commands unless explicitly approved.
- Do not modify RTL intent without human confirmation.
- Do not ingest DRM raw content or private credentials.
- Always return changed files, validation result, and unresolved assumptions.
- Prefer read-only exploration before write-capable changes.

## Skill package v0
- `rtl-log-triage`: lint/compile/simulation log 분류와 root-cause 후보 정리
- `sdc-cleanup-planner`: SDC cleanup 계획, risk, validation command 정리
- `evidence-reviewer`: claim마다 evidence/test/log/source ref 확인
- `guide-writer`: source notes에서 guide 문서 outline과 draft 생성
- `handoff-writer`: thread/task handoff를 표준 형식으로 정리

## Skill로 만들기 전 확인할 것
- 실제 task에서 2~3회 이상 반복 성공했는가
- 실패 사례와 correction이 기록되었는가
- validation 기준이 명확한가
- 공유 가능한 예시와 공유 불가 예시가 분리되었는가
- team 사용자가 이해할 만큼 짧은가

---

# Appendix D. Demo readiness checklist

## Live demo 준비
- demo repo clean 여부 확인
- 필요한 tool 설치 확인: Verilator, iverilog, pyslang 등
- expected command와 예상 runtime 확인
- network/license/path dependency 확인
- 실패 시 보여줄 static output 준비

## 발표 전 점검
- 정확한 세미나 시간과 audience 확정
- 내부 자료 공유 가능성 검토
- demo script 1회 rehearsal
- fallback screenshot/PDF/HTML 준비
- Q&A 예상 질문 작성

## Demo 완료 조건
- 참석자가 "내 업무에 어디부터 적용할지" 이해한다.
- 결과물에 evidence가 붙어 있다.
- 위험한 자동 수정이 아니라 검증 가능한 작은 workflow를 보여준다.
- 다음 action이 guide/FAQ/asset index로 이어진다.

---

# Appendix E. References

## Official OpenAI Codex documentation checked
- Codex manual: https://developers.openai.com/codex/codex-manual.md
- Best practices: https://developers.openai.com/codex/learn/best-practices
- Prompting: https://developers.openai.com/codex/prompting
- Codex app features: https://developers.openai.com/codex/app/features
- Codex CLI slash commands: https://developers.openai.com/codex/cli/slash-commands
- Worktrees: https://developers.openai.com/codex/app/worktrees
- Skills: https://developers.openai.com/codex/skills
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md
- Rules: https://developers.openai.com/codex/rules
- App Server: https://developers.openai.com/codex/app-server
- Subagents: https://developers.openai.com/codex/subagents
- Open Source: https://developers.openai.com/codex/open-source
- OpenAI cookbook, Agent improvement loop: https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop
- OpenAI cookbook, iterative repair loops with Codex: https://developers.openai.com/cookbook/examples/codex/build_iterative_repair_loops_with_codex

## External web research references checked
- Google Cloud, Open Knowledge Format overview: https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing
- GoogleCloudPlatform knowledge-catalog OKF spec: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Obsidian Help, Bases: https://obsidian.md/help/bases
- Obsidian Help, Bases syntax: https://obsidian.md/help/bases/syntax
- Palantir Foundry architecture platforms: https://www.palantir.com/docs/foundry/architecture-center/platforms
- Palantir AIP overview: https://www.palantir.com/docs/foundry/aip/overview
- Palantir Ontology System: https://www.palantir.com/docs/foundry/architecture-center/ontology-system
- Anthropic Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Anthropic Claude Artifacts support article: https://support.claude.com/en/articles/9487310-what-are-artifacts-and-how-do-i-use-them
- Microsoft PowerPoint Copilot Agent Mode support article: https://support.microsoft.com/en-US/PowerPoint/copilot/create-a-new-presentation-with-copilot-in-powerpoint
- Microsoft 365 Copilot agentic capabilities blog: https://www.microsoft.com/en-us/microsoft-365/blog/2026/04/22/copilots-agentic-capabilities-in-word-excel-and-powerpoint-are-generally-available/
- LazyCodex site: https://lazycodex.ai/
- LazyCodex GitHub repository: https://github.com/code-yeongyu/lazycodex

# Appendix F. Web research 기반 보강 슬라이드 후보

이 부록은 본문 43장에 추가하거나, Q&A/심화 세션에서 사용할 수 있는 web research 기반 장표 후보이다. 핵심은 "Codex 기능 소개"를 넘어서 agent 운영 체계, 지식 포맷, 검증 루프, 문서 산출물 workflow까지 연결하는 것이다.

## Add-on Slide F1. Codex는 coding chatbot이 아니라 agentic workspace다

화면 핵심:
- OpenAI Codex app은 thread, worktree, diff, terminal, artifact preview를 한 workspace에서 다룬다.
- 병렬 thread는 여러 후보 접근을 동시에 실험하게 해준다.
- worktree는 변경을 격리해서 원본 repo를 보호한다.
- terminal output은 agent가 validation evidence로 다시 읽을 수 있다.
- 비코드 산출물도 source data, file type, slide section, review check를 명확히 주면 생성/검토 workflow에 들어간다.

발표자 노트:
Codex를 "질문하면 코드 조각을 주는 도구"로 이해하면 seminar 가치가 낮아진다. 실제로 중요한 것은 agent가 하나의 workspace 안에서 계획, 수정, 검증, diff review, terminal evidence, artifact를 이어서 다룬다는 점이다. RTL/design engineer 관점에서는 이 차이가 크다. RTL/IP 업무는 코드 한 줄보다 log, constraint, waveform, review comment, regression evidence가 함께 움직인다. 따라서 Codex 활용법은 prompt 몇 개가 아니라 workspace 운영법으로 설명해야 한다.

PPT 시각화:
- 왼쪽: 기존 chatbot flow `질문 -> 답변`
- 오른쪽: Codex workspace flow `context -> plan -> edit -> terminal -> diff -> review -> artifact`

## Add-on Slide F2. Plan mode는 "느린 모드"가 아니라 risk control이다

화면 핵심:
- 어려운 task는 바로 구현하지 말고 Plan mode로 context를 먼저 모은다.
- Plan mode는 질문, 파일 조사, 변경 범위 정리, 검증 계획을 먼저 만든다.
- 세미나 demo에서는 Plan mode 결과를 보여준 뒤 edit/validation으로 넘어간다.
- 설계/검증 업무에서는 계획이 곧 품질 장치다.

발표자 노트:
OpenAI best practice는 복잡한 작업에서 먼저 계획을 세우는 것을 권장한다. 이 메시지는 design engineer에게 특히 잘 맞는다. RTL 수정은 "빨리 코드 변경"보다 "무엇을 건드리지 않을지"가 중요하다. Plan mode의 산출물은 변경 전 review checklist 역할을 한다. 예를 들어 SDC cleanup task라면 affected clocks, generated clocks, false path 의도, regression 범위, owner 확인 포인트를 먼저 뽑아야 한다. 이 계획이 없으면 agent가 빠르게 틀릴 수 있고, 계획이 있으면 사람이 검토 가능한 단위로 위험이 줄어든다.

PPT 시각화:
- `Task` 앞에 gate 추가: `Task -> Plan gate -> Human review -> Edit -> Validate`

## Add-on Slide F3. Prompt는 긴 글이 아니라 실행 계약서다

화면 핵심:
- 좋은 prompt에는 goal, context, constraints, output format, validation이 들어간다.
- Codex prompting guide의 방향은 "구체적으로, 검증 가능하게, 모호함을 줄이는 것"이다.
- RTL/IP 업무 prompt는 design intent를 agent가 추정하지 못하게 막아야 한다.
- 출력 형식을 고정하면 review 비용이 줄어든다.

발표자 노트:
prompt를 잘 쓴다는 것은 말을 예쁘게 쓰는 것이 아니다. agent에게 작업 계약서를 주는 것이다. 특히 design/RTL 환경에서는 "추정하지 말라"는 제약이 중요하다. technical intent, cross-module assumption, exception rationale처럼 owner 판단이 필요한 것은 코드만 보고 임의로 결정하면 안 된다. prompt에는 "확실하지 않으면 human decision needed로 표시하라"는 문장이 들어가야 한다. 이것이 hallucination을 완전히 없애지는 못하지만, 잘못된 확신을 줄이는 데 도움이 된다.

PPT 시각화:
- Prompt contract 5칸: `Goal`, `Context`, `Constraints`, `Output`, `Validation`

## Add-on Slide F4. Skill/Plugin은 team workflow를 포장하는 방식이다

화면 핵심:
- OpenAI Codex Skills는 반복 workflow를 재사용 가능한 instruction package로 만든다.
- Skill은 progressive disclosure 구조로 필요한 지식만 단계적으로 불러오는 방향이다.
- Plugin은 skill, MCP server, app integration 등을 배포하는 단위로 볼 수 있다.
- 팀 공통 업무는 prompt collection보다 skill package가 더 안정적이다.

발표자 노트:
세미나에서 skill을 너무 복잡하게 설명할 필요는 없다. 핵심은 "반복되는 성공 workflow를 문서화해서 agent가 다시 쓰게 하는 것"이다. 예를 들어 `rtl-log-triage`, `sdc-cleanup-planner`, `evidence-reviewer` 같은 skill은 개인 prompt보다 팀 품질 기준을 더 잘 담을 수 있다. Anthropic의 Agent Skills도 유사하게 instruction, resource, script, template를 묶는 패키지 개념을 제시한다. 이는 특정 vendor 기능 소개를 넘어 agent 시대의 공통 pattern으로 설명할 수 있다.

PPT 시각화:
- `1회성 prompt` vs `team skill package`
- Skill package 내부: `SKILL.md`, `examples`, `scripts`, `templates`, `checks`

## Add-on Slide F5. Agent improvement loop: trace, feedback, eval, repair

화면 핵심:
- OpenAI cookbook은 agent 개선을 trace, feedback, eval, Codex handoff의 loop로 설명한다.
- iterative repair loop는 `review -> repair -> validate` 구조다.
- 세미나 후에는 demo 자체보다 "개선 loop"를 남기는 것이 중요하다.
- 실패 사례도 asset이다. 반복 실패는 skill/rule/eval 후보가 된다.

발표자 노트:
agent 품질은 한 번에 완성되지 않는다. 중요한 것은 좋은 실패를 기록하는 것이다. agent가 어느 파일을 읽었는지, 어떤 가정을 했는지, 어떤 validation에서 틀렸는지 기록하면 다음 prompt, rule, skill, eval이 생긴다. 세미나의 목표도 "Codex가 한번에 다 한다"가 아니라 "작업을 더 빠르게 실험하고, 실패를 검증 가능한 형태로 남기고, 다음 실행을 개선한다"로 잡아야 한다.

PPT 시각화:
- Loop: `Trace -> Human/Model feedback -> Eval -> Codex fix -> New trace`
- 아래에 예시: `lint fail -> root cause note -> prompt rule -> regression pass`

## Add-on Slide F6. OKF는 agent-readable wiki를 파일 시스템으로 만드는 아이디어다

화면 핵심:
- Google Cloud의 Open Knowledge Format은 markdown + YAML frontmatter 기반의 portable knowledge format을 제안한다.
- 핵심은 vendor service가 아니라 파일, frontmatter, link, citation, version control이다.
- `type`, `title`, `description`, `resource`, `tags`, `timestamp` 같은 metadata가 agent retrieval을 도와준다.
- 문서 간 link가 knowledge graph 역할을 한다.

발표자 노트:
OKF를 소개하는 이유는 특정 Google 기술을 쓰자는 것이 아니다. 우리가 만들려는 SoC Knowledge DB와 LLM Wiki가 어떤 포맷이어야 오래가는지에 대한 힌트를 얻기 위해서다. 사람이 읽을 수 있고, agent가 parse할 수 있고, Git으로 version 관리가 되고, 특정 SaaS에 종속되지 않는 포맷이 중요하다. markdown + YAML + link 구조는 이 조건을 잘 만족한다.

PPT 시각화:
- File tree 예시:
  - `ip/uart.md`
  - `clock/reset_tree.md`
  - `constraints/sdc_policy.md`
  - `log.md`
  - `index.md`

## Add-on Slide F7. Obsidian Bases는 local markdown을 database처럼 보는 layer다

화면 핵심:
- Obsidian Bases는 local markdown note와 properties를 table/card 같은 view로 다룰 수 있게 한다.
- `.base` 파일은 YAML syntax로 view, filter, formula를 정의한다.
- Codex seminar 관점에서는 "agent-readable files + human-readable views" 조합이 중요하다.
- local-first 방식은 개인/팀 민감 지식 관리에 적합하다.

발표자 노트:
Obsidian Bases를 소개할 때는 "Obsidian을 반드시 쓰자"가 아니라 "지식 파일 위에 view layer를 얹는 방식"을 보여주면 된다. 같은 markdown knowledge가 Codex에게는 context source가 되고, 사람에게는 table/filter/dashboard가 된다. 예를 들어 IP별 owner, block status, known issue, validation command, related Jira, last reviewed date를 property로 관리하면, agent와 사람이 같은 자료를 다르게 소비할 수 있다.

PPT 시각화:
- 같은 markdown source에서 두 output:
  - Codex context
  - Obsidian table/card view

## Add-on Slide F8. Palantir Ontology analogy는 "데이터 + 행동"을 설명하기 좋다

화면 핵심:
- Palantir Ontology는 데이터를 단순 저장소가 아니라 운영 의사결정 model로 본다.
- Foundry는 data/logic/workflow 기반, AIP는 LLM/agent/tooling/eval layer, Apollo는 deployment/continuous delivery layer로 설명할 수 있다.
- Palantir 문서의 핵심은 ontology가 semantic layer와 action layer를 함께 가져야 한다는 점이다.
- SoC ontology도 block/property/link에서 멈추면 부족하고 action/evidence loop가 필요하다.

발표자 노트:
Palantir 사례는 회사 내부 도입을 주장하기 위한 것이 아니라 architecture analogy다. 많은 팀이 ontology를 "잘 정리된 용어집"으로 오해한다. 하지만 업무 자동화에서 진짜 ontology는 object, relation, rule, action, permission, audit이 연결되어야 한다. SoC Knowledge DB도 마찬가지다. IP block, clock, reset, interface, constraint, verification result가 연결되고, 그 위에서 log triage, review, validation, signoff action이 돌아가야 한다.

PPT 시각화:
- `Semantic model` 위에 `Action model`을 겹친 diagram
- `SoC object -> Evidence -> Decision -> Action -> Feedback`

## Add-on Slide F9. PowerPoint/Word generation도 agent workflow로 봐야 한다

화면 핵심:
- Microsoft PowerPoint Copilot Agent Mode는 prompt, clarifying question, outline, refine, slide generation, edit 흐름을 강조한다.
- 회사 template, referenced file permission, human review가 중요한 운영 조건이다.
- Claude Artifacts는 standalone content를 conversation과 분리해 반복 수정하는 pattern을 보여준다.
- Codex로 PPT/Word source를 만들 때도 outline, source, review checklist가 필요하다.

발표자 노트:
세미나 자료를 Codex로 만든다는 것도 좋은 demo다. 단, "AI가 예쁜 PPT를 만들어준다"가 핵심이 아니다. 핵심은 문서 생성도 agent workflow라는 점이다. source를 주고, outline을 만들고, review하고, slide text를 제한하고, 발표자 노트를 분리하고, 참고문헌을 남기는 흐름이 필요하다. 이 `codex_seminar.md` 파일 자체가 그 예시가 된다.

PPT 시각화:
- `Source notes -> Outline -> Slide bullets -> Speaker notes -> Review -> PPT`

## Add-on Slide F10. LazyCodex는 complex workflow harness 참고 사례다

화면 핵심:
- LazyCodex는 공식 Codex 기능이 아니라 third-party workflow package다.
- `$ulw-plan`, `$start-work`, `$ulw-loop` 같은 command로 계획, 실행, verified completion을 강조한다.
- 핵심 아이디어는 project memory, plan-before-edit, evidence gate, durable state다.
- 세미나에서는 이를 공식 Codex primitive로 재해석한다.

발표자 노트:
LazyCodex를 소개할 때는 도구 홍보처럼 말하지 않는 것이 좋다. 중요한 것은 third-party 생태계에서도 같은 문제가 반복된다는 점이다. 복잡한 codebase에서는 agent가 계획 없이 코드를 바꾸면 위험하다. 그래서 memory, plan, execution, verification, completion evidence를 묶는 harness가 나온다. 우리는 이 아이디어를 Codex의 Plan mode, AGENTS.md, skills, worktree, validation checklist로 구현하면 된다.

PPT 시각화:
- LazyCodex keyword를 오른쪽에 두고, 왼쪽에 Codex primitive mapping:
  - `Project memory -> AGENTS.md / local docs`
  - `Plan -> Plan mode`
  - `Evidence gate -> validation output`
  - `Durable state -> handoff / task log`

## Add-on Slide F11. Subagent는 많을수록 좋은 것이 아니라 역할이 선명해야 한다

화면 핵심:
- OpenAI subagents는 명시적으로 요청된 경우 병렬 전문 agent를 spawn하는 기능이다.
- subagent는 parent의 sandbox와 approval 설정을 상속한다.
- token cost가 증가하므로 비교/리서치/검증처럼 병렬 가치가 큰 곳에 써야 한다.
- RTL 업무에서는 `log triager`, `constraint reviewer`, `doc drafter`, `evidence checker` 정도가 후보 역할이다.

발표자 노트:
subagent는 강력하지만 남용하면 오히려 비용과 noise가 늘어난다. 세미나에서는 "역할 분리"가 핵심이다. 한 agent에게 모든 것을 시키는 대신, 독립적인 관점이 필요한 일을 나누는 것이다. 예를 들어 한 subagent는 lint log를 분류하고, 다른 subagent는 관련 RTL 파일을 읽고, 또 다른 subagent는 변경 없이 validation checklist를 만든다. 최종 decision은 coordinator가 evidence를 모아 사람에게 보여준다.

PPT 시각화:
- Center: `Coordinator`
- Around: `Log`, `RTL`, `SDC`, `Docs`, `Evidence`

## Add-on Slide F12. 세미나 메시지를 한 문장으로 정리하면

화면 핵심:
- Codex는 "개발자를 대체하는 자동 코더"보다 "검증 가능한 작업 loop를 빠르게 돌리는 agent workspace"에 가깝다.
- 실무 도입의 핵심은 prompt가 아니라 operating model이다.
- Operating model = context, rule, plan, permission, validation, review, artifact, feedback.
- 2개월 동안 남길 자산은 성공 prompt가 아니라 반복 가능한 workflow package다.

발표자 노트:
마지막 Q&A 전에 이 장표를 넣으면 전체 메시지가 정리된다. 참석자가 가져가야 할 것은 "Codex 명령어 몇 개"가 아니다. 본인 업무에서 어떤 작은 workflow를 agent loop로 바꿀 수 있는지다. 예를 들어 log triage, review summary, SDC check, guide draft, issue evidence collection처럼 작고 검증 가능한 task부터 시작한다. 성공 사례가 쌓이면 rule, skill, template, ontology로 승격한다.

PPT 시각화:
- 큰 문장 하나:
  - `Prompt collection -> Operating model -> Reusable workflow package`

---

# Appendix G. Web research 내용을 본문 슬라이드에 넣는 위치

| Research source | 본문 추천 위치 | 넣을 메시지 |
|---|---:|---|
| OpenAI Codex best practices | Slide 9, 10 | 복잡한 업무는 context와 plan이 먼저다. Prompt는 실행 계약서다. |
| OpenAI Codex app features | Slide 6, 7, 17 | Codex app은 thread/worktree/diff/terminal/artifact를 묶은 workspace다. |
| OpenAI Skills | Slide 13, 14 | 반복 업무는 prompt가 아니라 skill package로 승격한다. |
| OpenAI Subagents | Slide 19, 20, 21 | subagent는 명시적 병렬 역할 분리용이며 token/sandbox 비용을 고려해야 한다. |
| OpenAI cookbook agent loop | Slide 15, 16, 35 | trace, feedback, eval, repair loop가 품질 개선의 핵심이다. |
| Google OKF | Slide 27, 28, 29 | markdown + YAML + link는 portable knowledge graph의 최소 단위다. |
| Obsidian Bases | Slide 28 | local markdown knowledge를 사람이 table/view로 탐색하게 해준다. |
| Palantir Ontology/AIP | Slide 31, 32 | ontology는 data catalog가 아니라 action/evidence/decision loop다. |
| Microsoft PowerPoint Copilot | Slide 34 | deck generation도 outline, source, template, human review가 있는 workflow다. |
| Anthropic Skills/Artifacts | Slide 13, 34 | skill/artifact는 agent output을 재사용 가능한 단위로 분리하는 공통 패턴이다. |
| LazyCodex | Slide 21, Appendix C | third-party harness 사례로 plan, memory, evidence gate의 중요성을 보여준다. |

---

# Appendix H. Web research 기반 발표 멘트 확장본

## 1. Codex를 소개할 때 피해야 할 표현
- "AI가 코딩을 대신한다"는 표현은 반발을 부르기 쉽다.
- "검증 가능한 작업 loop를 빠르게 돌린다"가 더 정확하고 실무 친화적이다.
- RTL/design engineer에게는 자동 coding보다 evidence, review, regression, owner confirmation이 더 중요하다.

## 2. OKF/Obsidian/Palantir를 묶어 설명하는 문장
OKF는 지식의 file format 힌트, Obsidian Bases는 local markdown의 human view 힌트, Palantir Ontology는 data와 action을 연결하는 enterprise architecture 힌트다. 이 세 가지를 합치면 SoC Knowledge DB의 방향이 보인다. 사람이 읽는 문서, agent가 읽는 metadata, workflow가 남기는 evidence를 같은 knowledge system 안에 넣는 것이다.

## 3. Microsoft/Claude 사례를 넣는 이유
문서 생성 분야도 단순 생성에서 agentic workflow로 움직이고 있다. PowerPoint Copilot Agent Mode는 질문, outline, refinement, slide generation, human edit 흐름을 강조한다. Claude Artifacts는 긴 산출물을 대화와 분리된 reusable object로 다루는 방식을 보여준다. Codex seminar에서는 이 흐름을 PPT/Word/HTML 산출물 관리 방식으로 재해석하면 된다.

## 4. LazyCodex 사례를 조심스럽게 소개하는 방법
LazyCodex는 공식 OpenAI 문서가 아니므로 "참고 사례"로만 말한다. 다만 complex codebase에서 plan-before-edit, project memory, evidence gate, verified completion이 필요하다는 문제의식은 매우 유용하다. 회사 세미나에서는 특정 package 설치보다 이 원칙을 우리 업무 방식에 맞게 가져오는 것이 중요하다.

## 5. seminar의 최종 설득 구조
1. Codex는 coding answer machine이 아니라 작업 workspace다.
2. 실무 도입은 prompt가 아니라 rule, plan, skill, validation의 운영 체계다.
3. SoC/RTL 업무에는 ontology와 evidence loop가 특히 중요하다.
4. 2개월 동안 개인/팀 자산을 남기면 일회성 세미나가 아니라 capability build가 된다.

---

# Appendix I. Ultraresearch source map and 적용 결과

## Research method
- Date checked: 2026-06-23 KST
- Private local context was reviewed separately and is not listed in this shareable deck.
- Official Codex source route: current Codex manual fetched with the OpenAI docs helper, plus official developers.openai.com pages for app features, best practices, prompting, AGENTS.md, skills, subagents, worktrees, app-server, and open-source scope.
- External public sources checked for analogy only: Google OKF, Obsidian Bases, Palantir Ontology/AIP/Foundry/Apollo, Microsoft PowerPoint Copilot, Anthropic Agent Skills/Artifacts, LazyCodex.
- Privacy boundary: local private records were not promoted into slide text. The deck keeps only abstract task/concept names and public-safe workflow shapes.

## Main changes applied to the live slide body
| Area | Applied detail |
|---|---|
| Codex surfaces | App/CLI/IDE/cloud/app-server are framed by workflow and evidence path, not by feature list. |
| Prompting | Prompt is framed as an execution contract: Goal, Context, Constraints, Output, Validation, Done when. |
| Plan mode | Plan mode is framed as risk control with likely files, assumptions, validation, fallback, and human decision points. |
| Skills/plugins | Skill is workflow authoring; plugin is installable distribution. Repeated success and failure capture precede skill creation. |
| Evaluation | Quality threshold comes before token/tool/time optimization. Failures become FAQ, rules, skills, or eval cases. |
| RTL/IP | Added a concrete operating loop, do-not-infer boundaries, and a demo verification matrix for SDC/lint/compile/simulation. |
| Knowledge stack | OKF/Obsidian/HTML/PPT are positioned as views over canonical reviewed knowledge, not as the canonical source itself. |
| Palantir analogy | Reframed as object/action/evidence loop, not product-copying. |
| Company sharing | Added metadata-stub/reviewed-summary rules and `review required` handling for ambiguous content. |
| Closing | Summarized the operating model as context, rule, plan, permission, validation, review, artifact, feedback. |

## Source-to-slide map
| Source cluster | Supports |
|---|---|
| OpenAI Codex best practices and prompting | Slides 9, 10, 15, 16, 42, 43 |
| OpenAI Codex app, worktrees, review, CLI/IDE/cloud docs | Slides 6, 7, 17, 18, 21, 22 |
| OpenAI Codex AGENTS.md, Skills, Plugins, MCP, Subagents | Slides 12, 13, 14, 19, 20 |
| OpenAI Codex open-source page and openai/codex repo | Slide 23 |
| OpenAI cookbook agent improvement and iterative repair loops | Slides 15, 16, 35 |
| Google OKF spec/blog and Obsidian Bases docs | Slides 27, 28, 29 |
| Palantir Ontology/AIP/Foundry/Apollo docs | Slides 31, 32 |
| Microsoft PowerPoint Copilot and Anthropic Skills/Artifacts docs | Slide 34 and Appendix F9 |
| Private local context, abstracted for sharing | Slides 3, 29, 35, 40, 43 and the Appendix A program structure |

## Convergence summary
- Worker and web lanes converged on the same implementation target: keep the 43-slide structure stable, promote selected appendix detail into the body, and add source-backed operating detail.
- No source contradicted the main seminar thesis. The main caution is wording: avoid implying that LazyCodex, Palantir, Microsoft, Anthropic, Obsidian, or OKF are required for the Codex rollout.
- The remaining deck-production step is not more research; it is slide design and reduction for the actual 60-minute version.
