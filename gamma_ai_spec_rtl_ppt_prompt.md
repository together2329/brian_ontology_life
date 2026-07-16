# Gamma PPT 생성 프롬프트

다음 내용으로 한국어 세미나 발표용 PPT를 만들어줘.

디자인 톤:
- 깔끔한 기술 세미나 스타일
- 과한 마케팅 느낌보다 실무 회고와 workflow 중심
- 차분한 배경, 선명한 타이포그래피, 다이어그램 중심
- 내부 프로젝트명, 로컬 경로, 회사/개인 식별자는 넣지 말 것
- 너무 단정적인 표현은 피하고, "볼 수 있다", "도움이 된다", "고민해볼 수 있다" 같은 회고 톤 사용

발표 제목:
AI로 Spec을 만들고 RTL을 생성하는 과정에서 겪은 시행착오

부제:
AI 기반 개발에서 사람이 설계해야 할 context, 검증, 리뷰, 지식화 loop

전체 메시지:
구현 비용이 낮아지면서 더 많은 후보를 빠르게 실험할 수 있게 되었다. 다만 AI가 만든 구현이 단순한 실험으로 끝나지 않으려면, 요구, 가정, 계약, 근거, 검증, 결정을 다음 작업으로 이어주는 구조가 필요하다.

슬라이드 구성:

1. Title
   - AI로 Spec을 만들고 RTL을 생성하는 과정에서 겪은 시행착오
   - AI 기반 개발에서 고민해야 할 것들
   - 키워드: Spec, RTL, Verification, Agent Loop, Ontology

2. Starting Point
   - 예전에는 구현에 드는 비용이 컸다
   - 그래서 계획, 문서화, 리뷰 순서가 매우 중요했다
   - 지금은 AI로 구현 후보를 빠르게 만들 수 있다
   - 새로운 질문: 빨라진 구현을 어떻게 검증 가능한 학습 loop로 만들 것인가?

3. 바뀐 병목
   - 병목이 "코드를 쓰는 시간"에서 "가정과 검증을 관리하는 시간"으로 이동한다
   - Spec의 모호함, RTL의 암묵적 가정, Test의 coverage gap이 더 빨리 드러난다
   - 중요한 것은 많이 만드는 것 자체보다, 무엇을 배웠는지 남기는 방식이다

4. Codex/AI 기본 loop
   - Thread: 한 작업의 기억 단위
   - Plan: 구현 전 가정과 순서를 정리
   - Goal: 긴 작업 동안 유지되는 완료 기준
   - 발표 문장: AI를 잘 쓰는 것은 명령어를 많이 아는 것보다 작업 loop를 설계하는 감각에 가깝다

5. Agent를 역할로 나누기
   - Main agent: 요구, 결정, 최종 산출물 관리
   - Explorer/Subagent: 큰 repo, spec, log, RTL/TB를 read-only로 탐색
   - Reviewer: reset, handshake, width, evidence gap 확인
   - Worker: 제한된 candidate 구현
   - 주의: 역할이 많아지면 coordination cost도 같이 생긴다

6. Skill, Hook, Rule
   - Skill: 반복 workflow를 절차로 저장
   - Hook: agent loop 중간에 자동 검사/기록을 끼우는 지점
   - Rule: 위험 command와 외부 side effect를 제어하는 guardrail
   - 예시: RTL review checklist, log triage, evidence summary, git push 확인

7. 시행착오 1: 바로 구현하면 가정이 섞일 수 있다
   - 초기 요구가 짧거나 압축되어 있으면 RTL 후보가 내부 가정을 품기 쉽다
   - header format, packet size, handshake timing, interrupt/error behavior 같은 항목은 먼저 질문으로 분리하는 편이 좋다
   - 메시지: Spec 단계에서 모호함을 줄이고, 구현 후보는 그 가정을 확인하는 도구로 쓰는 흐름이 도움이 된다

8. 시행착오 2: Agent가 빨라질수록 혼란도 빨라질 수 있다
   - agent loop, parser, tool call, streaming, memory, subagent가 모두 새로운 failure mode를 만들 수 있다
   - context pollution, stale state, hallucinated observation, infinite loop 같은 문제가 생길 수 있다
   - 메시지: 구현 속도를 높이면 다음 병목은 loop control, context, verification, memory가 된다

9. 병렬 실험의 사용법
   - worktree와 subagent로 후보를 많이 돌려본다
   - 단, 하나하나 깊게 리뷰하면 많은 테스트를 못 한다
   - main thread는 raw log보다 action table과 decision table을 받아야 한다
   - 비교 기준: correctness, verification cost, PPA trade-off, maintainability

10. 온톨로지 기반 개발 기본 개념
   - 요구 문장 -> 요구 원자 -> 의무 -> 계약 -> 근거 -> 검증 -> 결정
   - 목적은 거창한 지식 그래프가 아니라, 실험 결과를 다음 loop의 입력으로 남기는 것
   - Requirement Atom: event, condition, response, timing을 가진 작은 요구
   - Contract Candidate: RTL/TB/review가 공유할 관찰 가능한 약속
   - Evidence: command, log, waveform, assertion, review note
   - Validation: evidence가 요구와 계약을 실제로 확인하는지 보는 단계

11. RTL/Spec 데모 workflow
   - Spec 초안 입력
   - /plan으로 ambiguity, assumption, owner decision 분리
   - /goal로 contract candidate, RTL skeleton, test checklist, review risk 정의
   - subagent로 spec trace, RTL risk, test gap 병렬 분석
   - evidence/validation 정리
   - 반복된 판단은 rule, skill, wiki로 업데이트

12. Takeaways
   - AI 이후 구현 비용은 낮아졌지만, 판단과 검증의 중요성은 줄지 않았다
   - 더 많이 실험하려면 더 좋은 loop control이 필요하다
   - Spec과 RTL은 한 번에 끝나는 산출물이라기보다, evidence와 decision을 통해 선명해지는 계약으로 볼 수 있다
   - 최종 목표는 "AI가 대신 만든 RTL"보다 "다음 설계가 더 나아지는 개발 지식"이다

시각 자료 제안:
- Slide 3: 병목 이동 다이어그램
- Slide 4: Thread -> Plan -> Goal -> Review -> Next turn loop
- Slide 5: Main agent와 subagent 역할 분리
- Slide 10: Requirement -> Contract -> Evidence -> Validation -> Decision flow
- Slide 11: Spec draft -> ambiguity question -> RTL skeleton -> test/check -> review -> rule/skill/wiki update pipeline

발표 시간:
- 20~30분용
- 각 slide는 bullet을 너무 많이 넣지 말고, 발표자가 말로 풀 수 있게 핵심 문장 중심으로 구성
