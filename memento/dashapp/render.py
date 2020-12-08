import uuid

import dash_html_components as html
import plotly.graph_objs as go
from flask_login import current_user
from plotly import subplots

from .utils import *


def apply_layout_with_auth(app, layout):
    """
        A hacky way to merry Dash layout renderer and jinja2
    """
    def serve_layout():
        if current_user and current_user.is_authenticated:
            session_id = str(uuid.uuid4())
            ### add logger here
            return html.Div([
                html.Div([session_id, current_user.username], id='session-id', style={'display': 'none'}),
                layout
            ])
        return html.Div('403 Access Denied')

    app.config.suppress_callback_exceptions = True
    app.layout = serve_layout

def annual_life_step_days(Z, dates):
    Z += 1
    Z *= 50
    Z[dates[...,0] == '-'*12] = 0

    Y, M, W, D = Z.shape
    fig = subplots.make_subplots(Y, 1, shared_xaxes=False, shared_yaxes=False, vertical_spacing=0.005,
                                 horizontal_spacing=0.02)
    for y in range(Y):
        fig.append_trace(go.Heatmap(
            z=np.moveaxis(Z[y], (0,1,2), (1,2,0)).reshape(D,M*W),
            text=np.moveaxis(dates[y,...,0], (0,1,2), (1,2,0)).reshape(D,M*W),
            xgap=3, ygap=3,
            showscale=False,
            colorscale=[[0, "rgba(255,225,255,120)"], [0.2, "rgba(220,120,160,150)"],
                        [0.6, "rgba(40,220,150,10)"], [1, "rgba(190,80,255,255)"]],
            coloraxis="coloraxis"),
            row=y + 1, col=1)

    for i in range(Y):
        fig['layout'][f'yaxis{i + 1}'].update(dict(showticklabels=True,
                                                   ticks="outside",
                                                   automargin=True,
                                                   zeroline=False,
                                                   ticktext=['Mon','Tue','Wen','Thu','Fri','Sat','Sun'],
                                                   tickvals=[0,1,2,3,4,5,6],
                                                   autorange='reversed'))
        fig['layout'][f'xaxis{i + 1}'].update(dict(showline=False, zeroline=False, showgrid=False, tickvals=[]))

    fig['layout'][f'xaxis1'].update(dict(ticktext=['w1', 'w2', 'w3', 'w4', 'w5', ''],
                                               tickvals=[0, 1, 2, 3, 4, 5],
                                               mirror="allticks",
                                               side="top"))

    fig.update_layout(title='single year of your life', clickmode='event',
                      height=Y*190, width=1400, margin={'t': 40},
                      transition_duration=0,
                      xaxis={"mirror": "allticks", 'side': 'top'},
                      coloraxis={'colorscale': [[0, "rgba(255,225,255,120)"], [0.2, "rgba(220,120,160,150)"],
                                               [0.6, "rgba(40,220,150,10)"], [1, "rgba(190,80,255,255)"]]},
                      plot_bgcolor='rgba(255,255,255,225)',
                      paper_bgcolor='#fff', font={'color': '#444444', 'size': 15})
    return fig

def annual_life_step_weeks(Z, dates, form=[6, 13], split=5):
    Z = zero_stats(Z)
    Z = Z.mean(axis=-1) #[Y,M,W,D] --> [Y,M,W]
    dates = dates[:,:,:,5,0] # [Y,M,W,D,T] --> [Y,M,W] TODO: change day 5 to switch in case of '-' instead of date on this day
    ZZ, Y = wrap_dates_by(Z, form=form, split=split)
    dates, _ = wrap_dates_by(dates, form=form, split=split)
    fig = subplots.make_subplots(Y, 1, shared_xaxes=False, shared_yaxes=True, vertical_spacing=0.005,
                                 horizontal_spacing=0.02)
    for y in range(Y):
        fig.append_trace(go.Heatmap(
            z=np.moveaxis(ZZ[y], (0,1,2), (1,0,2)).reshape(form[0], form[1]*split),
            text=np.moveaxis(dates[y], (0, 1, 2), (1, 0, 2)).reshape(form[0], form[1] * split),
            xgap=3, ygap=3,
            showscale=False,
            colorscale=[[0, "rgba(255,225,255,120)"], [0.2, "rgba(220,120,160,150)"],
                       [0.6, "rgba(40,220,150,10)"], [1, "rgba(190,80,255,255)"]]
                                 ),
            row=y + 1, col=1)

    for i in range(Y):
        fig['layout'][f'yaxis{i + 1}'].update(dict(showline=False, showgrid=False, zeroline=False,
                                                   autorange='reversed',
                                                   ticktext=['w1', 'w2', 'w3', 'w4', 'w5', ''],
                                                   tickvals=[0, 1, 2, 3, 4, 5]
                                                   ))
        fig['layout'][f'xaxis{i + 1}'].update(dict(showline=False, zeroline=False, showgrid=False, tickvals=[]))

    fig['layout'][f'xaxis1'].update(dict(showline=False, zeroline=False, showgrid=False,
                                         mirror="allticks",
                                         side="top",
                                         ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                                         tickvals=list(range(12))
                                         ))

    fig.update_layout(title='single year of your life (weeks)', clickmode='event',
                      height=Y*170, width=1400, margin={'t': 40},
                      transition_duration=0,
                      plot_bgcolor='rgba(255,255,255,225)',
                      paper_bgcolor='#fafafa', font={'color': '#444444', 'size': 15})
    return fig

