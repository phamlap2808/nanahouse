from dataclasses import dataclass

@dataclass(kw_only=True)
class TestController:
    def health(self):
        return {"status": "ok"}