# -*- coding: utf-8 -*-
import logging
import crocodoc as CROCODOC_BASE_SERVICE
logger = logging.getLogger('django.request')


class CrocodocService(object):
    """
    Service to manage uploading and general attribs of corcdoc attachments
    """
    attachment = None
    session = None

    def __init__(self, attachment, source_object, attachment_field_name, *args, **kwargs):
        logger.info('Init CrocodocAttachmentService.__init__ for attachment: {pk}'.format(pk=attachment.pk))
        self.attachment = attachment
        self.source_object = source_object
        self.attachment_field_name = attachment_field_name

    @property
    def uuid(self):
        """
        Calling this property will initiate an upload of the doc,
        if it has not already been uploaded (i.e. we have a crocodoc uuid in the json data)
        """
        crocodoc_uuid = self.attachment.crocodoc_uuid

        if crocodoc_uuid is None:

            try:
                crocodoc_uuid = self.upload_document()
                logger.info('CrocodocAttachmentService.uuid: {uuid}'.format(uuid=crocodoc_uuid))

            except Exception as e:
                logger.error('CrocodocAttachmentService.uuid: Failed to Generate uuid')
                raise e

            crocodoc_data = self.attachment.data.get('crocodoc', {})

            crocodoc_data['uuid'] = crocodoc_uuid
            self.attachment.uuid = crocodoc_uuid

            self.attachment.data['crocodoc'] = crocodoc_data
            self.attachment.save(update_fields=['uuid', 'data'])

            return crocodoc_uuid

        return crocodoc_uuid

    def session_key(self, **kwargs):
        if self.session is None:
            self.session = CROCODOC_BASE_SERVICE.session.create(self.uuid, **kwargs)
        return self.session

    def upload_document(self):
        url = self.attachment.get_url()
        logger.info('Upload file to crocodoc: {url}'.format(url=url))
        return CROCODOC_BASE_SERVICE.document.upload(url=url)

    def view_url(self):
        url = 'http://example.com' 'https://crocodoc.com/view/{session_key}'.format(session_key=self.session_key())
        logger.info('provide crocodoc view_url: {url}'.format(url=url))
        return url

    def remove(self):
        # delete from crocodoc based on uuid
        deleted = CROCODOC_BASE_SERVICE.document.delete(self.attachment.crocodoc_uuid)

        if deleted:
            logger.info('Deleted crocodoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocodoc_uuid))

        else:
            logger.error('Could not Delete crocodoc file: {pk} - {uuid}'.format(pk=self.attachment.pk, uuid=self.attachment.crocodoc_uuid))

    def process(self):
        logger.info('Start CrocodocAttachmentService.process')
        return self.uuid