def annual_life_step_months(Z, dates, split=5, form=[4,5]):
    Z = Z.mean(axis=-1).mean(axis=-1) # [Y,M,W,D] --> [Y,M]
    dates = dates[:, :, 2, 5, 0]  # [Y,M,W,D,T] --> [Y,M,W]
    ZZ, Ys = wrap_dates_by(Z, form=form, split=split)
    dates, _ = wrap_dates_by(dates, form=form, split=split)

    fig = subplots.make_subplots(Ys, 1, shared_xaxes=False, shared_yaxes=True, vertical_spacing=0.005,
                                 horizontal_spacing=0.02)
    for y in range(Ys):
        fig.append_trace(go.Heatmap(
            z=np.moveaxis(ZZ[y], (0,1,2), (1,0,2)).reshape(form[0], form[1]*split),
            text=np.moveaxis(dates[y], (0, 1, 2), (1, 0, 2)).reshape(form[0], form[1] * split),
            xgap=3, ygap=3,
            showscale=False,
            coloraxis="coloraxis",
            colorscale=[[0, "rgba(255,225,255,120)"], [0.2, "rgba(220,120,160,150)"],
                        [0.6, "rgba(40,220,150,10)"], [1, "rgba(190,80,255,255)"]]
                                    ),
            row=y + 1, col=1)

    for i in range(Ys):
        fig['layout'][f'yaxis{i + 1}'].update(dict(showline=False, zeroline=False, showgrid=False,
                                                   ticktext=['month-1', 'month-2', 'month-3'],
                                                   tickvals=[0, 1, 2],
                                                   tickmode="array",
                                                   mirror=True,
                                                   autorange='reversed'))
        fig['layout'][f'xaxis{i + 1}'].update(dict(showline=False, zeroline=False, showgrid=False, tickvals=[]))

    fig['layout'][f'xaxis1'].update(dict(showline=False, zeroline=False, showgrid=False,
                                         side="top",
                                         tickangle=25 if split == 5 else 90,
                                         ticktext=['winter', 'spring', 'summer', 'autumn'],
                                         tickvals=[0.4,1.4,2.4,3.4]))

    fig.update_layout(title='single year of your life', clickmode='none',
                      height=Ys*140, width=1400, margin={'t': 40},
                      transition_duration=0, coloraxis={'colorscale':'viridis'},
                      plot_bgcolor='#fff', paper_bgcolor='#fafafa', font={'color': '#444444', 'size': 15})

    return fig

def annual_life_step_years(Z, birthdate, split=5):
    Z = Z.mean(axis=-1).mean(axis=-1).mean(axis=-1) # [Y,M,W,D] --> [Y]
    ZZ = np.zeros(80)

    first_year = int(birthdate.split('-')[0])
    ZZ[:Z.shape[0]] = Z
    ZZ = ZZ.reshape([5, 16])
    fig = go.Figure(go.Heatmap(
        z=ZZ,
        text=[str(y) for y in np.arange(first_year, config['default'].LIFESPAN)],
        xgap=3, ygap=3,
        showscale=False,
        coloraxis="coloraxis",
        colorscale=[[0, "rgba(255,225,255,120)"], [0.2, "rgba(220,120,160,150)"],
                    [0.6, "rgba(40,220,150,10)"], [1, "rgba(190,80,255,255)"]])
    )


    fig.update_layout(title='Every Year of your life', clickmode='none',
                      yaxis=dict(showline=False, zeroline=False,
                                 ticktext=['year-1', 'year-2', 'year-3', 'year-4', 'year-5'],
                                 tickvals=[0,1,2,3,4],
                                 tickmode="array",
                                 showgrid=False, mirror=True, autorange='reversed'),
                      xaxis=dict(showline=False, zeroline=False, showgrid=False, side="top", tickvals=[]),
                      height=300, width=1200, margin={'t': 40},
                      transition_duration=0,
                      plot_bgcolor='#fff', paper_bgcolor='#fafafa', font={'color': '#444444', 'size': 15})

    return fig

"""
def annual_life_step_deprecated(Z):
    H,M,R,C = Z.shape
    fig0 = subplots.make_subplots(1,H, shared_xaxes=True, shared_yaxes=True, horizontal_spacing=0.02)
    for y in range(H):
        fig = subplots.make_subplots(R*C, shared_xaxes=True, shared_yaxes=True, vertical_spacing=0.02, horizontal_spacing=0.02)
        for m in range(M):
            fig.append_trace(go.Heatmap(
                            z=Z[y,m,...],
                            xgap=3, ygap=3, showscale=False,
                            colorscale=[[False, "#eeeeee"], [True, "#76cf63"]]
                                        ),
                            row=m+1, col=1)

        fig.update_yaxes(matches=None)
        fig.update_xaxes(matches=None)
        for i in range(R*C):
            fig['layout'][f'xaxis{i+1}'].update(dict(showline=False, showgrid=False, zeroline=False))
            fig['layout'][f'yaxis{i+1}'].update(dict(showline=False, showgrid=False, zeroline=False, tickmode="array", autorange='reversed'))
        fig0.append_trace(fig.data[0], row=1, col=y+1)


    fig0.update_layout(title='single year of your life', clickmode='event',
                      height=1000, width=1000, margin={'t': 40},
                      plot_bgcolor='#fff', paper_bgcolor='#fafafa', font={'color': '#444444', 'size': 15})
    return fig"
"""