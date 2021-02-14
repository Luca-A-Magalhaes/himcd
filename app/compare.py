import re

import pandas as pd
# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns; sns.set()
from scipy.spatial.distance import squareform
from scipy.spatial.distance import pdist, euclidean
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import base64
import plotly.figure_factory as ff

data_dir = 'data/'

def get_all_places(level='countries'):
    df_places = pd.read_csv(data_dir + 'all_{}_compare.csv'.format(level))
    return list(df_places['Name'])

def get_all_countries_response():
    df_places = pd.read_csv(data_dir + 'all_countries_response.csv')
    return list(df_places['Country'])

def get_df_similar_places(place, level = 'countries'):
    if level == 'cities':
        df_sim = pd.read_csv(data_dir + 'all_{}_similarity.csv'.format(level))
        df_sim = df_sim[df_sim['CityBase'] == place]
        df_sim = df_sim[['Name', 'gap', 'dist', 'Similarity']].set_index('Name')
        return df_sim
    df_orig = pd.read_csv(data_dir + 'total_cases_{}_normalized.csv'.format(level))
    df_orig_piv_day = df_orig.pivot(index='Name', columns='Day', values='TotalDeaths')

    df_orig_piv_day = df_orig_piv_day.fillna(0)

    sr_place = df_orig_piv_day.loc[place,]

    place_start = (sr_place > 0).idxmax()

    # place_start_cases = (df_orig.set_index('Name').loc[place,].set_index('Day')['Total'] > 0).idxmax()

    days_ahead = 14 #if level == 'countries' else 5

    df_places_ahead = df_orig_piv_day[df_orig_piv_day.loc[:, max(place_start - days_ahead,0)] > 0.0]

    df_places_rate_norm = df_orig_piv_day.loc[df_places_ahead.index, :]

    # df_places_rate_norm = df_orig_piv_day.loc[['France', 'Italy'], :]

    df_places_rate_norm = df_places_rate_norm.append(df_orig_piv_day.loc[place,])

    # reverse order to keep base place on top
    df_places_rate_norm = df_places_rate_norm.iloc[::-1]

    sr_place = df_orig_piv_day.loc[place,]

    # place_start = (sr_place > 0).idxmax()

    # sr_place_compare = sr_place.loc[place_start:].dropna()

    sr_place = df_orig_piv_day.loc[place,]

    place_start = (sr_place > 0).idxmax()

    sr_place_compare = sr_place.loc[place_start:].dropna()

    df_places_gap = pd.DataFrame({'Name': [], 'gap': [], 'dist': []})

    df_places_gap = df_places_gap.append(pd.Series([place, 0.0, -1], index=df_places_gap.columns),
                                               ignore_index=True)

    for other_place in df_places_rate_norm.index[1:]:
        sr_other_place = df_places_rate_norm.loc[other_place,].fillna(0)

        min_dist = np.inf

        min_pos = 0

        for i in range(0, 1 + len(sr_other_place) - len(sr_place_compare)):
            sr_other_place_compare = sr_other_place[i: i + len(sr_place_compare)]
            dist = euclidean(sr_place_compare, sr_other_place_compare)
            if (dist < min_dist):
                min_dist = dist
                min_pos = i
        day_place2 = sr_other_place.index[min_pos]
        gap = day_place2 - place_start

        df_places_gap = df_places_gap.append(
            pd.Series([other_place, gap, min_dist], index=df_places_gap.columns),
            ignore_index=True)



    df_places_gap = df_places_gap.set_index('Name')

    similar_places = df_places_gap.sort_values('dist')

    dist_max = euclidean(sr_place_compare, np.zeros(len(sr_place_compare)))

    similar_places['Similarity'] = similar_places['dist'].apply(lambda x: (1.0 - x / dist_max) if x >= 0 else 1)

    return similar_places

# get similar places based on alighment of death curve
def get_similar_places(place, level = 'countries'):

    similar_places = get_df_similar_places(place, level = level)
    # print(similar_places)
    tuples = [tuple(x) for x in similar_places[1:8].reset_index().to_numpy()]

    return tuples

