import os
import json
import shutil, sys
sys.path.insert(0, "./lib")
import globals
import logging

class config_handler():
    config_file = os.path.join("config", "config.json")
    config = dict()
    
    processed_image_id_file = os.path.join("config", "processed_images.json")
    processed_image_ids = dict()
    
    translations_file = os.path.join("config", "translations.json")
    translations = dict()

    def __init__(self):
        #Create config if it doesn't exist yet
        if not os.path.exists(self.config_file):
            with open(self.config_file, "w") as f:
                json.dump(obj=self.config, fp=f)
        
        if not os.path.exists(self.processed_image_id_file):
            with open(self.processed_image_id_file, "w") as f:
                json.dump(obj=self.processed_image_ids, fp=f)

        if not os.path.exists(self.translations_file):
            with open(self.translations_file, "w") as f:
                json.dump(obj=self.translations, fp=f)
        
        self.config = self.read_config_from_file(config=self.config, source_file=self.config_file)
        logging.info("config loaded with " + str(len(self.config)) + " records")

        self.processed_image_ids = self.read_config_from_file(config=self.processed_image_ids, source_file=self.processed_image_id_file)
        logging.info("processed_image_ids loaded with " + str(len(self.processed_image_ids)) + " records")

        self.translations = self.read_config_from_file(config=self.translations, source_file=self.translations_file)
        logging.info("translations loaded with " + str(len(self.translations)) + " records")
        
    def read_config_from_file(self, config, source_file):
        f = open(source_file, 'r')
        c = json.load(f)
        return c
    
    def get_config_value(self, config, key, create_if_missing=False, value_if_missing=None):
        if key in config:
            return config[key]
        elif create_if_missing:
            self.set_config_value(key=key, value=value_if_missing)
            return config[key]
        return None
    
    def set_config_value(self, key, value):
        self.config[key] = value
        with open(self.config_file, "w") as f:
            json.dump(obj=self.config, fp=f, indent=4, sort_keys=True)

    def get_translation(self, language_from:str, language_to:str, text_from:str):
        if language_from in self.translations and \
            language_to in self.translations[language_from] and \
                text_from in self.translations[language_from][language_to]:
                return self.translations[language_from][language_to][text_from]
        else:
            return None

    def set_translation(self, language_from:str, language_to:str, text_from:str, text_to:str):
        if not language_from in self.translations:
            self.translations[language_from] = dict()
        if not language_to in self.translations[language_from]:
            self.translations[language_from][language_to] = dict()
        if not text_from in self.translations[language_from][language_to]:
            self.translations[language_from][language_to][text_from] = text_to
        with open(self.translations_file, "w") as f:
            json.dump(obj=self.translations, fp=f, indent=4, sort_keys=True)
    
    def is_image_id_processed(self, image_id:int):
        if not image_id in self.processed_image_ids:
            return False
        else:
            return self.processed_image_ids[image_id]

    def set_processed_image_id(self, processed_image_id:int):
        if not processed_image_id in self.processed_image_ids:
            self.processed_image_ids[processed_image_id] = dict()
        self.processed_image_ids[processed_image_id]["processed"] = True
        with open(self.processed_image_id_file, "w") as f:
            json.dump(obj=self.processed_image_ids, fp=f, indent=4, sort_keys=True)
        

if __name__ == "__main__":
    config_handler()