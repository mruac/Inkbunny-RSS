from flask import Flask, render_template, request, Response
import xml.etree.ElementTree as ET
import sys
import urllib
import re
from datetime import date
app = Flask(__name__)

def ibrss(flags):
    urlq = ''
    i = 0
    while i < len(flags):
        ii = 0
        while ii < len(flags[i][1]):
            urlq = urlq + flags[i][0] + '=' + str(flags[i][1][ii]) + '&'
            ii += 1
        i += 1
    urlq = urlq.strip('&')
    #rebuild url query from flags

    xmllink = 'https://inkbunny.net/api_search.php?' + urlq + '&count_limit=10&output_mode=xml'
    # limit URL to 10 submissions and force xml output.

    xmlsource = urllib.urlopen(xmllink)
    tree = ET.parse(xmlsource)
    root = tree.getroot()

    if root[1].tag == 'error_message':
        return 'Error: ' + root[1].text
    elif len(root[7].getchildren()) == 0:
        return 'No submissions found. Try again when your search has at least one submission.'

    sid = re.search(r'(?!sid=)(?<=sid=).*?((?=&)|($))', xmllink).group()
    items = root[7].getchildren()
    vitemtitle = []
    vitemid = []
    vitemlink = []
    vitemthumb = []
    vitemtype = []
    vitemdesc = []
    vitemuser = []
    vitempubdate = []
    vrsstitle = 'Inkbunny - '
    filename = 'IB'

    # add contents of elements to their lists
    for content in root.iter('title'):
        vitemtitle.append(content.text)
    for content in root.iter('submission_id'):
        vitemid.append(content.text)
    for content in root.iter('username'):
        vitemuser.append(content.text)
    for content in root.iter('type_name'):
        vitemtype.append(content.text)

    # add link to vitemlink
    for i in vitemid:
        vitemlink.append('https://inkbunny.net/s/' + i)

    # make RSS title. If no query found, revert to 'ALL posts'
    # make filename for unique rss files.
    if re.search(r'((?!text=)|(?!user_id=)|(?!keyword_id=)|(?!username=)|(?!favs_user_id=)|(?!pool_id=))((?<=text=)|(?<=user_id=)|(?<=keyword_id=)|(?<=username=)|(?<=favs_user_id=)|(?<=pool_id=)).*?((?=&)|($))', xmllink) == None:
        vrsstitle = vrsstitle + 'ALL posts'
    else:
        if re.search(r'(?!text=)(?<=text=).*?((?=&)|($))', xmllink) != None:
            vrsstitle = vrsstitle + 'Search Query: "' + re.search(r'(?!text=)(?<=text=).*?((?=&)|($))',
                          xmllink).group() + '"; '
            if re.search(r'&$', filename) != None:
                filename = filename + '&'
            filename = filename + re.search(r'(text=).*?((?=&)|($))', xmllink).group()
        if re.search(r'(?!keyword_id=)(?<=keyword_id=).*?((?=&)|($))', xmllink) != None:
            keyurl = urllib.urlopen('https://inkbunny.net/api_submissions.php?sid=' + sid + '&output_mode=xml&show_pools=yes&submission_ids=' + root[7][0].find('submission_id').text)
            keyxml = ET.parse(keyurl)
            keyroot = keyxml.getroot()
            for i in keyroot[3][0].find('keywords'):
                if i[0].text == re.search(r'(?!keyword_id=)(?<=keyword_id=).*?((?=&)|($))', xmllink).group():
                    keyname = i[1].text
            vrsstitle = vrsstitle + 'Keyword: ' + keyname + '; '
            if re.search(r'&$', filename) != None:
                filename = filename + '&'
            filename = filename + re.search(r'(keyword_id=).*?((?=&)|($))', xmllink).group()
        if re.search(r'(?!username=)(?<=username=).*?((?=&)|($))', xmllink) != None:
            vrsstitle = vrsstitle + 'User: ' + re.search(r'(?!username=)(?<=username=).*?((?=&)|($))',
                          xmllink).group() + '; '
            if re.search(r'&$', filename) != None:
                filename = filename + '&'
            filename = filename + re.search(r'(username=).*?((?=&)|($))', xmllink).group()
        if re.search(r'(?!user_id=)(?<=user_id=).*?((?=&)|($))', xmllink) != None:
            vrsstitle = vrsstitle + 'User: ' + vitemuser[0] + '; '
            if re.search(r'&$', filename) != None:
                filename = filename + '&'
            filename = filename + re.search(r'(user_id=).*?((?=&)|($))', xmllink).group()
        if re.search(r'(?!favs_user_id=)(?<=favs_user_id=).*?((?=&)|($))', xmllink) != None:
            userurl = urllib.urlopen('https://inkbunny.net/api_search.php?sid=' + sid + '&output_mode=xml&user_id=' + re.search(r'(?!favs_user_id=)(?<=favs_user_id=).*?((?=&)|($))', xmllink).group())
            userxml = ET.parse(userurl)
            userroot = userxml.getroot()
            vrsstitle = vrsstitle + 'Favourites by ' + userroot[7][0].find('username').text + '; '
            if re.search(r'&$', filename) != None:
                filename = filename + '&'
            filename = filename + re.search(r'(favs_user_id=).*?((?=&)|($))', xmllink).group()
        if re.search(r'(?!pool_id=)(?<=pool_id=).*?((?=&)|($))', xmllink) != None:
            poolurl = urllib.urlopen('https://inkbunny.net/api_submissions.php?sid=' + sid
                                     + '&output_mode=xml&show_pools=yes&submission_ids=' + root[7][0].find('submission_id').text)
            poolxml = ET.parse(poolurl)
            poolroot = poolxml.getroot()
            for i in poolroot[3][0].find('pools'):
                if i[0].text == re.search(r'(?!pool_id=)(?<=pool_id=).*?((?=&)|($))', xmllink).group():
                    poolname = i[1].text
            vrsstitle = vrsstitle + 'Pool: ' + poolname + ' by ' + vitemuser[0] + '; '
            if re.search(r'&$', filename) != None:
                filename = filename + '&'
            filename = filename + re.search(r'(pool_id=).*?((?=&)|($))', xmllink).group()
    if filename == 'IB':
        filename = 'IBallposts'
    vrsstitle = vrsstitle.strip('; ')

    for i in items:
        # find thumbnail and append to vitemthumb
        if i.find('thumbnail_url_huge_noncustom') != None:
            vitemthumb.append(i.find('thumbnail_url_huge_noncustom').text)
        elif i.find('thumbnail_url_huge') != None:
            vitemthumb.append(i.find('thumbnail_url_huge').text)
    # if no thumbnail found, use default thumbnail
        elif re.search(r'...$|(jpeg)$', i.findtext('file_name')).group() in ['png', 'jpeg', 'jpg', 'gif', 'swf', 'flv', 'mp4', 'mp3', 'doc', 'rtf', 'txt']:
            if re.search(r'...$|(jpeg)$', i.findtext('file_name')).group() in ['png', 'jpg', 'jpeg', 'gif']:
                vitemthumb.append(
                    'https://au.ib.metapix.net/images78/overlays/nofile.png')
            elif re.search(r'...$|(jpeg)$', i.findtext('file_name')).group() in ['doc', 'rtf', 'txt']:
                vitemthumb.append(
                    'https://au.ib.metapix.net/images78/overlays/writing.png')
            elif re.search(r'...$|(jpeg)$', i.findtext('file_name')).group() in ['flv', 'mp4']:
                vitemthumb.append(
                    'https://au.ib.metapix.net/images78/overlays/video.png')
            elif re.search(r'...$|(jpeg)$', i.findtext('file_name')).group() in ['swf']:
                vitemthumb.append(
                    'https://au.ib.metapix.net/images78/overlays/shockwave.png')
            elif re.search(r'...$|(jpeg)$', i.findtext('file_name')).group() in ['mp3']:
                vitemthumb.append(
                    'https://au.ib.metapix.net/images78/overlays/audio.png')
        else:
            vitemthumb.append(
                'https://au.ib.metapix.net/images78/overlays/nofile.png')

    # add description to vitemdesc
    for i in range(len(items)):
        vitemdesc.append('<a href="' + vitemlink[i] + '"><img src="' + vitemthumb[i] + '"></a><br/>Type: '
                         + vitemtype[i] + '<br/><br/><a href="http://inkbunny.net/' + vitemuser[i] + '">By ' + vitemuser[i] + '</a>')

    #create integer to day string for vitempubdate
    def dayint(di):
        if di == 0:
            return 'Mon'
        elif di == 1:
            return 'Tue'
        elif di == 2:
            return 'Wed'
        elif di == 3:
            return 'Thu'
        elif di == 4:
            return 'Fri'
        elif di == 5:
            return 'Sat'
        elif di == 6:
            return 'Sun'

    #create integer to month string for vitempubdate
    def monint(mi):
        if mi == 1:
            return 'Jan'
        elif mi == 2:
            return 'Feb'
        elif mi == 3:
            return 'Mar'
        elif mi == 4:
            return 'Apr'
        elif mi == 5:
            return 'May'
        elif mi == 6:
            return 'Jun'
        elif mi == 7:
            return 'Jul'
        elif mi == 8:
            return 'Aug'
        elif mi == 9:
            return 'Sep'
        elif mi == 10:
            return 'Oct'
        elif mi == 11:
            return 'Nov'
        elif mi == 12:
            return 'Dec'

    # convert create_datetime to valid datetime for RSS
    for i in items:
        ibdate = i[4].text
        yyyy = ibdate[0:4]
        mm = ibdate[5:7]
        dd = ibdate[8:10]
        hhmmss = ibdate[11:19]
        tz = ibdate[len(ibdate) - 3:len(ibdate)] + '00'
        day = dayint(date(int(yyyy), int(mm), int(dd)).weekday())
        month = monint(int(mm))
        pubdate = day + ', ' + dd + ' ' + month + ' ' + yyyy + ' ' + hhmmss + ' ' + tz
        vitempubdate.append(pubdate)

    # RSS builder
    rss = ET.Element('rss', attrib={'version': '2.0'})
    channel = ET.Element('channel')
    rss.append(channel)

    rsstitle = ET.SubElement(channel, 'title')
    rsstitle.text = vrsstitle
    rsslink = ET.SubElement(channel, 'link')

    for i in range(len(items)):
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
        itempubdate = ET.SubElement(item, 'pubDate')
        itempubdate.text = vitempubdate[i]

    return Response(ET.tostring(rss,encoding='utf-8',method='xml'), mimetype='text/xml')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def searchquery():
    invalid = ''
    keylist = request.args.keys()
    flaglist = request.args.lists() # returns nested list. [('username', [u'ww'])] [0][1][0] = ww
    flags = ['sid','output_mode','field_join_type','text','string_join_type','keywords','title','description','md5','keyword_id','username','user_id','favs_user_id','unread_submissions','type','sales','pool_id','orderby','dayslimit','random','scraps']
    for i in keylist:
        if i not in flags:
            invalid += i + ', '
    if invalid == '':
        return ibrss(flaglist)
    else: return 'Invalid flag: ' + invalid.strip(', ') + '<br>Please check the URL queries and try again.'

if __name__ == '__main__':
  app.run()
