import uuid

class Id(str):
    def __init__(self, _id: str):
        self._id = _id

def from_mongoId(mongoId: object):
    pass

def create_id() -> Id:
    return Id(str(uuid.uuid4()))