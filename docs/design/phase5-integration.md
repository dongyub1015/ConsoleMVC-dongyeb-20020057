# Phase 5 설계: 통합 및 DoD 검증

**Phase:** 5 / 5
**목표:** `app.py`에서 세 계층을 조립하고, PRD의 DoD 7개 항목을 전부 통과한다.
**선행 조건:** Phase 1~4 모두 완료

---

## 1. 이 Phase에서 변경되는 파일

| 파일 | 변경 내용 |
|------|----------|
| `app.py` | 스켈레톤 → 실제 DI 조립 완성 |
| `main.py` | Phase 1 스켈레톤 확인·동결 |

새로 생성되는 파일은 없다.

---

## 2. `app.py` — 최종 구현

### 2.1 역할

`App`은 어느 계층에도 속하지 않는 **조립 레이어**다.
세 계층의 인스턴스를 생성하고 의존성을 주입한 뒤, Controller의 진입점을 실행한다.

### 2.2 의존 방향

```
app.py
  ├─ import ──► model.todo_repository.InMemoryTodoRepository
  ├─ import ──► view.todo_view.TodoView
  └─ import ──► controller.todo_controller.TodoController
```

`app.py`는 세 계층 모두를 알아야 하는 유일한 파일이다. 이 지점이 DI Root다.

### 2.3 구현 코드

```python
from model.todo_repository import InMemoryTodoRepository
from view.todo_view import TodoView
from controller.todo_controller import TodoController


class App:
    def __init__(self) -> None:
        repo = InMemoryTodoRepository()
        view = TodoView()
        self._controller = TodoController(repo, view)

    def run(self) -> None:
        self._controller.run()
```

**설계 결정**
- `App.__init__`에서만 `new`(인스턴스 생성)가 일어난다. 나머지 모든 곳은 주입받은 객체를 사용한다.
- 미래에 `JsonFileTodoRepository`로 교체하려면 `repo = ...` 한 줄만 바꾸면 된다.

---

## 3. `main.py` — 최종 확인

```python
from app import App

if __name__ == "__main__":
    App().run()
```

- 5줄 이내 (PRD DoD #6 충족).
- `app.run()` 외 로직 없음.

---

## 4. 최종 패키지 구조 확인

Phase 5 완료 시 예상 구조:

```
ConsoleMVC/
├── main.py
├── app.py
├── PRD.md
├── PLAN.md
├── docs/
│   └── design/
│       ├── phase1-foundation.md
│       ├── phase2-model.md
│       ├── phase3-view.md
│       ├── phase4-controller.md
│       └── phase5-integration.md
├── model/
│   ├── __init__.py
│   ├── todo.py
│   └── todo_repository.py
├── controller/
│   ├── __init__.py
│   └── todo_controller.py
└── view/
    ├── __init__.py
    └── todo_view.py
```

---

## 5. DoD 검증 절차

### DoD #1 — 패키지 디렉터리 존재

```bash
# Windows PowerShell
Test-Path model, controller, view
```

세 경로 모두 `True`여야 한다.

---

### DoD #2 — `view/`에 `input()` 없음

```bash
grep -rn "input(" view/
```

출력 결과가 없어야 한다.

---

### DoD #3 — `view/`가 `model`·`controller`를 import하지 않음

```bash
grep -rn "from model\|from controller\|import model\|import controller" view/
```

출력 결과가 없어야 한다.

---

### DoD #4 — `model/`에 `print`·`input` 없음

```bash
grep -rn "print\|input(" model/
```

출력 결과가 없어야 한다.

---

### DoD #5 — `model/`이 `controller`·`view`를 import하지 않음

```bash
grep -rn "from controller\|from view\|import controller\|import view" model/
```

출력 결과가 없어야 한다.

---

### DoD #6 — `main.py` 10줄 이내, `app.run()` 외 로직 없음

```bash
# 줄 수 확인
(Get-Content main.py).Count   # PowerShell
wc -l main.py                 # bash
```

10 이하여야 한다. 코드 리뷰로 로직 부재 확인.

---

### DoD #7 — Todo CRUD 콘솔 동작 확인

수동 실행 시나리오:

```
$ python main.py

[시나리오 1: 목록 조회 — 빈 상태]
선택 >> 1
(등록된 항목이 없습니다)

[시나리오 2: 항목 추가]
선택 >> 2
제목 입력: 장보기
[완료] 항목이 추가되었습니다.

선택 >> 2
제목 입력: 청소하기
[완료] 항목이 추가되었습니다.

[시나리오 3: 목록 조회]
선택 >> 1
 ID  상태  제목
 --  ----  --------------------
  1  [ ]   장보기
  2  [ ]   청소하기

[시나리오 4: 완료 처리]
선택 >> 3
완료할 ID: 1
[완료] ID 1 항목을 완료했습니다.

선택 >> 1
 ID  상태  제목
 --  ----  --------------------
  1  [v]   장보기
  2  [ ]   청소하기

[시나리오 5: 삭제]
선택 >> 4
삭제할 ID: 2
[완료] ID 2 항목이 삭제되었습니다.

[시나리오 6: 종료]
선택 >> 0
[완료] 프로그램을 종료합니다.
```

모든 시나리오가 예시와 동일하게 동작해야 한다.

---

## 6. 에지 케이스 확인 목록

| 케이스 | 입력 | 기대 출력 |
|--------|------|----------|
| 빈 제목 추가 | `add_todo` → title 입력에 Enter | `[오류] 제목을 입력해야 합니다.` |
| 존재하지 않는 ID 완료 | `complete_todo` → ID=99 | `[오류] 해당 ID를 찾을 수 없습니다.` |
| 존재하지 않는 ID 삭제 | `delete_todo` → ID=99 | `[오류] 해당 ID를 찾을 수 없습니다.` |
| 메뉴에서 문자 입력 | `run()` → "abc" | `[오류] 숫자를 입력해야 합니다.` (재입력 요청) |
| 메뉴에서 범위 밖 숫자 | `run()` → "9" | `[오류] 올바른 번호를 입력하세요.` |

---

## 7. 통합 후 의존 관계 최종 정리

```
main.py
  └─► app.py (App)
         ├─► model/todo_repository.py (InMemoryTodoRepository)
         │       └─► model/todo.py (Todo)
         ├─► view/todo_view.py (TodoView)
         └─► controller/todo_controller.py (TodoController)
                  ├─► model/todo_repository.py (TodoRepository)
                  ├─► model/todo.py (Todo)
                  └─► view/todo_view.py (TodoView)

허용된 방향만 존재하며, 역방향(View→Model 등) 의존 없음.
```

---

## 8. 체크리스트

- [ ] `app.py` 실제 DI 조립 완성
- [ ] `main.py` 최종 확인 (줄 수, 내용)
- [ ] DoD #1 패키지 구조 확인
- [ ] DoD #2 grep 통과
- [ ] DoD #3 grep 통과
- [ ] DoD #4 grep 통과
- [ ] DoD #5 grep 통과
- [ ] DoD #6 줄 수 + 코드 리뷰
- [ ] DoD #7 CRUD 전 시나리오 수동 실행 완료
- [ ] 에지 케이스 6개 항목 확인
