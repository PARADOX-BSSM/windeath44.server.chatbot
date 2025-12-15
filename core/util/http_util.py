import httpx
from typing import Any, Dict, Optional


class HTTPUtil:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _build_url(self, endpoint: str) -> str:
        url = self.base_url
        if not url.startswith(('http://', 'https://')):
            url = f"http://{url}"
        return f"{url}/{endpoint.lstrip('/')}"

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.get(url, params=params, headers=headers, **kwargs)

    async def post_json(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(url, json=json, headers=headers, **kwargs)

    async def post_data(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.post(url, data=data, headers=headers, **kwargs)

    async def patch_json(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.patch(url, json=json, headers=headers, **kwargs)

    async def patch_data(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.patch(url, data=data, headers=headers, **kwargs)

    async def put_json(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.put(url, json=json, headers=headers, **kwargs)

    async def put_data(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.put(url, data=data, headers=headers, **kwargs)

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> httpx.Response:
        url = self._build_url(endpoint)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await client.delete(url, headers=headers, **kwargs)