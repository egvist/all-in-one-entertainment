from PySide6.QtCore import QObject, Signal, Slot
from mediaatlas.api.igdb_client import IGDBClient

class GameSearchWorker(QObject):
    result_ready = Signal(object)
    finished = Signal()
    error = Signal(str)
    def __init__(self, query: str, client: IGDBClient):
        super().__init__()
        self.query = query
        self.client = client
    @Slot()
    def run(self):
        try:
        
            games = self.client.search_games(self.query)
            self.result_ready.emit(games)
        except Exception as exc:
            self.error.emit(str(exc))
        finally:
            self.finished.emit()
