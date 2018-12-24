import xml.etree.ElementTree as ET
import sys
import urllib
import re
# load required modules: XML reader, system arguments, url library for getting links, re for regex

try:
    sys.argv[1]
except IndexError:
    print 'No Inkbunny URL detected! Please use this command with [URL] in quotes: \n\n  python IBxml2rss.py "[URL]" \n\nRefer to Inkbunny\'s API under the search parameter for proper URL usage.'
# test if url exists as arguement. If not, print help.

xmllink = sys.argv[1] + '&count_limit=10&output_mode=xml'
# limit URL to 10 submissions and force xml output.

if re.search(r'^(https://inkbunny\.net/)', xmllink) == None:
    sys.exit('Error: Invalid Inkbunny URL')
elif xmllink.find('sid=') == -1:
    sys.exit('Error: Missing SID')
# if missing inkbunny.net or SID, return error and exit

xmlsource = urllib.urlopen(xmllink)
tree = ET.parse(xmlsource)
root = tree.getroot()

if root[0].tag == 'error_code':
    sys.exit('Error: Inkbunny returned error! Visit the offending URL for more information. \n\n' + xmllink)
# check if requested URL returns error

sid = re.search(r'(?!sid=)(?<=sid=).*?((?=&)|($))', xmllink).group()
numitems = len(root[7].getchildren())
vitemtitle = []
vitemid = []
vitemlink = []
vitemthumb = []
vitemtype = []
vitemdesc = []
vitemuser = []
vrsstitle = 'Inkbunny - '
filename = 'IB'
# create variables to be used in RSS builder. All lists must match numitems!

for content in root.iter('title'):
    vitemtitle.append(content.text)
for content in root.iter('submission_id'):
    vitemid.append(content.text)
for content in root.iter('username'):
    vitemuser.append(content.text)
for content in root.iter('type_name'):
    vitemtype.append(content.text)
# add contents of elements to their lists

i = 0
while i < numitems:
    vitemlink.append('https://inkbunny.net/s/' + vitemid[i])
    i += 1
# add link to vitemlink

if re.search(r'((?!text=)|(?!user_id=)|(?!keyword_id=)|(?!username=)|(?!favs_user_id=)|(?!pool_id=))((?<=text=)|(?<=user_id=)|(?<=keyword_id=)|(?<=username=)|(?<=favs_user_id=)|(?<=pool_id=)).*?((?=&)|($))', xmllink) == None:
    vrsstitle = vrsstitle + 'ALL posts'
# if no search parameters found, give rsstitle 'ALL posts'
else:
    if re.search(r'(?!text=)(?<=text=).*?((?=&)|($))', xmllink) != None:
        vrsstitle = vrsstitle + 'Search Query: "' + re.search(r'(?!text=)(?<=text=).*?((?=&)|($))', xmllink).group() + '"; '
        if re.search(r'&$',filename) != None:
            filename = filename + '&'
        filename = filename + re.search(r'(text=).*?((?=&)|($))', xmllink).group()
    if re.search(r'(?!keyword_id=)(?<=keyword_id=).*?((?=&)|($))', xmllink) != None:
        keyurl = urllib.urlopen('https://inkbunny.net/api_submissions.php?sid=' + sid + '&output_mode=xml&show_pools=yes&submission_ids=' + root[7][0].find('submission_id').text)
        keyxml = ET.parse(keyurl)
        keyroot = keyxml.getroot()
        i = 0
        while i < len(keyroot[3][0].find('keywords')):
            if keyroot[3][0].find('keywords')[i][0].text == re.search(r'(?!keyword_id=)(?<=keyword_id=).*?((?=&)|($))', xmllink).group():
                keyname = keyroot[3][0].find('keywords')[i][1].text
                break
            else:
                i += 1
        vrsstitle = vrsstitle + 'Keyword: ' + keyname + '; '
        if re.search(r'&$',filename) != None:
            filename = filename + '&'
        filename = filename + re.search(r'(keyword_id=).*?((?=&)|($))', xmllink).group()
    if re.search(r'(?!username=)(?<=username=).*?((?=&)|($))', xmllink) != None:
        vrsstitle = vrsstitle + 'User: ' + re.search(r'(?!username=)(?<=username=).*?((?=&)|($))', xmllink).group() + '; '
        if re.search(r'&$',filename) != None:
            filename = filename + '&'
        filename = filename + re.search(r'(username=).*?((?=&)|($))', xmllink).group()
    if re.search(r'(?!user_id=)(?<=user_id=).*?((?=&)|($))', xmllink) != None:
        vrsstitle = vrsstitle + 'User: ' + vitemuser[0] + '; '
        if re.search(r'&$',filename) != None:
            filename = filename + '&'
        filename = filename + re.search(r'(user_id=).*?((?=&)|($))', xmllink).group()
    if re.search(r'(?!favs_user_id=)(?<=favs_user_id=).*?((?=&)|($))', xmllink) != None:
        userurl = urllib.urlopen('https://inkbunny.net/api_search.php?sid=' + sid + '&output_mode=xml&user_id=' + re.search(r'(?!favs_user_id=)(?<=favs_user_id=).*?((?=&)|($))', xmllink).group())
        userxml = ET.parse(userurl)
        userroot = userxml.getroot()
        vrsstitle = vrsstitle + 'Favourites by ' + userroot[7][0].find('username').text + '; '
        if re.search(r'&$',filename) != None:
            filename = filename + '&'
        filename = filename + re.search(r'(favs_user_id=).*?((?=&)|($))', xmllink).group()
    if re.search(r'(?!pool_id=)(?<=pool_id=).*?((?=&)|($))', xmllink) != None:
        poolurl = urllib.urlopen('https://inkbunny.net/api_submissions.php?sid=' + sid + '&output_mode=xml&show_pools=yes&submission_ids=' + root[7][0].find('submission_id').text)
        poolxml = ET.parse(poolurl)
        poolroot = poolxml.getroot()
        i = 0
        while i < len(poolroot[3][0].find('pools')):
            if poolroot[3][0].find('pools')[i][0].text == re.search(r'(?!pool_id=)(?<=pool_id=).*?((?=&)|($))', xmllink).group():
                poolname = poolroot[3][0].find('pools')[i][1].text
                break
            else:
                i += 1
        vrsstitle = vrsstitle + 'Pool: ' + poolname + ' by ' + vitemuser[0] + '; '
        if re.search(r'&$',filename) != None:
            filename = filename + '&'
        filename = filename + re.search(r'(pool_id=).*?((?=&)|($))', xmllink).group()
