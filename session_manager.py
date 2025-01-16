from collections import defaultdict

class SessionManager:
    def __init__(self):
        self.sessions = defaultdict(dict)

    def get_session(self, user_id):
        return self.sessions[user_id]

    def update_session(self, user_id, key, value):
        self.sessions[user_id][key] = value

    def clear_session(self, user_id):
        self.sessions[user_id].clear()

session_manager = SessionManager()