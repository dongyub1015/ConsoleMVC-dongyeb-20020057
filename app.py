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
