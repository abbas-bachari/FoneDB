
import aiohttp
import ssl
from aiohttp_proxy import ProxyConnector
from .configs import HEADERS
class HTTPClient:
    def __init__(self, client_cert_file=None,proxy_url:str=None):
        self.client_cert = client_cert_file
        self.proxy_url = proxy_url
        self._session = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session:
            return self._session

        ssl_context = ssl.create_default_context()
        if self.client_cert:
            ssl_context.load_verify_locations(cafile=self.client_cert)

        if self.proxy_url:
            connector = ProxyConnector.from_url(self.proxy_url, rdns=True, ssl=ssl_context)
        else:
            connector = aiohttp.TCPConnector(ssl=ssl_context)

        self._session = aiohttp.ClientSession(connector=connector, headers=HEADERS)
        return self._session

    async def get(self, url, **kwargs):
        session = await self.get_session()
        async with session.get(url, **kwargs) as resp:
            return await resp.text()
    async def post(self, url, **kwargs):
        session = await self.get_session()
        async with session.post(url, **kwargs) as resp:
            return await resp.text()
    async def close(self):
        if self._session:
            await self._session.close()