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