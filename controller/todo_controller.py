from model.todo import Todo
from model.todo_repository import TodoRepository
from view.todo_view import TodoView


class TodoController:

    def __init__(self, repo: TodoRepository, view: TodoView) -> None:
        self._repo = repo
        self._view = view

    def run(self) -> None:
        while True:
            self._view.show_menu()
            choice = self._prompt_int()
            match choice:
                case 1:
                    self.list_todos()
                case 2:
                    self.add_todo()
                case 3:
                    self.complete_todo()
                case 4:
                    self.delete_todo()
                case 0:
                    self._view.show_success("프로그램을 종료합니다.")
                    break
                case _:
                    self._view.show_error("올바른 번호를 입력하세요.")

    def list_todos(self) -> None:
        todos = self._repo.find_all()
        self._view.show_todo_list(todos)

    def add_todo(self) -> None:
        title = input("제목 입력: ").strip()
        if not title:
            self._view.show_error("제목을 입력해야 합니다.")
            return
        try:
            todo = Todo(id=0, title=title)
            self._repo.save(todo)
            self._view.show_success("항목이 추가되었습니다.")
        except ValueError as e:
            self._view.show_error(str(e))

    def complete_todo(self) -> None:
        todo_id = self._prompt_int("완료할 ID: ")
        todo = self._repo.find_by_id(todo_id)
        if todo is None:
            self._view.show_error("해당 ID를 찾을 수 없습니다.")
            return
        todo.done = True
        self._repo.update(todo)
        self._view.show_success(f"ID {todo_id} 항목을 완료했습니다.")

    def delete_todo(self) -> None:
        todo_id = self._prompt_int("삭제할 ID: ")
        if self._repo.delete(todo_id):
            self._view.show_success(f"ID {todo_id} 항목이 삭제되었습니다.")
        else:
            self._view.show_error("해당 ID를 찾을 수 없습니다.")

    def _prompt_int(self, prompt: str = "선택 >> ") -> int:
        while True:
            raw = input(prompt).strip()
            if raw.lstrip("-").isdigit():
                return int(raw)
            self._view.show_error("숫자를 입력해야 합니다.")
