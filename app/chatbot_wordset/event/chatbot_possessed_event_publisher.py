import time

from core.events.event_publisher import EventPublisher


async def publish_chatbot_possessed_event(
    publisher: EventPublisher,
    *,
    chatbot_id: int,
    talkset_request_id: str,
    applicant_id: str,
    approver_id: str,
) -> bool:
    """챗봇 말투셋 승인 이벤트 발행"""
    approved_at_ms = int(time.time() * 1000)

    event = {
        "chatbot_id": chatbot_id,
        "talkset_request_id": talkset_request_id,
        "applicant_id": applicant_id,
        "approved_at_ms": approved_at_ms,
    }

    topic = "chatbot-possessed-request"
    key = f"{chatbot_id}:{talkset_request_id}"

    headers = {"approver_id": approver_id}

    return await publisher.publish(topic=topic, message=event, key=key, headers=headers)
