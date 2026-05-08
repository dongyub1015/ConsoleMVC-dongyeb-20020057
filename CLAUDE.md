# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Python 3.10+ 콘솔 애플리케이션으로, **Model / Controller / View 계층 분리**를 목표로 한다.
외부 라이브러리 없이 표준 라이브러리만 사용한다.

기준 문서: `PRD.md` | 구현 계획: `PLAN.md` | 계층별 설계: `docs/design/phase*.md`

---

## 실행 방법

```bash
python main.py
```

---

## 아키텍처

### 계층 구조와 의존 방향

```
main.py  →  app.py (DI Root)
                ├→  model/       (도메인 엔티티 + 저장소)
                ├→  view/        (콘솔 출력 전담)
                └→  controller/  (입력 수신 + Model·View 조율)
```

의존 방향은 단방향: **Controller → Model**, **Controller → View**.
`model/`과 `view/`는 서로를, 그리고 `controller/`를 절대 import하지 않는다.

### 각 계층의 핵심 책임

| 계층 | 허용 | 금지 |
|------|------|------|
| `model/` | 도메인 상태 소유, 유효성 검사, CRUD | `print()`, `input()`, `controller.*`/`view.*` import |
| `view/` | `print()` 출력만 | `input()`, `model.*`/`controller.*` import |
| `controller/` | `input()` 수신, 흐름 제어, Model·View 조율 | `print()` 직접 호출 |
| `app.py` | 세 계층 인스턴스 생성 + DI 주입 | 비즈니스 로직 |
| `main.py` | `App().run()` 한 줄 | 그 외 모든 로직 |

### 핵심 클래스

- `model/todo.py` — `Todo` dataclass (`id`, `title`, `done`)
- `model/todo_repository.py` — `TodoRepository` ABC + `InMemoryTodoRepository`
- `view/todo_view.py` — `TodoView` (`show_menu`, `show_todo_list`, `show_success`, `show_error`)
- `controller/todo_controller.py` — `TodoController(repo, view)`, `run()` 메인 루프
- `app.py` — `App` (DI Root, 인스턴스 조립)

---

## 구현 Phase

Phase 2(Model)와 Phase 3(View)는 병렬 작업 가능. 나머지는 순서 의존.

```
Phase 1 (기반) → Phase 2 (Model) ─┐
               → Phase 3 (View)  ─┴→ Phase 4 (Controller) → Phase 5 (통합·DoD)
```

각 Phase 상세 설계: `docs/design/phase{1~5}-*.md`

---

## 계층 경계 위반 검증 (DoD)

코드 작성 후 아래 명령으로 계층 경계를 검증한다. **모두 결과가 없어야 한다.**

```bash
# view/ 에 input() 없음
grep -rn "input(" view/

# view/ 가 model·controller를 import하지 않음
grep -rn "from model\|from controller\|import model\|import controller" view/

# model/ 에 print·input 없음
grep -rn "print\|input(" model/

# model/ 이 controller·view를 import하지 않음
grep -rn "from controller\|from view\|import controller\|import view" model/

# controller/ 에 print() 직접 호출 없음
grep -rn "^\s*print(" controller/
```

---

## 설계 결정 사항 (변경 전 확인 필요)

- **Repository ABC 분리** — `TodoRepository`(ABC)와 `InMemoryTodoRepository`(구현체)를 분리해 두었으므로, 파일 기반 저장소 추가 시 ABC만 구현하면 된다. Controller는 항상 `TodoRepository` 타입으로만 참조한다.
- **`id` 생성 책임** — `Todo` 엔티티가 ID를 자체 생성하지 않는다. `repo.save()` 내부에서 `_next_id`를 부여한다.
- **View의 타입 힌트** — `show_todo_list`의 파라미터는 `list`(또는 `Protocol` 기반 `_TodoLike`)로 선언해 `model` import를 피한다. `list[Todo]`로 바꾸면 계층 경계 규칙 위반이다.
- **`input()` 집중** — `input()` 호출은 `TodoController._prompt_int()`와 `add_todo()` title 입력, 두 곳에만 존재한다.
- **`match-case` 사용** — `run()` 메뉴 분기는 Python 3.10+ `match-case`로 작성한다.
