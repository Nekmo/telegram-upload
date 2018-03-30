from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import mimetypes

from telegram_upload.video import DocumentAttributeStreamVideo, get_video_thumb, video_metadata

mimetypes.init()


def get_file_mime(file):
    return (mimetypes.guess_type(file)[0] or ('')).split('/')[0]


def get_file_attributes(file):
    attrs = []
    mime = get_file_mime(file)
    if mime == 'video':
        metadata = video_metadata(file)
        attrs.append(DocumentAttributeStreamVideo(
            (0, metadata.get('duration').seconds)[metadata.has('duration')],
            (0, metadata.get('width'))[metadata.has('width')],
            (0, metadata.get('height'))[metadata.has('height')]
        ))
    return attrs


def get_file_thumb(file):
    if get_file_mime(file) == 'video':
        return get_video_thumb(file)
