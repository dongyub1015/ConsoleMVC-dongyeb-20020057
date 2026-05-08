# PLAN: Python Console MVC 구현 계획

**기준 문서:** PRD.md
**작성일:** 2026-05-08

---

## 전체 Phase 요약

| Phase | 이름 | 산출물 | 설계 문서 |
|-------|------|--------|----------|
| 1 | 프로젝트 기반 | 디렉터리 골격, `main.py`, `app.py` 스켈레톤 | `docs/design/phase1-foundation.md` |
| 2 | Model 계층 | `model/todo.py`, `model/todo_repository.py` | `docs/design/phase2-model.md` |
| 3 | View 계층 | `view/todo_view.py` | `docs/design/phase3-view.md` |
| 4 | Controller 계층 | `controller/todo_controller.py` | `docs/design/phase4-controller.md` |
| 5 | 통합 및 DoD 검증 | `app.py` 완성, `main.py` 완성, DoD 체크리스트 통과 | `docs/design/phase5-integration.md` |

> 각 Phase는 이전 Phase의 산출물이 완성된 후 시작한다.
> Phase 2·3는 서로 의존이 없으므로 병렬 작업 가능.

---

## Phase 1 — 프로젝트 기반

**목표:** 패키지 디렉터리 골격과 진입점·의존성 조립 파일의 스켈레톤을 만든다.

**작업 목록**

- [ ] `model/`, `controller/`, `view/`, `docs/design/` 디렉터리 생성
- [ ] 각 패키지에 빈 `__init__.py` 생성
- [ ] `main.py` 스켈레톤 작성 (`app.run()` 호출만 포함)
- [ ] `app.py` 스켈레톤 작성 (빈 `App` 클래스 + `run()` 메서드 시그니처)

**완료 기준**
- `python main.py` 실행 시 오류 없이 종료된다.
- 세 패키지 디렉터리가 각각 `__init__.py`를 보유한다.

**설계 문서:** [`docs/design/phase1-foundation.md`](docs/design/phase1-foundation.md)

---

## Phase 2 — Model 계층

**목표:** 도메인 엔티티와 인메모리 저장소를 구현한다.

**작업 목록**

- [ ] `model/todo.py` — `Todo` dataclass 구현 (필드: `id`, `title`, `done`)
  - `__post_init__` 에서 `title` 빈 문자열 유효성 검사
- [ ] `model/todo_repository.py` — `InMemoryTodoRepository` 구현
  - `find_all`, `find_by_id`, `save`, `update`, `delete` 5개 메서드
  - `_next_id` 자동 증가 로직
- [ ] 모델 파일에 `print` / `input` / `controller` / `view` import 없음 확인

**완료 기준**
- `Todo(id=1, title="test")` 생성 정상 동작.
- `InMemoryTodoRepository`로 CRUD 전 과정이 Python REPL에서 동작 확인.
- PRD DoD #4, #5 통과.

**설계 문서:** [`docs/design/phase2-model.md`](docs/design/phase2-model.md)

---

## Phase 3 — View 계층

**목표:** 콘솔 출력을 전담하는 View를 구현한다. Model·Controller에 의존하지 않는다.

**작업 목록**

- [ ] `view/todo_view.py` — `TodoView` 클래스 구현
  - `show_menu()` — 번호 메뉴 출력
  - `show_todo_list(todos)` — 목록 테이블 출력
  - `show_success(message)` — 성공 메시지 출력
  - `show_error(message)` — 오류 메시지 출력
- [ ] View 파일에 `input()` / `model` / `controller` import 없음 확인

**완료 기준**
- `TodoView` 인스턴스를 생성하고 각 메서드를 직접 호출해 출력 포맷 확인.
- PRD DoD #2, #3 통과.

**설계 문서:** [`docs/design/phase3-view.md`](docs/design/phase3-view.md)

---

## Phase 4 — Controller 계층

**목표:** 사용자 입력을 받아 Model을 조작하고, 결과를 View에 위임하는 Controller를 구현한다.

**작업 목록**

- [ ] `controller/todo_controller.py` — `TodoController` 클래스 구현
  - 생성자: `(repo: TodoRepository, view: TodoView)` DI 주입
  - `run()` — 메인 루프 (메뉴 표시 → 입력 → 분기 → 반복)
  - `list_todos()` — 전체 조회 후 View 위임
  - `add_todo()` — 제목 입력 → 저장 → 결과 View 위임
  - `complete_todo()` — ID 입력 → 완료 처리 → 결과 View 위임
  - `delete_todo()` — ID 입력 → 삭제 → 결과 View 위임
  - `_prompt_int(prompt)` — 정수 입력 보조 메서드 (재입력 루프 포함)
- [ ] Controller 파일에 `print()` 없음 확인

**완료 기준**
- `TodoController`를 `InMemoryTodoRepository` + `TodoView`로 초기화해 `run()` 실행 시 메뉴가 표시된다.
- 각 메뉴 기능이 정상 동작한다.

**설계 문서:** [`docs/design/phase4-controller.md`](docs/design/phase4-controller.md)

---

## Phase 5 — 통합 및 DoD 검증

**목표:** 모든 계층을 `app.py`에서 조립하고, PRD DoD 7개 항목을 전부 통과한다.

**작업 목록**

- [ ] `app.py` — `App` 클래스 완성
  - `__init__`: Repository, View, Controller 인스턴스 생성
  - `run()`: `controller.run()` 호출
- [ ] `main.py` — 10줄 이내 진입점 완성
- [ ] DoD 검증 스크립트(grep) 실행 및 전 항목 통과 확인
- [ ] `python main.py` 통합 실행으로 전체 CRUD 흐름 수동 확인

**완료 기준 (PRD DoD 전체)**

| # | 검증 명령 / 방법 | 결과 |
|---|----------------|------|
| 1 | 디렉터리 구조 확인 | [ ] |
| 2 | `grep -rn "input()" view/` → 결과 없음 | [ ] |
| 3 | `grep -rn "from model\|from controller" view/` → 결과 없음 | [ ] |
| 4 | `grep -rn "print\|input" model/` → 결과 없음 | [ ] |
| 5 | `grep -rn "from controller\|from view" model/` → 결과 없음 | [ ] |
| 6 | `main.py` 10줄 이내, `app.run()` 외 로직 없음 | [ ] |
| 7 | 콘솔에서 CRUD 4가지 기능 수동 동작 확인 | [ ] |

**설계 문서:** [`docs/design/phase5-integration.md`](docs/design/phase5-integration.md)

---

## 의존성 그래프

```
Phase 1 (기반)
    ├── Phase 2 (Model)   ──┐
    └── Phase 3 (View)   ──┤
                            ▼
                       Phase 4 (Controller)
                            │
                            ▼
                       Phase 5 (통합)
```

Phase 2와 Phase 3는 Phase 1 완료 후 병렬로 진행 가능.
Phase 4는 Phase 2·3 모두 완료 후 시작.
Phase 5는 Phase 4 완료 후 시작.
