import os
import webapp2
import jinja2
import logging
from xml.dom import minidom

import urllib2
from google.appengine.api import memcache
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

IP_URL  = "http://api.hostip.info/?ip="

def top_products(update = False):
    key = 'top'
    theProducts = memcache.get(key)
    logging.info('get products from cash!')

    if  update or theProducts is None:
        logging.error("DB Query")
        products = db.GqlQuery("select * from product order by created desc")

        theProducts = list(products)
        logging.info('products list %s', theProducts[0].name )
        memcache.set(key, theProducts)

    return theProducts

def get_node(x, tagname, i = 0):
#   x = minidom.parseString(contents)
    coord = x.getElementsByTagName(tagname)

    if coord[i].childNodes[0].nodeValue:
        return coord[i].childNodes[0].nodeValue;

def get_nodePair(x, tagname, i = 0):
#   x = minidom.parseString(contents)
    coord = x.getElementsByTagName(tagname)
    #print coord[0] 

    if coord and coord[i].childNodes[0].nodeValue:
        lon, lat = coord[i].childNodes[0].nodeValue.split(',')
        return lat, lon

def get_coords(ip):
    url =  IP_URL + ip
    content = None
    try:
       content = urllib2.urlopen(url).read()
    except URLError:
        return
    x1 = minidom.parseString(content)
    aPoint = get_nodePair(x1, 'gml:coordinates' )
    return aPoint

GMAPS = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&zoom=5&"

def gmaps_img(points):
    markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
    return GMAPS + markers


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class productCategory(db.Model):
    category = db.StringProperty(required = True)

class product(db.Model):
    name =    db.StringProperty(required = True)
    description = db.StringProperty(required = True)
    imgURL  =  db.StringListProperty()
    quantity = db.IntegerProperty()
    category = db.ReferenceProperty(productCategory)
    user     = db.Key()
    enabled =  db.BooleanProperty(required = True)
    remarks =  db.StringProperty()
    cost =     db.IntegerProperty()

    coords   = db.GeoPtProperty()
    created  = db.DateTimeProperty(auto_now_add = True)
#   db.CategoryProperty()

class MainPage(Handler):
    def render_front(self, name="", description="", error=""):
        products = top_products()
        #find which products have coords
        points = filter(None, (a.coords for a in products))
        img_url = None
        if points:
            img_url = gmaps_img( points )

#        img_url = download.jpg

        self.render("front.html", name=name, description=description, 
                     error=error, products = products ) #, img_url = img_url )
#    <script src="jquery.preimage.js"></script>

    def get(self):
        logging.info('get ... ')
        self.write( self.request.remote_addr )
#        self.write(repr(get_coords(self.request.remote_addr)))
        self.render_front()

    def post(self):
        logging.info('entered post: ...') 
        name = self.request.get('name')
        description = self.request.get('description')
        enabled = self.request.get('enabled')
        browse = self.request.get('browse')
        imgList = []
        imgList.append(browse)
        
        if enabled is "on":
            anEnabled = True
        else:
            anEnabled = False

        logging.info('post name=%s; description=%s; enabled=%s; browse=%s ',
                      name, description, enabled, browse )
        
        if name and description:
#            self.write("thanks!")
            logging.info('new product put')
            a = product( name = name, description = description,
                         enabled = anEnabled, imgURL = imgList)

            coords = get_coords(self.request.remote_addr)
            if coords:
                a.coords = db.GeoPt(coords[0] +', '+coords[1])

            a.put()
            top_products(update=True)
            self.redirect("/")
        else:
            error = "we need both a product name and some description!"
            self.render_front(name, description, error)

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)