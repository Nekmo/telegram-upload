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
        video_meta = metadata
        meta_groups = metadata._MultipleMetadata__groups
        if not metadata.has('width') and meta_groups:
            video_meta = meta_groups[next(filter(lambda x: x.startswith('video'), meta_groups._key_list))]
        attrs.append(DocumentAttributeStreamVideo(
            (0, metadata.get('duration').seconds)[metadata.has('duration')],
            (0, video_meta.get('width'))[video_meta.has('width')],
            (0, video_meta.get('height'))[video_meta.has('height')]
        ))
    return attrs


def get_file_thumb(file):
    if get_file_mime(file) == 'video':
        return get_video_thumb(file)
