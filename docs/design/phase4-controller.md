# Phase 4 설계: Controller 계층

**Phase:** 4 / 5
**목표:** 사용자 입력을 수신하고 Model을 조작한 뒤 View에 결과를 위임하는 `TodoController`를 구현한다.
**선행 조건:** Phase 2 (Model), Phase 3 (View) 완료

---

## 1. 파일 목록

| 파일 | 역할 |
|------|------|
| `controller/todo_controller.py` | 메인 루프, 입력 처리, Model·View 조율 |

---

## 2. `TodoController` 설계

### 2.1 생성자 — 의존성 주입

```python
class TodoController:
    def __init__(
        self,
        repo: TodoRepository,
        view: TodoView,
    ) -> None:
        self._repo = repo
        self._view = view
```

**설계 결정**
- Repository와 View를 생성자로 주입받는다(DI). Controller가 직접 인스턴스를 만들지 않는다.
- `_repo`와 `_view`는 private 필드로 외부에서 접근하지 않는다.

---

### 2.2 `run()` — 메인 루프

```
run()
  └─ while True
        ├─ view.show_menu()
        ├─ _prompt_int("선택 >> ")
        ├─ match 입력값
        │    ├─ 1 → list_todos()
        │    ├─ 2 → add_todo()
        │    ├─ 3 → complete_todo()
        │    ├─ 4 → delete_todo()
        │    ├─ 0 → break (종료)
        │    └─ _ → view.show_error("올바른 번호를 입력하세요.")
        └─ (반복)
```

**설계 결정**
- `match-case`(Python 3.10+)를 사용해 분기 의도를 명확히 한다.
- `0` 입력 시 루프를 종료하며 `view.show_success("프로그램을 종료합니다.")`를 출력한다.

```python
def run(self) -> None:
    while True:
        self._view.show_menu()
        choice = self._prompt_int()
        match choice:
            case 1: self.list_todos()
            case 2: self.add_todo()
            case 3: self.complete_todo()
            case 4: self.delete_todo()
            case 0:
                self._view.show_success("프로그램을 종료합니다.")
                break
            case _:
                self._view.show_error("올바른 번호를 입력하세요.")
```

---

### 2.3 `list_todos()`

```
list_todos()
  ├─ repo.find_all()
  └─ view.show_todo_list(todos)
```

```python
def list_todos(self) -> None:
    todos = self._repo.find_all()
    self._view.show_todo_list(todos)
```

---

### 2.4 `add_todo()`

```
add_todo()
  ├─ input("제목 입력: ").strip()
  ├─ [유효성] 빈 문자열 → view.show_error() + return
  ├─ Todo(id=0, title=title) 생성
  │     └─ id는 repo.save()가 부여하므로 임시값 사용
  ├─ repo.save(todo)
  └─ view.show_success("항목이 추가되었습니다.")
```

**설계 결정**
- `Todo` 생성 시 `id=0`을 임시로 넘기지 않고, Repository의 `save()`가 ID를 부여하는 책임을 가지도록 한다. `save()` 내부에서 `todo.id`를 덮어쓴다.
- Controller에서 `ValueError`를 catch해 View로 위임한다.

```python
def add_todo(self) -> None:
    title = input("제목 입력: ").strip()
    if not title:
        self._view.show_error("제목을 입력해야 합니다.")
        return
    try:
        from model.todo import Todo
        todo = Todo(id=0, title=title)
        self._repo.save(todo)
        self._view.show_success("항목이 추가되었습니다.")
    except ValueError as e:
        self._view.show_error(str(e))
```

> `Todo(id=0, ...)` 호출 시 `__post_init__`의 `id <= 0` 검사를 통과하도록
> Phase 2에서 `save()` 호출 전에 id를 부여하거나, 검사 기준을 조정한다.
> **대안:** `save()`가 title만 받아 내부에서 `Todo`를 생성하는 팩토리 방식으로 변경.
> (Phase 2 설계 시 최종 결정)

---

### 2.5 `complete_todo()`

```
complete_todo()
  ├─ _prompt_int("완료할 ID: ")
  ├─ repo.find_by_id(id)
  │    └─ None → view.show_error("해당 ID를 찾을 수 없습니다.") + return
  ├─ todo.done = True
  ├─ repo.update(todo)
  └─ view.show_success(f"ID {id} 항목을 완료했습니다.")
```

