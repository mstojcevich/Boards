from functools import lru_cache
from io import BytesIO
from urllib.parse import urljoin
from PIL import Image
from urllib.request import Request, urlopen
import asyncio
from boards.database import engine
from bs4 import BeautifulSoup
import aiohttp

user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
request_headers = {
    'User-Agent': user_agent
}


class HeadRequest(Request):
    def get_method(self):
        return 'HEAD'


def get_content_type(url):
    """
    Get the content type of a url without downloading
    :return: lowercase content type of the url
    :rtype: string
    """
    request = HeadRequest(url, data=None, headers=request_headers)
    response = urlopen(request)
    response_headers = dict(response.info())
    headers_lowercase = {k.lower(): v for k, v in response_headers.items()}
    return headers_lowercase.get('content-type').lower()


@lru_cache(maxsize=128)
@asyncio.coroutine
def get_image_dimensions(url, referer=None):  # modified version of getImageInfo from bfg-pages
    """
    Get dimensions from a partial image download from a url
    :param url: URL of the image
    :return: (url, width, height)
    :rtype: (string, number, number)
    """
    headers = {
        'User-Agent': user_agent,
        'Range': 'bytes=0-1024'
    }
    if referer:
        headers['Referer'] = referer
    try:
        response = yield from aiohttp.request('get', url, headers=headers)
        data = yield from response.content.read(1024)
        response.close()
    except (OSError, ValueError):  # Couldn't read
        return

    if not data:
        return
    try:
        image = Image.open(BytesIO(data))
        if image:
            return url, image.size[0], image.size[1]
    except Exception as e:
        print(str(e) + ' at ' + url)
    return

def is_square(dimensions, max_ratio=1.0):
    """
    :param dimensions: (width, height)
    :type dimensions: (number, number)
    :param max_ratio: Maximum aspect ratio.
    :return: True if the dimensions represent a square
    """
    width, height = dimensions[0], dimensions[1]
    if width == 0 or height == 0:
        return False
    return 1/max_ratio <= width / height <= max_ratio


def find_largest_square_image(url, max_ratio=1.0, min_area=0):
    """
    Find the largest square image on the page
    :param url: URL to an HTML page
    :param max_ratio: Maximum aspect ratio. Must be greater than 1
    :return: URL of the largest image, None if no square images exist
    """
    request = Request(url, headers=request_headers)
    html = urlopen(request).read()

    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img', src=True)

    urls = [urljoin(url, img['src']) for img in images]

    biggest_src = None
    biggest_area = 0
    coroutines = [get_image_dimensions(img_url) for img_url in urls]
    results = asyncio.get_event_loop().run_until_complete(asyncio.gather(*coroutines))
    for result in results:
        if result is not None:
            img_url, width, height = result
            if is_square((width, height), max_ratio=max_ratio):
                area = width*height
                if area > biggest_area and area > min_area:
                    biggest_area = area
                    biggest_src = img_url

    return biggest_src


def create_thumbnail(url, post_id):
    """
    Creates a thumbnail for a post

    :returns path to the thumbnail
    """
    content_type = get_content_type(url)
    if 'image/' in content_type:
        try:
            request = Request(url, data=None, headers=request_headers)
            img_bytes = BytesIO(urlopen(request).read())
            og_image = Image.open(img_bytes)
        except OSError:  # Usually happens when link wasn't an image
            return
    elif 'text/html' in content_type:
        url = find_largest_square_image(url, max_ratio=2, min_area=2000)
        request = Request(url, data=None, headers=request_headers)
        img_bytes = BytesIO(urlopen(request).read())
        og_image = Image.open(img_bytes)
    else:
        return
    og_image.thumbnail((128, 128))
    path = 'static/images/thumbnails/%d.jpg' % post_id
    og_image.save('boards/' + path, 'JPEG', quality=85)
    engine.execute('UPDATE posts SET thumbnail=\'%s\' WHERE id=%d' % ('/' + path, post_id))
