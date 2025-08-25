import re
from urllib.parse import urljoin, urlparse, urlunparse,parse_qs
from .objects import Description,Device
from bs4 import BeautifulSoup
from typing import List


SDKs= {
    "android 4"  : 14,
    "android 4.0": 14,
    "android 4.1": 16,
    "android 4.2": 17,
    "android 4.3": 18,
    "android 4.4": 19,
    "android 5"  : 21,
    "android 5.0": 21,
    "android 5.1": 22,
    "android 6"  : 23,
    "android 6.0": 23,
    "android 7"  : 24,
    "android 7.0": 24,
    "android 7.1": 25,
    "android 8"  : 26,
    "android 8.0": 26,
    "android 8.1": 27,
    "android 9"  : 28,
    "android 9.0": 28,
    "android 10":  29,
    "android 11":  30,
    "android 12":  31,
    "android 12L": 32,
    "android 13":  33,
    "android 14":  34,
    "android 15":  35,
}
def clean_all(text_list:list[str], words:list[str]):
    text_list=[t.strip().lower() for t in text_list if t.strip()]
    for i  in words:
        i=i.strip().lower() if i and i.strip() else i
        if i in text_list:
            text_list.remove(i)
        
    return ' '.join (text_list).strip()
def normalize_url(url):
    # حذف fragment (#...) و پارامترهای اضافی اگر لازم است
    parsed = urlparse(url)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", parsed.query, ""))
    return clean_url.strip().lower()

def parse_pages(html) -> list[int]:
    soup = BeautifulSoup(html, "html.parser")
    buttons = soup.find_all('button', class_='list_button')
    pages=[btn.get('value') for btn in buttons]
    return pages

def extract_devices_from_page(html: str, BASE_URL: str = "https://phonedb.net") -> List[Description]:
    """
    Extract device descriptions from a single HTML page.

    Args:
        html (str): HTML content of the page.
        BASE_URL (str, optional): Base URL to resolve relative links. Default is "https://phonedb.net".

    Returns:
        List[Description]: A list of Description objects containing
                           the device's URL, title, and description.
    """
    soup = BeautifulSoup(html, 'html.parser')
    devices = []

    for block in soup.select('.content_block'):
        # عنوان و لینک
        title_tag = block.select_one('.content_block_title a')
        title = title_tag.get('title') if title_tag else None
        link = title_tag.get('href') if title_tag else None
        full_url = normalize_url(urljoin(BASE_URL, link)) if link else None
        raw_text = block.get_text(separator=' ', strip=True)
        parts = raw_text.split('|')
        description_text = parts[0].strip() if parts else ''

        if title and full_url:
            devices.append(
                Description(
                    url=full_url,
                    title=title,
                    description=description_text.replace(title, '').strip()
                )
            )

    return devices



