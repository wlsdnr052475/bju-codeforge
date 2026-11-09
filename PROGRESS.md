# BJU CodeForge 진행 상황

## 현재 작업 — Windows 실행 파일 (2026-11-09, Asia/Seoul)

- 사용자 요청: 기존 디자인을 유지한 채 더블 클릭으로 실행할 수 있는 `.exe` 생성.
- 작업 브랜치: `codex/windows-exe` (기존 MVP 커밋 `37e61ac` 기반).
- 구현 완료: Windows x64 PyInstaller 단일 파일 빌드 설정, 실제 프로그램의
  `--smoke-test` 경로, 검증 테스트 5개, 사용/개발 문서.
- 클라우드 테스트 통과: Linux에서 `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q`
  실행 결과 **24 passed in 1.31s**. 실패/스킵 0개.
- `.venv/bin/python -m ruff check .`: **All checks passed!**
- `.venv/bin/python -m ruff format --check .`: **20 files already formatted**.
- `git diff --check`: 통과.
- Linux 검증 환경: Python 3.12.14 / PySide6 6.12.0 / pytest 9.1.1 / Ruff 0.17.2.
- 진행 중인 작업: 없음. 실행 파일 생성 및 다운로드 제공 완료.
- 클라우드 테스트 통과 (Windows): Python 3.12.10 x64 / PySide6 6.12.0 /
  PyInstaller 6.22.3 / pytest 9.2.0 / Ruff 0.17.4, `windows-2022` 러너.
  `python -m pytest -q` **24 passed in 1.46s**. Ruff 검사/포맷 검사 모두 통과.
- Windows 빌드/자동 검증 통과: PyInstaller 단일 실행 파일 생성 후, 소스 폴더 밖의
  `BJU 실행 확인` 경로에서 `BJU-CodeForge.exe --smoke-test` 실행.
  Qt Windows 플랫폼의 실제 창 생성, 한국어 메시지 전송, 정확한 Mock 응답,
  입력 복구, 정상 창 종료와 프로세스 종료 코드 0을 확인했다.
