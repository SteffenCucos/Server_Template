class TreeStore:
    def __init__(self):
        self.role_ids_by_user_id = {}
        self.role_tree_by_role_id = {}

    def invalidate_user(self, user_id):
        self.role_ids_by_user_id.pop(str(user_id), None)

    def invalidate_role(self, role_id):
        self.role_tree_by_role_id.pop(str(role_id), None)

    def clear(self):
        self.role_ids_by_user_id.clear()
        self.role_tree_by_role_id.clear()
