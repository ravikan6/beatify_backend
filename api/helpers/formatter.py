import random
import time

class JioSaavn:
    @staticmethod
    def generate_jiosaavan_id(original_id):
        return f"BJS_#{original_id}"

    @staticmethod
    def get_id(id):
        return id.split("_#")[1]

    @staticmethod
    def image_quility(url: str, imageQuility: str | int = "150x150") -> str:
        if type(imageQuility) is int:
            if imageQuility == 1:
                imageQuility = "50x50"
            elif imageQuility == 2:
                imageQuility = "150x150"
            elif imageQuility == 3:
                imageQuility = "500x500"
            else:
                imageQuility = "150x150"
        if url is None: return None
        if url.find("50x50") != -1: return url.replace("50x50", imageQuility)
        if url.find("150x150") != -1: return url.replace("150x150", imageQuility)
        if url.find("175x175") != -1: return url.replace("500x500", imageQuility)
        return url

    @staticmethod
    def jiosaavan_albums_formatted(albums: list, imageQuility: str | int = "150x150") -> list:
        return [jiosaavan_album_formatter(album, imageQuility) for album in albums]



def jiosaavan_album_formatter(album: dict, imageQuility) -> dict:
    
    _primary_artists = album.get('more_info', {}).get('artistMap', {}).get('primary_artists', [])
    _featured_artists = album.get('more_info', {}).get('artistMap', {}).get('featured_artists', [])
    _artists = album.get('more_info', {}).get('artistMap', {}).get('artists', [])

    data = {
        "id": JioSaavn.generate_jiosaavan_id(album.get('id', None)),
        "title": album.get('title', 'Unknown Album'),
        "subtitle": album.get('subtitle', None),
        "type": album.get('type', 'album'),
        "image": JioSaavn.image_quility(album.get('image', None), imageQuility),
        "language": album.get('language', None),
        "play_count": album.get('play_count', 0),
        "explicit_content": album.get('explicit_content', None),
        "list_count": album.get('list_count', 0),
        "list_type": album.get('list_type', None),
        "list": album.get('list', None),
        "year": album.get('year', None),
        "more": {
            "songs": int(album.get('more_info', {}).get('song_count', 0)),
            "release_date": album.get('more_info', {}).get('release_date', None),
            "artists": {
                "primary": [jiosaavan_content_artist_formatter(artist) for artist in _primary_artists],
                "featured": [jiosaavan_content_artist_formatter(artist) for artist in _featured_artists],
                "all": [jiosaavan_content_artist_formatter(artist) for artist in _artists],
            },
        }   
    }

    return data

def jiosaavan_content_artist_formatter(artist):
    return {
        "id": JioSaavn.generate_jiosaavan_id(artist.get('id', None)),
        "name": artist.get('name', 'Unknown Artist'),
        "role": artist.get('role', None),
        "type": artist.get('type', 'artist'),
        "image": JioSaavn.image_quility(artist.get('image', None), None),
        # "more": {
        #     "followers": artist.get('more_info', {}).get('followers', None),
        #     "top_songs": artist.get('more_info', {}).get('top_songs', None),
        #     "top_albums": artist.get('more_info', {}).get('top_albums', None),
        #     "bio": artist.get('more_info', {}).get('bio', None),
        #     "twitter": artist.get('more_info', {}).get('twitter', None),
        #     "facebook": artist.get('more_info', {}).get('facebook', None),
        #     "instagram": artist.get('more_info', {}).get('instagram', None),
        #     "youtube": artist.get('more_info', {}).get('youtube', None),
        # }
    }