def parse_device_info(url: str, description: str) -> Device:
    """
    Extract and normalize device information from URL and description text.

    Args:
        url (str): URL of the device page.
        description (str): Full description text of the device.

    Returns:
        Device: A Device object with fields populated such as
                brand, model, OS, memory, regions, edition, dual SIM, operator, and name.
    """
    patterns = {
        'brand': r'\bSamsung\b|\bXiaomi\b',
        'model': r"\bSM-[A-Z0-9/]+\b|\b[A-Z]?\d{4}[A-Z0-9-]+\b",
        'android': r"\bAndroid (\d+(?:\.\d+)?)\b",
        'memory': r'\b(\d+GB)\b|\b(\d{2}[\d]+G)\b|\b(\d+TB)\b',
        'regions': r"\b(MEA|LATAM|US|CA|EU|EMEA|AP|CN|RU|TW|AU|JP|HK|KR|IN|Global)\b",
        'edition': r'\b(limited|Standard|Premium|Top|Extreme Speed|BTS|Thom Browne|Olympic Games|Maison Margiela|Bespoke|BMW M) Edition\b|\b(Standard|Premium|Bespoke|limited|Thom Browne|Maison Margiela)\b',
        'global': r'\bGlobal\b',
        'dual_sim': r'\bDual SIM\b',
        'operator': r"\bSC-\d+[A-Z]?\b|\bSCG\d+\b|SCV\d+\b",
    }

    device = Device(
        model="",
        regions="GLOBAL",
        edition="Standard Edition",
        is_global=False,
        dual_sim=False,
        url=url
    )

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    slug = query.get("c", [""])[0]
    main_part, short_code = (slug.split("__", 1) + [""])[:2] if "__" in slug else (slug, "")
    main_title = main_part.replace("_", " ")

    operator = None

    for key, value in patterns.items():
        pattern = re.compile(value, re.IGNORECASE)
        match key:
            case 'brand':
                match_obj = pattern.search(main_title)
                if match_obj:
                    device.brand = match_obj.group(0).capitalize()
            case 'model':
                match_obj = pattern.search(main_title)
                if match_obj:
                    model = match_obj.group(0).upper()
                    # Fix DS formatting
                    if re.search(r"\bsm-[a-z0-9/]+(?:ds[a-z]?)?\b", model, re.I):
                        model = re.sub(r"DS([A-Z]?)$", r"/DS\1", model)
                    device.model = model
            case 'android':
                match_obj = pattern.search(description)
                if match_obj:
                    device.os_system = 'Android'
                    device.os_version = match_obj.group(1)
                    device.sdk_version = SDKs.get(match_obj.group(0).lower())
            case 'memory':
                match_obj = pattern.search(main_title)
                if match_obj:
                    device.memory = match_obj.group(0).upper()
            case 'regions':
                match_obj = pattern.findall(main_title)
                if match_obj:
                    device.regions = ','.join([r.upper() for r in match_obj])
            case 'edition':
                match_obj = pattern.search(main_title)
                if match_obj:
                    device.edition = match_obj.group(0).title().strip()
            case 'global':
                device.is_global = pattern.search(main_title) is not None
            case 'dual_sim':
                device.dual_sim = pattern.search(main_title) is not None
            case 'operator':
                match_obj = pattern.search(main_title)
                if match_obj:
                    operator = match_obj.group(0).upper()
            case _:
                pass

    # Extract year for filtering words
    

    
    words_to_upper = ['uw', 'td-lte','4g','5g','32gb','64gb','128gb','256gb','512gb','1tb']
    words_to_upper.extend([r for r in device.regions.lower().split(',') if r != 'global'])
    if operator:
        words_to_upper.append(operator.lower())
    if device.model:
        words_to_upper.append(device.model.lower().replace('/ds','ds'))

    
    words =  main_title.replace('plus', '+').split()

    for i, w in enumerate(words):
        if w.lower() in words_to_upper:
            words[i] = w.upper()
        else:
            words[i]=w.capitalize()

    main_name = " ".join(words)

    if device.model:
        pattern = re.compile(r"\bsm-[a-z0-9/]+(?:ds[a-z]?)?\b", re.IGNORECASE)
        def format_model(match):
            model = match.group(0).upper()
            model = re.sub(r"DS([A-Z]?)$", r"/DS\1", model)
            return model

        main_name = pattern.sub(format_model, main_name, count=1)

    device.name = main_name
    

    return device


def short_name(device:Device):
        operator=''
        pattern=re.compile(r"\bSC-\d+[A-Z]?\b|\bSCG\d+\b|SCV\d+\b",flags=re.IGNORECASE)
        mach=pattern.search(device.name)
        if mach:
            operator=mach.group(0).lower()


        year_match = re.search(r'\b(20\d{2})\b', device.name)
        
        filter_words=[
            'td-lte','lte','dual','sim','edition','limited','apac','Lamborghini',
              'Squadra', 'Corse','Lte-A','Retro','Jet','Black','Harry', 'Potter','World', 
              'Xig05','Champions','Daniel', 'Arsham',"A001Xm","Special","Dimensity","A201Xm",
              "Racing","Explorer",operator]
        
        edition=device.edition.lower().split()
       

        filter_words.extend(edition)
        
        # filter_words.extend(device.regions.lower().split(','))
        
        if device.model:
            filter_words.append(device.model.lower().replace("/ds","ds"))
        
        if device.memory:
            filter_words.append(device.memory.lower())
        
        if year_match:
            filter_words.append(year_match.group(1))
        
        
        main_name=clean_all(device.name.replace('plus',"+").split(),filter_words )
        name=main_name.title().split()
        split_main_name=main_name.split()
        to_upper_words=['uw','td-lte']
        
        to_upper_words.extend([r for r in device.regions.lower().split(',') if r != 'global'])
        if operator:
            to_upper_words.append(operator.lower())
        for e in to_upper_words:
            if e in split_main_name:
                name[split_main_name.index(e)]=e.upper()
       
       
        return " ".join(name)