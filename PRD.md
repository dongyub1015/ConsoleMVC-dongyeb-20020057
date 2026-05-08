# PRD: Python Console MVC — 패키지 구조와 역할 분리 완성

**작성일:** 2026-05-08
**상태:** 초안

---

## 1. 목표

Python 콘솔 애플리케이션에서 **Model / Controller / View 패키지를 명확히 분리**하고, 각 계층이 자신의 책임 범위만 담당하도록 구조를 완성한다.
- 어느 계층도 다른 계층의 내부 구현에 직접 접근하지 않는다.
- 각 파일을 읽었을 때 그 역할이 즉시 자명해야 한다.
- 계층 간 의존 방향은 단방향(Controller → Model, Controller → View)을 유지한다.

---

## 2. 배경 및 문제 정의

콘솔 기반 Python 프로젝트는 초기에 단일 스크립트로 작성되는 경우가 많아, 시간이 지날수록 비즈니스 로직·입력 처리·출력 처리가 혼재된다. 이로 인해:

- 로직 변경이 출력 코드를 파괴하거나 그 반대 현상이 발생한다.
- 단위 테스트 작성이 어렵다 (입력·출력이 로직에 엉켜 있음).
- 새 기능 추가 위치가 불명확해 코드가 비대해진다.

본 프로젝트는 이 문제를 해결하는 **MVC 패턴의 표준 Python 콘솔 구현체**를 목표로 한다.

---

## 3. 범위

| 포함 | 제외 |
|------|------|
| 패키지 디렉터리 구조 설계 | 데이터베이스 연동 |
| 각 계층의 기본 클래스·인터페이스 정의 | 웹/GUI 인터페이스 |
| 계층 간 데이터 전달 규약 | 인증·권한 관리 |
| 진입점(`main.py`) 및 의존성 조립(`app.py`) | 외부 API 호출 |
| 예시 도메인 (Todo 목록 CRUD) | 프레임워크 수준의 라우터 |

---

## 4. 패키지 구조

```
ConsoleMVC/
├── main.py                  # 진입점 — app.run() 한 줄만 존재
├── app.py                   # 의존성 조립 (DI Root)
├── PRD.md
│
├── model/
│   ├── __init__.py
│   ├── todo.py              # Todo 도메인 엔티티
│   └── todo_repository.py   # 저장소 인터페이스 + 인메모리 구현
│
├── controller/
│   ├── __init__.py
│   └── todo_controller.py   # 사용자 명령 → Model 조작 → View 호출
│
└── view/
    ├── __init__.py
    └── todo_view.py         # 콘솔 출력 전담 (print 는 여기서만)
```

> `model/`, `controller/`, `view/`는 각각 독립 Python 패키지이며
> 서로의 파일을 직접 `import`하는 것은 Controller만 허용된다.

---

## 5. 계층별 역할과 책임

### 5.1 Model

**책임:** 도메인 상태와 비즈니스 규칙을 소유한다.

| 항목 | 규칙 |
|------|------|
| 엔티티 | 순수 Python dataclass / 일반 클래스. `print`, `input` 금지. |
| 저장소 | CRUD 메서드를 제공. I/O 라이브러리 외 외부 의존 금지. |
| 유효성 검사 | 엔티티 생성 시점에 수행. Controller·View에 위임 금지. |
| 반환값 | 도메인 객체 또는 기본 타입만 반환. View 전용 문자열 금지. |

**허용 의존:** 표준 라이브러리만.
**금지 의존:** `controller.*`, `view.*`.

---

### 5.2 Controller

**책임:** 사용자 입력을 받아 Model을 조작하고, 결과를 View에 전달한다.

| 항목 | 규칙 |
|------|------|
| 입력 수신 | `input()` 호출은 Controller에서만 허용. |
| 흐름 제어 | 메뉴 루프, 분기, 예외 처리를 담당한다. |
| Model 사용 | Repository를 통해서만 데이터에 접근. 엔티티 내부 필드 직접 조작 금지. |
| View 사용 | View 메서드를 호출해 출력을 위임. 직접 `print` 금지. |
| 반환값 | 없음 (void). 상태는 Model이 소유한다. |

**허용 의존:** `model.*`, `view.*`.
**금지 의존:** 다른 Controller (순환 참조 방지).

---

### 5.3 View

**책임:** 콘솔 출력만 담당한다. 상태를 보유하지 않는다.

| 항목 | 규칙 |
|------|------|
| 출력 | `print()` 호출은 View에서만 허용. |
| 입력 | `input()` 호출 금지. |
| 상태 | 인스턴스 변수로 도메인 상태 저장 금지. |
| 인자 | 도메인 객체 또는 기본 타입을 받아 포맷 후 출력. |
| 의존 | 없음 — View는 어느 계층에도 의존하지 않는다. |

