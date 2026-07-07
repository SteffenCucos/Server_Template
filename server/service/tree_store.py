class TreeStore:
    def __init__(self):
        self.role_ids_by_user_id = {}
        self.role_tree_by_role_id = {}

    def clear(self):
        self.role_ids_by_user_id.clear()
        self.role_tree_by_role_id.clear()
