import re
from urllib.parse import urljoin, urlparse, urlunparse,parse_qs
from .objects import Description,Device
from bs4 import BeautifulSoup
SDKs={
            "android 9"     : 28,
            "android 10"    : 29,
            "android 11"    : 30,
            "android 12"    : 31,
            "android 12L"   : 32,
            "android 12.1"  : 32,
            "android 13"    : 33,
            "android 14"    : 34,
            "android 15"    : 35
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

def get_pages(html) -> list[int]:
    soup = BeautifulSoup(html, "html.parser")
    buttons = soup.find_all('button', class_='list_button')
    pages=[btn.get('value') for btn in buttons]
    return pages

def get_all_devices_in_page(html,BASE_URL = "https://phonedb.net") -> list [Description]:
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
            description = parts[0].strip() if parts else ''
            if title and full_url:
                
                devices.append(Description(url=full_url,title=title,description=description.replace(title, '').strip()))
            else:
                continue
            
        
        return devices

def get_device_info(url: str,description:str) -> Device:
    
        
        patterns={
            'brand'   :  r'\bSamsung\b|\bXiaomi\b',
            "model"   :  r"\bSM-[A-Z0-9/]+\b|\b[A-Z]?\d{4}[A-Z0-9-]+\b",
            "android" :  r"\bAndroid (\d+(?:\.\d+)?)\b",
            "memory"  :  r'\b(\d+GB)\b|\b(\d{2}[\d]+G)\b|\b(\d+TB)\b',
            "regions" :  r"\b(MEA|LATAM|US|CA|EU|EMEA|AP|CN|RU|TW|AU|JP|HK|KR|IN|Global)\b",
            "edition" :  r'\b(limited|Standard|Premium|Top|Extreme Speed|BTS|Thom Browne|Olympic Games|Maison Margiela|Bespoke|BMW M) Edition\b |\b(Standard|Premium|Bespoke|limited|thom browne|Maison Margiela)\b',
            "global"  :  r'\bGlobal\b',
            "dual_sim":  r'\bDual SIM\b',
            "operator":  r"\bSC-\d+[A-Z]?\b|\bSCG\d+\b|SCV\d+\b",
        

        }
        
        
        device=Device(model="",regions="GLOBAL",edition="Standard Edition",is_global=False,dual_sim=False,url=url)
        
        parsed = urlparse(url)
        query  = parse_qs(parsed.query)
        slug = query.get("c", [""])[0]
        
        
        if "__" in slug:
            main_part, short_code = slug.split("__", 1)
        else:
            main_part, short_code = slug, ""
        
        main_title = main_part.replace("_", " ")
        

        operator=None
        
        for key,value in patterns.items():
            pattern=re.compile(value,re.IGNORECASE)
            match key:
                case 'brand':
                    mach=pattern.search(main_title)
                    if mach:
                        device.brand=mach.group(0).capitalize()
                case 'model':
                    mach=pattern.search(main_title)
                    if mach:
                        model= mach.group(0).upper()
                        if model.startswith("SM-"):
                            model=model.replace("DS","/DS")
                        
                        device.model=model

                case 'android':
                    mach=pattern.search(description)
                    if mach:
                        device.os_system='Android'
                        device.os_version=int(mach.group(1))
                        device.sdk_version=SDKs.get(mach.group(0).lower())
                
                case 'memory':
                    mach=pattern.search(main_title)
                    if mach:
                        device.memory= mach.group(0).upper()

                    
                case 'regions':
                    mach=pattern.findall(main_title)
                    if mach:
                        device.regions=','.join([r.upper() for r in mach])
                        
                
                case 'edition':
                    mach=pattern.search(main_title)
                    if mach:
                        
                        device.edition= mach.group(0).title()

                case 'global':
                    
                    device.is_global=pattern.search(main_title) is not None
                    
                
                case 'dual_sim':
                  
                    device.dual_sim=pattern.search(main_title) is not None
                case 'operator':
                    mach=pattern.search(main_title)
                    if mach:
                        operator=mach.group(0).upper()
                        
                        
                case _:
                    pass

        
        year_match = re.search(r'\b(20\d{2})\b', main_title)
        # filter_words=['td-lte','lte','dual','sim',operator]
        filter_words=['td-lte','lte',operator]
        if device.model:
            filter_words.append(device.model.lower().replace("/ds","ds"))
        if device.memory:
            filter_words.append(device.memory.lower())
        
        if year_match:
            filter_words.append(year_match.group(1))
            
        
        main_name=clean_all(main_title.replace('plus',"+").split(),filter_words )
        name=main_name.title().split()
        split_main_name=main_name.split()
        to_upper_words=['uw','td-lte']
        
        to_upper_words.extend([r for r in device.regions.lower().split(',') if r != 'global'])
        if operator:
            to_upper_words.append(operator.lower())
        for e in to_upper_words:
            if e in split_main_name:
                name[split_main_name.index(e)]=e.upper()
       
       
        device.name=" ".join(name)
       
        return device