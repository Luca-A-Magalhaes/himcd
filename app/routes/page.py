from flask import render_template, flash, redirect, send_file, url_for, abort, request, jsonify
from app import app
from datetime import datetime, timedelta
from app.models import Event
from app.forms import CompareCountryForm, CompareCityForm, ResponseCountryForm, SubmitEventRequestForm
from app.compare import get_similar_places, get_fig_compare_rates, get_fig_compare_doubling_rates, \
    get_all_places, get_timeline_list, get_place_live_stats, get_place_socio_stats, get_similar_places_socio, \
    get_fig_response, get_places_by_variable, get_html_compare_response, get_html_compare_response_econ


@app.context_processor
def inject_countries():
    '''
    Injector on all pages to render a list of places on the header menu
    '''
    return dict(countries=get_all_places(level = "countries"))

@app.route('/report-event', methods=['GET', 'POST'])
def reportEvent():
    '''
    Report Event Page
    Renders the form to report an event about the epidemic on a place.
    If completed correctly, renders a success message. Otherwise will present the errors on the form.
    '''
    form_event = SubmitEventRequestForm()
    if form_event.validate_on_submit():
        event = Event()
        form_event.populate_obj(event)
        event.save()
        return render_template('submit_event_success.html')

    return render_template('submit_event.html', form_event=form_event)


@app.route('/timeline/<place>/<place2>/<level>')
def timeline(place, place2, level):
    '''
    Timeline Page
    Renders the timeline of two places.
    '''
    tl = get_timeline_list(place, place2, level = level)
    return render_template("pages/timeline.html.jinja", place=place, place2 = place2, level = level, timeline = tl)


@app.route('/comparison/<place>/<place2>/<level>')
def comparison(place, place2, level):
    '''
    Comparison Page
    Renders the comparison of two places.
    '''
    html_compare_resp = get_html_compare_response(place, place2, level) if level == 'countries' else ''
    html_compare_resp_econ = None
    return render_template("pages/compare_places.html.jinja", place=place, place2 = place2, level = level,
                           ls_place = get_place_live_stats(place = place, level = level), ls_place2 = get_place_live_stats(place = place2, level = level),
                            ss_place = get_place_socio_stats(place = place, level = level), ss_place2 = get_place_socio_stats(place = place2, level = level),
                           html_compare_resp = html_compare_resp, html_compare_resp_econ = html_compare_resp_econ)


@app.route('/place/<place>')
def place(place):
    '''
    Place Page. 
    Renders the comparison list for other places and links to comparisons pages
    '''
    simcountries = get_similar_places(place = place, level = 'countries')
    simcountries_socio = get_similar_places_socio(place = place, level = 'countries')

    live_stats = get_place_live_stats(place = place, level = 'countries')
    return render_template('pages/compare_init.html.jinja', country=place, level = 'countries', simcountries=simcountries, simcountries_socio = simcountries_socio, live_stats=live_stats)


@app.route('/faq')
def faq():
    '''
    FAQ Page
    Renders a list of QA about the project and the group
    '''
    return render_template("pages/faq.html.jinja")

@app.route('/about-us')
def aboutUs():
    '''
    About Us Page
    Renders a list of information about the project and the group
    '''
    return render_template("pages/about_us.html.jinja")

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    Home Page
    Renders a form to select a place to inspect
    '''
    type = 'list_posts'
    form_countries = CompareCountryForm()
    payload = request.args
    print(payload)
    if payload:
        return redirect(url_for("place", place=payload['place']))
    return render_template('pages/index.html.jinja', form_countries=form_countries, type = type)


@app.route('/page')
def page():
    '''
    Example route for a page
    '''
    return render_template('pages/page.html.jinja')