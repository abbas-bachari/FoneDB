from sqlalchemy import Column, Integer,  String,Boolean
from sqlalchemy.orm import declarative_base
from dbflux import Sqlite,DBModel,BaseDB
import json
Base = declarative_base()



class Device(Base):
    __tablename__ = "devices"

    model       = Column(String,primary_key=True)
    brand       = Column(String)
    name        = Column(String)
    os_system   = Column(String)
    os_version  = Column(String)
    sdk_version = Column(Integer)
    memory      = Column(String)
    regions     = Column(String)
    edition     = Column(String)
    is_global   = Column(Boolean)
    dual_sim    = Column(Boolean)
    url         = Column(String)

    
    def __init__(self,model:str,brand:str=None,name:str=None,os_system:str=None,os_version:int=None,sdk_version:int=None,memory:str=None,regions:str=None,edition:str=None,is_global:bool=None,dual_sim:bool=None,url:str=None):
        self.model=model
        self.brand=brand
        self.name=name
        self.os_system=os_system
        self.os_version=os_version
        self.sdk_version=sdk_version
        self.memory=memory
        self.regions=regions
        self.edition=edition
        self.is_global=is_global
        self.dual_sim=dual_sim
        self.url=url
    
    def to_dict(self):
        return {
            "model": self.model,
            "brand": self.brand,
            "name": self.name,
            "os_system": self.os_system,
            "os_version": self.os_version,
            "sdk_version": self.sdk_version,
            "memory": self.memory,
            "regions": self.regions,
            "edition": self.edition,
            "is_global": self.is_global,
            "dual_sim": self.dual_sim,
            "url": self.url
        }
    def __repr__(self):
        return f"{self.__class__.__name__}({", ".join(f"{key}={value!r}" for key, value in self.to_dict().items())})"
    def __str__(self):
        
        return json.dumps(self.to_dict(),indent=4,ensure_ascii=False)
    

class Storage(DBModel):
    def __init__(self,base_db:BaseDB=Sqlite(db_name="phones.db")):
        """
        Initialize the storage object.

        Args:
            base_db (BaseDB): The base for the model. Defaults to a Sqlite database
                with the name "phones.db".
        """
        super().__init__(Device,base_db)
        self.create_tables(Base)



