import re
import htmlentitydefs

from BeautifulSoup import BeautifulSoup, Comment
from HTMLParser import HTMLParseError

def clean_html(html):

    if not html:
        return None

    try:
        # BeautifulSoup is catching out-of-order and unclosed tags, so markup
        # can't leak out of comments and break the rest of the page.
        soup = BeautifulSoup(html)
    except HTMLParseError, e:
        # special handling?
        raise e

    to_remove = [ ('div', {'id':'div_barra_lila'}),
        ('div', {'id':'div_barra_lila_eqMed'}),
        ('span', {'id':'lbl_hl_tratamientos'}),
        ('div', {'id':'lnk_treatments'}),
        ('div', {'class':'spacer'}),
        ('span', {'id':'lbl_lastupdated'}),
        ('o:p'),
        ('div', {'class':'lyr_helpmitratamiento'}),
        ('div', {'class':'SolucionEugin_boton'}) ]

    for args in to_remove:
        tags = soup.findAll(*args)
        for tag in tags:
            if tag:
                tag.extract()


    tags = soup.findAll(True)

    for t in tags:
        if t.has_key('style'):
            del(t['style'])
        if t.has_key('class'):
            new_class = []
            for c in t['class'].split(' '):
                if not 'Mso' in c:
                    new_class.append(c)
            joined_class = ' '.join(new_class)
            if joined_class != '':
                t['class'] = joined_class
            else:
                del(t['class'])
        if t.has_key('onmouseout'):
            del(t['onmouseout'])
        if t.has_key('onmouseover'):
            del(t['onmouseover'])

    # scripts can be executed from comments in some cases
    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    html = unicode(soup)

    opening = re.compile('<(table|td|tr|span|font|o:p|st1|v|tbody)[^>]*>')
    closing = re.compile('</(table|td|tr|span|font|o:p|st1|v|tbody)[^>]*>')
    doctype = re.compile('<\?[^>]*\?>')

    html = html.replace('&#160;', ' ')
    html = html.replace('&#13;', ':')
    html = html.replace('&#8211;', '')
    html = html.replace('&#038;', '&')
    html = html.replace('&#8217;', "'")
    html = html.replace('&#8230;', '...')
    html = opening.sub('', html)
    html = closing.sub('', html)
    html = doctype.sub('', html)


    if html == ", -":
        return None


    return html

def _attr_name_whitelisted(attr_name):
    return attr_name.lower() in ["href", "target"]

def safe_css(attr, css):
    if attr == "style":
        return re.sub("(width|height):[^;]+;", "", css)
    return css

def plaintext(input):
    """Converts HTML to plaintext, preserving whitespace."""

    # from http://effbot.org/zone/re-sub.htm#unescape-html
    def _unescape(text):
        def fixup(m):
            text = m.group(0)
            if text[:2] == "&#":
                # character reference
                try:
                    if text[:3] == "&#x":
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text # leave as is
        return re.sub("&#?\w+;", fixup, text)

    input = safe_html(input) # basic sanitation first
    text = "".join(BeautifulSoup("<body>%s</body>" % input).body(text=True))
    text = text.replace("xml version='1.0' encoding='%SOUP-ENCODING%'", "") # strip BS meta-data
    return _unescape(text)