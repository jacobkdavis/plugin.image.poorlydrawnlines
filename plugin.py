# -*- coding: utf8 -*-

# Copyright (C) 2016 - Jacob Davis
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcplugin
import xbmcgui
import random
import datetime
import routing
import re
from resources.lib.Utils import *

from lxml import html
import requests

plugin = routing.Plugin()

MAX_COUNT = 3868
ITEMS_PER_PAGE = 10


@plugin.route('/')
def root():
    items = [
        (plugin.url_for(todaysimages), xbmcgui.ListItem("Today´s images"), True),
        (plugin.url_for(browsebyoffset), xbmcgui.ListItem("Browse by offset"), True),
    ]
    xbmcplugin.addDirectoryItems(plugin.handle, items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/todaysimages')
def todaysimages():
    xbmcplugin.setContent(plugin.handle, 'images')
    items = get_pdl_images(randomize=True)
    for item in items:
        add_image(item)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/browsebyoffset')
def browsebyoffset():
    xbmcplugin.setContent(plugin.handle, 'genres')
    items = []
    for i in range(0, MAX_COUNT // ITEMS_PER_PAGE):
        items.append((plugin.url_for(browsebyoffset_view, i * ITEMS_PER_PAGE),
                      xbmcgui.ListItem("%s - %s" % (str(i * ITEMS_PER_PAGE + 1), str((i + 1) * ITEMS_PER_PAGE))),
                      True))
    xbmcplugin.addDirectoryItems(plugin.handle, items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/browsebyoffset/<offset>')
def browsebyoffset_view(offset):
    xbmcplugin.setContent(plugin.handle, 'images')
    items = get_pdl_images(offset=int(offset))
    for item in items:
        add_image(item)
    xbmcplugin.endOfDirectory(plugin.handle)


def get_pdl_images(limit=ITEMS_PER_PAGE, offset=0, randomize=False):
    now = datetime.datetime.now()
    filename = "pdl%ix%ix%i" % (now.month, now.day, now.year)
    path = xbmc.translatePath(ADDON_DATA_PATH + "/" + filename + ".txt")
    if xbmcvfs.exists(path) and randomize:
        return read_from_file(path)
    
    items = []

    archiveurl = "http://poorlydrawnlines.com/archive/"
    baseurl = "http://poorlydrawnlines.com/comic/"

    r = requests.get(archiveurl)
    comicurls = re.findall("href='http://poorlydrawnlines.com/comic/(.+?)/'", r.content, re.DOTALL)

    for i in range(0, limit):
        comic_id = random.randrange(1, MAX_COUNT) if randomize else i + offset
        
        url = baseurl + comicurls[comic_id]
        
        comiccontent = requests.get(url).content
        img = re.search("<img.*?src=\"(http://poorlydrawnlines.com/wp-content/uploads/.+?)\"", comiccontent).group(1)
        
        newitem = {'thumb': img,
                    'index': comicurls[comic_id],
                    'label': comicurls[comic_id]}
        items.append(newitem)
            
    save_to_file(content=items,
                 filename=filename,
                 path=ADDON_DATA_PATH)



    return items

if (__name__ == "__main__"):
    plugin.run()
xbmc.log('finished')

