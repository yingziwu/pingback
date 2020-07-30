import re
import logging
from urllib.request import urlopen
from xml.parsers.expat import ExpatError
from xmlrpc.client import ServerProxy, Error


def ping(source_url, target_url):
    '''
    Makes a pingback request to target_url on behalf of source_url, i.e.
    effectively saying to target_url that "the page at source_url is
    linking to you".
    '''

    def search_link(f):
        content = f.read(512 * 1024)
        match = re.search(rb'<link rel="pingback" href="([^"]+)" ?/?>', content)
        return match and match.group(1).decode('utf-8')

    request_url = 'http:%s' % target_url if target_url.startswith('//') else target_url
    ping_status = False
    logging.debug('Request origin url: {0}'.format(request_url))
    f = urlopen(request_url, timeout=3)
    try:
        info = f.info()
        server_url = info.get('X-Pingback', '') or search_link(f)
        if server_url:
            logging.debug('Send pingback: server_url: {0}, '
                          'source url: {1}, target url: {2}.'.format(server_url, source_url, target_url))
            server = ServerProxy(server_url)
            server.pingback.ping(source_url, target_url)
            ping_status = True
    finally:
        f.close()
    return ping_status


def ping_urls(source_url, target_url_list):
    '''
    Makes pingback requests to all links in url list.
    source_url is a URL of the page contaning HTML fragment.
    '''
    result = {}
    for url in target_url_list:
        if (url.startswith('http://') or url.startswith('https://')) and url not in result:
            try:
                ping_status = ping(source_url, url)
                result[url] = {"status": True, "ping_status": ping_status}
                logging.info('url: {0}, status: {1}, ping status: {2}'.format(url, True, ping_status))
            except IOError:
                result[url] = {"status": False, "error": "IOerror."}
                logging.info('url: {0}, status: {1}, error: {2}'.format(url, True, "IOerror."))
            except (Error, ExpatError):
                result[url] = {"status": False, "error": "XMP-RPC error."}
                logging.info('url: {0}, status: {1}, error: {2}'.format(url, True, "XMP-RPC error."))
        else:
            result[url] = {"status": False}
    return result
