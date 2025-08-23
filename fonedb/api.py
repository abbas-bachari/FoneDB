
from .http_client import HTTPClient
from .configs import DATA_FORM
import asyncio
from .utils import get_pages, get_all_devices_in_page, get_device_info
from .storage import Base, Storage
from typing import List, Optional

class FoneDB(HTTPClient):

    def __init__(self, client_cert_file: Optional[str] = None, proxy_url: Optional[str] = None, database: Storage = Storage()):
        super().__init__(client_cert_file, proxy_url)
        self.DevicesDB = database
        self.DevicesDB.create_tables(Base)
        self._pages: List[str] = None

    def get_pages(self, html: str) -> List[str]:
        """Extract pages from HTML or return cached pages."""
        if self._pages is None:
            self._pages = get_pages(html)
        return self._pages

    def _save_devices(self, html: str) -> List[dict]:
        """Extract devices from HTML and save to the database."""
        devices_description = get_all_devices_in_page(html)
        devices = []
        for description in devices_description:
            device = get_device_info(description.url, description.description)
            if device.model:
                devices.append(device.to_dict())
        count = self.DevicesDB.insert(devices)
        print(f"Saved {count} devices ...")
        return devices

    async def get_devices(self, brand: str = "Samsung", from_date: str = '2018-01-01', sleep_time: int = 5) -> Storage:
        """Scrape devices for a given brand starting from from_date."""
        data_form = DATA_FORM.copy()
        data_form['brand'] = brand
        data_form['released_min'] = from_date

        self._pages  = None
        current_page = '0'

        while True:
            if self._pages:
                try:
                    page_number = self._pages.index(current_page) + 1
                    total_pages = len(self._pages)
                    print(f"Load {brand} page {page_number} from {total_pages}")
                except ValueError:
                    print(f"Current page {current_page} not found, starting from page 1")
                    page_number = 1
            else:
                print(f"Load {brand} page 1")

            data_form["result_lower_limit"] = current_page
            html = await self.post("https://phonedb.net/index.php?m=device&s=query&d=detailed_specs", data=data_form)
            self._save_devices(html)

            pages = self.get_pages(html)
            try:
                next_index = pages.index(current_page) + 1
            except ValueError:
                break

            if next_index >= len(pages):
                break

            current_page = pages[next_index]
            await asyncio.sleep(sleep_time)

        return self.DevicesDB

        
        
    
        