"""Shared delivered-record fixture; contains no discoverable test cases."""
from test_records import RecordsHarness


class DeliveredRecordsHarness(RecordsHarness):
    def delivered(self, criteria=None):
        if criteria is None:
            self.prepared()
        else:
            self.initialize(); self.backlog(); self.authorization()
            self.mutate({"operation": "prepare", "operation_id": "prepare-parts", "purpose": "Prepare parts", "increment": {"item_ids": ["ITEM-0001"], "objective": "Deliver parts", "scope": "Response", "criteria": criteria, "required_checks": ["unit"], "authorization": "DEC-0001"}})
        self.mutate({"operation": "start", "operation_id": "start", "purpose": "Start", "increment_id": "INC-0001"})
        self.mutate({"operation": "mark-implemented", "operation_id": "implemented", "purpose": "Deliver", "increment_id": "INC-0001"})
