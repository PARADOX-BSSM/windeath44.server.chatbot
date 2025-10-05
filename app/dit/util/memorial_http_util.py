import os
from core.util.http_util import HTTPUtil
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
memorial_domain = os.getenv("MEMORIAL_DOMAIN")
if not memorial_domain:
    raise ValueError("MEMORIAL_DOMAIN environment variable is not set")

memorial_http_util = HTTPUtil(base_url=memorial_domain, timeout=30)

async def write_memorial_comment(
    user_id: str,
    memorial_id: int,
    content: str,
    parent_comment_id: Optional[str] = None
):
    headers = {"user-id": user_id}
    body = {"content": content, "parentCommentId" : parent_comment_id if parent_comment_id else None}

    return await memorial_http_util.post_json(
        endpoint=f"/comment/{memorial_id}",
        json=body,
        headers=headers
    )