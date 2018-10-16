import rhyth_box
import os
import ujson
import utime
import gc

class SelectionScreen:
    DIR_TRACKS = 'tracks'
    def __init__(self, rhythbox):
        self.box = rhythbox
        self.selector = rhythbox.encoder_left

    def do_select(self):
        tracks = os.listdir(self.DIR_TRACKS)
        print(tracks)
        cur_idx = self.selector.value
        self.show_track(tracks[cur_idx])
        while True:
            # utime.sleep_ms(100)
            new_idx = self.selector.value
            if new_idx != cur_idx:
                print("new", new_idx, new_idx % len(tracks))
                cur_idx = new_idx
            # elif self.selector.turned_left:
            #     print("LEFT")
            #     print(self.selector.value, self.selector._value_last_checked)
            #     if cur_idx >= len(tracks)-1:
            #         continue
            #     else:
            #         cur_idx = min(len(tracks)-1, cur_idx + 1)
            else:
                continue
            print(tracks[cur_idx % len(tracks)])
            # self.show_track(tracks[cur_idx % len(tracks)])
            # gc.mem_free()

    def show_track(self, trackname):
        print("Loading", trackname)
        track = Track(self.DIR_TRACKS, trackname)
        # self.box.tft.clear()
        print(track.bg_image)
        self.box.show_image(track.bg_image, trackname)

class Track:
    def __init__(self, dirpath, trackname):
        self.trackname = trackname
        path = "{}/{}".format(dirpath, trackname)
        self.meta = ujson.load(open("{}/meta.json".format(path)))
        self.difficulties = self.meta['charts']
        print(os.listdir(path))
        print([f for f in os.listdir(path) if f.endswith("-bg.jpg")])
        self._bg_image = [f for f in os.listdir(path) if f.endswith("-bg.jpg")][0]

        self.path = path

    @property
    def bg_image(self):
        return "{}/{}".format(self.path, self._bg_image)


r = rhyth_box.RhythBox()
s = SelectionScreen(r)
s.do_select()



# import rhyth_box
# import os
# import ujson
# import utime
# import gc
# r = rhyth_box.RhythBox()
# selector = r.encoder_left
# val = selector.value
# import os
# import time
# img_folder = 'images'
# images = os.listdir(img_folder)
# while True:
#     if selector.value != val:
#         print("kaof")
#         val = selector.value
#         print(val)
#         image = images[val%len(images)]
#         img_path = '{}/{}'.format(img_folder, image)
#         print(img_path)
#         r.show_image(img_path)
#         time.sleep(1)