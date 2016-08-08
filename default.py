import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import re
import urllib
import urllib2
import urlparse
import json

# uris
plugin_url = sys.argv[0]
base_url = 'http://nos.nl/livestream'
channel_name = ['npo nieuws', 'npo politiek', 'npo sport']
channel_url = {'npo nieuws': '/npo-nieuws.html', 'npo politiek': '/npo-politiek.html', 'npo sport': '/npo-sport.html'}

# regex
re_video = re.compile('<video[ ]{1,}class="[^"]+"[ ]{0,}controls="[^"]+"[ ]{0,}data-type="[^"]+"[ ]{0,}data-stream="([^"]+)"[ ]{0,}data-path="([^"]+)"[ ]{1,}data-muted="[^"]+"[ ]{0,}data-controls="[^"]+"[ ]{0,}>[ ]{0,}</video>')
re_stream = re.compile('.*\("([^"]+)"\)')

# args
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
loc = args.get('location', None)
xbmcplugin.setContent(addon_handle, 'episodes')

def build_url(query):
    return plugin_url + '?' + urllib.urlencode(query)
    
def addLink(channel, location, mode):
    url = build_url({'mode': mode, 'location': location})
    li = xbmcgui.ListItem(channel)
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(addon_handle, url = url, listitem = li, isFolder=False)

def getHtml(url):
    req = urllib2.Request(url)
    # don't use a header as you won't get the 'video' node if you do
    
    return urllib2.urlopen(req).read().replace('\n', '')

def playStream(location):
    html = getHtml(base_url + location)
    videos = re.findall(re_video, html)
    
    for video in videos:
        stream = getStream(video[1], video[0])
        
        listItem = xbmcgui.ListItem(path=stream)
        listItem.setProperty('IsPlayable', 'true')
        
        xbmcplugin.setResolvedUrl(addon_handle, True, listItem)

        
def getStream(url, data):
    # first we'll retrieve a token
    req = urllib2.Request(url)
    response = urllib2.urlopen(req, '{"stream":"' + data + '"}').read().replace('\\', '')
    xbmc.log(response)
    response_json = json.loads(response)

    # then we'll use the token to retrieve the stream uri
    stream_req = urllib2.Request(response_json['url'])
    stream_response = urllib2.urlopen(stream_req).read().replace('\\', '')
    streams = re.findall(re_stream, stream_response)

    # return the first match (should be one)
    for stream in streams:
        return stream

if mode is None:
    for name in channel_name:
        addLink(name, channel_url[name], 'channel')

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'channel':
    playStream(loc[0])
        
    xbmcplugin.endOfDirectory(addon_handle)