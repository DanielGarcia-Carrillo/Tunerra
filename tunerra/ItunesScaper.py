import xmltodict
import os.path
import json
import getpass
import requests

songList = []

def Scanner():
    
    credentials = dict()    
    #credentials['username'] = raw_input('Please enter your Tunerra username: ')
    #credentials['password'] = getpass.getpass()
    credentials['username'] = 'bob'
    credentials['password'] = '12345678'
    songList.append(credentials)
    
    libPath = 'C:\users\david\music\itunes'
    xmlStr = libPath + '\iTunes Music Library.xml'
    
    filefound = 1
    while not filefound:
        libPath = raw_input("Please enter the directory of your Itunes Library file\n")
        xmlStr = libPath + '\iTunes Library.xml'
        filefound = os.path.isfile(xmlStr)
        if not filefound:
            xmlStr = libPath + '\iTunes Music Library.xml'
            filefound = os.path.isfile(xmlStr)
            if not filefound:
                print "Library file not found."
    
    print xmlStr
    f = open(xmlStr)
    print f
    itunesDict = xmltodict.parse(f.read())
    level2 = itunesDict['plist']
    level3 = level2['dict']
    level4 = level3['dict']
    level5 = level4['dict']
    
    for song in level5:
        try:
            songdict = dict()
            songdict['title'] = song['string'].pop(0)
            songdict['artist'] = song['string'].pop(0)
            songList.append(songdict)
        except:
            continue
    sendToServer()
    

def sendToServer():
    JSONsongList = json.dumps(songList)
    print "Sending to server"
    path = 'http://127.0.0.1:14689/'
    headers = {'Conetnt-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(path, data=JSONsongList, headers=headers)
    print "Done!"
Scanner()