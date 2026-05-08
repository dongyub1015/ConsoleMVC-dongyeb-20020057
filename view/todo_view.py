class TodoView:

    _MENU = (
        "\n========== Todo 관리 ==========\n"
        "  1. 목록 보기\n"
        "  2. 항목 추가\n"
        "  3. 항목 완료\n"
        "  4. 항목 삭제\n"
        "  0. 종료\n"
        "==============================\n"
    )

    def show_menu(self) -> None:
        print(self._MENU, end="")

    def show_todo_list(self, todos: list) -> None:
        if not todos:
            print("(등록된 항목이 없습니다)")
            return
        print(f"{'ID':>3}  {'상태':<5}  제목")
        print(f"{'--':>3}  {'----':<5}  {'-' * 20}")
        for todo in sorted(todos, key=lambda t: t.id):
            status = "[v]" if todo.done else "[ ]"
            print(f"{todo.id:>3}  {status:<5}  {todo.title}")

    def show_success(self, message: str) -> None:
        print(f"[완료] {message}")

    def show_error(self, message: str) -> None:
        print(f"[오류] {message}")
