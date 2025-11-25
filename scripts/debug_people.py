import sys
import re
from pathlib import Path

# Mocking the class for quick test
class EntityExtractorV2:
    def __init__(self):
        self.vip_list = [] # Ignore VIP list for this test
        
    def extract_people(self, text: str):
        people = set()
        
        # Improved regex
        honorifics_list = r"श्री|श्रीमती|डॉ\.|माननीय|महामहिम|Shri|Smt|Dr|Mananiya|मुख्यमंत्री|प्रधानमंत्री|अध्यक्ष|मंत्री|सांसद|विधायक|Governor|Minister|CM|PM"
        name_pattern = f"(?:(?:{honorifics_list})\\s+)+((?:(?!{honorifics_list})[\u0900-\u097FA-Za-z]+\\s*){{1,3}})(?:\\s+जी|ji)?"
        
        for match in re.finditer(name_pattern, text, re.IGNORECASE):
            name = match.group(1).strip()
            name = re.sub(r"\s+(?:जी|ji)$", "", name, flags=re.IGNORECASE)
            
            if name not in ["मुख्यमंत्री", "प्रधानमंत्री", "अध्यक्ष", "CM", "PM", "Governor", "Minister", "सांसद", "विधायक"]:
                people.add(name)
        return sorted(list(people))

text = "आज अंबिकापुर में महामहिम राष्ट्रपति श्रीमती द्रौपदी मुर्मु जी के मुख्य आतिथ्य में आयोजित जनजातीय गौरव दिवस समारोह में आदरणीय केंद्रीय राज्य जनजातीय कार्य मंत्री श्री दुर्गा दास उइके जी, माननीय राज्यपाल श्री रमेन डेका जी, माननीय मुख्यमंत्री श्री विष्णु देव साय जी"

extractor = EntityExtractorV2()
print(extractor.extract_people(text))
