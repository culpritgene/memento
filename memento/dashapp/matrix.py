import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from loguru import logger

from .render import *
from .utils import *

url_base = '/dash/'


def init_dash(server, url_base):
    dash_app = dash.Dash(server=server,
                    #requests_pathname_prefix='/matrix/',
                    #routes_pathname_prefix=url_base,
                    url_base_pathname=url_base,
                    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css',
                                          './memento/static/main.css'])

    ### TODO: Move to Static
    styles = {
        'pre': {
            'border': 'thin lightgrey solid',
            'overflowX': 'scroll',
            'width': '100%',
            'height': 400,
            'float': 'right',
        }
    }

    layout = html.Div(
        [
        dcc.Location(id='get-url', refresh=False),
        html.Div(id='url-params', hidden=True),
        dcc.Storage(id='user-data'),
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='data-type',
                        options=[{'label': i, 'value': i} for i in config['default'].AVAILABLE_DATAENTRIES],
                        value='mood'),
                    dcc.RangeSlider(
                        id='num-years-slider',
                        min=0,
                        max=config['default'].LIFESPAN,
                        value=[0, 3],
                        allowCross=False,
                        marks={str(y): str(y) for y in range(config['default'].LIFESPAN)}, step=1)
                        ]),
            ], style={'width': '100%', 'height': '15%', 'float': 'top'}
            ),
            html.Div(style={'width':'100%', 'height':20}),
            html.Div([
                html.Div(
                    children=[
                    html.Div([
                        html.H3(""" Diary Entry """, style={'align':'center'}),
                        dcc.Textarea(id='click-data', value="Hm!", style=styles['pre'],
                                     draggable=False, className='display field'),
                        html.Button(id='save-button', n_clicks=0, children='Save', style={'width':'50%'}),
                        html.Button(id='forget-button', n_clicks=0, children='Forget', style={'width':'50%'})
                            ]),
                            ], className='row', style={'width':'14%','float': 'left'}),
                html.Div(dcc.Graph(id='main-plot'), style={'width':'85%','float': 'left'}, # config={'displayModeBar': False}
                         className='multifaceted heatmap')
                    ], style={'width':'100%', 'height': '85%', 'float': 'bottom'})
            ])
        ], className='main', style={'background-color': '#fff'})

    apply_layout_with_auth(dash_app, layout)
    init_callbacks(dash_app)

    return dash_app.server


def init_callbacks(app):
    @app.callback(Output('click-data', 'value'),
                  [Input('main-plot', 'clickData')],
                  [State('data-type', 'value')])
    def event_on_click(clickData, data_type):
        logger.info('Value of the lifeline {} changed from {} to {} at date {}'.format(
            data_type,
            clickData['points']['z'],
            clickData['points']['z']+50,
            clickData['points']['text'],
            ))
        return clickData['points'][0]['text']


    @app.callback(Output('main-plot', 'figure'),
                  [Input('user-data', 'data'),
                   Input('data-type', 'value'),
                   Input('num-years-slider', 'value')])
    def serve_matrix(user_data, data_type, years_range):
        if not user_data:
            logger.warning('Attempt to serve matrix without user data!')
            raise PreventUpdate
        else:
            start, stop = years_range
            cells = np.array(user_data[data_type])[start:stop]
            dates = np.array(user_data['liveyears'])[start:stop]
            if stop - start <= config['default'].DAY_DISPLAY_MAX:
                logger.info('Serving matrix for the days layout on years range: {}-{}'.format(start, stop))
                fig = annual_life_step_days(cells, dates)
            elif config['default'].DAY_DISPLAY_MAX < stop - start <= config['default'].WEEKS_DISPLAY_MAX:
                logger.info('Serving matrix for the weeks layout on years range: {}-{}'.format(start, stop))
                fig = annual_life_step_weeks(cells, dates)
            elif config['default'].WEEKS_DISPLAY_MAX < stop - start <= config['default'].MONTHS_DISPLAY_5_MAX:
                logger.info('Serving matrix for the months layout on years range: {}-{}'.format(start, stop))
                fig = annual_life_step_months(cells, dates, split=5)
            elif config['default'].MONTHS_DISPLAY_5_MAX < stop - start <= config['default'].MONTHS_DISPLAY_10_MAX:
                logger.info('Serving matrix for the years layout on years range: {}-{}'.format(start, stop))
                fig = annual_life_step_months(cells, dates, split=10) ### TODO: optimize view - plot size depending on split
            else:
                fig = annual_life_step_years(cells, user_data['birthdate'])
            return fig

    def save_data_to_db(user_data, session_id):
        logger.info('Saving data to the database for the user {} with uuid {}.'.format(session_id[1], session_id[0]))
        # TODO: add proper logger with loguru
        session_uid, current_username = session_id
        user = db.session.query(User).filter_by(username=current_username).first()
        for k in config['default'].AVAILABLE_DATAENTRIES:
            logger.info('Setting user model lifeline {}.'.format(k))
            setattr(user.lifelines, k, user_data[k])
        db.session.commit()
        return None


    @app.callback(Output('user-data', 'data'),
                  [Input('main-plot', 'clickData'),
                   Input('data-type', 'value'),
                   Input('save-button', 'n_clicks'),
                   Input('forget-button', 'n_clicks'),
                   Input('session-id', 'children')],
                  [State('num-years-slider', 'value'),
                   State('user-data', 'data')])
    def update_on_click(clickData, data_type, n_clicks_save, n_clicks_forget,  session_id, years_range, user_data):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered]
        if not user_data or 'forget-button.n_clicks' in changed_id:
            session_uid, current_username = session_id
            user_data = get_data_from_db(current_username)
        else:
            logger.info('Update-on-click method called with data input from {}'.format(changed_id))
            if 'save-button.n_clicks' in changed_id:
                save_data_to_db(user_data, session_id)
            selected_lifeline = np.array(user_data[data_type])
            Y, M, W, D = selected_lifeline.shape
            start, stop = years_range
            if stop-start <= config['default'].DAY_DISPLAY_MAX:
                point_data = clickData['points'][0]
                z, y, wm, d, text = point_data['z'], point_data['curveNumber'], point_data['x'], point_data['y'], point_data['text']
                m, w = wm // W, wm % W
                if not text.startswith('--'):
                    selected_lifeline[start:stop][y][m][w][d] = 2 # TODO: add selection
            elif config['default'].DAY_DISPLAY_MAX < stop-start <= config['default'].WEEKS_DISPLAY_MAX:
                #logger.info('Updating data for the weeks view.')
                point_data = clickData['points'][0]
                z, yy, y, w = point_data['z'], point_data['curveNumber'], point_data['y'], point_data['x']
                # TODO: add latent lifeline containing notes for weeks only
            else:
                pass
            user_data[data_type] = selected_lifeline
        return user_data

    @app.callback(Output('url-params', 'children'),
                  [Input('get-url', 'pathname')])
    def parse_url(url):
        return url
