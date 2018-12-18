import xml.etree.ElementTree as ET
import sys
import urllib
import re
#load required modules: XML reader, system arguments, url library for getting links, re for regex

try:
 sys.argv[1]
except IndexError:
    print 'No Inkbunny URL detected! Please use this command with [URL] in quotes: \n\n  python testxml.py "[URL]" \n\nRefer to Inkbunny\'s API under the search parameter for proper URL usage.'
#test if url exists as arguement. If not, print help.

xmllink = sys.argv[1] + '&submissions_per_page=10&output_mode=xml'
# limit URL to 10 submissions and force xml output.

if re.search(r'^(https://inkbunny\.net/)',xmllink) == None:
        sys.exit('Error: Invalid Inkbunny URL')
elif xmllink.find('sid=') == -1:
        sys.exit('Error: Missing SID')
#if missing inkbunny.net or SID, return error and exit

xmlsource = urllib.urlopen(xmllink)
tree = ET.parse(xmlsource)
root = tree.getroot()

if root[0].tag == 'error_code':
    sys.exit('Error: Inkbunny returned error! Visit the offending URL for more information. \n\n' + xmllink)
# check if requested URL returns error

numitems = len(root[7].getchildren())
vitemtitle = []
vitemid = []
vitemlink = []
vitemthumb = []
vitemtype = []
vitemdesc = []
vitemuser = []
vrsstitle = 'Inkbunny search: '
#create variables to be used in RSS builder. All lists must match numitems!

if re.search(r'(?!.*text=)(?<=text=).*?((?=&)|($))', xmllink) == None:
    vrsstitle = vrsstitle + 'ALL posts'
elif re.search(r'(?!.*text=)(?<=text=).*?((?=&)|($))', xmllink) != None:
    vrsstitle = vrsstitle + '"' + re.search(r'(?!.*text=)(?<=text=).*?((?=&)|($))', xmllink).group() + '"'
# make RSS title. Two states: search query and no query.

for content in root.iter('title'):
    vitemtitle.append(content.text)
for content in root.iter('submission_id'):
    vitemid.append(content.text)
for content in root.iter('username'):
    vitemuser.append(content.text)
# add contents of elements to their lists

i = 0
while i < numitems:
#find thumbnail and append to vitemthumb
    if root[7][i].find('thumbnail_url_huge_noncustom') != None:
        vitemthumb.append(root[7][i].find('thumbnail_url_huge_noncustom').text)
    elif root[7][i].find('thumbnail_url_huge') != None:
        vitemthumb.append(root[7][i].find('thumbnail_url_huge').text)
# if no thumbnail found, use default thumbnail
    elif any(re.search(r'...$|(jpeg)$',root[7][i].findtext('file_name')).group() in item for item in ['png', 'jpeg', 'jpg', 'gif', 'swf', 'flv', 'mp4', 'mp3', 'doc', 'rtf', 'txt']) == True:
        if re.search(r'...$|(jpeg)$',root[7][i].findtext('file_name')).group() in ('png','jpg','jpeg','gif') == True:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/nofile.png')
        elif re.search(r'...$|(jpeg)$',root[7][i].findtext('file_name')).group() in ('doc','rtf','txt') == True:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/writing.png')
        elif re.search(r'...$|(jpeg)$',root[7][i].findtext('file_name')).group() in ('flv','mp4') == True:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/video.png')
        elif re.search(r'...$|(jpeg)$',root[7][i].findtext('file_name')).group() in ('swf') == True:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/shockwave.png')
        elif re.search(r'...$|(jpeg)$',root[7][i].findtext('file_name')).group() in ('mp3') == True:
            vitemthumb.append('https://au.ib.metapix.net/images78/overlays/audio.png')
        else: vitemthumb.append('https://au.ib.metapix.net/images78/overlays/nofile.png')
    i += 1

i = 0
while i < numitems:
    vitemlink.append('https://inkbunny.net/s/' + vitemid[i])
    i += 1
#add link to vitemlink

i = 0
while i < numitems:
    vitemdesc.append('<a href="' + vitemlink[i] + '"><img src="' + vitemthumb[i] + '"></a> <br/><br/><a href="http://inkbunny.net/' + vitemuser[i] + '">By ' + vitemuser[i] + '</a>')
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
tree.write('filename.xml', encoding='UTF-8')

print vrsstitle + ' made!'