**허용 의존:** 표준 라이브러리(포맷팅 한정).
**금지 의존:** `model.*`, `controller.*`.

---

## 6. 데이터 흐름

```
사용자 입력
    │
    ▼
[Controller]
  input() 수신
    │  ① 명령 파싱
    ▼
[Model / Repository]
  비즈니스 로직 실행
  도메인 객체 반환
    │  ② 결과 전달
    ▼
[Controller]
  결과를 View 메서드에 인자로 전달
    │  ③ 렌더링 요청
    ▼
[View]
  print() 로 콘솔 출력
    │
    ▼
사용자 화면
```

- Model → View 직접 참조 없음.
- View → Controller · Model 직접 참조 없음.

---

## 7. 예시 도메인: Todo CRUD

구조 증명을 위한 최소 기능 집합.

| 기능 | Controller 메서드 | Model 동작 | View 메서드 |
|------|------------------|-----------|------------|
| 목록 조회 | `list_todos()` | `repo.find_all()` | `show_todo_list(todos)` |
| 항목 추가 | `add_todo()` | `repo.save(todo)` | `show_success(message)` |
| 항목 완료 | `complete_todo()` | `repo.update(todo)` | `show_success(message)` |
| 항목 삭제 | `delete_todo()` | `repo.delete(id)` | `show_success(message)` |
| 오류 표시 | — | — | `show_error(message)` |

---

## 8. 인터페이스 계약 (핵심 시그니처)

### `model/todo.py`
```python
@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
```

### `model/todo_repository.py`
```python
class TodoRepository:
    def find_all(self) -> list[Todo]: ...
    def find_by_id(self, id: int) -> Todo | None: ...
    def save(self, todo: Todo) -> Todo: ...
    def update(self, todo: Todo) -> Todo: ...
    def delete(self, id: int) -> bool: ...
```

### `view/todo_view.py`
```python
class TodoView:
    def show_menu(self) -> None: ...
    def show_todo_list(self, todos: list[Todo]) -> None: ...
    def show_success(self, message: str) -> None: ...
    def show_error(self, message: str) -> None: ...
```

### `controller/todo_controller.py`
```python
class TodoController:
    def __init__(self, repo: TodoRepository, view: TodoView) -> None: ...
    def run(self) -> None: ...          # 메인 루프
    def list_todos(self) -> None: ...
    def add_todo(self) -> None: ...
    def complete_todo(self) -> None: ...
    def delete_todo(self) -> None: ...
```

---

## 9. 완료 기준 (Definition of Done)

| # | 기준 | 검증 방법 |
|---|------|----------|
| 1 | 세 패키지(`model`, `controller`, `view`)가 각각 독립 디렉터리로 존재한다. | 디렉터리 확인 |
| 2 | `view/` 내 파일에 `input()` 호출이 없다. | `grep -rn "input()" view/` |
| 3 | `view/` 내 파일이 `model` 또는 `controller`를 `import`하지 않는다. | `grep -rn "^from model\|^import model\|^from controller" view/` |
| 4 | `model/` 내 파일에 `print()` · `input()` 호출이 없다. | `grep -rn "print(\|input(" model/` |
| 5 | `model/` 내 파일이 `controller` 또는 `view`를 `import`하지 않는다. | `grep -rn "^from controller\|^from view" model/` |
| 6 | `main.py`가 10줄 이내이며 `app.run()` 외 로직이 없다. | 코드 리뷰 |
| 7 | Todo CRUD 4가지 기능이 콘솔에서 정상 동작한다. | 수동 실행 확인 |

---

## 10. 비기능 요구사항

- **Python 버전:** 3.10 이상 (union type `X | Y`, match-case 사용 가능).
- **외부 라이브러리:** 없음 (표준 라이브러리만 사용).
- **타입 힌트:** 모든 public 메서드에 필수.
- **포맷터:** 별도 지정 없음; 들여쓰기 4 space 일관.

---

## 11. 미결 사항 (Open Questions)

| 항목 | 내용 |
|------|------|
| OQ-1 | 저장소를 파일(JSON/CSV) 기반으로 확장할 계획이 있는가? → 있다면 Repository 추상 클래스(ABC) 분리 필요. |
| OQ-2 | Controller 간 공통 입력 처리(정수 파싱, 재입력 루프)를 별도 유틸로 추출할 것인가? |
| OQ-3 | 향후 단위 테스트 추가 시 `tests/` 패키지를 루트에 추가할 것인가? |