if filename == 'IB':
    filename = 'IBallposts'
# make RSS title. If no query found, revert to 'ALL posts'
# make filename for unique rss files.

i = 0
while i < numitems:
    # find thumbnail and append to vitemthumb
    if root[7][i].find('thumbnail_url_huge_noncustom') != None:
        vitemthumb.append(root[7][i].find('thumbnail_url_huge_noncustom').text)
    elif root[7][i].find('thumbnail_url_huge') != None:
        vitemthumb.append(root[7][i].find('thumbnail_url_huge').text)
# if no thumbnail found, use default thumbnail
    elif re.search(r'...$|(jpeg)$', root[7][i].findtext('file_name')).group() in ['png', 'jpeg', 'jpg', 'gif', 'swf', 'flv', 'mp4', 'mp3', 'doc', 'rtf', 'txt']:
        if re.search(r'...$|(jpeg)$', root[7][i].findtext('file_name')).group() in ['png', 'jpg', 'jpeg', 'gif']:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/nofile.png')
        elif re.search(r'...$|(jpeg)$', root[7][i].findtext('file_name')).group() in ['doc', 'rtf', 'txt']:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/writing.png')
        elif re.search(r'...$|(jpeg)$', root[7][i].findtext('file_name')).group() in ['flv', 'mp4']:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/video.png')
        elif re.search(r'...$|(jpeg)$', root[7][i].findtext('file_name')).group() in ['swf']:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/shockwave.png')
        elif re.search(r'...$|(jpeg)$', root[7][i].findtext('file_name')).group() in ['mp3']:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/audio.png')
    else:
        vitemthumb.append('https://au.ib.metapix.net/images78/overlays/nofile.png')
    i += 1

i = 0
while i < numitems:
    vitemdesc.append('<a href="' + vitemlink[i] + '"><img src="' + vitemthumb[i] + '"></a><br/>Type: ' + vitemtype[i] + '<br/><br/><a href="http://inkbunny.net/' + vitemuser[i] + '">By ' + vitemuser[i] + '</a>')
    i += 1
# add description to vitemdesc


# RSS builder
rss = ET.Element('rss', attrib={'version': '2.0'})
channel = ET.Element('channel')
rss.append(channel)

rsstitle = ET.SubElement(channel, 'title')
rsstitle.text = vrsstitle
rsslink = ET.SubElement(channel, 'link')

i = 0
while i < numitems:
    item = ET.Element('item')
    channel.append(item)
    itemtitle = ET.SubElement(item, 'title')
    itemtitle.text = vitemtitle[i]
    itemlink = ET.SubElement(item, 'link')
    itemlink.text = vitemlink[i]
    itemdesc = ET.SubElement(item, 'description')
    itemdesc.text = vitemdesc[i]
    itemguid = ET.SubElement(item, 'guid')
    itemguid.text = vitemlink[i]
    i += 1
tree = ET.ElementTree(rss)
tree.write(filename + '.rss', encoding='UTF-8')

print vrsstitle + ' made!'
