import asyncio
from typing import List, Optional
from .http_client import HTTPClient
from .configs import DATA_FORM
from .utils import parse_pages, parse_device_info, extract_devices_from_page
from .storage import Base, Storage


class FoneDB(HTTPClient):
    def __init__(
        self,
        client_cert_file: Optional[str] = None,
        proxy_url: Optional[str] = None,
        database: Storage = Storage(),
    ):
        super().__init__(client_cert_file, proxy_url)
        self.DevicesDB = database
        self.DevicesDB.create_tables(Base)
        self._pages: Optional[List[str]] = None

    def get_pages(self, html: str) -> List[str]:
        """Extract pagination indices from HTML or return cached ones."""
        if self._pages is None:
            self._pages = parse_pages(html)
        return self._pages

    def _save_devices(self, html: str) -> List[dict]:
        """Extract devices from HTML and save them into the database."""
        devices_description = extract_devices_from_page(html)
        devices = []
        for description in devices_description:
            device = parse_device_info(description.url, description.description)
            if device.model:
                devices.append(device.to_dict())
        
        count = self.DevicesDB.insert(devices)
        print(f"Saved {count} devices ...")
        return devices

    async def scrape_devices(
        self,
        brand: str = "Samsung",
        from_date: str = "2015-01-01",
        sleep_time: int = 5,
        start_index: int = 0,
    ) -> Storage:
        """
        Scrape devices for a given brand starting from a given date.

        ## Notes:
            - Only devices running **Android 8.0 (Oreo) and above** are extracted.
            - Based on the current Android version, this means results will cover
              devices from Android 8.0 up to **Android 15**.

        Args:
            brand (str): Brand name to scrape (default: "Samsung").
            from_date (str): Minimum release date in 'YYYY-MM-DD' format.
            sleep_time (int): Delay (in seconds) between requests.
            start_index (int): Page index to start scraping from.

        Returns:
            Storage: Database instance containing scraped devices.
        """
        data_form = DATA_FORM.copy()
        data_form["brand"] = brand
        data_form["released_min"] = from_date

        self._pages = None
        next_index = start_index

        while True:
            if self._pages:
                if next_index >= len(self._pages):
                    break
                page_number = next_index + 1
                total_pages = len(self._pages)
                print(f"Load {brand} page {page_number} of {total_pages}")
            else:
                print(f"Load {brand} page 1")

            data_form["result_lower_limit"] = ( self._pages[next_index] if self._pages else "0")

            html = await self.post("https://phonedb.net/index.php?m=device&s=query&d=detailed_specs",data=data_form)

            self._save_devices(html)
            self._pages = self.get_pages(html)
            next_index += 1
          
            await asyncio.sleep(sleep_time)

        return self.DevicesDB
