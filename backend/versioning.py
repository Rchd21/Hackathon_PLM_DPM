from datetime import datetime
from backend.models import Requirement, RequirementHistoryItem


def create_history_item(
    requirement: Requirement, change_type: str, diff_summary: str
) -> RequirementHistoryItem:
    return RequirementHistoryItem(
        requirement_id=requirement.id,
        version=requirement.version,
        timestamp=datetime.utcnow(),
        change_type=change_type,
        diff_summary=diff_summary,
    )