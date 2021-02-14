from flask import render_template, flash, redirect, send_file, url_for, abort, request, jsonify
from app import app
from datetime import datetime, timedelta
from app.models import Event
from app.forms import CompareCountryForm, CompareCityForm, ResponseCountryForm, SubmitEventRequestForm
from app.compare import get_similar_places, get_fig_compare_rates, get_fig_compare_doubling_rates, \
    get_all_places, get_timeline_list, get_place_live_stats, get_place_socio_stats, get_similar_places_socio, \
    get_fig_response, get_places_by_variable, get_html_compare_response, get_html_compare_response_econ

@app.route('/new-event', methods=['POST'])
def newEvent():
    payload = request.json
    required_fields = ['place', 'type', 'source']
    # Check the required fields
    if not (payload and all(field in payload and payload[field] != '' for field in required_fields)):
        abort(400)

    # Check if description for type other
    if payload['type'] == 'other' and payload['description'] == '':
        abort(400)

    # Create event
    new_event = Event(place=payload['place'],
                        date=datetime.strptime(payload['date'],'%Y-%m-%d'),
                        desc=payload['type'],
                        fulltext=payload['description'],
                        source=payload['source'])

    new_event.save()
    return new_event.json()

@app.route('/countries', methods=['GET', 'POST'])
def countries():
    form_countries = CompareCountryForm()
    if form_countries.validate_on_submit():
        return redirect(url_for("country", country=form_countries.countries.data))
    return redirect(url_for("index"))

@app.route('/figresponse/<place>.png')
def figresponse(place):
    img = get_fig_response(place)
    return send_file(img, mimetype='image/png')

@app.route('/htmlcomparerespecon/<place>/<place2>/<level>.html')
@app.route('/htmlcomparerespecon/<place>/<place2>/<level>/<scale>/<y>/<mode>/<priority>.html')
def htmlcomparerespecon(place, place2, level, scale='log', y='total', mode='static', priority = 'now'):
    img = get_html_compare_response_econ(place, place2, level, scale=scale, y=y, mode=mode, priority = priority)
    return img


@app.route('/figcomparerates/<place>/<place2>/<level>.png')
@app.route('/figcomparerates/<place>/<place2>/<level>/<scale>/<y>/<mode>/<priority>.png')
def figcomparerates(place, place2, level, scale='log', y='total', mode='static', priority = 'now'):
    img = get_fig_compare_rates(place, place2, level, scale=scale, y=y, mode=mode, priority = priority)
    return send_file(img, mimetype='image/png')

@app.route('/figcomparedblrates/<place>/<place2>/<level>.png')
def figcomparedblrates(place, place2, level):
    img = get_fig_compare_doubling_rates(place, place2, level)
    return send_file(img, mimetype='image/png')

@app.route('/htmlcompareresp/<place>/<place2>/<level>.html')
@app.route('/htmlcompareresp/<place>/<place2>/<level>/<scale>/<y>/<mode>/<priority>.html')
def htmlcompareresp(place, place2, level, scale='log', y='total', mode='static', priority = 'now'):
    img = get_html_compare_response(place, place2, level, scale=scale, y=y, mode=mode, priority = priority)
    return img

# @app.route('/place/<place>/<level>')
# def place(place, level):
#     if level == 'countries':
#         return redirect(url_for("country", country = place))
#     else:
#         return redirect(url_for("city", city = place))
