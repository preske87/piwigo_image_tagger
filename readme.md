# About
This is my first project I am making publically available, so please bear with me if it is not meeting all expectations.

The `piwigo_image_tagger` is a small tool which 
* Retrieves images from a Piwigo image library
* Sends those images to Micsoroft Azure cognitive services for image recognition and tagging
* Adds the identified tags and descriptions then to the image in Piwigo.

![result in piwigo](readme_images/2021-12-30_09-39-36.png)


## About Piwigo
Find more about Piwigo on [their website](http://piwigo.org/)

### Piwigo API
Documentation on the Piwigo API can be found [here](https://your-piwigo-installation/tools/ws.htm)

## About Azure Cognitive Services
Find out more on Azure Cognitive Services [here](https://azure.microsoft.com/en-us/services/cognitive-services)

Already with the **Free** pricing tier noticeable results can be achieved.

# How to use it?

For all options you need to create a proper `config.json`, either into the project's `/config` directory or via mapping respective file/volume into the docker container.

## Option 1: run it locally

Execute the script [generate_tags.py](generate_tags.py) with locally installed python runtime.

It is recommended to use a virtual environment, but not mandatory.


Install the PIP requirements:
```
python3 -m pip install requests
python3 -m pip install -r pip_requirements.txt
```

Then execute the script 
```
python3 generate_tags.py
```
## Option 2: Run in Docker (recommended)
 Build a docker container based on the [Dockerfile](Dockerfile):
 ```
 docker build --tag pwigo_image_tagger .
 ``` 

 Then start the container and ensure volumes are mapped for `/config` and `/log`. Volume on `/config` is required for persistency.

 Or make use of [docker-compose](docker-compose.yml) (make sure volumes are mapped as defined in `docker-compose.yml`)
 ```
 docker-compose build
 docker-compose up -d
 ```

 There is also another `docker-compose` file which contains piwigo and mariadb database to run everything locally: [docker-compose.withPiwigo.yml](docker-compose.withPiwigo.yml).

# Configuration
All configuration is done through file `config/config.json`. 

If it doesn't exist, it is being automatically created on startup with dummy values.

Minimum config looks as followed (yes, due to the null-values it will throw errors)
```
{
    "azure_ai_endpoint_url_images": null,
    "azure_ai_endpoint_url_translate": null,
    "azure_ai_subscription_key_images": null,
    "azure_ai_subscription_key_translate": null,
    "azure_ai_subscription_region_translate": null,
    "image_file_extensions": [
        "JPG",
        "JPEG",
        "PNG"
    ],
    "minimum_confidence_level": 0.7,
    "wait_time_between_api_calls": 3,
    "piwigo_pass": null,
    "piwigo_url_root": null,
    "piwigo_user": null,
    "translation_from": "en",
    "translation_to": "de"
}
```
* `azure_ai_endpoint_url_images`: this is the Azure endpoint URL you get when you configure the Azure AI image recognition
* `azure_ai_endpoint_url_translate`: this is the Azure endpoint URL you get when you configure the Azure AI translation
* `azure_ai_subscription_key_images`: this is the subscription key for Azure AI image recognition
* `azure_ai_subscription_key_translate`: this is the subscription key for Azure AI translation
* `azure_ai_subscription_region_translate`: this is the region defined for the Azure AI translation
* `image_file_extensions`: list of file extensions to be processed (uppercase)
* `minimum_confidence_level`: the minimum confidence level for identified tags and descriptions. Only tags and description with higher or equal confidence level will be inserted.
* `piwigo_url_root`: the base URL of your piwigo installation
* `piwigo_user`: the user to be used for accessing piwigo
* `piwigo_pass`: the password for the pwigo_user
* `wait_time_between_api_calls`: the time period to be waited between images being sent to Azure API. Setting this is required when using the free tiers since they limit the amount of calls per minute.
* `translation_from`: the language code from which translation should be done. Unless there is an explicit need, leave it it `"en"`
* `translation_to`: the language code into which translation should be done. Use the language codes [support by Microsoft Azure Translater](https://docs.microsoft.com/en-us/azure/cognitive-services/translator/language-support)


# How does it work?

1. A user (or multiple users) upload images into a piwigo library
2. The script `generate_tags.py` is scheduled for automated execution
   1. Through the piwigo API (all) images are retrieved as json
   2. The script iterates through each of the images
      1. If the derived `id` is already known (hereby it is matched against the the stored value in `processed_images.json`), the image is skipped. If not: continue
      2. If the image does not have an allowed file extension (again as per `image_file_extensions` in `config.json`), the image is skipped. If the extension is allowed: continue
      3. The *large* image is being downloaded into a temporary directory
      4. The downloaded image is being sent into the Azure AI endpoint
      5. The identified tags/keywords meeting the minimum relevance are being translated
         1. Firstly it is being checked if there is already a translation for the keyword available, if not a new translation is taken from Azure AI
      6. The identfiied and translated tags are stored into piwigo database
      7. The image ID is stored into local config

# Azure Services
## Cognitive Services: Computer vision (image recognition)

This service is responsible for image recognition.

See [product page](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/#overview).

Or see [Quickstart](https://docs.microsoft.com/en-gb/azure/cognitive-services/Computer-vision/quickstarts-sdk/client-library?pivots=programming-language-python&tabs=visual-studio)

### Pricing
Already the free tier is sufficient for small-medium image libraries
* Free
    * 20 calls per minute
    * 5000 calls per month
    * 1 call = 1 image

## Cognitive Services: Translator
This service is responsible for translation.

See [product page](https://azure.microsoft.com/en-us/services/cognitive-services/translator/#overview).

Or see [What is Translater?](https://docs.microsoft.com/en-gb/azure/cognitive-services/translator/translator-overview?WT.mc_id=Portal-Microsoft_Azure_ProjectOxford)

### Pricing Tier
Already the free tier is sufficient for small-medium image libraries.
* Free
    * 2 Mio characters per month