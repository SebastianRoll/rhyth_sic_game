import pandas as pd
from boom_clap.meta import meta as dr_chaos
for chart in dr_chaos['charts']:
    df = pd.DataFrame(chart['notes'], columns=['time', 'note'])
    df.set_index('time', inplace=True)
    df.to_csv('{}.csv'.format(chart['difficulty_coarse']))