```python
def complete_todo(self) -> None:
    todo_id = self._prompt_int("완료할 ID: ")
    todo = self._repo.find_by_id(todo_id)
    if todo is None:
        self._view.show_error("해당 ID를 찾을 수 없습니다.")
        return
    todo.done = True
    self._repo.update(todo)
    self._view.show_success(f"ID {todo_id} 항목을 완료했습니다.")
```

---

### 2.6 `delete_todo()`

```
delete_todo()
  ├─ _prompt_int("삭제할 ID: ")
  ├─ repo.delete(id)
  │    ├─ True  → view.show_success("삭제되었습니다.")
  │    └─ False → view.show_error("해당 ID를 찾을 수 없습니다.")
```

```python
def delete_todo(self) -> None:
    todo_id = self._prompt_int("삭제할 ID: ")
    if self._repo.delete(todo_id):
        self._view.show_success(f"ID {todo_id} 항목이 삭제되었습니다.")
    else:
        self._view.show_error("해당 ID를 찾을 수 없습니다.")
```

---

### 2.7 `_prompt_int(prompt: str)` — 보조 메서드

정수가 입력될 때까지 재입력을 요청한다.

```python
def _prompt_int(self, prompt: str = "선택 >> ") -> int:
    while True:
        raw = input(prompt).strip()
        if raw.lstrip("-").isdigit():
            return int(raw)
        self._view.show_error("숫자를 입력해야 합니다.")
```

**설계 결정**
- `int(raw)` 실패 가능성을 `try/except` 대신 `isdigit()` 전처리로 방어한다.
- 음수 입력도 `int`로 변환 후 `match-case`의 `_` 분기에서 처리된다.
- `input()` 호출은 이 메서드와 `add_todo()`의 title 입력 두 곳에만 집중된다.

---

## 3. 전체 의존 관계

```
controller/todo_controller.py
  ├─ import ──► model.todo_repository.TodoRepository
  ├─ import ──► model.todo.Todo
  └─ import ──► view.todo_view.TodoView

  금지:
  └─ print() 직접 호출 금지
  └─ 다른 Controller import 금지
```

---

## 4. 예외 처리 전략

| 예외 발생 위치 | 처리 방법 |
|--------------|----------|
| `Todo.__post_init__` (ValueError) | Controller에서 catch → `view.show_error()` |
| `repo.update()` (KeyError) | Controller에서 catch → `view.show_error()` |
| 정수 파싱 실패 | `_prompt_int()`에서 재입력 루프로 처리 |
| 예상치 못한 예외 | `run()` 최상위에서 catch → `view.show_error()` 후 루프 유지 |

---

## 5. 시퀀스 다이어그램 — `add_todo()` 흐름

```
사용자          Controller          Model(repo)       View
  │                 │                    │               │
  │─ "2" 입력 ────►│                    │               │
  │                 │─ input("제목") ──►│               │
  │─ "장보기" ─────►│                   │               │
  │                 │─ Todo(title) ─────►│               │
  │                 │─ repo.save(todo) ──►│               │
  │                 │◄── todo(id=1) ─────│               │
  │                 │──────────────────────── show_success()►│
  │                 │                    │               │─ print("[완료]...")►│
```

---

## 6. DoD 검증 명령

```bash
# print() 직접 호출 없음 확인
grep -rn "^\s*print(" controller/
```

결과가 없어야 한다.

---

## 7. 체크리스트

- [ ] `controller/todo_controller.py` 작성 — `TodoController` 클래스
- [ ] `__init__`: DI 주입 (`repo`, `view`)
- [ ] `run()`: `match-case` 메인 루프
- [ ] `list_todos()`: 전체 조회 + View 위임
- [ ] `add_todo()`: 입력 → 저장 → View 위임
- [ ] `complete_todo()`: ID 입력 → 완료 처리 → View 위임
- [ ] `delete_todo()`: ID 입력 → 삭제 → View 위임
- [ ] `_prompt_int()`: 정수 재입력 루프
- [ ] `InMemoryTodoRepository` + `TodoView` 조합으로 `run()` 수동 실행 확인
