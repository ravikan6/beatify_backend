import random
import time
from ..utils import decrypt_saavan_media_link
import urllib.parse
import html
class JioSaavn:
    @staticmethod
    def generate_jiosaavan_id(original_id):
        return f"BJS_@{original_id}"

    @staticmethod
    def get_id(id):
        try:
            id = urllib.parse.unquote(id)
            return id.split("_@")[1]
        except:
            return id

    @staticmethod
    def image_size(url: str, imageSize: str = 'low') -> str:
        if imageSize == 'low': imageSize = "50x50"
        elif imageSize == 'medium': imageSize = "150x150"
        elif imageSize == 'high': imageSize = "500x500"
        else : imageSize = "150x150"
        if url is None: return None
        if url.find("50x50") != -1: return url.replace("50x50", imageSize)
        if url.find("150x150") != -1: return url.replace("150x150", imageSize)
        if url.find("175x175") != -1: return url.replace("500x500", imageSize)
        return url

    @staticmethod
    def link_to_id_extracter(url: str):
        url = urllib.parse.unquote(url)
        url = url.split('/')[-1]
        return url

    @staticmethod
    def jiosaavan_albums_formatted(albums: list, imageSize: str, include_songs: bool) -> list:
        return [JioSaavn.jiosaavan_album_formatter(album, imageSize, include_songs) for album in albums]

    @staticmethod
    def jiosaavan_playlist_formatted(lists: list, imageSize: str) -> list:
        return [JioSaavn.jiosaavan_playlist_formatter(_list, imageSize) for _list in lists]

    @staticmethod
    def jiosaavan_album_formatter(album: dict, imageSize,include_songs: bool, include_color: bool = False ) -> dict:
        
        _primary_artists = album.get('more_info', {}).get('artistMap', {}).get('primary_artists', [])
        _featured_artists = album.get('more_info', {}).get('artistMap', {}).get('featured_artists', [])
        _artists = duplicate_filter(album.get('more_info', {}).get('artistMap', {}).get('artists', []))

        if album.get('perma_url', None):
            id = JioSaavn.link_to_id_extracter(album.get('perma_url', None))
        else:
            id = album.get('id', None)

        # if include_color and album.get('image', None):
        #     img_array = image_from_url(JioSaavn.image_size(album.get('image', None), 'medium'), image_processing_size=(150, 150))
        #     extractor = ColorExtractor(img_array)
        #     best_color = extractor.best_color(plot=False)
        #     album['color'] = extractor.format_color(best_color)

        data = {
            "id": JioSaavn.generate_jiosaavan_id( id ),
            "key": album.get('id', None),
            "title": unescaper(album.get('title', 'Unknown Album')),
            "subtitle": unescaper(album.get('subtitle', None)),
            "type": album.get('type', 'album'),
            "color": album.get('color', None),
            "album_type": 'single' if stringToInt(album.get('list_count', 0)) == 1 else album.get('album_type', None) or album.get('type', 'album'),
            "image": JioSaavn.image_size(album.get('image', None), imageSize),
            "language": album.get('language', None),
            "play_count": stringToInt(album.get('play_count', 0)),
            "explicit_content": stringToInt(album.get('explicit_content', None)) == 1 or False,
            "list_count": stringToInt(album.get('list_count', 0)),
            "list_type": album.get('list_type', None),
            "list":  [jiosaavan_track_formatter(track, imageSize) for track in album.get('list', [])] if include_songs else [],
            "year": album.get('year', None),
            "more": {
                "songs": stringToInt(album.get('more_info', {}).get('song_count', 0)),
                "release_date": album.get('more_info', {}).get('release_date', None),
                "artists": {
                    "primary": [jiosaavan_content_artist_formatter(artist) for artist in _primary_artists],
                    "featured": [jiosaavan_content_artist_formatter(artist) for artist in _featured_artists],
                    "all": [jiosaavan_content_artist_formatter(artist) for artist in _artists],
                },
                "copyright_text": unescaper(album.get('more_info', {}).get('copyright_text', None)),
            }   
        }

        return data

    @staticmethod
    def jiosaavan_playlist_formatter(_list: dict, imageSize, include_songs: bool = False, include_color: bool = False ) -> dict:

        if _list.get('perma_url', None):
            id = JioSaavn.link_to_id_extracter(_list.get('perma_url', None))
        else:
            id = _list.get('id', None)

        _artists = duplicate_filter(_list.get('more_info', {}).get('artists', []))

        more_info = _list.get('more_info', {})

        data = {
            "id": JioSaavn.generate_jiosaavan_id( id ),
            "key": _list.get('id', None),
            "title": unescaper(_list.get('title', 'Unknown Album')),
            "subtitle": unescaper(_list.get('subtitle', None)),
            "type": _list.get('type', 'playlist'),
            "playlist_type": more_info.get('playlist_type', 'playlist'),
            "color": _list.get('color', None),
            "image": JioSaavn.image_size(_list.get('image', None), imageSize),
            "language": _list.get('language', None),
            "play_count": stringToInt(_list.get('play_count', 0)),
            "explicit_content": stringToInt(_list.get('explicit_content', None)) == 1 or False,
            "list_count": stringToInt(_list.get('list_count', 0)),
            "list_type": _list.get('list_type', None),
            "list":  [jiosaavan_track_formatter(track, imageSize) for track in _list.get('list', [])] if include_songs else [],
            "year": _list.get('year', None),
            "more": {
                "songs": stringToInt(more_info.get('song_count', 0)),
                "isWeekly": more_info.get('isWeekly', 0) == 'true' or False,
                "followers": stringToInt(more_info.get('follower_count', 0)),
                "fans": more_info.get('fan_count', '0'),
                'artists':  [jiosaavan_content_artist_formatter(artist) for artist in _artists],
                "description": unescaper(_list.get('header_desc', None)),
                "last_updated": stringToInt(more_info.get('last_updated', None)),
                "user_id": None,
                "username": (more_info.get('firstname', None) + ' ' + more_info.get('lastname', None)),
                "user_image": None,
                "meta_string": ', '.join(more_info.get('subtitle_desc', [])),
            }   
        }

        return data


