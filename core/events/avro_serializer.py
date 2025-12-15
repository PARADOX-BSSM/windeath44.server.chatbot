"""
Avro Serializer for Kafka using fastavro and Schema Registry
"""
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

import fastavro
import httpx
from fastavro.schema import load_schema

logger = logging.getLogger(__name__)


class AvroSerializer:
    """
    Confluent Schema Registry와 호환되는 Avro Serializer

    Confluent Wire Format:
    - Byte 0: Magic byte (0x0)
    - Bytes 1-4: Schema ID (4 bytes, big-endian)
    - Bytes 5-: Avro serialized data
    """

    MAGIC_BYTE = 0

    def __init__(
        self,
        schema_registry_url: str,
        schema_file_path: str,
        subject: Optional[str] = None
    ):
        """
        Args:
            schema_registry_url: Schema Registry URL (e.g., "http://localhost:8081")
            schema_file_path: Avro 스키마 파일 경로 (.avsc)
            subject: Schema Registry subject name (기본값: 스키마 이름-value)
        """
        self.schema_registry_url = schema_registry_url.rstrip('/')
        self.schema_file_path = Path(schema_file_path)

        # 스키마 로드
        self.schema = self._load_schema()
        self.subject = subject or f"{self.schema['name']}-value"

        # 스키마 ID (등록 후 할당됨)
        self._schema_id: Optional[int] = None

    def _load_schema(self) -> Dict[str, Any]:
        """Avro 스키마 파일을 로드합니다."""
        if not self.schema_file_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_file_path}")

        with open(self.schema_file_path, 'r') as f:
            schema = json.load(f)

        # fastavro의 parsed schema로 변환
        parsed_schema = fastavro.parse_schema(schema)
        logger.info(f"Loaded Avro schema: {parsed_schema.get('name')}")
        return parsed_schema

    async def register_schema(self) -> int:
        """
        Schema Registry에 스키마를 등록하고 schema ID를 반환합니다.
        이미 등록된 스키마면 기존 ID를 반환합니다.
        """
        if self._schema_id is not None:
            return self._schema_id

        url = f"{self.schema_registry_url}/subjects/{self.subject}/versions"

        # Schema Registry는 JSON 형태로 스키마를 전송
        payload = {
            "schema": json.dumps(self.schema)
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/vnd.schemaregistry.v1+json"}
                )
                response.raise_for_status()

                result = response.json()
                self._schema_id = result["id"]
                logger.info(f"Schema registered with ID: {self._schema_id} for subject: {self.subject}")
                return self._schema_id

            except httpx.HTTPError as e:
                logger.error(f"Failed to register schema: {e}")
                raise

    def serialize(self, data: Dict[str, Any]) -> bytes:
        """
        Python dict를 Confluent Wire Format의 Avro 바이트로 직렬화합니다.

        Args:
            data: 직렬화할 데이터 (dict)

        Returns:
            bytes: Confluent Wire Format으로 인코딩된 Avro 데이터
        """
        if self._schema_id is None:
            raise RuntimeError("Schema not registered. Call register_schema() first.")

        try:
            # Avro 데이터를 바이트로 직렬화
            from io import BytesIO
            output = BytesIO()
            fastavro.schemaless_writer(output, self.schema, data)
            avro_bytes = output.getvalue()

            # Confluent Wire Format 생성
            # [magic_byte(1) + schema_id(4) + avro_data(n)]
            result = bytearray()
            result.append(self.MAGIC_BYTE)
            result.extend(self._schema_id.to_bytes(4, byteorder='big'))
            result.extend(avro_bytes)

            return bytes(result)

        except Exception as e:
            logger.error(f"Failed to serialize data: {e}")
            raise


class AsyncAvroSerializer:
    """
    AsyncIO 환경에서 사용하는 Avro Serializer wrapper
    """

    def __init__(self, serializer: AvroSerializer):
        self.serializer = serializer
        self._registered = False

    async def ensure_registered(self):
        """스키마가 등록되어 있는지 확인하고, 없으면 등록합니다."""
        if not self._registered:
            await self.serializer.register_schema()
            self._registered = True

    async def __call__(self, data: Dict[str, Any]) -> bytes:
        """
        Async callable로 사용될 때 호출되는 메서드

        Args:
            data: 직렬화할 데이터

        Returns:
            bytes: Avro로 직렬화된 데이터
        """
        await self.ensure_registered()
        return self.serializer.serialize(data)
