# -*- coding: utf-8 -*-
from resources.lib.gui.gui import cGui
from resources.lib.gui.guiElement import cGuiElement
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser
from resources.lib import logger
from resources.lib.handler.ParameterHandler import ParameterHandler
from resources.lib.handler.pluginHandler import cPluginHandler
from resources.lib.util import cUtil
import re

SITE_IDENTIFIER = 'szene-streams_com'
SITE_NAME = 'Szene-Streams'

URL_MAIN = 'http://www.szene-streams.com/'
URL_MOVIES = URL_MAIN + 'publ/'

def load():
    logger.info("Load %s" % SITE_NAME)
    oGui = cGui()
    oGui.addFolder(cGuiElement('Filme', SITE_IDENTIFIER, 'showMovieMenu'))
    oGui.setEndOfDirectory()

def showMovieMenu():
    oGui = cGui()
    oGui.addFolder(cGuiElement('Genre', SITE_IDENTIFIER, 'showMovieGenre'))
    oGui.setEndOfDirectory()

def showMovieGenre():
    oGui = cGui()
    params = ParameterHandler()
    oRequestHandler = cRequestHandler(URL_MOVIES)
    sHtmlContent = oRequestHandler.request()
    pattern = '<a class="CatInf" href="([^"]+)">' # Get the URL
    pattern += '.*?<div class="CatNumInf">([^<>]+)</div>' # Get the entry count
    pattern += '.*?<div class="CatNameInf">([^<>]+)</div>' # Get the genre name
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]:
        return
    for sUrl, sNum, sName in aResult[1]:
        if not sUrl or not sNum or not sName: return
        oGuiElement = cGuiElement("%s (%d)" %(sName, int(sNum)), SITE_IDENTIFIER, 'showMovies')
        params.setParam('sUrl', sUrl)
        oGui.addFolder(oGuiElement, params)
    oGui.setEndOfDirectory()

def showMovies():
    oGui = cGui()
    params = ParameterHandler()
    oRequestHandler = cRequestHandler(params.getValue('sUrl'))
    sHtmlContent = oRequestHandler.request()
    pattern = '<div class="screenshot".*?<a href="([^"]+)" class="ulightbox"'
    pattern += '.*?<a class="newstitl entryLink".*?href="([^"]+)">([^<>]+)</a>'
    pattern += '.*?<div class="MessWrapsNews2".*?>([^<>]+).*?</div>'
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]:
        return
    for sThumbnail, sUrl, sName, sDesc in aResult[1]:
        oGuiElement = cGuiElement(sName, SITE_IDENTIFIER, 'showHosters')
        oGuiElement.setMediaType('movie')
        oGuiElement.setThumbnail(sThumbnail)
        oGuiElement.setDescription(sDesc.strip())
        params.setParam('entryUrl', sUrl)
        oGui.addFolder(oGuiElement, params, bIsFolder = False)
    oGui.setView('movie')
    oGui.setEndOfDirectory()

# Show the hosters dialog
def showHosters():
    params= ParameterHandler()
    oRequestHandler = cRequestHandler(params.getValue('entryUrl'))
    sHtmlContent = oRequestHandler.request()
    pattern = '<div class="inner" style="display:none;">'
    pattern += '.*?<a target="_blank" href="([^"]+)">'
    aResult = cParser().parse(sHtmlContent, pattern)
    if not aResult[0]:
        return
    hosters = []
    for sUrl in aResult[1]:
        logger.info(sUrl)
        hoster = dict()
        hoster['link'] = sUrl
        hname = 'Unknown Hoster'
        try:
            hname = re.compile('^(?:https?:\/\/)?(?:[^@\n]+@)?([^:\/\n]+)', flags=re.I | re.M).findall(hoster['link'])[0]
        except:
            pass
        hoster['name'] = hname
        hoster['displayedName'] = hname
        hosters.append(hoster)
    if hosters:
        hosters.append('getHosterUrl')
    return hosters

def getHosterUrl(sUrl=False):
    oParams = ParameterHandler()
    if not sUrl:
        sUrl = oParams.getValue('url')
    results = []
    result = {}
    result['streamUrl'] = sUrl
    result['resolved'] = False
    results.append(result)
    return results