def unescaper(_str):
    if _str is None: return _str
    try: 
        return html.unescape(_str)
    except: 
        return _str


def jiosaavan_track_formatter(track: dict, imageSize: str) -> dict:
    _primary_artists = track.get('more_info', {}).get('artistMap', {}).get('primary_artists', [])
    _featured_artists = track.get('more_info', {}).get('artistMap', {}).get('featured_artists', [])
    _artists = duplicate_filter(track.get('more_info', {}).get('artistMap', {}).get('artists', []))

    media_url = decrypt_saavan_media_link(track.get('more_info', {}).get('encrypted_media_url', None))

    more_info = track.get('more_info', {})

    album = {
        "id": JioSaavn.generate_jiosaavan_id(JioSaavn.link_to_id_extracter(more_info.get('album_url', None))),
        "title": unescaper(more_info.get('album', None)),
        "type": 'album',
        "play_count": 0,
        'more': {
            'songs': 0,
            'release_date': more_info.get('release_date', None),
            'artists': {
                'primary': [],
                'featured': [],
                'all': [],
            }
        }
    }

    data = {
        "id": JioSaavn.generate_jiosaavan_id(JioSaavn.link_to_id_extracter(track.get('perma_url', None))),
        "key": track.get('id', None),
        "title": unescaper(track.get('title', 'Unknown Song')),
        "subtitle": unescaper(track.get('subtitle', None)),
        "type": track.get('type', 'song'),
        "album": album,
        "image": JioSaavn.image_size(track.get('image', None), imageSize),
        "language": track.get('language', None),
        "play_count": stringToInt(track.get('play_count', 0)),
        "explicit_content": stringToInt(track.get('explicit_content', None)) == 1 or False,
        "duration": stringToInt(more_info.get('duration', 0)),
        "can_play": media_url is not None,
        "media_url": media_url,
        "more": {
            "release_date": track.get('more_info', {}).get('release_date', None),
            "artists": {
                "primary": [jiosaavan_content_artist_formatter(artist) for artist in _primary_artists],
                "featured": [jiosaavan_content_artist_formatter(artist) for artist in _featured_artists],
                "all": [jiosaavan_content_artist_formatter(artist) for artist in _artists],
            },
            "music": track.get('more_info', {}).get('music', None),
            "label": track.get('more_info', {}).get('label', None),
            "origin": track.get('more_info', {}).get('origin', None),
            # "is_dolby_content": track.get('more_info', {}).get('is_dolby_content', None),
            # "rights": track.get('more_info', {}).get('rights', {}),
            "has_lyrics": track.get('more_info', {}).get('has_lyrics', None) == 'true' or False,
            "lyrics_snippet": track.get('more_info', {}).get('lyrics_snippet', None),
            # "starred": track.get('more_info', {}).get('starred', None),
            "copyright_text": track.get('more_info', {}).get('copyright_text', None),
            "vcode": track.get('more_info', {}).get('vcode', None),
            "vlink": track.get('more_info', {}).get('vlink', None),
            "triller_available": track.get('more_info', {}).get('triller_available', None),
            "webp": track.get('more_info', {}).get('webp', None),
            "lyrics_id": track.get('more_info', {}).get('lyrics_id', None)
        }
    }

    return data

def duplicate_filter(data: list):
    seen = set()
    filtered_data = []

    for item in data:
        identifier = item.get('key')
        
        if identifier not in seen:
            seen.add(identifier)
            filtered_data.append(item)

    return filtered_data


def stringToInt(value):
    if type(value) is int: return value
    if type(value) is not str: return 0
    try: return int(value)
    except: return 0

def jiosaavan_content_artist_formatter(artist):
    return {
        "id": JioSaavn.generate_jiosaavan_id(JioSaavn.link_to_id_extracter(artist.get('perma_url', None))),
        "key": artist.get('id', None),
        "name": artist.get('name', 'Unknown Artist'),
        "role": artist.get('role', None),
        "type": artist.get('type', 'artist'),
        "image": JioSaavn.image_size(artist.get('image', None), None),
    }
