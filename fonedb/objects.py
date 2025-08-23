class Description:
    def __init__(self,url:str,title:str,description:str):
        self.url=url
        self.title=title
        self.description=description

    def to_dict(self):
        return {"url":self.url,"title":self.title,"description":self.description}

    def __repr__(self):
        return f"Description(url={self.url},title={self.title},description={self.description})"


class Device:
    
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
        return f"Device(brand={self.brand}, model={self.model} , name={self.name})"
    def __str__(self):
        _dbr=f'("{self.brand} {self.model}","SDK {self.sdk_version}"),'
        return f'{_dbr:<40} # {self.name} ({self.os_system} {self.os_version})'