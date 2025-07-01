# Temporary placeholder classes to stabilize application launch


class CollaborationManager:
    def __init__(self, server_url=None, user_id=None, team_id=None):
        self.server_url = server_url
        self.user_id = user_id
        self.team_id = team_id

    def connect(self):
        pass

    def disconnect(self):
        pass

    def set_task_update_callback(self, callback):
        pass

    def start(self):
        pass


class Config:
    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value


class OnboardingAnalytics:
    def __init__(self):
        self.data = {}

    def track(self, event, data=None):
        pass

    def flush(self):
        pass

    def initialize(self):
        pass

    def start_session(self):
        pass

    def track_event(self, category, action, label):
        pass
