import urllib.parse
from app.services.data_retrieval.sector_data import SectorData

def build_openalex_query(sector_name: str, sector_data: SectorData):

    keywords = sector_data.get_keywords(sector_name)
    if not keywords:
        return ""

    # Enclose each keyword in double quotes
    quoted_keywords = [f'"{kw}"' for kw in keywords]
    query_string = " OR ".join(quoted_keywords)

    return query_string


