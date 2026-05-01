# core/rate_limit.py
import time
from collections import defaultdict

class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, lockout_minutes: int = 15):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self.attempts = defaultdict(list)

    def is_blocked(self, username: str) -> bool:
        now = time.time()
        self.attempts[username] = [t for t in self.attempts[username] if now - t < self.lockout_minutes * 60]
        return len(self.attempts[username]) >= self.max_attempts

    def add_attempt(self, username: str):
        self.attempts[username].append(time.time())

    def reset_attempts(self, username: str):
        self.attempts[username] = []