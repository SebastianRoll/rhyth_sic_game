import pandas as pd
import struct
import importlib
import json
import os


def process_dir(dirpath):
    print(path)
    for dirname, dirnames, filenames in os.walk(dirpath):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            process_track(os.path.join(dirname, subdirname))


def process_track(path):
    print(path)
    json_files = [filename for filename in os.listdir(path) if filename.endswith('.json')]
    for json_file in json_files:
        meta = json.load(open('{path}/{json_file}'.format(path=path, json_file=json_file)))
        # from boom_clap.meta_with_charts import meta as dr_chaos
        newdir = os.path.join(path,json_file.rstrip('.json'))
        if not os.path.exists(newdir):
            os.makedirs(newdir)
        for chart in meta['charts']:
            print(chart['type'])
            if chart['type'] == "dance-double":
                print('skipping dance-double!')
                continue
            df = pd.DataFrame(chart['notes'], columns=['time', 'note'])
            df['time_b'] = df['time'].apply(lambda v: struct.pack('>f', v))
            df['note_b'] = df['note'].apply(lambda v: str.encode(v))
            df['out'] = df.apply(lambda row: row['time_b']+row['note_b'], axis=1)
            with open(os.path.join(newdir,'{}.b'.format(chart['difficulty_coarse'])), 'wb') as f:
                f.writelines(list(df['out'].values))

            # df.set_index('time', inplace=True)
            # df.to_csv(os.path.join(newdir,'{}.csv'.format(chart['difficulty_coarse'])), float_format='%.3f')


def read_all(filepath):
    with open(filepath, 'rb') as f:
        beat = f.read()
        print(beat)
        print(len(beat))
        gen = struct.iter_unpack('>f4c', beat)
        for (ts, *notebytes) in gen:
            print(ts, notebytes)


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

if __name__ == "__main__":
    import sys
    path = sys.argv[1]
    process_dir(path)
    # import fire
    # fire.Fire(process_track)