#get similar places based on socioeconomic features
def get_similar_places_socio(place, level = 'countries'):
    df_socio_stats_orig = pd.read_csv(data_dir + 'socio_stats_{}.csv'.format(level)).drop('score', axis=1)

    if not len(df_socio_stats_orig.query('Name == "{}"'.format(place))): return []

    df_socio_stats_orig_piv = df_socio_stats_orig.pivot(index='Name', columns='variable')

    df_socio_stats_orig_piv = df_socio_stats_orig_piv.fillna(df_socio_stats_orig_piv.mean())

    scaler = MinMaxScaler()  # feature_range=(-1, 1)

    df_socio_stats_orig_piv_norm = pd.DataFrame(scaler.fit_transform(df_socio_stats_orig_piv),
                                                columns=df_socio_stats_orig_piv.columns,
                                                index=df_socio_stats_orig_piv.index)

    df_dist = pd.DataFrame(squareform(pdist(df_socio_stats_orig_piv_norm)), index=df_socio_stats_orig_piv_norm.index,
                           columns=df_socio_stats_orig_piv_norm.index)

    df_sim = df_dist.loc[:, place].to_frame(name='dist')

    df_sim['similarity'] = 1 - (df_sim['dist'] / df_sim['dist'].max())

    df_sim = df_sim.sort_values('similarity', ascending=False).drop('dist', axis=1)

    tuples = [tuple(x) for x in df_sim[1:11].reset_index().to_numpy()]

    return tuples

def get_places_by_variable(type = 'socio', level = 'countries', variable = 'Population', ascending = False):
    if type == 'socio':
        df_orig = pd.read_csv(data_dir + 'socio_stats_{}.csv'.format(level)).drop('score', axis=1)
    else:
        df_orig = pd.read_csv(data_dir + 'live_stats_{}.csv'.format(level))
        # df_orig = df_orig.groupby(['Name', 'Date']).tail(1)

    df_orig = df_orig[df_orig['variable'] == variable].pivot(index='Name', columns='variable', values='value').reset_index()
    df_orig = df_orig[['Name', variable]].sort_values(variable, ascending = ascending).head(10)

    tuples = [tuple(x) for x in df_orig.reset_index(drop=True).to_numpy()]
    return tuples


def get_fig_compare_rates(place, place2, level = 'countries', scale='log', y='total', mode='static', priority = 'now'):
    df_places_to_show = get_place_comparison_df(place, place2, level = level, priority = priority)
    fig = make_chart_comparison(df_places_to_show, level = level, scale=scale, y=y, mode=mode)
    return fig

def get_html_compare_response(place, place2, level = 'countries', scale='log', y='total', mode='static', priority = 'now'):
    # df_places_to_show = get_place_comparison_df(place, place2, level = level, priority = priority, type = 'response')
    data_dir = 'data/'

    df_orig = pd.read_csv(data_dir + 'response/official_response_countries.csv', parse_dates=['Date'])

    cols = list(df_orig.columns[df_orig.dtypes.eq('float64')][:15]) + ['ConfirmedDeaths']

    df_orig[cols] = df_orig[cols].astype(pd.Int64Dtype())

    countries = [place, place2]

    df_orig = df_orig[df_orig['Name'].isin(countries)]

    df_gantt = df_orig[['Name', 'Date', 'StringencyIndexForDisplay', 'ConfirmedDeaths']].rename(
        columns={'Date': 'Start', 'Name': 'Task'})
    df_gantt['StringencyIndexForDisplay'] = df_gantt['StringencyIndexForDisplay'].fillna(0)
    df_gantt['Finish'] = df_gantt['Start'] + timedelta(days=1)
    df_gantt['Description'] = df_orig.apply(lambda
                                                x: "Stringency Index: {StringencyIndexForDisplay}<br>Confirmed Deaths: {ConfirmedDeaths}<br>School closing: {C1_School closing}<br>Workplace closing: {C2_Workplace closing}<br>Cancel public events: {C3_Cancel public events}<br>Restrictions on gatherings: {C4_Restrictions on gatherings}<br>Close public transport: {C5_Close public transport}<br>Stay at home requirements: {C6_Stay at home requirements}<br>Restrictions on internal movement: {C7_Restrictions on internal movement}<br>International travel controls: {C8_International travel controls}".format(
        **x), axis=1)
    df_gantt['ConfirmedDeaths'] = np.log(df_gantt['ConfirmedDeaths'])
    df_gantt = df_gantt.replace([-np.inf], 0)
    df_gantt['DeathsNorm'] = 0.7 * (df_gantt['ConfirmedDeaths'] - df_gantt['ConfirmedDeaths'].min()) / (
                df_gantt['ConfirmedDeaths'].max() - df_gantt['ConfirmedDeaths'].min()) - 0.35

    df_gantt_c1 = df_gantt[df_gantt['Task'] == place]
    df_gantt_c1['DeathsNorm'] = df_gantt_c1['DeathsNorm'] + 1

    df_gantt_c2 = df_gantt[df_gantt['Task'] == place2]


    fig = make_chart_response_comparison(df_gantt_c1, df_gantt_c2, level = level, scale=scale, y=y, mode=mode)
    return fig

