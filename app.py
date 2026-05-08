class App:
    def __init__(self) -> None:
        # Phase 5에서 실제 Repository·View·Controller로 교체
        self._controller = None

    def run(self) -> None:
        if self._controller is None:
            print("[Phase 1] Skeleton - not yet implemented.")
            return
        self._controller.run()
