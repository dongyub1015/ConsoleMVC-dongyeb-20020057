# Phase 1 설계: 프로젝트 기반

**Phase:** 1 / 5
**목표:** 패키지 디렉터리 골격과 진입점·의존성 조립 파일의 스켈레톤 생성

---

## 1. 최종 디렉터리 구조

```
ConsoleMVC/
├── main.py
├── app.py
├── PRD.md
├── PLAN.md
├── docs/
│   └── design/
│       ├── phase1-foundation.md   ← 이 문서
│       ├── phase2-model.md
│       ├── phase3-view.md
│       ├── phase4-controller.md
│       └── phase5-integration.md
├── model/
│   └── __init__.py
├── controller/
│   └── __init__.py
└── view/
    └── __init__.py
```

> `model/`, `controller/`, `view/`의 소스 파일은 이후 Phase에서 추가된다.
> 이 Phase에서는 골격(디렉터리 + `__init__.py`)만 만든다.

---

## 2. 파일별 설계

### 2.1 `main.py`

**역할:** 프로세스의 유일한 진입점. 로직을 포함하지 않는다.

```python
from app import App

if __name__ == "__main__":
    App().run()
```

**설계 결정**
- `if __name__ == "__main__"` 가드를 사용해 모듈로 import 시 실행되지 않도록 한다.
- `App` 인스턴스 생성과 `run()` 호출만 존재한다. 예외 처리도 `App.run()` 내부에서 담당한다.
- 줄 수 제한: 5줄 이내 (PRD DoD #6).

---

### 2.2 `app.py`

**역할:** 의존성 조립(Dependency Injection Root). 세 계층의 인스턴스를 생성하고 연결한다.

```python
class App:
    def __init__(self) -> None:
        # Phase 2~4 완료 후 실제 인스턴스로 교체
        self._controller = None

    def run(self) -> None:
        if self._controller is None:
            print("[Phase 1] 스켈레톤 실행 — 아직 구현되지 않았습니다.")
            return
        self._controller.run()
```

**설계 결정**
- `App`은 계층을 소유하되, 어느 계층에도 속하지 않는 별도 조립 레이어다.
- Phase 5에서 `__init__`에 실제 Repository·View·Controller를 주입한다.
- `App`이 직접 비즈니스 로직을 수행하지 않는다.

**Phase 5 이후 최종 형태 (미리보기)**

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

---

### 2.3 각 패키지 `__init__.py`

세 패키지 모두 Phase 1에서는 빈 파일로 생성한다.

```python
# 내용 없음 — 패키지 선언 목적
```

**설계 결정**
- `__init__.py`에 클래스를 re-export하지 않는다. 각 모듈을 직접 import하는 명시적 방식을 채택한다.
  - 좋음: `from model.todo import Todo`
  - 피함: `from model import Todo` (암묵적 re-export)

---

## 3. 의존 관계 다이어그램

```
main.py
  └─ import ──► app.py (App)
                  │
                  │  [Phase 5 이후]
                  ├─ import ──► model.todo_repository.InMemoryTodoRepository
                  ├─ import ──► view.todo_view.TodoView
                  └─ import ──► controller.todo_controller.TodoController
```

Phase 1 완료 시점에서 `main.py → app.py` 연결만 실제로 동작한다.

---

## 4. 체크리스트

- [ ] `model/`, `controller/`, `view/` 디렉터리 생성
- [ ] `model/__init__.py`, `controller/__init__.py`, `view/__init__.py` 생성 (빈 파일)
- [ ] `docs/design/` 디렉터리 생성
- [ ] `main.py` 작성 (5줄 이내)
- [ ] `app.py` 스켈레톤 작성
- [ ] `python main.py` 실행 시 오류 없이 종료 확인