def get_html_compare_response_econ(place, place2, level = 'countries', scale='log', y='total', mode='static', priority = 'now'):
    # df_places_to_show = get_place_comparison_df(place, place2, level = level, priority = priority, type = 'response')
    data_dir = 'data/'

    df_orig = pd.read_csv(data_dir + 'response/official_response_economic_countries.csv', parse_dates=['Date'])

    # cols = list(df_orig.columns[df_orig.dtypes.eq('float64')][:15]) + ['ConfirmedDeaths']

    # df_orig[cols] = df_orig[cols].astype(pd.Int64Dtype())

    countries = [place, place2]

    df_orig = df_orig[df_orig['Name'].isin(countries)]

    df_gantt = df_orig[['Name', 'Date', 'EconomicSupportIndexForDisplay', 'ConfirmedDeaths', 'Description']].rename(
        columns={'Date': 'Start', 'Name': 'Task'})
    df_gantt['EconomicSupportIndexForDisplay'] = df_gantt['EconomicSupportIndexForDisplay'].fillna(0)
    df_gantt['Finish'] = df_gantt['Start'] + timedelta(days=1)
    df_gantt['ConfirmedDeaths'] = np.log(df_gantt['ConfirmedDeaths'])
    df_gantt = df_gantt.replace([-np.inf], 0)
    df_gantt['DeathsNorm'] = 0.7 * (df_gantt['ConfirmedDeaths'] - df_gantt['ConfirmedDeaths'].min()) / (
                df_gantt['ConfirmedDeaths'].max() - df_gantt['ConfirmedDeaths'].min()) - 0.35

    df_gantt_c1 = df_gantt[df_gantt['Task'] == place]
    df_gantt_c1['DeathsNorm'] = df_gantt_c1['DeathsNorm'] + 1

    df_gantt_c2 = df_gantt[df_gantt['Task'] == place2]


    fig = make_chart_response_comparison(df_gantt_c1, df_gantt_c2, level = level, scale=scale, y=y, mode=mode, var='EconomicSupportIndexForDisplay')
    return fig

def get_fig_compare_doubling_rates(place, place2, level = 'countries'):
    df_places_to_show = get_place_comparison_df(place, place2, level = level)
    fig = make_chart_comparison_growth(df_places_to_show, level = level)
    return fig

def get_fig_response(country):
    df_orig_response = pd.read_csv(data_dir + 'pollution_countries_raw.csv', parse_dates=['Date'])

    df_orig_cases = pd.read_csv(data_dir + 'total_cases_countries_normalized.csv', parse_dates=['Date']).rename(
        columns={'Name': 'Country'})
    df_orig = pd.merge(df_orig_response, df_orig_cases, how='left')

    df_to_show = df_orig[df_orig['Country'] == country][['Country', 'City', 'Date', 'no2', 'TotalDeaths']].sort_values('Date')

    deaths_start = 10
    start_deaths = (df_to_show['TotalDeaths'] >= deaths_start).idxmax()

    avg_before_deaths = df_to_show.loc[:start_deaths, 'no2'].mean()

    start_display = max(start_deaths - 60, 0)

    df_to_show = df_to_show.loc[start_display:, ]

    df_to_show['no2'] = df_to_show[['no2']].rolling(5).mean()

    fig = make_chart_response(country, deaths_start, avg_before_deaths, df_to_show)
    return fig

