
class ExceptionHandlerContextRunner:

    async def run(self):
        pass

    def __aenter__(self):
        return self.run()

    def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            raise ConnectionError(f"connection to mysql error {exc_type} {exc_val}")
        return self.run()
