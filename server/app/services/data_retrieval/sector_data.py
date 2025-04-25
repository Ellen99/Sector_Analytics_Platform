import json

class SectorData:
    def __init__(self, json_path):
        with open(json_path, 'r') as file:
            self._data = json.load(file)
    
    def get_description(self, sector_name):
        return self._data.get(sector_name, {}).get('description', '')

    def get_keywords(self, sector_name):
        return self._data.get(sector_name, {}).get('keywords', [])

    def get_all_descriptions(self):
        return {sector: details['description'] for sector, details in self._data.items()}

    def get_all_keywords(self):
        return {sector: details['keywords'] for sector, details in self._data.items()}
    def get_all_sectors(self):
        return self._data.keys()