# Phase 3 설계: View 계층

**Phase:** 3 / 5
**목표:** 콘솔 출력을 전담하는 `TodoView`를 구현한다. 어느 계층에도 의존하지 않는다.
**선행 조건:** Phase 1 완료 (패키지 디렉터리 존재)
**병렬 가능:** Phase 2와 동시에 진행 가능 (상호 의존 없음)

---

## 1. 파일 목록

| 파일 | 역할 |
|------|------|
| `view/todo_view.py` | 콘솔 출력 전담 클래스 |

---

## 2. `TodoView` 설계

### 2.1 클래스 개요

```
TodoView
├── show_menu() -> None
├── show_todo_list(todos: list) -> None
├── show_todo_detail(todo) -> None      # 선택적
├── show_success(message: str) -> None
└── show_error(message: str) -> None
```

**핵심 제약**
- 모든 `print()` 호출은 이 클래스에서만 이루어진다.
- 상태(인스턴스 변수)를 보유하지 않는다 — 메서드는 순수 출력 함수다.
- `input()` 호출 금지.
- `model.*`, `controller.*` import 금지.

---

## 3. 메서드별 상세 설계

### 3.1 `show_menu()`

콘솔에 번호 메뉴를 출력한다.

**출력 예시**
```
========== Todo 관리 ==========
  1. 목록 보기
  2. 항목 추가
  3. 항목 완료
  4. 항목 삭제
  0. 종료
==============================
선택 >>
```

**설계 결정:** 메뉴 문자열은 상수(`_MENU`)로 분리해 테스트 시 변경 없이 재사용한다.

```python
_MENU = """\
========== Todo 관리 ==========
  1. 목록 보기
  2. 항목 추가
  3. 항목 완료
  4. 항목 삭제
  0. 종료
==============================
선택 >> """
```

---

### 3.2 `show_todo_list(todos: list)`

Todo 목록을 테이블 형태로 출력한다.

**파라미터:** `todos` — `Todo` 객체 리스트 (또는 `id`, `title`, `done` 속성을 가진 객체)

**출력 예시 — 항목 있음**
```
ID  상태  제목
--  ----  --------------------
 1  [ ]   장보기
 2  [v]   청소하기
 3  [ ]   독서
```

**출력 예시 — 항목 없음**
```
(등록된 항목이 없습니다)
```

**설계 결정**
- `done=True`이면 `[v]`, `done=False`이면 `[ ]` 표시.
- 정렬: ID 오름차순 (Controller가 정렬된 리스트를 전달하거나, View 내부에서 `sorted(todos, key=lambda t: t.id)` 정렬).

```python
def show_todo_list(self, todos: list) -> None:
    if not todos:
        print("(등록된 항목이 없습니다)")
        return
    print(f"{'ID':>3}  {'상태':<4}  제목")
    print(f"{'--':>3}  {'----':<4}  {'-' * 20}")
    for todo in sorted(todos, key=lambda t: t.id):
        status = "[v]" if todo.done else "[ ]"
        print(f"{todo.id:>3}  {status:<4}  {todo.title}")
```

---

### 3.3 `show_success(message: str)`

성공 메시지를 출력한다.

**출력 예시**
```
[완료] 항목이 추가되었습니다.
```

```python
def show_success(self, message: str) -> None:
    print(f"[완료] {message}")
```

---

### 3.4 `show_error(message: str)`

오류 메시지를 출력한다.

**출력 예시**
```
[오류] 해당 ID를 찾을 수 없습니다.
```

```python
def show_error(self, message: str) -> None:
    print(f"[오류] {message}")
```

---

## 4. 전체 구현 스켈레톤

```python
class TodoView:

    _MENU = """\
========== Todo 관리 ==========
  1. 목록 보기
  2. 항목 추가
  3. 항목 완료
  4. 항목 삭제
  0. 종료
==============================
선택 >> """

    def show_menu(self) -> None:
        print(self._MENU, end="")

    def show_todo_list(self, todos: list) -> None:
        if not todos:
            print("(등록된 항목이 없습니다)")
            return
        print(f"{'ID':>3}  {'상태':<4}  제목")
        print(f"{'--':>3}  {'----':<4}  {'-' * 20}")
        for todo in sorted(todos, key=lambda t: t.id):
            status = "[v]" if todo.done else "[ ]"
            print(f"{todo.id:>3}  {status:<4}  {todo.title}")

    def show_success(self, message: str) -> None:
        print(f"[완료] {message}")

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")
```

---

## 5. 타입 힌트 전략

`show_todo_list`의 파라미터 타입을 `list[Todo]`로 지정하면 `view/todo_view.py`가 `model.todo`를 import해야 한다. 이는 PRD의 "View는 model에 의존하지 않는다" 규칙을 위반한다.

**해결 방법: 구조적 타이핑(덕 타이핑) 활용**

```python
from typing import Protocol

class _TodoLike(Protocol):
    id: int
    title: str
    done: bool
```

`Protocol`은 `typing` 표준 라이브러리에 포함되므로 외부 의존이 발생하지 않는다. `show_todo_list(self, todos: list[_TodoLike])`로 선언하면 `Todo` 객체를 넘겨도 타입 검사를 통과하면서 실제 import는 없다.

> 단순성 우선 원칙에 따라 초기에는 `list` (타입 없음) 또는 `list[Any]`로 작성하고,
> 타입 엄격성이 필요한 시점에 `Protocol`로 격상한다.

---

## 6. 의존 관계

```
view/todo_view.py
  └─ 의존: 표준 라이브러리(typing 선택적)만
  └─ 금지: model.*, controller.*
```

---

## 7. DoD 검증 명령

```bash
# input() 없음 확인
grep -rn "input(" view/

# model·controller import 없음 확인
grep -rn "from model\|from controller\|import model\|import controller" view/
```

두 명령 모두 결과가 없어야 한다.

---

## 8. 체크리스트

- [ ] `view/todo_view.py` 작성 — `TodoView` 클래스
- [ ] `show_menu()` — 메뉴 상수 분리 후 출력
- [ ] `show_todo_list()` — 빈 목록 분기 + 테이블 포맷
- [ ] `show_success()`, `show_error()` — 접두사 포함 출력
- [ ] Python REPL에서 각 메서드 직접 호출해 출력 포맷 확인
- [ ] DoD #2, #3 grep 검증 통과
