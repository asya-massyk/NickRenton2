import uuid
from typing import Any, Union
from uuid import UUID


class ExternalRequest:
    data: dict[str, Any]
    transaction_id: UUID

    def __init__(self, data: dict[str, Any], transaction_id: Union[UUID, str]) -> None:
        self.data = data
        if isinstance(transaction_id, str):
            self.transaction_id = UUID(transaction_id)
        else:
            self.transaction_id = transaction_id

    def to_dict(self) -> dict[str, Union[Any, UUID]]:
        """Повертає словник з доданим transaction_id"""
        result = self.data.copy()
        result['transaction_id'] = self.transaction_id
        return result