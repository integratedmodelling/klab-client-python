

class KlabSpace():

    @staticmethod
    def isWKT(urn:str):
        return ("POLYGON" in urn or "POINT" in urn or "LINESTRING" in urn) and "(" in urn and ")" in urn


