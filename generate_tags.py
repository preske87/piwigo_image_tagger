#!/usr/bin/python3
import os
import datetime as dt
import json
import requests
import urllib
import re
import lib.config_handler as ch
import lib.classes as classes
from lib.classes import image
import lib.helper as helper
import lib.globals
import piwigo as piwi
import time
import logging


class tag_generator():

    def main(self):

        # Magic starts from here
        logging.info("Starting script....")
        self.piwigo_labels = dict()


        logging.debug("Retrieving config...")
        self.conf_handler = ch.config_handler()
        self.working_directory = "tmp"
        self.image_file_extensions = list(self.conf_handler.get_config_value(config=self.conf_handler.config, key="image_file_extensions", create_if_missing=True, value_if_missing=["JPG", "JPEG", "PNG"]))
        self.minimum_confidence_level = float(self.conf_handler.get_config_value(config=self.conf_handler.config, key="minimum_confidence_level", create_if_missing=True, value_if_missing=0.7))
        
        self.piwigo_url_root = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="piwigo_url_root", create_if_missing=True))
        self.piwigo_user = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="piwigo_user", create_if_missing=True))
        self.piwigo_pass = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="piwigo_pass", create_if_missing=True))
        
        self.subscription_key_images = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="azure_ai_subscription_key_images", create_if_missing=True))
        self.endpoint_url_images = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="azure_ai_endpoint_url_images", create_if_missing=True))

        self.subscription_key_translate = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="azure_ai_subscription_key_translate", create_if_missing=True))
        self.endpoint_url_translate = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="azure_ai_endpoint_url_translate", create_if_missing=True))
        self.region_translate = str(self.conf_handler.get_config_value(config=self.conf_handler.config, key="azure_ai_subscription_region_translate", create_if_missing=True))

        #TODO: Make configurable, currently hardcoded also in areas below
        self.translation_from = "en"
        self.translation_to = "de"

        self.pw = piwi.Piwigo(self.piwigo_url_root)
        self.pw.pwg.session.login(username=self.piwigo_user, password=self.piwigo_pass)
        
        _continue_fetch_images = True
        _page_size = 10
        _page_count = 0
        while _continue_fetch_images:
            logging.info("Fetching Images from Piwigo: page " + str(_page_count))
            _pw_images = self.pw.pwg.categories.getImages(page=_page_count,per_page=_page_size)
            self.process_pw_images(pw_images=_pw_images)
            try:
                if _pw_images["paging"]["count"] == 0:
                    _continue_fetch_images = False
                    logging.info("Stopping fetching further images, page has 0 images")
                _page_count = _page_count+1
            except Exception as ex:
                logging.error("Error while fetching images from Piwigo." + 
                    "\npw_images: " + str(_pw_images) + "\n\n",
                    exc_info=ex)
        
    def process_pw_images(self, pw_images):
        logging.info("Processing images from pw_images with " + str(len(pw_images["images"])) + " images")
        for pw_image in pw_images['images']:
            img = image()
            img.id = pw_image['id']
            img.file_name = pw_image['file']
            img.web_url = pw_image['derivatives']['large']['url']
            img.extension = pw_image['file'].split('.')[1]
            img.local_file = os.path.join(self.working_directory, str(img.id) + "." + img.extension)

            logging.debug("Processing image " + pw_image['file'] + ": id " + str(img.id))

            if self.conf_handler.is_image_id_processed(img.id):
                logging.debug("Skipping image " + str(img.file_name) + ": It was already processed")
                continue

            logging.debug("Downloading image " + str(img.file_name) + " as " + img.local_file)
            response = requests.get(img.web_url)
            with open(img.local_file, 'wb') as f:
                f.write(response.content)

            if not img.extension.upper() in self.image_file_extensions:
                logging.debug("Skipping image " + str(img.file_name) + ": Image has extension '" + img.extension + "', this is not in the list of defined extensions (" + ','.join(self.image_file_extensions) + ")")
                continue

            if os.stat(img.local_file).st_size < 1024:
                logging.debug("Skipping image " + str(img.file_name) + ": File is too small (<1kB), deleting it again and skipping analysis")
            else:    
                #Image analysis
                logging.info("Analyzing image " + img.local_file)
                try:
                    #TODO: this could be made configurable later on
                    logging.debug("Waiting 3 seconds for the request to prevent exceeding the limit of 20 calls per minute")
                    time.sleep(3)
                    ai_helper_images = helper.azure_ai_helper(self.endpoint_url_images, self.subscription_key_images, region=None)
                    ai_helper_translate = helper.azure_ai_helper(self.endpoint_url_translate, self.subscription_key_translate, region=self.region_translate)
                    analysis = ai_helper_images.get_image_analysis(img.local_file)
                    tags = analysis["tags"]
                    logging.info("Fetched " + str(len(tags)) + " tags")
                    for tag in tags:
                        if tag["confidence"] >= self.minimum_confidence_level:
                            logging.debug("Tag '" + tag['name'] + "'is relevant enough, translating...")
                            try:
                                tag_original = tag["name"]
                                tag_translated = self.conf_handler.get_translation(language_from=self.translation_from, language_to=self.translation_to, text_from=tag_original)
                                
                                if tag_translated:
                                    logging.debug("Translation does exist: " + tag_original + " -> " + tag_translated)
                                else:
                                    logging.info("Getting translation for tag '" + tag_original + "' from Azure")
                                    tag_translated = ai_helper_translate.get_translation_en_de(tag['name'])
                                    self.conf_handler.set_translation(language_from=self.translation_from, language_to=self.translation_to, text_from=tag_original, text_to=tag_translated)
                                    
                                tag_translated = tag_translated.capitalize()
                                
                                logging.info("Adding tag '" + tag_translated + "' to the source image")
                                img.tags.append(tag_translated)
                            
                            except Exception as ex:
                                logging.error("Exception during tag translation", exc_info=ex)
                                img.has_processing_error = True
                        else:
                            logging.info("Tag '" + tag["name"] + "' has confidence of less than " + str(self.minimum_confidence_level) + ", (" + str(tag["confidence"]) + ") - skipping ")
                    if len(analysis["description"]["captions"]) > 0:
                        logging.info("Description was found")
                        if analysis["description"]["captions"][0]["confidence"] >= self.minimum_confidence_level:
                            logging.debug("Description meets minimum confidence level")
                            #TODO: Make language configurable
                            caption_en = analysis["description"]["captions"][0]["text"].capitalize()
                            logging.debug("Description is getting translated")
                            caption_de = ai_helper_translate.get_translation_en_de(caption_en)
                            img.caption = caption_de
                except Exception as ex:
                    logging.error("Exception during image analyzing", exc_info=ex)
                    img.has_processing_error = True
            
            self.get_pw_tags()
            pw_tags_changed = False
            for img_tag in img.tags:
                if not img_tag in self.pw_tags:
                    try:
                        logging.info("Adding new tag to piwigo: " + img_tag)
                        self.pw.pwg.tags.add(name=img_tag)
                        pw_tags_changed = True
                    except Exception as ex:
                        logging.exception("Exception during creation new tag", exc_info=ex)
                        img.has_processing_error = True
            
            if pw_tags_changed:
                self.get_pw_tags()

            for img_tag in img.tags:
                logging.info("Adding tag '" + img_tag + "' to image with id " + str(img.id))
                try:
                    self.pw.pwg.images.setInfo(image_id=img.id, tag_ids=self.pw_tags[img_tag])
                except Exception as ex:
                    logging.exception("Exception during adding tag to image", exc_info=ex)
                    img.has_processing_error = True
            
            if img.caption and len(img.caption) > 0:
                logging.info("Adding image comment")
                try:
                    self.pw.pwg.images.setInfo(image_id=img.id, comment=img.caption)
                except Exception as ex:
                    logging.error("Exception during adding comment to image", exc_info=ex)
                    img.has_processing_error = True

            if not img.has_processing_error:
                logging.info("Adding image id " + str(img.id) + " to the list of processed_images_ids")
                self.conf_handler.set_processed_image_id(processed_image_id=img.id)
            else:
                logging.error("Cannot add image id " + str(img.id) + " to the list of processed_images_ids, img.has_processing_error is " + str(img.has_processing_error))
            
            logging.info("Deleting file " + img.local_file)
            os.remove(img.local_file)

    def get_pw_tags(self):
        logging.info("Getting tags in use at Piwigo")
        pw_tag_getlist_reply = self.pw.pwg.tags.getAdminList()
        self.pw_tags = dict()
        for pw_tag in pw_tag_getlist_reply["tags"]:
            self.pw_tags[pw_tag['name']] = pw_tag["id"]
        return None

if __name__ == "__main__":
    tg = tag_generator()
    try:
        tg.main()
    except Exception as ex:
        logging.error("A general error has occured: " + str(ex), exc_info=ex)
