from time import sleep

import requests
from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template
from geopy import GoogleV3
from geopy.exc import GeocoderQuotaExceeded

app = Flask(__name__)
buildings = []

@app.route("/")
def map():
    return render_template('map.html', buildings=buildings)

def geocode_all(addresses):
    geo = GoogleV3()
    for name, address in addresses:
        for t in [.1, .2, .4, .8, 1.6, 3.2, 6.4]:
            try:
                loc = geo.geocode(address.encode('ascii', 'ignore'))
                yield (name, address, loc.latitude, loc.longitude)
                break
            except GeocoderQuotaExceeded:
                sleep(t)
            except:
                print('Couldn\'t find %s - %s' % (name, repr(address)))
                break

def scrape():
    response = requests.get('http://www.condointernet.net/our-buildings/')
    soup = BeautifulSoup(response.text)
    cells = soup.findAll('div', 'bldg_cel')
    return [(c.find('a', 'bldg_title').getText(), list(c.find('p').childGenerator())[0]) for c in cells]

if __name__ == '__main__':
    buildings = list(geocode_all(scrape()))
    print('%d buildings loaded' % len(buildings))
    app.debug = True
    app.run(host='0.0.0.0')
