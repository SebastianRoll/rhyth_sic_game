import pandas as pd
import struct

def process_track():
    from boom_clap.meta_with_charts import meta as dr_chaos
    for chart in dr_chaos['charts']:
        df = pd.DataFrame(chart['notes'], columns=['time', 'note'])
        df['time'] = df['time'].apply(lambda v: struct.pack('>f', v))
        df['note'] = df['note'].apply(lambda v: str.encode(v))
        df['out'] = df.apply(lambda row: row['time']+row['note'], axis=1)
        with open('{}.b'.format(chart['difficulty_coarse']), 'wb') as f:
            f.writelines(list(df['out'].values))

        # df.set_index('time', inplace=True)
        # df.to_csv('{}.csv'.format(chart['difficulty_coarse']), float_format='%.3f')



def read_all(filepath):
    with open(filepath, 'rb') as f:
        beat = f.read()
        print(beat)
        print(len(beat))
        gen = struct.iter_unpack('>f4c', beat)
        for (ts, *notebytes) in gen:
            print(ts, notebytes)
read_all('Challenge.b')
def read_chunks(filepath):
    with open(filepath, 'rb') as f:
        while True:
            beat = f.read(8)
            if not beat:
                break
            print(beat)
            print(len(beat))
            (ts, *notebytes) = struct.unpack('>f4c', beat)
            print(ts, notebytes)