def get_places_gap_df(df_orig, place, place2, priority = 'now'):
    df_places_gap = pd.DataFrame({'Name': [], 'gap': [], 'dist': []})
    df_places_gap = df_places_gap.append(pd.Series([place, 0.0, -1], index=df_places_gap.columns),
                                               ignore_index=True)
    df_orig = df_orig.set_index('Name')

    if not ((df_orig.loc[place,'TotalDeaths'].max()>0) and (df_orig.loc[place2,'TotalDeaths'].max()>0)):
        # one of the places has 0 deaths
        min_dist = 0 # means nothing here
        dist_max = 1 # means nothing here
        gap = 0
    elif priority != 'now':
        # must align based on beginning of deaths
        day_place = (df_orig.loc[place,:].set_index('Day')['TotalDeaths'] > 10).idxmax()
        day_place2 = (df_orig.loc[place2,:].set_index('Day')['TotalDeaths'] > 10).idxmax()
        min_dist = 0 # means nothing here
        dist_max = 1 # means nothing here
        gap = day_place2 - day_place
    else:
        # similarity alignment
        df_orig_piv_day = df_orig.reset_index().pivot(index='Name', columns='Day', values='TotalDeaths')

        sr_place = df_orig_piv_day.loc[place,]

        place_start = (sr_place > 0).idxmax()

        sr_place_compare = sr_place.loc[place_start:].dropna()

        sr_other_place = df_orig_piv_day.loc[place2,].fillna(0)
        min_dist = np.inf
        min_pos = 0
        for i in range(0, 1 + len(sr_other_place) - len(sr_place_compare)):
            sr_other_place_compare = sr_other_place[i: i + len(sr_place_compare)]
            dist = euclidean(sr_place_compare, sr_other_place_compare)

            if (dist < min_dist):
                min_dist = dist
                min_pos = i

        dist_max = euclidean(sr_place_compare, np.zeros(len(sr_place_compare)))
        day_place2 = sr_other_place.index[min_pos]

        # gap = min_pos - place_start
        gap = day_place2 - place_start
    df_places_gap = df_places_gap.append(
        pd.Series([place2, gap, min_dist], index=df_places_gap.columns),
        ignore_index=True)


    df_places_gap = df_places_gap.set_index('Name')#.sort_values('dist')

    df_places_gap['Similarity'] = df_places_gap['dist'].apply(lambda x: (1.0 - x / dist_max) if x >= 0 else 1)

    return df_places_gap

def get_total_cases_df_adjusted(df_orig, df_places_gap, place, place2):

    df_total_cases = df_orig.set_index('Name')

    df_total_cases_top = df_total_cases.join(df_places_gap)

    df_total_cases_top['DayAdj'] = ((df_total_cases_top['Day'] - df_total_cases_top['gap']) - 1).astype(int)

    # df_total_cases_top.loc[place2, 'DayAdj'] = ((df_total_cases_top.loc[place2, 'Day'] - df_total_cases_top.loc[place2, 'gap']) - 1)

    # df_total_cases_top['DayAdj'] = df_total_cases_top['DayAdj'].astype(int)

    return  df_total_cases_top

def get_place_comparison_df(place, place2, level = 'countries', priority = 'now'):

    df_orig = pd.read_csv(data_dir + 'total_cases_{}_normalized.csv'.format(level))

    # to force place order
    df_orig_c1 = df_orig[df_orig['Name'] == place]
    df_orig_c2 = df_orig[df_orig['Name'] == place2]

    len_c1 = len(df_orig_c1[df_orig_c1['TotalDeaths']  > 0])
    len_c2 = len(df_orig_c2[df_orig_c2['TotalDeaths'] > 0])

    # place has to be the one with smallest number of values for Deaths
    if (len_c1 > len_c2):
        place, place2 = place2, place
        df_orig = pd.concat([df_orig_c2, df_orig_c1])
    else:
        df_orig = pd.concat([df_orig_c1, df_orig_c2])

    df_countries_gap = get_places_gap_df(df_orig, place, place2, priority)

    df_total_cases_top = get_total_cases_df_adjusted(df_orig, df_countries_gap, place, place2)

    place_start_cases = (df_orig.set_index('Name').loc[place,].set_index('Day')['Total'] > 0).idxmax()

    df_total_cases_top = df_total_cases_top[df_total_cases_top['DayAdj'] >= place_start_cases]

    return df_total_cases_top.reset_index()