- 최종 클라우드 테스트 실패: Linux/Windows 모두 실패 0개, 스킵 0개.
- [Windows 빌드/검증 기록](https://github.com/wlsdnr052475/bju-codeforge/actions/runs/42561343783)
  / [검증된 실행파일 ZIP 다운로드](https://github.com/wlsdnr052475/bju-codeforge/actions/runs/42561343783/artifacts/13648848965).
- 빌드 소스 커밋: `7298a9d800301d9ffd9ed54a9d9c10035e353654`.
  이후 문서 커밋은 결과 기록만 변경하며 실행 코드/빌드 설정은 동일하다.
- 산출물: `BJU-CodeForge-Windows-x64.zip` (49,049,879 bytes, 약 46.8 MiB).
  ZIP 안에 `BJU-CodeForge.exe`, `README.txt`, `build-info.json`, `SHA256SUMS.txt` 포함.
- ZIP SHA-256: `45aab45737e2e02b130e80c6644c23c740ff3ce9a8b2f545841df25eae5da034`.
  EXE의 SHA-256은 ZIP에 동봉한 `SHA256SUMS.txt`에 기록된다.
- GitHub Actions artifact 보관 만료 예정: 2027-02-07 (Asia/Seoul). 이후 새 빌드 필요.
- 데스크탑 검증 대기: 사용자 Windows 11에서 압축 해제, 더블 클릭, 한글 입력,
  버튼/Enter 전송, DPI/화면, 종료/재실행을 확인해야 한다.
- 현재 미해결 구현 결함은 발견되지 않았다. 실행파일은 코드 서명되지 않는다.
- 남은 구현 작업: 이번 실행파일 패키징 범위에서는 없음.
- 다음 단계 한 가지: 사용자 Windows 11에서 실행 파일 수동 검증.

아래는 기존 MVP 1 완료 당시의 기록이다. 실행 파일 패키징은 이후 사용자 요청으로
추가된 범위이며, 아래 당시의 제외 항목은 현재 패키징 작업을 제한하지 않는다.

## 이전 MVP 1 기록 (2026-10-24)

- 현재 단계: MVP 1 구현 및 클라우드 자동 검증 완료 (2026-10-24, Asia/Seoul)
- 작업 브랜치: `codex/mvp1-desktop-mock`
- 기준: GitHub `wlsdnr052475/bju-codeforge`, `main`의 초기 커밋 `5955b2a`.

## 상태

| 구분 | 상태 |
| --- | --- |
| 구현 완료 | MVP 1의 프로젝트 구성, GUI, Mock Provider, 테스트, 문서 완료 |
| 클라우드 테스트 통과 | pytest 19개 통과, Ruff 검사 및 포맷 검사 통과 |
| 클라우드 테스트 실패 | 최종 실행에서 실패 0개, 건너뛴 테스트 0개 |
| 데스크탑 검증 대기 | Windows 11 실기 검증 필요 |
| 데스크탑 검증 통과 | 확인하지 않음 |

## 완료한 기능
- `src` 패키지, `pyproject.toml`, Git 제외 규칙, `python -m bju_codeforge` 진입점.
- 프로그램 이름, 사용자 메시지/AI 응답 영역, 입력창, 전송 버튼을 갖춘 PySide6 GUI.
- 버튼/Enter 전송, 빈 입력 차단, 입력과 응답의 일반 텍스트 표시.
- Qt에 의존하지 않는 ChatAgent, 교체 가능한 LLMProvider 계약, 고정 Mock 응답.
- 메시지 검증, Provider 호출, 유효 응답 처리 및 오류 전달.
- QThread 기반 호출, 중복 전송 방지, 오류 후 입력 복구와 재시도.
- 요청 처리 중 창 닫기를 보류하고 스레드 종료 후 창을 닫는 수명 관리.
- README.md, AGENTS.md, 재사용 가능한 `bju-codeforge-verify` 검증 스킬.
- 핵심 로직, GUI, 모듈 진입점 자동 테스트.

## 진행 중인 작업
- 없음. MVP 1 구현을 마무리하고 Windows 11 사용자 검증을 기다린다.

## 남은 개발 작업
- 현재 범위에서 확인된 미완료 구현 없음.
- Windows 11에서 발견되는 문제는 실제 결과를 받은 뒤 수정한다.
- 실제 Strata/Qwen 연결, GPU 가속, 파일/명령 도구, exe 패키징 등은 범위 밖이다.

## 테스트 결과

환경: Codex Cloud Linux x86_64, Python 3.12.14, PySide6 6.12.0,
pytest 9.1.1, Ruff 0.17.2. 아래 명령은 저장소 루트에서 실행했다.

| 실행 명령 | 실제 결과 |
| --- | --- |
| `PIP_CACHE_DIR=/workspace/.cache/pip .venv/bin/python -m pip install -e '.[dev]'` | 개발용 editable 설치 성공, bju-codeforge 0.1.0 |
| `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q` | **19 passed in 0.35s**, 종료 코드 0 |
| `.venv/bin/python -m ruff check .` | **All checks passed!**, 종료 코드 0 |
| `.venv/bin/python -m ruff format --check .` | **18 files already formatted**, 종료 코드 0 |
| `git diff --check` | 공백 오류 없음, 종료 코드 0 |

검증한 동작:
- 고정 Mock 응답, 공백 정규화와 입력 전달, 빈 입력 거부, 응답 검증, 오류 전달.
- PySide6 import를 차단한 별도 Python 프로세스에서 핵심 로직 독립 실행.
- 기본 Qt 위젯 생성, 버튼/Enter 전송, HTML 형태 문자열의 일반 텍스트 보존.
- 제어 가능한 느린 Provider로 GUI 타이머 반응, 다른 스레드 실행,
  중복 전송 방지, 오류 후 재시도, 작업 중 창 닫기를 검증.
- 별도 프로세스에서 모듈 진입점을 실행하고 실제 Qt 이벤트 루프에서 창 생성과
  정상 종료를 확인. 강제 종료를 성공으로 취급하지 않음.

최종 테스트 실패/스킵 없음. 위 결과는 offscreen 자동 검증이며 실제 화면 조작이나
Windows 호환성 검증을 대신하지 않는다.

## 발견된 문제
- 현재 자동 테스트와 코드 검토에서 미해결 애플리케이션 결함은 발견되지 않았다.
- 향후 Provider가 반환하지 않으면 종료 대기가 계속될 수 있다. 실제 Provider를
  도입할 때 요청 시간 제한과 취소 정책이 필요하며 현재 Mock에는 네트워크 호출이 없다.
- 환경의 최초 기본 샌드박스 Git 연결은 프록시 접근 실패였으며, 네트워크 권한을
  지정한 재실행으로 원격 `main` 확인을 완료했다. 설치/테스트에는 미해결 차단 없음.

## 데스크탑 검증 상태
- **데스크탑 검증 대기**. Windows 11에서 실행하거나 수동 조작하지 않았다.
- README의 PowerShell 절차에 따른 설치와 `python -m bju_codeforge` 실행.
- 한글 입력기, 한글/영문 표시, 버튼/Enter 전송, 빈 입력 차단, 반복 대화.
- 창 크기 조절, DPI/배율, 창 이동/종료/재실행 시 충돌 여부.
- Windows 환경의 pytest와 Ruff 실행. 실제 창 확인 전 `QT_QPA_PLATFORM` 제거.
- 실제 Strata API, Qwen, AMD GPU는 MVP 1 범위 밖이며 검증하지 않음.

## 다음 단계
- **Windows 11 데스크탑에서 MVP 1 수동 실행 검증**.
- 별도 요청 전 다음 기능 개발 단계로 진행하지 않는다.
