class RegistrationError(Exception):
    def __init__(self, message="Error in registration process. Edge case detected. Report as an issue or PR."):
        self.message = message
        super().__init__(self.message)