def make_chart_comparison(df_places_to_show, level='countries', scale='log', y='total', mode='static'):
    week = mdates.WeekdayLocator(interval=2)  # every year
    months = mdates.MonthLocator()  # every month
    month_fmt = mdates.DateFormatter('%b-%d')

    var_y_suffix = '' if y == 'total' else 'Per100k'
    label_y_scale = ' (log)' if scale == 'log' else ''
    label_y_y = '' if y == 'total' else ' per 100k'

    # get last date from dataframe
    date = df_places_to_show['Date'].max()  # datetime.today().strftime('%Y-%m-%d')

    gap = int(df_places_to_show['gap'].min())

    y_lim = df_places_to_show['Total' + var_y_suffix].max() #* 1.2

    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=(8, 5))

    ax = fig.subplots()

    places_to_show = df_places_to_show['Name'].unique()[:2]

    place_name = 'Country' if level == 'countries' else 'City'
    df_places_to_show = df_places_to_show.rename(columns={'Name': place_name})

    ax.set_title('{} Comparison - COVID-19 Cases vs. Deaths - {}'.format(place_name, date), fontsize=14)

    sns.scatterplot(x="DayAdj", y='Total' + var_y_suffix, hue=place_name, lw=6, alpha=0.8, data=df_places_to_show,
                    ax=ax)

    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(month_fmt)

    ax.legend(loc='upper left', title="Confirmed cases", frameon=True)

    ax.set(ylabel='Total confirmed cases{}{}'.format(label_y_y, label_y_scale),
           xlabel="Date for {} ({}'s data shifted {} days to align death curves)".format(places_to_show[0],
                                                                                        places_to_show[1], gap))

    ax.set_ylim(0.5, y_lim) if scale == 'log' else ax.set_ylim(-5, y_lim)

    ax2 = ax.twinx()

    if scale == 'log':
        ax.set_yscale('log')
        ax2.set_yscale('log')

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))

    ax2.grid(False)

    sns.lineplot(x="DayAdj", y='TotalDeaths' + var_y_suffix, hue=place_name, alpha=0.7, lw=6, ax=ax2,
                 data=df_places_to_show)

    ax2.legend(loc='lower right', title="Deaths", frameon=True)

    ax2.set(ylabel='Total deaths{}{}'.format(label_y_y, label_y_scale))

    ax2.set_ylim(0.5, y_lim) if scale == 'log' else ax2.set_ylim(-5, y_lim)

    logo = plt.imread('./static/img/new_logo_site.png')
    ax.figure.figimage(logo, 95, 70, alpha=.35, zorder=1)

    fig.tight_layout()

    # display(fig)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

def make_chart_response_comparison(df_gantt_c1, df_gantt_c2, level='countries', scale='log', y='total', mode='static', var='StringencyIndexForDisplay'):
    # to force place order
    df_gantt = pd.concat([df_gantt_c1, df_gantt_c2])

    fig = ff.create_gantt(df_gantt, colors=['#93e4c1', '#333F44'], index_col=var,
                          show_colorbar=False, bar_width=0.2, showgrid_x=True, showgrid_y=True, group_tasks=True,
                          title='Comparing response',
                          height=350
                          )

    fig.add_scatter(x=df_gantt_c1['Start'], y=df_gantt_c1['DeathsNorm'], hoverinfo='skip',
                    line=dict(color='rgb(222, 132, 82)', width=4))

    fig.add_scatter(x=df_gantt_c2['Start'], y=df_gantt_c2['DeathsNorm'], hoverinfo='skip',
                    line=dict(color='rgb(222, 132, 82)', width=4))

    fig.update_layout(
        xaxis=dict(
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
            type="date"

        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
            autorange=True,
        ),
        autosize=False,
        margin=dict(
            autoexpand=False,
            l=100,
            r=20,
            t=110,
        ),
        showlegend=False,
        plot_bgcolor='white'
    )

    annotations = []

    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.13,
                            xanchor='center', yanchor='top',
                            text='Date',
                            font=dict(family='Arial',
                                      size=12,
                                      color='rgb(150,150,150)'),
                            showarrow=False))

    fig.update_layout(annotations=annotations)

    # fig.write_html("gantt.html")
    # fig.show()
    html = fig.to_html(full_html=False, include_plotlyjs=False, )

    return html

