import pandas as pd
from dr_chaos.meta import dr_chaos
chart = dr_chaos['charts'][2]
df = pd.DataFrame(chart['notes'], columns=['time', 'note'])
df.set_index('time', inplace=True)
df.to_csv('{}.csv'.format(chart['difficulty_coarse']))