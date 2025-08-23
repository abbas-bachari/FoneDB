<h1 align="center">🚀 FoneDB</h1>

<p align="center">
<a href="https://github.com/abbas-bachari/fonedb"><img src="https://img.shields.io/badge/Python%20-3.8+-green?style=plastic&logo=Python" alt="Python"></a>
<a href="https://pypi.org/project/fonedb/"><img src="https://img.shields.io/pypi/l/fonedb?style=plastic" alt="License"></a>
<a href="https://pepy.tech/project/fonedb"><img src="https://pepy.tech/badge/fonedb?style=flat-plastic" alt="Downloads"></a>
</p>

## 🛠️ Version 1.0.0

## 🌟 **Introduction**

### **FoneDB** A simple script to scrape and collect smartphone specifications from PhoneDB automatically..  

---

## 📚 **Requirements**

* **Python 3.8+**
* **DBFlux>= 1.0.2**

---


## 🔧 **Installation**

### install from source:

```bash
git clone https://github.com/abbas-bachari/fonedb.git
cd fonedb
pip install .
```

---


## 💡 **Quick Start**

```python
from fonedb import FoneDB,Storage,Device
from dbflux import Sqlite
import asyncio

DB= Storage(base_db=Sqlite(db_name="phones.db"))

async def scrape():
    phone_db = FoneDB(r'Certificates/RapidSSL_TLS_RSA_CA_G1.crt',database=DB)
    brands=["Samsung","Xiaomi"]
    try:
        for brand in brands:
            await phone_db.get_devices(brand)
    finally:
        await phone_db.close()
    
    print(f"✅ Total stored models: {DB.get_record_count()}")

def loade_devices():
    total=DB.get_record_count()
    total_samsung=DB.get_record_count(conditions=[Device.brand=="Samsung"])
    total_xiaomi=DB.get_record_count(conditions=[Device.brand=="Xiaomi"])
    


    print(f"✅ Total stored models: {total}")
    print(f"✅ Total stored Samsung models: {total_samsung}")
    print(f"✅ Total stored Xiaomi models: {total_xiaomi}")

    devices:list[Device]= DB.get()
    print("✅ First device:\n",  devices[0])
    
   




if __name__ == "__main__":
    asyncio.run(scrape())
    loade_devices()

```

---

### Example Output:

```
✅ Total stored models: 1082
✅ Total stored Samsung models: 734
✅ Total stored Xiaomi models: 348
✅ First device:
{
    "model": "SM-E066B/DS",
    "brand": "Samsung",
    "name": "Samsung Galaxy F06 5G Standard Edition Global Dual Sim",
    "os_system": "Android",
    "os_version": 14,
    "sdk_version": 34,
    "memory": "128GB",
    "regions": "GLOBAL",
    "edition": "Standard Edition ",
    "is_global": true,
    "dual_sim": true,
    "url": "https://phonedb.net/index.php?m=device&id=24739&c=samsung_sm-e066bds_galaxy_f06_5g_2025_standard_edition_global_dual_sim_td-lte_128gb__samsung_a066"
}

```

## 📜 **License**

This project is licensed under the **[MIT License](LICENSE)**.

---

## 👤 **Publisher / ناشر**

**[Abbas Bachari / عباس بچاری](https://github.com/abbas-bachari)**

---

## 💖 **Sponsor**

Support development by sponsoring on **[Github Sponsors](https://github.com/sponsors/abbas-bachari)**.