def make_chart_comparison_growth(df_places_to_show, level='countries'):
    # get last date from dataframe
    date = df_places_to_show['Date'].max()  # datetime.today().strftime('%Y-%m-%d')
    gap = int(df_places_to_show['gap'].min())

    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=(8, 6))

    axs = fig.subplots(nrows=2)


    place_name = 'Country' if level == 'countries' else 'City'

    axs[0].set_title('{} Comparison - COVID-19 Weekly Growth (%) - {}'.format(place_name, date), fontsize=14)

    places_to_show = df_places_to_show['Name'].unique()[:2]
    df_places_to_show = df_places_to_show.rename(columns={'Name': place_name})


    sns.lineplot(x="DayAdj", y='WeeklyGrowth', hue=place_name, lw = 6, alpha = 0.8, ax=axs[0], data=df_places_to_show)


    axs[0].set(ylabel='Weekly growth of cases', xlabel='')
    axs[0].set_ylim(0, 500)

    sns.lineplot(x="DayAdj", y='WeeklyGrowthDeaths', hue=place_name, alpha = 0.7, lw = 6, ax=axs[1], data=df_places_to_show)

    axs[1].set(ylabel='Weekly growth of deaths', xlabel="Day ({}'s data shifted {} days for the death curves to align)".format(places_to_show[1], gap))
    axs[1].set_ylim(0, 500)

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

def make_chart_response(country, deaths_start, avg_before_deaths, df_to_show):
    city = df_to_show['City'].iloc[0]
    df_quar = pd.read_csv(data_dir + 'all_countries_response.csv', parse_dates = ['Quarantine'])
    quarantine = df_quar[df_quar['Country'] == country]['Quarantine'].iloc[0]

    week = mdates.WeekdayLocator(interval=2)   # every year
    months = mdates.MonthLocator()  # every month
    month_fmt = mdates.DateFormatter('%b-%d')

    y_lim = df_to_show['TotalDeaths'].max() * 1.2
    y2_lim = df_to_show['no2'].max() * 1.8

    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=(10, 5))

    ax = fig.subplots()


    ax.set_title('Assessing quarantine implementation - ' + country, fontsize=16, loc='left')

    if not pd.isnull(quarantine): ax.axvline(x=quarantine, color='k', linestyle='--', lw=3, label='Official quarantine')

    ax.scatter(df_to_show['Date'], df_to_show['TotalDeaths'], color='black', alpha = 0.7, label = 'Confirmed deaths')

    ax.xaxis.set_major_locator(week)
    ax.xaxis.set_major_formatter(month_fmt)

    ax.set_yscale('log')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: '{:g}'.format(y)))
    ax.set_ylim(1, y_lim)
    ax.set(ylabel='Confirmed deaths')

    ax2 = ax.twinx()

    sns.lineplot(x="Date", y='no2',  alpha = 0.7, lw = 6, label = 'Daily $\mathrm{{NO}}_2$ pollution *', ax=ax2, data=df_to_show)
    sns.lineplot(x="Date", y=avg_before_deaths,  alpha = 0.7, lw = 6, label = 'Average pollution **', ax=ax2, data=df_to_show)

    ax2.grid(False)
    ax2.xaxis.set_major_locator(week)
    ax2.xaxis.set_major_formatter(month_fmt)
    ax2.set_ylim(1, y2_lim)
    ax2.set(ylabel='$\mathrm{{NO}}_2$ pollution')

    # ask matplotlib for the plotted objects and their labels
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper left')

    annotation = """* Median of $\mathrm{{NO}}_2$ measurements in the most affected city ({city}), 5 days rolling average over time series\n** Average daily $\mathrm{{NO}}_2$ measurements from the begining of 2020 until the first day after {deaths_start} deaths""".format(city=city, deaths_start = deaths_start)
    ax.annotate(annotation, (0,0), (0, -30), xycoords='axes fraction', textcoords='offset points', va='top')

    logo = plt.imread('./static/img/new_logo_site.png')
    ax.figure.figimage(logo, 100, 110, alpha=.35, zorder=1)

    fig.tight_layout()
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

