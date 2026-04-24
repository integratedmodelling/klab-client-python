class ObservationResource():
    '''
    Holds information of all resources used to Observe an Observable in a Context
    '''

    def __init__(self, id: str = None, description: str = None, urls: list[str] = None, originatorDescription: str = None, authors:list[str]= None, bibliographicReference:str=None)->None:
        self._id = id
        self._description = description
        self._urls = urls
        self._originatorDescription = originatorDescription
        self._authors = authors
        self._bibliographicReference = bibliographicReference

    @staticmethod
    def fromDict(d: dict)->list:
        if not d:
            return None
        
        obsResources:list[ObservationResource] = []
        
        for resItem in d:
            resource = resItem.get("resource", None)
            if resource is None:
                continue
            obsResources.append(ObservationResource(
                id = resItem.get("id"),
                description = resource.get("resourceDescription"),
                urls = resource.get("urls"),
                originatorDescription = resource.get("originatorDescription"),
                authors = resource.get("authors")
            ))

        return obsResources

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, id):
        self._id = id
    
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, description):
        self._description = description

    @property
    def urls(self):
        return self._urls
    @urls.setter
    def urls(self, urls):
        self._urls = urls
    
    @property
    def originatorDescription(self):    
        return self._originatorDescription
    @originatorDescription.setter
    def originatorDescription(self, originatorDescription):
        self._originatorDescription = originatorDescription

    @property
    def authors(self):
        return self._authors
    @authors.setter
    def authors(self, authors):
        self._authors = authors
    
    @property
    def bibliographicReference(self):
        return self._bibliographicReference
    @bibliographicReference.setter
    def bibliographicReference(self, bibliographicReference):
        self._bibliographicReference = bibliographicReference