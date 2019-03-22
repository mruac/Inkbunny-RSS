from datetime import date
from flask import Flask, render_template, request, Response, g
import xml.etree.ElementTree as ET
import sys
import urllib.request
import urllib.parse
from configparser import ConfigParser
import redis
import os
config = ConfigParser()
app = Flask(__name__)

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
def initdb():
    db = redis.from_url(redis_url)
    return db

@app.before_request
def before_request():
    g.db = initdb()

# check if SID exists in config.ini
if config.read('config.ini') != [] and config.get('IB', 'sid') != '':
    sid = config.get('IB', 'sid')
# check if SID exists in environment variable
elif os.environ.get('SID') is not None:
    sid = os.environ.get('SID')
# else get guest SID from IB
else:
    data = urllib.parse.urlencode(
        {'username': 'guest', 'password': '', 'output_mode': 'xml'}).encode('utf-8')
    source = urllib.request.urlopen(
        url='https://inkbunny.net/api_login.php', data=data)
    sid = ET.parse(source).getroot()[0].text

# datadict is flags used for IB search, root is xml builder,
#cachename is key name for redis cache
def ibrss(datadict,root,cachename):

    rating = datadict.get('rating')
    items = list(root[7])
    vitemtitle = []
    vitemid = []
    vitemlink = []
    vitemthumb = []
    vitemtype = []
    vitemdesc = []
    vitemuser = []
    vitemrating = []
    vitempubdate = []
    vitemimg = []
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
    for content in root.iter('rating_id'):
        vitemrating.append(content.text)
	for content in root.iter('file_url_full'):
		vitemimg.append(content.text)

    # add link to vitemlink
    for i in vitemid:
        vitemlink.append('https://inkbunny.net/s/' + i)

    # make RSS title. If no query found, revert to 'ALL posts'
    # make filename for unique rss files.
    flags = ['text', 'keyword_id', 'username',
        'user_id', 'favs_user_id', 'pool_id']
    for key in flags:
        if key in datadict:
            if key == 'text':
                vrsstitle = vrsstitle + 'Search Query: "' + \
                    datadict.get(key) + '"; '
            elif key == 'keyword_id':
                tmpdata = {'sid': sid, 'output_mode': 'xml', 'show_pools': 'yes', 'count_limit': '1',
                    'submission_ids': root[7][0].find('submission_id').text}
                tmpdata = urllib.parse.urlencode(tmpdata).encode('utf-8')
                tmpsource = urllib.request.urlopen(
                    url='https://inkbunny.net/api_submissions.php', data=tmpdata)
                tmptree = ET.parse(tmpsource)
                tmproot = tmptree.getroot()
                for i in tmproot[3][0].find('keywords'):
                    if i[0].text == datadict.get(key):
                        vrsstitle = vrsstitle + 'Keyword: ' + i[1].text + '; '
            elif key == 'username':
                vrsstitle = vrsstitle + 'User: ' + datadict.get(key) + '; '
            elif key == 'user_id':
                vrsstitle = vrsstitle + 'User: ' + vitemuser[0] + '; '
            elif key == 'favs_user_id':
                tmpdata = {'sid': sid, 'output_mode': 'xml','count_limit': '1',
                    'user_id': datadict.get(key)}
                tmpdata = urllib.parse.urlencode(keydata).encode('utf-8')
                tmpsource = urllib.request.urlopen(
                    url='https://inkbunny.net/api_search.php', data=tmpdata)
                tmptree = ET.parse(tmpsource)
                tmproot = tmptree.getroot()
                vrsstitle = vrsstitle + 'Favourites by ' + \
                    tmproot[7][0].find('username').text + '; '
            elif key == 'pool_id':
                tmpdata = {'sid': sid, 'output_mode': 'xml', 'count_limit':'1',
                    'show_pools': 'yes', 'submission_ids': '1776649'}
                tmpdata = urllib.parse.urlencode(tmpdata).encode('utf-8')
                tmpsource = urllib.request.urlopen(
                    url='https://inkbunny.net/api_submissions.php', data=tmpdata)
                tmptree = ET.parse(tmpsource)
                tmproot = tmptree.getroot()
                for i in tmproot[3][0].find('pools'):
                    if i[0].text == datadict.get(key):
                        vrsstitle = vrsstitle + 'Pool: ' + \
                            i[1].text + ' by ' + vitemuser[0] + '; '
    if vrsstitle == 'Inkbunny - ':
        vrsstitle = vrsstitle + 'ALL posts'
    vrsstitle = vrsstitle.strip('; ')


    for i in items:
            filenamelength = len(i.findtext('file_name'))
            # find thumbnail and append to vitemthumb
            if i.find('thumbnail_url_huge_noncustom') != None:
                vitemthumb.append(i.find('thumbnail_url_huge_noncustom').text)
            elif i.find('thumbnail_url_huge') != None:
                vitemthumb.append(i.find('thumbnail_url_huge').text)
        # if no thumbnail found, use default thumbnail
            elif i.findtext('file_name')[filenamelength - 3:filenamelength] in ['png', 'jpg', 'gif', 'swf', 'flv', 'mp4', 'mp3', 'doc', 'rtf', 'txt']:
                if i.findtext('file_name')[filenamelength - 3:filenamelength] in ['png', 'jpg', 'gif']:
                    vitemthumb.append(
                        'https://au.ib.metapix.net/images78/overlays/nofile.png')
                elif i.findtext('file_name')[filenamelength - 3:filenamelength] in ['doc', 'rtf', 'txt']:
                    vitemthumb.append(
                        'https://au.ib.metapix.net/images78/overlays/writing.png')
                elif i.findtext('file_name')[filenamelength - 3:filenamelength] in ['flv', 'mp4']:
                    vitemthumb.append(
                        'https://au.ib.metapix.net/images78/overlays/video.png')
                elif i.findtext('file_name')[filenamelength - 3:filenamelength] in ['swf']:
                    vitemthumb.append(
                        'https://au.ib.metapix.net/images78/overlays/shockwave.png')
                elif i.findtext('file_name')[filenamelength - 3:filenamelength] in ['mp3']:
                    vitemthumb.append(
                        'https://au.ib.metapix.net/images78/overlays/audio.png')
            else:
                vitemthumb.append(
                    'https://au.ib.metapix.net/images78/overlays/nofile.png')

    # add description to vitemdesc
    for i in range(len(items)):
        vitemdesc.append('<a href="' + vitemlink[i] + '"><img src="' + vitemthumb[i] + '"></a><p><a href="' + vitemlink[i] + '">Submission</a> | <a href="' + vitemimg[i] + '">Direct</a></p>Type: '
                         + vitemtype[i] + ' <br/><br/><a href="http://inkbunny.net/' + vitemuser[i] + '">By ' + vitemuser[i] + '</a>')

    # create integer to day string for vitempubdate
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

    # create integer to month string for vitempubdate
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
        # skip submissions if posts don't fit the rating
        if rating == '001':
            if vitemrating[i] == '0': continue
            elif vitemrating[i] == '1': continue
        elif rating == '011':
            if vitemrating[i] == '0': continue
        elif rating == '110':
            if vitemrating[i] == '2': continue
        elif rating == '010':
            if vitemrating[i] == '0': continue
            elif vitemrating[i] == '2': continue
        elif rating == '100':
            if vitemrating[i] == '1': continue
            elif vitemrating[i] == '2': continue
        elif rating == '101':
            if vitemrating[i] == '1': continue
        # elif rating == '111'
        item = ET.Element('item')
        channel.append(item)
        itemtitle = ET.SubElement(item, 'title')
        itemtitle.text = vitemtitle[i]
        itemlink = ET.SubElement(item, 'link')
        itemlink.text = vitemlink[i]
        itemdesc = ET.SubElement(item, 'description')
        itemdesc.text = vitemdesc[i]
        itemguid = ET.SubElement(item, 'guid', isPermaLink='false')
        itemguid.text = vitemid[i]
        itempubdate = ET.SubElement(item, 'pubDate')
        itempubdate.text = vitempubdate[i]

    feed = ET.tostring(rss, encoding='utf-8', method='xml')
    g.db.set(cachename, feed, ex=86400) # set feed cache to expire in 24 hours unless if updated.
    return Response(feed, mimetype='application/rss+xml')