def get_timeline_list(place, place2, level = 'countries'):
    df_orig = pd.read_csv(data_dir + 'total_cases_{}_normalized.csv'.format(level))

    # to force place order
    df_orig_c1 = df_orig[df_orig['Name'] == place]
    df_orig_c2 = df_orig[df_orig['Name'] == place2]

    len_c1 = len(df_orig_c1[df_orig_c1['TotalDeaths']  > 0])
    len_c2 = len(df_orig_c2[df_orig_c2['TotalDeaths'] > 0])

    # place has to be the one with smallest number of values for Deaths
    if (len_c1 > len_c2):
        place, place2 = place2, place
        df_orig = pd.concat([df_orig_c2, df_orig_c1])
    else:
        df_orig = pd.concat([df_orig_c1, df_orig_c2])

    df_places_gap = get_places_gap_df(df_orig, place, place2)

    df_total_cases_top = get_total_cases_df_adjusted(df_orig, df_places_gap, place, place2)

    places = [place, place2]

    df_places_to_show = df_total_cases_top.loc[places, :]

    places_to_show = list(df_places_to_show.index.unique())

    df_events_owd = pd.DataFrame({'Date': [], 'Name': [], 'Desc': [], 'FullText': [], 'Highlight': []})

    today = df_places_to_show['Date'].max()

    for c in places_to_show:
        df_place = df_places_to_show.loc[c,]

        #     df_events_owd = df_events_owd.append(pd.DataFrame({'Date':['2019-12-31'], 'Name': [c], 'Desc':['Begining of epidemic'], 'FullText':['First day of data tracking.']}))

        df_events_owd = df_events_owd.append(
            pd.Series([(df_place.set_index('Date')['Total'] > 0).idxmax(), c, '1st Confirmed Case', '', 1],
                      index=df_events_owd.columns), ignore_index=True)

        df_events_owd = df_events_owd.append(
            pd.Series([(df_place.set_index('Date')['TotalDeaths'] > 0).idxmax(), c, '1st Death', '', 5],
                      index=df_events_owd.columns), ignore_index=True)

        msg = """{} is approximately {} days behind {}'s epidemic progression. 
                      This is an estimate based on matching their death growth curves.""".format(place, abs(
            df_places_gap.loc[place2, 'gap']), place2)

        df_events_owd = df_events_owd.append(pd.Series([today, c, 'Today', msg, 1], index=df_events_owd.columns),
                                             ignore_index=True)

    df_events_owd['Source'] = 'Our World in Data'

    # Adding data from Situation Reports
    if level == 'countries':
        df_events_sr = pd.read_csv(data_dir + 'situation_reports_countries_highlight.csv')
    else:
        df_events_sr = pd.DataFrame({'Name':[]})

    df_events_sr = df_events_sr[df_events_sr['Name'].isin([place, place2])]

    df_events = pd.concat([df_events_owd, df_events_sr], sort=True)

    # Groups events that happen on the same day

    df_events_grouped = pd.DataFrame(df_events.groupby(['Date', 'Name'])['Desc'].apply(lambda x: "\n".join(x)))

    df_events_grouped['FullText'] = df_events.groupby(['Date', 'Name'])['FullText'].apply(lambda x: "\n".join(x))

    df_events_grouped['Source'] = df_events.groupby(['Date', 'Name'])['Source'].apply(lambda x: "\n".join(x))

    df_events_grouped['Highlight'] = df_events.groupby(['Date', 'Name'])['Highlight'].max()

    df_events_adj = pd.merge(df_events_grouped, df_places_to_show[['Date', 'DayAdj']].reset_index(), how='left',
                             on=['Date', 'Name'])

    df_events_adj['Highlight'] = df_events_adj['Highlight'].astype(int)

    df_places_events = pd.merge(df_events_adj[['Name', 'DayAdj', 'Desc', 'FullText', 'Highlight', 'Source']],
                                   df_places_to_show.reset_index(), how='outer', on=['DayAdj', 'Name'])

    df_places_events = df_places_events.set_index('Name')

    df_places_events_merged = pd.merge(df_places_events.loc[place, :].reset_index(),
                                          df_places_events.loc[place2, :].reset_index(), on='DayAdj', how='outer',
                                          suffixes=('', '2'))

    df_places_events_merged = df_places_events_merged.set_index('DayAdj').sort_index()

    start_events = min(df_places_events_merged['Desc'].first_valid_index(),
                       df_places_events_merged['Desc2'].first_valid_index())

    end_events = max(df_places_events_merged['TotalDeaths'].last_valid_index(),
                     df_places_events_merged['TotalDeaths2'].last_valid_index())

    df_places_events_trimed = df_places_events_merged.loc[start_events:end_events]

    df_places_events_trimed = df_places_events_trimed[
        ['Name', 'Date', 'Desc', 'FullText', 'Highlight', 'Source', 'Total', 'TotalDeaths', 'GrowthRate',
         'GrowthRateDeaths', 'DaysToDouble', 'DaysToDoubleDeaths', 'Date2', 'Name2', 'Desc2', 'FullText2',
         'Highlight2', 'Source2', 'Total2', 'TotalDeaths2', 'GrowthRate2', 'GrowthRateDeaths2', 'DaysToDouble2',
         'DaysToDoubleDeaths2', ]]

    # Fill place name for 1st place
    df_places_events_trimed['Name'] = df_places_events_trimed['Name'].ffill()

    # Fill place name for 2nd place
    df_places_events_trimed['Name2'] = df_places_events_trimed['Name2'].ffill()

    # Fill TotalDeath
    # df_places_events_trimed['TotalDeaths'] = df_places_events_trimed['TotalDeaths'].ffill()
    # df_places_events_trimed['TotalDeaths2'] = df_places_events_trimed['TotalDeaths2'].ffill()

    # Fill dates for 1st place
    # sr_days = pd.to_datetime(df_places_events_trimed['Date'].ffill())
    # sr_adj_days = df_places_events_trimed.groupby(df_places_events_trimed['Date'].notnull().cumsum()).cumcount()
    # df_places_events_trimed['Date'] = (sr_days + pd.to_timedelta(sr_adj_days, unit='d')).dt.strftime('%Y-%m-%d')

    # Fill dates for 2nd place
    # sr_days = pd.to_datetime(df_places_events_trimed['Date2'].ffill())
    # sr_adj_days = df_places_events_trimed.groupby(df_places_events_trimed['Date2'].notnull().cumsum()).cumcount()
    # df_places_events_trimed['Date2'] = (sr_days + pd.to_timedelta(sr_adj_days, unit='d')).dt.strftime('%Y-%m-%d')

    df_places_events_trimed = df_places_events_trimed.fillna('').replace({'NaT': ''})

    return df_places_events_trimed.to_dict('records')


