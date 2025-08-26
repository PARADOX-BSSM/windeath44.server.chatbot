import os, grpc
from dotenv import load_dotenv
load_dotenv()

def create_channel() -> grpc.aio.Channel:
    target = os.getenv("GRPC_TARGET", "localhost:9002")
    return grpc.aio.insecure_channel(
        target,
        options=(
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ),
    )
