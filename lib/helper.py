from .classes import image
import requests
import logging
import urllib
import re
import globals

class azure_ai_helper():

    def __init__(self, endpoint, subscription_key):
        self.endpoint = endpoint
        self.subscription_key = subscription_key
        logging.info("Creating azure_ai_helper with endpoint '" + self.endpoint + "' and subscription_key '" + self.subscription_key + "'")

    def get_translation_en_de(self, text):
        
        # Set image_path to the local path of an image that you want to analyze.
        translateable_text = text

        # Read the image into a byte array
        headers = {'Ocp-Apim-Subscription-Key': self.subscription_key, 'Content-Type': 'application/json'}
        params = {'api-version': '3.0', 'from': 'en', 'to': ['de']}
        body = []
        body.append({'Text': translateable_text})
        response = requests.post(self.endpoint + "/translate", headers=headers, params=params, json=body)
        response.raise_for_status()

        # The 'analysis' object contains various fields that describe the image. The most
        # relevant caption for the image is obtained from the 'description' property.
        translations_response = response.json()
        logging.info("Response from translate: " + str(translations_response))
        if len(translations_response) > 0:
            for translations in translations_response[0].values():
                #l.log("t is of type: " + str(type(translations)))
                for translation in translations:
                    #l.log(str(translation))
                    #l.log(translation["text"])
                    if translation["to"] == "de":
                        return translation["text"]
        return text

    def get_image_analysis(self, local_image):
        
        # Set image_path to the local path of an image that you want to analyze.
        image_path = local_image

        # Read the image into a byte array
        image_data = open(image_path, "rb").read()
        headers = {'Ocp-Apim-Subscription-Key': self.subscription_key, 'Content-Type': 'application/octet-stream'}
        params = {'visualFeatures': 'Categories,Description,Color,Tags,Faces,ImageType,Color,Adult,Objects,Brands'}
        response = requests.post(self.endpoint + "/vision/v2.0/analyze", headers=headers, params=params, data=image_data)
        response.raise_for_status()

        # The 'analysis' object contains various fields that describe the image. The most
        # relevant caption for the image is obtained from the 'description' property.
        analysis = response.json()
        logging.info("Response from analyze: " + str(analysis))
        logging.info(str(analysis))
        return analysis