def fix_variable_names(series):
    new_names = series.apply(lambda x: re.sub("([a-z])([A-Z])","\g<1> \g<2>", x))
    new_names = new_names.apply(lambda x: re.sub("^Total$","Total Confirmed Cases", x))
    new_names = new_names.apply(lambda x: re.sub("Per100k","per 100k", x))
    new_names = new_names.apply(lambda x: re.sub("^Weekly Growth$","Weekly Growth (%)", x))
    new_names = new_names.apply(lambda x: re.sub("^Weekly Growth Deaths$","Weekly Growth Deaths (%)", x))
    new_names = new_names.str.capitalize()
    return new_names


def get_place_live_stats(place, level = 'countries'):
    df_live_stats_orig = pd.read_csv(data_dir + 'live_stats_{}.csv'.format(level))
    variables = fix_variable_names(pd.Series(df_live_stats_orig['variable'].unique(), name='variable'))

    df_live_stats_place = df_live_stats_orig[df_live_stats_orig['Name'] == place]

    if not len(df_live_stats_place):
        df_live_stats_place = pd.merge(variables, df_live_stats_place, how='left')

    df_live_stats_place.variable = fix_variable_names(df_live_stats_place['variable'])

    return df_live_stats_place[['variable', 'value', 'change']].to_dict('records')


def get_place_socio_stats(place, level = 'countries'):
    df_socio_stats_orig = pd.read_csv(data_dir + 'socio_stats_{}.csv'.format(level))
    variables = fix_variable_names(pd.Series(df_socio_stats_orig['variable'].unique(), name='variable'))

    df_socio_stats_place = df_socio_stats_orig[df_socio_stats_orig['Name'] == place]

    if not len(df_socio_stats_place):
        df_socio_stats_place = pd.merge(variables, df_socio_stats_place, how='left')

    df_socio_stats_place.variable = fix_variable_names(df_socio_stats_place['variable'])

    return df_socio_stats_place[['variable', 'value', 'score']].to_dict('records')

if __name__ == "__main__":
    # execute only if run as a script
    # df = get_place_comparison_df('Brazil', 'Iran', level = 'countries', priority='start')
    df = get_place_comparison_df('Osasco-SP', 'São Paulo-SP', level = 'cities', priority='now')


    # get_fig_compare_rates('Brazil', 'Italy')
    # tl = get_timeline_list('Bolivia', 'Hungary')

    # df = get_df_similar_places('Fortaleza-CE', level='cities')

    # df =  get_place_live_stats('Salvador-BA', level='cities')

    print('bla', df)