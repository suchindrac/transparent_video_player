import sys
import os
import argparse

if sys.version_info[0] < 3:
    import Tkinter as tkinter
else:
    import tkinter

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

gi.require_version('GstVideo', '1.0')
from gi.repository import GstVideo

def set_frame_handle(bus, message, frame_id):
    if not message.get_structure() is None:
        if message.get_structure().get_name() == 'prepare-window-handle':
            display_frame = message.src
            display_frame.set_property('force-aspect-ratio', True)
            display_frame.set_window_handle(frame_id)

def on_key(event):
    global window
    player.get_state(5000000000)
    video_pad = player.emit('get-video-pad', 0)

    caps = video_pad.get_current_caps()
    width = caps.get_structure(0).get_int("width")
    height = caps.get_structure(0).get_int("height")

    width = width.value
    height = height.value

    if event.char == 'i':
        alpha = window.attributes('-alpha')
        window.wm_attributes('-alpha', alpha + 0.05)
    elif event.char == 'd':
        alpha = window.attributes('-alpha')
        window.wm_attributes('-alpha', alpha - 0.05)
    elif event.char == 'q':
        window.destroy()
    elif event.char == 'f':
        window.geometry("%dx%d" % (width, height))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", type = str, required = True, help = "Input file")
    parser.add_argument("-a", "--alpha", type = str, required = True, help = "Initial alpha")

    args = parser.parse_args()
    file_name = args.input_file
    alpha = args.alpha

    window = tkinter.Tk()
    
    window.wait_visibility(window)
    window.wm_attributes('-alpha', alpha)
    window.wm_attributes('-topmost', True)
    window.wm_attributes('-type', 'splash')
    # window.wm_attributes('-type', 'dock')
    window.geometry("640x480")
    window.bind("<Key>", on_key)

    display_frame = tkinter.Frame(window, bg='')
    display_frame.place(relx = 0, rely = 0,
            anchor = tkinter.NW, relwidth = 1, relheight = 1)
    display_frame.pack(expand = tkinter.YES,fill = tkinter.BOTH)
    frame_id = display_frame.winfo_id()

    Gst.init(None)
    GObject.threads_init()

    player = Gst.ElementFactory.make('playbin', None)

    fullname = os.path.abspath(file_name)
    player.set_property('uri', 'file://%s' % fullname)
    player.set_property("audio-sink", None)

    player.set_state(Gst.State.PLAYING)

    bus = player.get_bus()
    bus.enable_sync_message_emission()
    bus.connect('sync-message::element', set_frame_handle, frame_id)

    window.mainloop()
