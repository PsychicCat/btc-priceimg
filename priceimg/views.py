"""
Copyright (C) 2014 Ford Hurley

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from flask import send_file, request, render_template
import misaka

from priceimg import app, cache
import util

_body_html = None

@app.route('/')
def home():
    """Serve the home page."""
    global _body_html
    if _body_html is None:
        with open('README.md') as f:
            _body_html = misaka.html(f.read())
    return render_template('index.html', body=_body_html)


@app.route('/img')
@app.route('/img/<price_usd>')
@app.route('/img/<price_usd>/<color>')
def priceimg(price_usd=None, color='0'):
    """Serve the image.

    The StringIO trick is from here:
    http://stackoverflow.com/a/10170635/576932
    """
    try:
        price_usd = float(price_usd)
    except ValueError:
        return "Error: bad USD price argument"

    try:
        color = util.parse_color(color)
    except ValueError:
        return "Error: bad color argument"

    try:
        btc_per_usd = util.get_exchange_rate('USD', 'BTC')
    except Exception:
        return "Error: exchange rate error"

    price_btc = price_usd * btc_per_usd

    img_io = util.get_image_io(price_btc, 'BTC', color)

    return send_file(img_io, attachment_filename='img.png')


@app.route('/advimg')
def priceimgadv():
    """Serve the image, with advanced options.

    The StringIO trick is from here:
    http://stackoverflow.com/a/10170635/576932
    """
    price_string = request.args.get('price')
    output_currency = request.args.get('currency', 'BTC').upper()
    color_string = request.args.get('color', '0')

    try:
        price, input_currency = util.parse_price(price_string)
    except ValueError:
        return "Error: bad price argument"

    try:
        color = util.parse_color(color_string)
    except ValueError:
        return "Error: bad color argument"

    try:
        exchange_rate = util.get_exchange_rate(input_currency, output_currency)
    except KeyError:
        return 'Error: unsupported currency pair - %s -> %s' % (input_currency, output_currency)
    except Exception:
        return 'Error: exchange rate error'

    output_price = price * exchange_rate

    img_io = util.get_image_io(output_price, output_currency, color)

    return send_file(img_io, attachment_filename='img.png')


@app.route('/balance')
@app.route('/balance/<address>')
@app.route('/balance/<address>/<color>')
def balimg(address=None, color='0'):
    """Serve image with address balance."""
    try:
        balance = float(util.get_balance(address))
    except ValueError:
        return "Error: bad address argument"
    except Exception:
        return 'Error: Blockchain.info error'

    try:
        color = util.parse_color(color)
    except ValueError:
        return "Error: bad color argument"

    img_io = util.get_image_io(balance, 'BTC', color)

    return send_file(img_io, attachment_filename='img.png')
