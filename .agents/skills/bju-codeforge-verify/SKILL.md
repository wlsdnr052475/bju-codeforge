---
name: bju-codeforge-verify
description: BJU CodeForge 코드 변경 후 관련 pytest 테스트와 Ruff 검사를 실행하고 클라우드 결과 및 Windows 11 검증 상태를 PROGRESS.md에 기록한다.
---

# BJU CodeForge 변경 검증

저장소 루트에서 실행한다. 별도 검증 스크립트나 외부 서비스를 추가하지 않는다.
가상환경이 없으면 README.md의 운영체제별 설치 절차로 생성하고
`python -m pip install -e ".[dev]"`로 설치한다. 아래 명령은 가상환경을 직접
지정하므로 활성화가 필요 없다.

1. **AGENTS.md 확인**
   - 현재 개발 범위, Python 규칙, GUI/핵심 로직 분리, 파일 수정 안전 규칙을 읽는다.
   - 사용자 요청 범위를 확인하며 별도 요청 없이 MVP 1 이후 기능을 구현하지 않는다.

2. **PROGRESS.md 확인**
   - 현재 단계, 기존 실패, 미해결 문제, 데스크톱 검증 상태를 읽는다.
   - 이전 실행의 성공을 현재 변경에 대한 검증으로 취급하지 않는다.

3. **변경한 파일 파악**
   - `git status --short`, `git diff --stat`, `git diff`, `git diff --cached`로
     추적/스테이징 변경을 확인하고, `git ls-files --others --exclude-standard`로
     새 파일도 확인한다.
   - 이미 커밋한 작업이면 명시한 기준 브랜치와의 diff도 확인한다.
   - 사용자 변경을 보존하고 테스트 범위를 정한다.

4. **관련 테스트 실행**
   - Linux 클라우드의 전체 MVP 1 테스트:

     ```bash
     QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
     ```

   - Windows PowerShell:

     ```powershell
     $env:QT_QPA_PLATFORM = "offscreen"
     .\.venv\Scripts\python.exe -m pytest -q
     Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
     ```

   - 변경에 맞는 테스트를 먼저 선택하려면 `pytest -q` 뒤에 실제 테스트 경로를
     지정한다. 완료 전 변경 영향에 필요한 회귀 테스트를 실행한다.
   - Mock 응답, 사용자 입력 전달, 응답 처리, GUI 요소 및 핵심 모듈 독립성이
     검증되는지 확인한다. 실패한 테스트를 임의로 제거하거나 건너뛰지 않는다.

5. **Ruff 코드 검사**
   - Linux:

     ```bash
     .venv/bin/python -m ruff check .
     .venv/bin/python -m ruff format --check .
     ```

   - Windows PowerShell:

     ```powershell
     .\.venv\Scripts\python.exe -m ruff check .
     .\.venv\Scripts\python.exe -m ruff format --check .
     ```

6. **실패 원인 확인**
   - 명령의 종료 코드와 오류를 확인하고 구현 오류와 환경 오류를 구분한다.
   - Qt 플랫폼 플러그인/시스템 라이브러리 문제도 실패 또는 검증 불가로 기록한다.
   - 승인된 범위의 문제를 수정한 경우 관련 검사를 재실행한다. 무조건적인 스킵,
     오류 무시, 실행하지 않은 성공 기록은 금지한다.

7. **클라우드 검증 결과 기록**
   - 실제 실행 명령, Python/PySide6 버전, 테스트 통과·실패 수, Ruff 결과 및
     실패 원인을 수집한다. 실제 실행 환경이 Windows면 Windows 결과로 명시한다.
   - `구현 완료`, `클라우드 테스트 통과`, `클라우드 테스트 실패`를 구분한다.
     실행하지 못한 검사는 실행하지 못했다고 쓴다.

8. **데스크톱 검증 필요 사항 확인**
   - Windows 11 설치/모듈 실행, 한국어 입력, 버튼/Enter 전송, DPI/레이아웃,
     창 종료와 재실행 등 변경 영향에 해당하는 항목을 정리한다.
   - 화면 검증 전 `QT_QPA_PLATFORM`을 제거하고 README.md의 실제 실행 명령을 쓴다.
   - 직접 확인하지 않은 항목은 `데스크톱 검증 대기`로 유지한다.
     `데스크톱 검증 통과`는 실제 데스크톱에서 확인된 결과에만 사용한다.
   - Strata/Qwen/GPU 성능은 MVP 1의 대상이 아니며 클라우드에서 검증했다고
     기록하지 않는다.

9. **PROGRESS.md 갱신**
   - 현재 단계, 완료 기능, 진행 중인 작업, 남은 작업, 실제 검사 결과,
     발견된 문제, 데스크톱 상태 및 다음 단계 한 가지를 갱신한다.
   - 수정 후 보고 내용과 실제 결과가 일치하는지 확인한다.
   - AGENTS.md의 완료 보고 형식으로 한국어 보고를 작성하고 MVP 1 범위에서 멈춘다.
