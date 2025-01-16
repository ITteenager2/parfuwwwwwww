import json
from database import db

class DialogueManager:
    def __init__(self):
        self.memory_cache = {}

    def get_dialogue_history(self, user_id):
        if user_id in self.memory_cache:
            return self.memory_cache[user_id]
        
        history = db.get_dialogue_history(user_id)
        if history:
            self.memory_cache[user_id] = json.loads(history)
        else:
            self.memory_cache[user_id] = []
        
        return self.memory_cache[user_id]

    def add_to_dialogue_history(self, user_id, role, content):
        if user_id not in self.memory_cache:
            self.get_dialogue_history(user_id)
        
        self.memory_cache[user_id].append({"role": role, "content": content})
        
        # Ограничиваем историю последними 10 сообщениями
        if len(self.memory_cache[user_id]) > 20:
            self.memory_cache[user_id] = self.memory_cache[user_id][-20:]
        
        db.update_dialogue_history(user_id, json.dumps(self.memory_cache[user_id]))

    def clear_dialogue_history(self, user_id):
        self.memory_cache.pop(user_id, None)
        db.clear_dialogue_history(user_id)

dialogue_manager = DialogueManager()
