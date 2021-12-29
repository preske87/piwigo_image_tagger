# About
This is my first project I am making publically available, so please bear with me if it is not meeting all expectations.

the `piwigo_image_tagger` is a small tool which 
* Retrieves images from a Piwigo image library
* Sends those images to Micsoroft Azure cognitive services for image recognition and tagging
* Adds the identified tags and descriptions then to the image in Piwigo.


## About Piwigo
Find more about Piwigo on [their website](http://piwigo.org/)

### Piwigo API
Documentation on the Piwigo API can be found [here](https://your-piwigo-installation/tools/ws.htm)

## About Azure Cognitive Services
Find out more on Azure Cognitive Services [here](https://azure.microsoft.com/en-us/services/cognitive-services)

Already with the **Free** pricing tier noticeable results can be achieved.

# How to use it?
Insert advise for Docker

````
python3 -m pip install piwigo
oder
pip install piwigo
oder
python -m pip install piwigo
````

# How does it work?

1. A user (or multiple users) upload images into a piwigo library
2. The script `generate_tags.py` is scheduled for automated execution
   1. Through the piwigo API (all) images are retrieved as json
   2. The script iterates through each of the images
      1. If the derived `id` is already known (hereby it is matched against the the stored value in `config.json`), the image is skipped. If not: continue
      2. If the image does not have an allowed file extension (again as per `config.json`), the image is skipped. If the extension is allowed: continue
      3. The **large** image is being downloaded into a temporary directory
      4. The downloaded image is being sent into the Azure AI endpoint
      5. The identified tags/keywords meeting the minimum relevance are being translated
         1. Firstly it is being checked if there is already a translation for the keyword available, if not a new translation is taken from Azure AI
      6. The identfiied and translated tags are stored into piwigo database
      7. The image ID is stored into local config

# Azure Services
## Cognitive Services: Bilderkennung

Ist zuständig für die Erkennung von Stichworten auf einem Bild

### Pricing Tier
* Free
    * 20 Calls per minute
    * 5000 Calls pro Monat
    * 1 Call = 1 Bild

## Cognitive Services: Translator
Ist zuständig für die Übersetzung eines englischen Begriffs in einen Deutschen

### Pricing Tier
* Free
    * 2 Mio Zeichen pro Monat