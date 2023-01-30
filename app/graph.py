import plotly.graph_objects as go


def winrate(df):
    colors = ['#5383e8', '#E84057']
    wr = int(df['win'].mean()*100)

    fig = go.Figure(data=[go.Pie(labels=['Win', 'Lose'],
                                 values=[wr, 100-wr],
                                 hole=0.6,
                                 showlegend=False,
                                 sort=False)])
    fig.update_traces(hoverinfo='label+percent',
                      hoverlabel_font_color='white',
                      title=f'{wr}%',
                      title_font_size=40,
                      textposition='none',
                      marker=dict(colors=colors))
    return fig


def champexp_graph(champ_df, df):
    name = champ_df.sort_values('count', ascending=False).reset_index(
        drop=True)['champion'][0]
    exp_timeline = df[df['champion'] == name]['champ_exp'].to_list()
    exp_timeline = sorted(exp_timeline)

    fig = go.Figure(data=go.Scatter(
        y=exp_timeline, line=dict(color='#c89b3c', width=3)))
    fig.update_traces(hoverinfo='y',
                      hoverlabel_font_color='white')
    fig.update_xaxes(visible=False)
    fig.update_layout(title=f'{name} mastery',
                      yaxis_title='Experience')

    return fig
