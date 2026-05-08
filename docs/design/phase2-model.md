# Phase 2 설계: Model 계층

**Phase:** 2 / 5
**목표:** 도메인 엔티티(`Todo`)와 인메모리 저장소(`InMemoryTodoRepository`)를 구현한다.
**선행 조건:** Phase 1 완료 (패키지 디렉터리 존재)

---

## 1. 파일 목록

| 파일 | 역할 |
|------|------|
| `model/todo.py` | `Todo` 엔티티 dataclass |
| `model/todo_repository.py` | 저장소 인터페이스 + 인메모리 구현체 |

---

## 2. `model/todo.py` 설계

### 2.1 클래스 다이어그램

```
Todo
├── id: int
├── title: str
└── done: bool = False
```

### 2.2 설계 결정

| 결정 사항 | 선택 | 이유 |
|-----------|------|------|
| 클래스 형태 | `@dataclass` | 보일러플레이트 제거, `__eq__`·`__repr__` 자동 생성 |
| 불변성 | `frozen=False` | `done` 필드를 완료 처리 시 변경해야 함 |
| `id` 생성 | Repository가 부여 | 엔티티가 자기 ID를 생성하면 저장소와 강결합 발생 |
| 유효성 검사 위치 | `__post_init__` | 잘못된 상태의 `Todo`가 존재하지 못하게 막는 fail-fast 전략 |

### 2.3 유효성 검사 규칙

| 필드 | 규칙 | 위반 시 |
|------|------|--------|
| `title` | 빈 문자열(`""`) 또는 공백만인 경우 거부 | `ValueError("title must not be blank")` |
| `id` | 생성자 직접 호출 시 0 이하 거부 | `ValueError("id must be positive")` |

### 2.4 구현 코드

```python
from dataclasses import dataclass


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError("id must be positive")
        if not self.title or not self.title.strip():
            raise ValueError("title must not be blank")
```

---

## 3. `model/todo_repository.py` 설계

### 3.1 책임 분리 구조

저장소를 **추상 인터페이스**와 **구현체** 두 클래스로 나눈다.

```
TodoRepository (ABC)        InMemoryTodoRepository
  find_all()          ◄──────── find_all()
  find_by_id(id)      ◄──────── find_by_id(id)
  save(todo)          ◄──────── save(todo)
  update(todo)        ◄──────── update(todo)
  delete(id)          ◄──────── delete(id)
```

> PRD OQ-1(파일 기반 저장소 확장)을 고려해 ABC를 지금 정의한다.
> Controller는 항상 `TodoRepository` 타입으로만 참조한다.

### 3.2 `TodoRepository` — 추상 인터페이스

```python
from abc import ABC, abstractmethod
from model.todo import Todo


class TodoRepository(ABC):

    @abstractmethod
    def find_all(self) -> list[Todo]: ...

    @abstractmethod
    def find_by_id(self, id: int) -> Todo | None: ...

    @abstractmethod
    def save(self, todo: Todo) -> Todo: ...

    @abstractmethod
    def update(self, todo: Todo) -> Todo: ...

    @abstractmethod
    def delete(self, id: int) -> bool: ...
```

### 3.3 `InMemoryTodoRepository` — 인메모리 구현체

**내부 자료구조:** `dict[int, Todo]` — ID를 키로 사용해 O(1) 조회.

**`_next_id` 전략:** 현재 저장된 최대 ID + 1. 삭제 후 재사용하지 않는다(단순성 우선).

```python
class InMemoryTodoRepository(TodoRepository):

    def __init__(self) -> None:
        self._store: dict[int, Todo] = {}
        self._next_id: int = 1

    def find_all(self) -> list[Todo]:
        return list(self._store.values())

    def find_by_id(self, id: int) -> Todo | None:
        return self._store.get(id)

    def save(self, todo: Todo) -> Todo:
        todo.id = self._next_id
        self._next_id += 1
        self._store[todo.id] = todo
        return todo

    def update(self, todo: Todo) -> Todo:
        if todo.id not in self._store:
            raise KeyError(f"Todo id={todo.id} not found")
        self._store[todo.id] = todo
        return todo

    def delete(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True
```

### 3.4 메서드별 계약 (Pre/Post Condition)

| 메서드 | Pre-condition | 반환 | 예외 |
|--------|--------------|------|------|
| `find_all()` | 없음 | 저장된 모든 Todo 리스트 (순서 미보장) | 없음 |
| `find_by_id(id)` | 없음 | `Todo` 또는 `None` | 없음 |
| `save(todo)` | `todo.title` 비어 있지 않음 | ID가 부여된 `todo` | 없음 |
| `update(todo)` | `todo.id`가 저장소에 존재 | 업데이트된 `todo` | `KeyError` |
| `delete(id)` | 없음 | 삭제 성공 여부 `bool` | 없음 |

---

## 4. 의존 관계

```
model/todo.py
  └─ 의존: 표준 라이브러리(dataclasses)만

model/todo_repository.py
  └─ 의존: abc, model.todo
  └─ 금지: controller.*, view.*
```

---

## 5. DoD 검증 명령

```bash
# print / input 없음 확인
grep -rn "print\|input(" model/

# controller·view import 없음 확인
grep -rn "from controller\|from view\|import controller\|import view" model/
```

두 명령 모두 결과가 없어야 한다.

---

## 6. 체크리스트

- [ ] `model/todo.py` 작성 — `Todo` dataclass + `__post_init__` 유효성 검사
- [ ] `model/todo_repository.py` 작성 — `TodoRepository` ABC
- [ ] `model/todo_repository.py` 작성 — `InMemoryTodoRepository` 구현
- [ ] REPL에서 CRUD 전 과정 동작 확인
- [ ] DoD #4, #5 grep 검증 통과