@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def searchquery():
    invalid = ''
    cachename = ''
    keylist = list(request.args.keys())
    # returns nested list. [('username', [u'ww'])] [0][1][0] = ww
    flaglist = list(request.args.lists())
    flags = ['rating', 'sid', 'output_mode', 'field_join_type', 'text', 'string_join_type', 'keywords', 'title', 'description', 'md5', 'keyword_id',
             'username', 'user_id', 'favs_user_id', 'unread_submissions', 'type', 'sales', 'pool_id', 'orderby', 'dayslimit', 'random', 'scraps']
    for i in keylist:
        if i not in flags:
            invalid += i + ', '

    for flag in flaglist:
        if 'sid' in flag:
            return 'User defined SIDs are restricted for this app.<br>Please define the SID in <code>config.ini</code> or in the <code>SID</code> environment variable'

    if request.args.get('rating') == '000':
        return 'Oi m8 wth are ya tryna do? Break ma code?'
    elif request.args.get('rating') not in ['001','011','010','110','101','100','111',None]:
        invalid += 'rating'

    if invalid == '': #no errors in url query
        # rebuild url query from flags
        data = {}
        if isinstance(flaglist, tuple):  # patch for single arguement
            flaglist = [flaglist]
        for flag in flaglist:
            for value in flag[1]:
                cachename = cachename + flag[0] + ':' + value + ','
                data[flag[0]] = value
        cachename = str(cachename.strip(',')) # make unique name for redis
        data.update({'sid': sid, 'output_mode': 'xml'})

        datadict = data.copy() #clone dictionarys - datadict for ibrss() and data for API request
        if 'rating' in data: del data['rating'] #remove custom flag 'rating' before using in API request
        url = 'https://inkbunny.net/api_search.php'
        data = urllib.parse.urlencode(data).encode('utf-8')
        root = ET.parse(urllib.request.urlopen(url=url, data=data)).getroot()

        if root[1].tag == 'error_message':
            return 'Error: ' + root[1].text
        elif len(list(root[7])) == 0:
            return 'No submissions found. Try again when your search has at least one submission.'

        try:
            if ET.fromstring(g.db.get(cachename))[0][2][3].text == root[7][0].find('submission_id').text:
                source = ''
                return Response(g.db.get(cachename), mimetype='application/rss+xml')  #already exists, return feed from cache
            else:
                return ibrss(datadict,root,cachename) # latest post doesn't match, update feed
        except TypeError: #doesnt exist in cache
            return ibrss(datadict,root,cachename)
        except IndexError: #unknown error in the flags (bypassed the error checker) last resort.
            g.db.delete(cachename)
            return ibrss(datadict,root,cachename)

    else:
        return 'Invalid flag(s): ' + invalid.strip(', ') + '<br>Please check the URL and try again.'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
