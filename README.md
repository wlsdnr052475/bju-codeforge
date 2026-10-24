# BJU CodeForge

개인이 직접 사용하고 장기적으로 발전시킬 AI 코딩 에이전트입니다.
Windows 11에서 실행하는 **Python/PySide6 데스크톱 프로그램**이며,
웹 서버나 브라우저 UI를 사용하지 않습니다.

현재 범위는 **MVP 1: 기본 GUI와 Mock AI**입니다. 실제 언어 모델 없이
메시지 전달과 응답 표시 흐름을 검증하는 단계입니다. 최신 구현 상태와
실제 테스트 결과는 [PROGRESS.md](PROGRESS.md)를 확인하세요.

## MVP 1 기능과 범위

- 프로그램 이름, 사용자 메시지 영역, AI 응답 영역, 입력창, 전송 버튼.
- 전송 버튼 또는 Enter로 메시지 전송. 빈 메시지는 보내지 않습니다.
- Mock Provider가 입력 내용과 관계없이 정해진 테스트 응답을 반환합니다.
- Provider 호출을 백그라운드 스레드에서 실행하여 GUI 이벤트 처리를 유지합니다.
- 처리 중 중복 전송 방지, 오류 표시, 작업 종료 후 입력 복구.
- 작업 중 창을 닫으면 종료 대기 상태를 표시하고, 작업이 끝난 뒤 자동으로 닫습니다.
- 입력과 응답을 일반 텍스트로 표시하며 명령이나 HTML로 실행하지 않습니다.
- Provider/핵심 로직/GUI를 분리하고 자동 테스트와 Ruff 검사를 제공합니다.

대화는 현재 창의 메모리에만 존재합니다. 설정 저장, 대화 저장, 프로젝트 파일
접근, 파일 수정·삭제, 셸 명령 실행 기능은 없습니다.

**이번 단계에서 제외:** 실제 Strata 연결, Qwen 실행, GPU 가속, 코드 자동 수정,
파일 관리 에이전트, GitHub 자동 연동, RAG/벡터 데이터베이스, 모델 미세조정,
복잡한 플러그인 구조, exe 패키징.

## 기술 스택과 개발 환경

| 구분 | 구성 |
| --- | --- |
| 언어 | Python 3.11 이상 |
| GUI | PySide6 6.8 이상, 7 미만 |
| 패키지 | `src` 구조, `pyproject.toml`, setuptools |
| 테스트 | pytest, PySide6 QtTest, offscreen 플랫폼 |
| 코드 검사 | Ruff |
| 개발/자동 검증 | Codex Cloud의 Linux 환경 |
| 최종 실행/수동 검증 | 사용자 Windows 11 데스크톱 |

MVP 1에는 모델 가중치, API 키, 추론 서버, GPU 드라이버 설정이 필요하지 않습니다.
사용자 데스크톱은 Ryzen 5 5500X3D, Radeon RX 9070 XT 16GB, DDR4 32GB,
SATA 500GB + M.2 1TB 구성입니다. 해당 하드웨어의 실제 모델 실행과 GPU 성능은
향후 데스크톱에서 검증하며, 클라우드 테스트 결과로 대신하지 않습니다.

## AI 시스템 구조

현재 구현 흐름:

```text
PySide6 GUI → 백그라운드 작업 → ChatAgent → LLMProvider → MockProvider
```

`ChatAgent.send_message()`가 사용자 메시지를 검증하고
`LLMProvider.generate(message)`를 호출합니다. Provider는 메시지를 받아 문자열을
반환하는 인터페이스입니다. 핵심 로직과 Provider에는 PySide6 의존성이 없고,
GUI는 생성 시 전달받은 에이전트를 사용합니다.

향후 방향은 `GUI → 에이전트 → Provider → 로컬 추론 엔진 → Qwen`입니다.
승인된 작업 도구는 에이전트 계층에 별도로 연결할 예정입니다. 추론 엔진은
Strata를 우선 검토하되 API 지원 범위와 통신 방식은 통합 단계에서 확인합니다.
Provider 구현을 교체하여 Ollama 등 다른 엔진에도 연결할 수 있도록 분리합니다.
LLM이나 추론 엔진 자체를 개발하지 않습니다.

## 디렉터리 구성

```text
bju-codeforge/
├── pyproject.toml
├── .gitignore
├── README.md
├── AGENTS.md
├── PROGRESS.md
├── .agents/skills/bju-codeforge-verify/SKILL.md
├── src/bju_codeforge/
│   ├── __init__.py
│   ├── __main__.py
│   ├── core/agent.py
│   ├── providers/base.py
│   ├── providers/mock.py
│   └── gui/
│       ├── app.py
│       └── main_window.py
└── tests/
```

사용자 설정과 프로젝트 데이터는 향후 소스 코드 및 서로의 저장 위치와 분리합니다.
현재는 저장 기능을 구현하지 않습니다. 가상환경, 캐시, 빌드 산출물 및 민감한
로컬 설정은 Git 추적에서 제외합니다.

## Windows 11 설치와 실행

Python 3.11 이상을 설치하고, 저장소를 내려받은 폴더에서 PowerShell을 엽니다.
아래 명령은 가상환경을 활성화하지 않아도 실행할 수 있습니다.

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m bju_codeforge
```

`py -3 --version`이 3.11 미만이면 지원되는 Python을 먼저 설치하세요.
실행만 필요한 경우 개발 도구를 제외하고 `-m pip install -e .`로 설치할 수 있습니다.
이미 가상환경을 활성화했다면 동일한 진입점인 `python -m bju_codeforge`를 사용합니다.

창의 입력란에 한국어 또는 영어 메시지를 입력하고 전송 버튼이나 Enter를 누릅니다.
사용자 영역에는 입력이, AI 영역에는 고정된 Mock 응답이 표시됩니다.
창을 닫으면 현재 대화가 사라집니다.

## Linux 클라우드 개발 환경

저장소 루트에서 실행합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
```

화면이 있는 Linux 환경에서는 `.venv/bin/python -m bju_codeforge`로 실행할 수 있습니다.
`offscreen`은 화면 없는 환경의 자동 테스트용이며 실제 창을 보여 주지 않습니다.
Qt 공유 라이브러리 또는 플랫폼 플러그인 로딩에 실패하면 오류를 환경 문제로
기록하고 필요한 시스템 라이브러리를 확인하세요. 해당 실패를 GUI 검증 통과로
처리하지 않습니다.

## Windows 자동 테스트와 수동 검증

PowerShell에서 다음 명령을 실행합니다.

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m bju_codeforge
```

자동 테스트는 Mock 응답, 입력 전달, 응답 검증, 핵심 모듈의 Qt 독립성,
GUI 생성과 메시지 전송 및 백그라운드 처리 흐름을 확인합니다.
마지막 실행 전 `QT_QPA_PLATFORM`을 제거해야 실제 데스크톱 창이 표시됩니다.

Windows 11에서 별도로 확인할 항목:

- 설치 및 `python -m bju_codeforge` 실행, 창 제목과 필수 UI 표시.
- 한국어 입력기, 한글·영문 표시, 전송 버튼과 Enter 동작.
- 빈 입력 방지, 반복 전송과 Mock 응답 표시.
- 창 크기 변경, 배율/DPI에 따른 글자와 레이아웃 표시.
- 창 이동/닫기 및 재실행 시 충돌 여부.

오류 복구와 느린 작업 중 응답성은 테스트용 Provider로 자동 검증합니다.
고정 Mock 응답은 즉시 반환되므로 일반 실행만으로 장시간 추론을 검증할 수 없습니다.
실행 중인 Provider를 강제로 중단하는 기능은 없으므로, 향후 실제 Provider를
연결할 때는 통신 타임아웃과 취소 정책을 함께 설계해야 합니다.
Windows GUI 수동 조작과 GPU/모델 성능은 클라우드 offscreen 테스트의 검증 범위에
포함되지 않습니다.

## 개발 규칙과 향후 방향

[AGENTS.md](AGENTS.md)에 개발·안전 규칙을 기록하고,
[검증 스킬](.agents/skills/bju-codeforge-verify/SKILL.md)로 변경 후 절차를 재사용합니다.
파일 도구를 추가하는 단계에서는 허용 작업 폴더 제한, 경로 탐색 및 심볼릭 링크
이탈 방지, 변경 전 diff, 중요한 변경·삭제에 대한 사용자 승인을 먼저 구현해야 합니다.

장기 목표는 자연어 대화, 프로젝트 구조 분석, 코드 생성·수정 제안, 승인 후 변경,
테스트/오류 분석, 파일 탐색, GitHub 연동, 이력·문맥·로그·설정 관리, 기능 모듈의
활성화/비활성화, 도구 확장 및 제한된 자율 코딩입니다. 이 목표들은 MVP 1에
구현하지 않습니다. 실행 파일 또는 설치 프로그램 배포도 향후 단계입니다.

**다음 단계는 Windows 11 데스크톱에서 MVP 1 실행 검증입니다.**
발견된 문제를 기록하고 수정한 뒤, 별도 요청에 따라 다음 개발 범위를 결정합니다.
