import curses # pyTUI framework
import time # .sleep() to pace animations and get timestamps for ffmpeg debug logs
import threading # starting download threads
import subprocess # running ffmpeg, ffprobe and mkvmerge
import json # processing ffmpeg's & ffprobe's outputs
import os # setting curses env variable
import tomllib # loading config
import tomlkit # editing config
import inspect # dynamic loading of indexers
import re # parsing media filenames to normalize them
from wcwidth import wcswidth # (attempt to) handle asian characters' width
from pathlib import Path # file discovery, and path handling for composing commands

import fingers # declared indexers
from pioggerella import download_torrent # in-app torrent download client
from coloring import init_colors # xterm colors



# since we aren't expecting any character sequences from the user, have `ESC` instantly quit out of input fields
os.environ.setdefault('ESCDELAY', '1')
# init colors
colors = init_colors()



def print_title(stdscr, l_alignment=None):
    """Creates and returns a `curses.newwin()`, centered at y 11 by default, `l_alignment` can be set"""
    #                                ⠀⠀⠀⠀⠀⠀⠠⣴⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    #                            )   ⠀⠀⣀⣶⡄⠀⠀⠹⣿⣷⣀⠀⠀⢀⣤⣾⣧⠀⠀⠀
    #     )  (    (    (  (   ( /(   ⠀⠀⠈⢿⣿⣆⠀⠀⠈⠻⣿⣿⣿⡿⠿⠋⠁⠀⠀⠀
    #  ( /(  )(   )(   )\))(  )\())  ⠀⠀⠀⠀⢻⣿⡆⠀⠀⠀⠀ ⠀⠀⠀⠀⣀⣤⣶⡀
    #  )(_))(()\ (()\ ((_))\ ((_)\   ⠀⠀⠀⣀⣾⣿⠃⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠟⠋⠁
    # ((_)_  ((_) ((_) (()(_)| |(_)  ⢠⣴⣾⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⢰⣿⠏⠁⠀⠀⠀
    # / _` || '_|| '_|/ _` | | ' \   ⠀⠛⠉⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠘⣿⣷⠀⠀⠀⠀
    # \__,_||_|  |_|  \__, | |_||_|  ⠀⠀⠀⣠⣶⣿⡿⠿⠿⣿⣷⣄⠀⠀⠙⣿⣷⣄⠀⠀
    #                 |___/          ⠀⠀⠈⠹⠟⠉⠀⠀⠀⠈⢻⣿⣦⠀⠀⠈⠛⠀⠀⠀
    #                                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠏⠁⠀⠀⠀⠀⠀⠀

    # get stdscr width to center title_window
    h, w = stdscr.getmaxyx()
    # set `title_window`'s size, and coordinates according to `l_alignment`
    if not l_alignment:
        title_window = curses.newwin(11, 51, 5, max(0, (w-51)//2))
    else:
        title_window = curses.newwin(11, 51, 2, 3)

    # carved by hand on nano, with love
    title_window.addstr(0, 0, "                               ⠀⠀⠀ ⠀⠀⠠⣴⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", colors['anger_emoji_color'])
    title_window.addstr(1, 27, ")", colors['fire_color_third']); title_window.addstr(1, 29, " ⠀⠀ ⣀⣶⡄⠀⠀⠹⣿⣷⣀⠀⠀⢀⣤⣾⣧⠀⠀⠀", colors['anger_emoji_color'])
    title_window.addstr(2, 4, ")", colors['smoke_color_first']); title_window.addstr(2, 7, "(", colors['fire_color_third']); title_window.addstr(2, 12, "(", colors['fire_color_third']); title_window.addstr(2, 17, "(", colors['smoke_color_first']); title_window.addstr(2, 20, "(", colors['smoke_color_first']); title_window.addstr(2, 24, "(", colors['fire_color_third']); title_window.addstr(2, 26, "/", colors['smoke_color_first']); title_window.addstr(2, 27, "(", colors['fire_color_second']); title_window.addstr(2, 29, " ⠀⠀ ⠈⢿⣿⣆⠀⠀⠈⠻⣿⣿⣿⡿⠿⠋⠁⠀⠀⠀", colors['anger_emoji_color'])
    title_window.addstr(3, 1, "(", colors['fire_color_third']); title_window.addstr(3, 3, "/", colors['fire_color_first']); title_window.addstr(3, 4, "(", colors['fire_color_third']); title_window.addstr(3, 7, ")", colors['fire_color_third']); title_window.addstr(3, 8, "(", colors['fire_color_second']); title_window.addstr(3, 12, ")", colors['fire_color_third']); title_window.addstr(3, 13, "(", colors['fire_color_second']); title_window.addstr(3, 17, ")", colors['fire_color_second']); title_window.addstr(3, 18, "\\", colors['fire_color_first']); title_window.addstr(3, 19, ")", colors['smoke_color_first']); title_window.addstr(3, 20, ")", colors['fire_color_third']); title_window.addstr(3, 21, "(", colors['smoke_color_first']); title_window.addstr(3, 24, ")", colors['fire_color_second']); title_window.addstr(3, 25, "\\", colors['fire_color_second']); title_window.addstr(3, 26, "(", colors['fire_color_third']); title_window.addstr(3, 27, ")", colors['smoke_color_first']); title_window.addstr(3, 28, ")", colors['fire_color_first']); title_window.addstr(3, 29, " ⠀⠀⠀⠀ ⢻⣿⡆⠀⠀⠀⠀ ⠀⠀⠀⠀⣀⣤⣶⡀", colors['anger_emoji_color']);
    title_window.addstr(4, 1, ")", colors['smoke_color_first']); title_window.addstr(4, 2, "(", colors['fire_color_first']); title_window.addstr(4, 3, "_", colors['fire_color_second']); title_window.addstr(4, 4, ")", colors['fire_color_first']); title_window.addstr(4, 5, ")", colors['fire_color_third']); title_window.addstr(4, 6, "(", colors['fire_color_third']); title_window.addstr(4, 7, "(", colors['fire_color_second']); title_window.addstr(4, 8, ")", colors['fire_color_first']); title_window.addstr(4, 9, "\\", colors['fire_color_first']); title_window.addstr(4, 11, "(", colors['smoke_color_first']); title_window.addstr(4, 12, "(", colors['fire_color_third']); title_window.addstr(4, 13, ")", colors['fire_color_first']); title_window.addstr(4, 14, "\\", colors['fire_color_first']); title_window.addstr(4, 16, "(", colors['fire_color_second']); title_window.addstr(4, 17, "(", colors['smoke_color_first']); title_window.addstr(4, 18, "_", colors['fire_color_first']); title_window.addstr(4, 19, ")", colors['fire_color_second']); title_window.addstr(4, 20, ")", colors['fire_color_second']); title_window.addstr(4, 21, "\\", colors['fire_color_first']); title_window.addstr(4, 23, "(", colors['fire_color_third']); title_window.addstr(4, 24, "(", colors['fire_color_first']); title_window.addstr(4, 25, "_", colors['fire_color_first']); title_window.addstr(4, 26, ")", colors['fire_color_second']); title_window.addstr(4, 27, "\\", colors['fire_color_third']); title_window.addstr(4, 29, "  ⠀⠀⠀⣀⣾⣿⠃⠀⠀⠀⠀⠀⠀⠀⣠⣾⡿⠟⠋⠁", colors['anger_emoji_color']);
    title_window.addstr(5, 0, "(", colors['fire_color_second']); title_window.addstr(5, 1, "(", colors['fire_color_first']); title_window.addstr(5, 2, "_", colors['title_text_color']); title_window.addstr(5, 3, ")", colors['fire_color_first']); title_window.addstr(5, 4, "_", colors['title_text_color']); title_window.addstr(5, 7, "(", colors['fire_color_second']); title_window.addstr(5, 8, "(", colors['fire_color_first']); title_window.addstr(5, 9, "_", colors['title_text_color']); title_window.addstr(5, 10, ")", colors['fire_color_first']); title_window.addstr(5, 12, "(", colors['fire_color_first']); title_window.addstr(5, 13, "(", colors['fire_color_first']); title_window.addstr(5, 14, "_", colors['title_text_color']); title_window.addstr(5, 15, ")", colors['fire_color_first']); title_window.addstr(5, 17, "(", colors['fire_color_first']); title_window.addstr(5, 18, "(", colors['fire_color_first']); title_window.addstr(5, 19, ")", colors['fire_color_first']); title_window.addstr(5, 20, "(", colors['fire_color_first']); title_window.addstr(5, 21, "_", colors['fire_color_second']); title_window.addstr(5, 22, ")", colors['fire_color_first']); title_window.addstr(5, 23, "| |", colors['title_text_color']); title_window.addstr(5, 26, "(", colors['fire_color_second']); title_window.addstr(5, 27, "_", colors['fire_color_third']); title_window.addstr(5, 28, ")", colors['smoke_color_first']); title_window.addstr(5, 29, "  ⢠⣴⣾⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⢰⣿⠏⠁⠀⠀⠀", colors['anger_emoji_color']);
    title_window.addstr(6, 0, "/ _` || '_|| '_|/ _` | | ' \\ ", colors['title_text_color']); title_window.addstr(6, 29, "  ⠀⠛⠉⠀⠀⠀⢀⣀⣀⡀⠀⠀⠀⠘⣿⣷⠀⠀⠀⠀", colors['anger_emoji_color'])
    title_window.addstr(7, 0, "\\__,_||_|  |_|  \\__, | |_||_|", colors['title_text_color']); title_window.addstr(7, 29, "  ⠀⠀⠀⣠⣶⣿⡿⠿⠿⣿⣷⣄⠀⠀⠙⣿⣷⣄⠀⠀", colors['anger_emoji_color'])
    title_window.addstr(8, 0, "                |___/        ", colors['title_text_color']); title_window.addstr(8, 29, "  ⠀⠀⠈⠹⠟⠉⠀⠀⠀⠈⢻⣿⣦⠀⠀⠈⠛⠀⠀⠀", colors['anger_emoji_color'])
    title_window.addstr(9, 29, "  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠏⠁⠀⠀⠀⠀⠀⠀", colors['anger_emoji_color'])

    title_window.refresh()
    return title_window

def redraw_windows(stdscr, l_alignment=None):
    """Correctly redraws windows. `l_alignment` can be set for `title_window`"""
    # correctly draw windows
    stdscr.noutrefresh() # prime base screen for update
    title_window = print_title(stdscr, l_alignment) # draw title
    title_window.noutrefresh() # prime title_window for update
    curses.doupdate() # update entire physical screen



def add_input_field(stdscr, input_y, input_x, width):
    """Adds a text input field of given width at the specified stdscr coordinates. Returns inputted data on `curses.KEY_ENTER`"""
    cursor_x = 0 # initialize user's cursor position at x 0
    text = ""
    curses.echo() # enable curses to echo characters
    curses.curs_set(1) # enable cursor blinking

    # user input loop
    while True:
        # draw input field, and inputted text as it gets written
        stdscr.addstr(input_y, input_x, "_" * width, colors['input_text_background'])
        stdscr.addstr(input_y, input_x, text, colors['input_text_foreground'])

        # move the user's cursor to the expected position
        stdscr.move(input_y, input_x + cursor_x)
        stdscr.refresh()

        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `KEY_LEFT`, move cursor to the left, while preventing user from going out of bounds
        if key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - 1)

        # on `KEY_RIGHT`, move cursor to the right, while preventing user from going out of bounds
        elif key == curses.KEY_RIGHT:
            cursor_x = min(len(text), cursor_x + 1)

        # if caught key is part of ascii's alphabet characters, append to `text` and modify user's cursor coordinates accordingly
        elif 32 <= key <= 126:
            if len(text) < width:
                text = text[:cursor_x] + chr(key) + text[cursor_x:]
                if cursor_x < width-1:
                    cursor_x += 1

        # on `KEY_BACKSPACE`, delete character to the left of the user's cursor, and modify `text` accordingly
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if cursor_x > 0:
                text = text[:cursor_x - 1] + text[cursor_x:]
                cursor_x -= 1

        # on `KEY_ENTER`, return inputted data, rstripped of '_'
        elif key == curses.KEY_ENTER or key in (10, 13):
            inputted_data = stdscr.instr(input_y, input_x, width).decode().rstrip()
            inputted_data = inputted_data.rstrip('_')
            curses.noecho() # disable curses echo again
            curses.curs_set(0) # disable cursor blinking again
            return inputted_data, False # this False value is to handle quitting during editing of a config parameter

        # on `KEY_RESIZE`, begrudgingly quit out of current menu
        #    handling this is possible, but it would involve accounting for every different menu inside this very function, which would turn out real ugly
        #    so im pretty please asking the user to just settle on a terminal size!
        elif key == curses.KEY_RESIZE:
            stdscr.clear()
            h, w = stdscr.getmaxyx() # sorry, i am NOT handling that
            curses.noecho() # disable curses echo again
            curses.curs_set(0) # disable cursor blinking again
            stdscr.addstr(h//2, (w-3)//2, ">:(", colors['anger_emoji_color'])
            stdscr.getch()
            return None, False # this False value is to handle quitting during editing of a config parameter

        # on `ESC`, quit out of input field and current menu
        elif key == ord('\x1b'):
            curses.noecho() # disable curses echo again
            curses.curs_set(0) # disable cursor blinking again
            return None, True # this False value is to handle quitting during editing of a config parameter


def select_from_list(stdscr, y_pos, max_y, selection_list):
    """Prints scrollable menu from a given list at specified `y_pos`. Returns selected index from given list. `max_y` must be at least 3, i think"""
    # initialize selected idx and scroll offset at 0
    # also calculate how many entries can fit in one refresh
    selected_idx = 0
    scroll_offset = 0
    max_entries = max_y - 2
    h, w = stdscr.getmaxyx()

    # user input loop
    while True:
        # calculate entry's max length before it reaches out of bounds
        entry_max_length = min(max(len(entry) for entry in selection_list), w-6)
        # clear line, and print `^` indicator centered
        stdscr.addstr(y_pos, 0, " "*w)
        stdscr.addstr(y_pos, (entry_max_length+6)//2, "^")

        # split list into visible entries
        visible_entries = selection_list[scroll_offset:scroll_offset+max_entries]

        for visible_i, entry in enumerate(visible_entries):
            actual_visible_i = scroll_offset + visible_i

            # truncate entry's name in case it would be drawn out of bounds
            if len(entry) > w-6:
                entry = entry[:(w-9)] + "..."

            # print entry, highlighted if currently selected or not
            stdscr.addstr(y_pos+1+visible_i, 0, " "*w) # clear entry's line
            if actual_visible_i == selected_idx:
                stdscr.addstr(y_pos+1+visible_i, 3, entry, colors['selected_entry_color'])
            else:
                stdscr.addstr(y_pos+1+visible_i, 3, entry, colors['unselected_entry_color'])

        # clear line, and print `v` indicator centered
        stdscr.addstr(y_pos+max_y, 0, " "*w)
        stdscr.addstr(y_pos+max_y, (entry_max_length+6)//2, "v")

        stdscr.refresh()

        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # handle user scrolling up & down the menu, printing additional entries accorindgly
        if key == curses.KEY_UP:
            if selected_idx > 0:
                selected_idx -= 1
            if selected_idx < scroll_offset:
                scroll_offset = selected_idx
        elif key == curses.KEY_DOWN:
            if selected_idx < len(selection_list)-1:
                selected_idx += 1
            if selected_idx >= scroll_offset+max_entries:
                scroll_offset = selected_idx-max_entries+1

        # on `KEY_ENTER`, return user's selected index
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return selected_idx

        # on `KEY_RESIZE`, begrudgingly quit out of current menu
        #    handling this is possible, but it would involve accounting for every different menu inside this very function, which would turn out real ugly
        #    so im pretty please asking the user to just settle on a terminal size!
        elif key == curses.KEY_RESIZE:
            stdscr.clear()
            h, w = stdscr.getmaxyx() # sorry, i am NOT handling that
            stdscr.addstr(h//2, (w-3)//2, ">:(", colors['anger_emoji_color'])
            stdscr.getch()
            return None

        # on `q`, quit out of input field and current menu
        elif key in [81, 113]:
            return None
            break

        # on `ESC`, quit out of input field and current menu
        elif key == ord('\x1b'):
            return None



def print_entries_table(stdscr, search_results, title_max_length, seeders_max_length, leechers_max_length, completed_max_length, current_idx=0, downloading_list=None):
    """Prints the entries table, including header. Properties max lenght must be passed along with the current selected index. Accounts for handling torrent status printing if list of downloading torrents is passed"""
    header_string = "    Date                  Title " + " "*(title_max_length-5) + "S" + " "*(seeders_max_length) +  "L" + " "*(leechers_max_length) + "C" + " "*(completed_max_length) + "Size"
    stdscr.addstr(16, 3, header_string, colors['header_string_color'])
    border_line = "-" * (4+22+title_max_length+1+seeders_max_length+1+leechers_max_length+1+completed_max_length+9)
    stdscr.addstr(17, 3, border_line, colors['border_line_color'])

    item_n = 0
    global page_n
    for item in search_results:
        title = ""
        seeders = ""
        leechers = ""
        completed = ""
        # padding or "..." truncate
        if len(item['title']) > title_max_length:
            title = item['title'][:title_max_length-3] + "..."
        elif len(item['title']) < title_max_length:
            title = item['title'] + " " * (title_max_length - len(item['title']))
        elif len(item['title']) == title_max_length:
            title = item['title']
        if len(item['seeders']) == seeders_max_length:
            seeders = item['seeders']
        elif len(item['seeders']) < seeders_max_length:
            seeders = item['seeders'] + " " * (seeders_max_length - len(item['seeders']))
        if len(item['leechers']) == leechers_max_length:
            leechers = item['leechers']
        elif len(item['leechers']) < leechers_max_length:
            leechers = item['leechers'] + " " * (leechers_max_length - len(item['leechers']))
        if len(item['completed']) == completed_max_length:
            completed = item['completed']
        elif len(item['completed']) < completed_max_length:
            completed = item['completed'] + " " * (completed_max_length - len(item['completed']))
        # printing entry
        torrent_selected = False
        if downloading_list: # if any torrent has begun downloading
            for downloading_item in downloading_list:
                if downloading_item['completed'] == False and downloading_item['page_index'] == item_n and downloading_item['page_n'] == page_n: # , and item_n is not completed: avoid printing date, as that is handled by upper function
                    torrent_selected = True
                    stdscr.addstr(18+item_n, 3, "    ", colors['unselected_entry_color'])
                    stdscr.addstr(18+item_n, 3+4+21, " "+title, colors['unselected_entry_color'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title), " "+seeders, colors['seeders_text_color'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders), " "+leechers, colors['leechers_text_color'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers), " "+completed, colors['unselected_entry_softer'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers)+len(completed)+1, " "+item['size'], colors['unselected_entry_softer'])
                elif downloading_item['completed'] == True and downloading_item['page_index'] == item_n and downloading_item['page_n'] == page_n: # . and item_n is completed, print completion message instead of date
                    torrent_selected = True
                    stdscr.addstr(18+item_n, 3, " ●➤ ", colors['unselected_entry_color'])
                    stdscr.addstr(18+item_n, 3+4, "Completed!", colors['downloaded_torrent_color'])
                    stdscr.addstr(18+item_n, 3+4+21, " "+title, colors['unselected_entry_color'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title), " "+seeders, colors['seeders_text_color'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders), " "+leechers, colors['leechers_text_color'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers), " "+completed, colors['unselected_entry_softer'])
                    stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers)+len(completed)+1, " "+item['size'], colors['unselected_entry_softer'])
        if torrent_selected == True:
            item_n += 1
            continue
        if item_n == current_idx:
            stdscr.addstr(18+item_n, 3, " ●➤ ", colors['selected_entry_color'])
            stdscr.addstr(18+item_n, 3+4, item['pubDate'], colors['selected_entry_color'])
            stdscr.addstr(18+item_n, 3+4+21, " "+title, colors['selected_entry_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title), " "+seeders, colors['selected_entry_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders), " "+leechers, colors['selected_entry_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers), " "+completed, colors['selected_entry_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers)+len(completed)+1, " "+item['size'], colors['selected_entry_color'])
        else:
            stdscr.addstr(18+item_n, 3, " ○  ", colors['unselected_entry_color'])
            stdscr.addstr(18+item_n, 3+4, item['pubDate'], colors['unselected_entry_softer'])
            stdscr.addstr(18+item_n, 3+4+21, " "+title, colors['unselected_entry_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title), " "+seeders, colors['seeders_text_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders), " "+leechers, colors['leechers_text_color'])
            stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers), " "+completed, colors['unselected_entry_softer'])
            stdscr.addstr(18+item_n, 3+4+22+len(title)+1+len(seeders)+1+len(leechers)+len(completed)+1, " "+item['size'], colors['unselected_entry_softer'])
        item_n += 1

    redraw_windows(stdscr, l_alignment="left-aligned")

def create_torrent_status(): # callback factory to retrieve each torrent's progress info
    """Generates callbacks to be passed to the `download_torrent` function in order to receive torrent status updates"""
    torrent_status = {
        "progress": "0.00%",
        "download_speed": "0kB/s",
        "peers": "0"
    }
    def get_torrent_status(status):
        torrent_status.update(status)

    return torrent_status, get_torrent_status

# set current page and thread pause variables, global to avoid ugly passing fuckery
pause_thread = threading.Event()
pause_thread.set()
page_n = 0
def download_torrent_print_status(infohash, download_path, stdscr, y, x, downloading_torrent, stop_torrent_status_printing):
    """Starts a thread which initiates torrent download and prints live status data on the correct entries table page. Printing thread can be stopped by setting and passing `stop_torrent_status_printing`. The torrent will continue downloading until app is quit"""
    global page_n
    h, w = stdscr.getmaxyx()

    # spinny spin!
    spinner_frames = "⠂⠒⠲⠴⠤⠄⠄⠤⢤⣠⣀⡀⡀⣀⢀⢀⣀⣄⡤⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒"
    spinner_i = 0

    # create callback to receive torrent's progress info
    torrent_status, get_torrent_status = create_torrent_status()

    # start torrent download thread
    torrent_status_thread = threading.Thread(
        target=download_torrent,
        args=(infohash, download_path, get_torrent_status),
        daemon=True
    )
    torrent_status_thread.start()

    # if on the current page, display live torrent progress and spinner animation
    while torrent_status_thread.is_alive() and not stop_torrent_status_printing.is_set():
        if downloading_torrent['page_n'] == page_n:
            pause_thread.wait() # pause printing thread while `download_menu` is drawing to screen
            spinner_frame = spinner_frames[spinner_i % len(spinner_frames)]
            spinner_i += 1
            stdscr.addstr(y, x, " "*24)
            stdscr.addstr(y, x, spinner_frame, colors['downloading_torrent_color'])
            stdscr.addstr(y, x+2, torrent_status['progress'], colors['downloading_torrent_color'])
            stdscr.addstr(y, x+2+8, torrent_status['download_speed'], colors['downloading_torrent_color'])
            stdscr.addstr(y, x+2+8+11, torrent_status['peers']+"ጰ", colors['downloading_torrent_color'])
            redraw_windows(stdscr, l_alignment="left-aligned")
            time.sleep(0.1)
    # once downloaded, mark torrent as completed and exit
    downloading_torrent['completed'] = True

def download_menu(stdscr, y_pos, max_y, config, indexer):
    """Prints download menu at specified stdscr coordinates; takes care of search field, search results table and starting download threads. `max_y` has to be of at least 12"""
    # clear screen, check terminal size, draw title
    stdscr.clear()
    min_downm_h = 35
    min_downm_w = 60
    check_terminal_size(stdscr, min_downm_h, min_downm_w)
    h, w = stdscr.getmaxyx()
    redraw_windows(stdscr, l_alignment="left-aligned")

    global page_n

    # draw input field
    stdscr.addstr(y_pos, 3, "Search: ", colors['entry_text_color'])
    stdscr.addstr(y_pos+1, 11, "'q' to quit search", colors['quit_search_color'])
    search_query, d = add_input_field(stdscr, y_pos, 11, w-25) # d for discard
    # handle quitting during input
    if search_query is None:
        return
    # make query to indexer
    search_results = indexer(search_query)
    # handle no results being found
    if search_results is None:
        stdscr.addstr(16, 15, "No results found :(", colors['anger_emoji_color'])
        stdscr.getch()
        return

    # set current page as first
    page_n = 0

    # split entries into multiple pages
    max_fit_entries = max_y-11
    fitted_search_results = []
    for i in range(0, len(search_results), max_fit_entries):
        single_page = search_results[i:i + max_fit_entries]
        fitted_search_results.append(single_page)

    # set current index as first
    current_idx = 0

    # create lists to account for current search results' torrents, and initialize progress printing threads stop event when menu is quit
    downloading_torrents = []
    torrent_status_printing_threads = []
    stop_torrent_status_printing = threading.Event()

    # user input loop
    while True:
        # calculate actual `search_results` index, by accounting for current page
        search_results_actual_index = current_idx + max_fit_entries*page_n


        # draw cycle

        # pause torrent status printing so it doesn't interfere with drawing the menu again
        pause_thread.clear()

        # clear screen
        stdscr.clear()

        # redraw search field with its input
        stdscr.addstr(y_pos, 3, "Search: ", colors['entry_text_color'])
        stdscr.addstr(y_pos, 11, "_" * 48, colors['input_text_background'])
        stdscr.addstr(y_pos, 11, search_query, colors['input_text_foreground'])
        stdscr.addstr(y_pos+1, 11, "'q' to quit search", colors['quit_search_color'])

        # calculate max width for each column, and draw entries table
        title_max_length = (min(max(wcswidth(item["title"]) for item in search_results)+1,w-58)) # i think i found out for once why the code needs a random +1, but la scala looks nice so
        seeders_max_length = (min(max(len(item["seeders"]) for item in search_results),w-58))
        leechers_max_length = (min(max(len(item["leechers"]) for item in search_results),w-58))
        completed_max_length = (min(max(len(item["completed"]) for item in search_results),w-58))
        print_entries_table(stdscr, fitted_search_results[page_n], title_max_length, seeders_max_length, leechers_max_length, completed_max_length, current_idx, downloading_torrents)

        # draw page indicator
        pages_indicator = "< " + str(page_n+1) + " / " + str(len(fitted_search_results)) + " >"
        stdscr.addstr(y_pos+max_y-5, (4+title_max_length+seeders_max_length+leechers_max_length+completed_max_length+33)//2, pages_indicator)

        # selected entry full title line wrap
        selected_string = "Selected: " + search_results[search_results_actual_index]['title']
        if len(selected_string) > w-6:
            lines = []
            while selected_string:
                lines.append(selected_string[:w-6])
                selected_string = selected_string[w-6:]
            i = 0
            for line in lines:
                stdscr.addstr(y_pos+max_y-3+i, 3, line, colors['selected_full_entry'])
                i += 1
                if y_pos+i == max_y-2:
                    break
        else:
            stdscr.addstr(y_pos+max_y-3, 3, selected_string, colors['selected_full_entry'])

        redraw_windows(stdscr, l_alignment="left-aligned")
        # unpause torrent status printing
        pause_thread.set()


        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `KEY_UP`, move selection up, while updating the index, and preventing the user from going out of bounds
        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
            if downloading_torrents: # avoid selecting downloading torrents
                for downloading in downloading_torrents:
                    if downloading['page_n'] == page_n and downloading['page_index'] == current_idx and current_idx > 0:
                        current_idx -= 1
                    elif downloading['page_n'] == page_n and downloading['page_index'] == current_idx and current_idx == 0:
                        current_idx += 1

        # on `KEY_DOWN`, move selection down, while updating the index, and preventing the user from going out of bounds
        elif key == curses.KEY_DOWN and current_idx < len(fitted_search_results[0])-1:
            current_idx += 1
            if page_n == len(fitted_search_results)-1 and current_idx == len(fitted_search_results[-1]): # avoid going below number of entries on last page
                current_idx -= 1
            if downloading_torrents: # avoid selecting downloading torrents
                for downloading in downloading_torrents:
                    if downloading['page_n'] == page_n and downloading['page_index'] == current_idx and len(fitted_search_results)-1 > 0:
                        current_idx += 1
                    elif downloading['page_n'] == page_n and downloading['page_index'] == current_idx and len(fitted_search_results)-1 == 0:
                        current_idx -= 1

        # on `KEY_LEFT`, move to previous page, if not out of bounds
        elif key == curses.KEY_LEFT and page_n > 0:
            page_n -= 1

        # on `KEY_RIGHT`, move to next page, if not out of bounds, while moving selection up accorindgly if the last page has less entries than the previous page
        elif key == curses.KEY_RIGHT and page_n < len(fitted_search_results)-1:
            page_n += 1
            if page_n == len(fitted_search_results)-1 and current_idx > len(fitted_search_results[-1])-1:
                current_idx = len(fitted_search_results[-1])-1

        # on `KEY_ENTER`, start torrent download thread
        elif key == curses.KEY_ENTER or key in [10,13]:
            # get infohash from current selected index
            infohash = search_results[search_results_actual_index]['infoHash']

            # initialize torrent info dictionary
            downloading_torrent = {
                "page_index": current_idx,
                "page_n": page_n,
                "completed": False
            }

            # start torrent download thread and append to monitoring lists
            torrent_download_thread = threading.Thread(
                target=download_torrent_print_status,
                args=(infohash, config['download_path']['value'], stdscr, 18+current_idx, 4, downloading_torrent, stop_torrent_status_printing),
                daemon=True
            )
            torrent_download_thread.start()
            torrent_status_printing_threads.append(torrent_download_thread)
            downloading_torrents.append(downloading_torrent)

        # on `KEY_RESIZE`, check if terminal size is sufficient, and update screen's h & w for dynamic resizing
        elif key == curses.KEY_RESIZE:
            check_terminal_size(stdscr, max_y+18, 60)
            h, w = stdscr.getmaxyx()

        # on `q`, quit and go back to main menu
        elif key in [81, 113]:
            stop_torrent_status_printing.set()
            for thread in torrent_status_printing_threads:
                thread.join(timeout=1)
            return



def get_streams_info(media_file, wanted_languages, media_file_path):
    """Parses given file's media streams and returns two lists of dictionaries containing audio and subtitle id's and titles of those that match wanted_languages"""
    # compose ffprobe command
    ffprobe_command = [
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=index,codec_type,codec_name:stream_tags=language,title', '-of', 'json', Path(media_file_path)/(media_file+'.mkv')
    ]
    # execute and get json output
    found_streams = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
    found_streams = json.loads(found_streams.stdout)

    # initialize streams lists
    audio_streams = []
    subtitle_streams = []

    # parsing streams found in file
    for stream in found_streams["streams"]:
        # get stream's type to match to either audio or subtitle stream
        stream_type = stream.get("codec_type")

        # get stream's tags, and check against `wanted_languages`
        tags = stream.get("tags", {})
        language = tags.get("language", "").lower()
        if language not in wanted_languages:
            continue

        # compose info dictionary with the stream's metadata we're interested in
        stream_metadata = {
            "id": stream["index"],
            "language": language,
            "title": tags.get("title", "")
        }

        # append dictionary to either audio or subtitle streams list
        if stream_type == "audio":
            audio_streams.append(stream_metadata)
        elif stream_type == "subtitle":
            subtitle_streams.append(stream_metadata)

    return audio_streams, subtitle_streams

def rename_media_output(media_input, audio_streams, subtitle_streams):
    """Given an input media file name and found wanted_languages streams; strips release groups, quality tags and the such to format it as following: `{Title} - {SxxExx} {Quality} {audio_streams} (sub {subtitle_streams}).mkv`"""
    media_rename = media_input

    # strip release group (first [])
    media_rename = re.sub(r"^\s*\[[^\]]+\]\s*", "", media_rename, count=1)

    # get resolution
    resolution_match = re.search(r"(?:\(\s*)?(2160p|1440p|1080p|900p|720p|576p|480p|360p)(?:\s*\))?", media_rename, flags=re.IGNORECASE)
    resolution = resolution_match.group(1).lower() if resolution_match else ""

    # strip '.' and '_' separators
    media_rename = re.sub(r"[._]+", " ", media_rename)
    media_rename = re.sub(r"\s+", " ", media_rename).strip()

    # strip hashes or trailing release groups
    media_rename = re.sub(r"\s*\[[0-9A-Fa-f]{6,}\]\s*$", "", media_rename)

    # get SxxExx if present
    episode_match = re.search(
        r"\b("
        r"S\d{1,2}(?:E\d{1,2}(?:[-_]E?\d{1,2})?)?"
        r"|"
        r"\d{1,2}x\d{1,2}"
        r")\b",
        media_rename,
        flags=re.IGNORECASE,
    )
    episode = ""
    if episode_match:
        episode = episode_match.group(1).upper()
        # normalize 1x03 -> S01E03
        if re.fullmatch(r"\d{1,2}x\d{1,2}", episode, re.IGNORECASE):
            season, ep = re.split(r"x", episode, flags=re.IGNORECASE)
            episode = f"S{int(season):02d}E{int(ep):02d}"

    # get rid of quality/metadata and misplaced release group
    media_rename = re.sub(r"\s*\[[^\]]*\]", "", media_rename)
    metadata_pattern = (
        r"WEB[- ]?DL|WEB[- ]?Rip|WEBRip|"
        r"Blu[- ]?Ray|BDRip|BRRip|"
        r"HDTV|DVDRip|DVDScr|"
        r"REMUX|REMASTERED|"
        r"HDR|HDR10\+?|DV|Dolby Vision|"
        r"x26[45]|H\.?26[45]|HEVC|AVC|"
        r"AAC|AC3|EAC3|DDP|DTS|TRUEHD|FLAC|"
        r"10bit|8bit|"
        r"NF|AMZN|DSNP|CR|ATVP|"
        r"MultiSub|Multi|Dual[\s-]?Audio"
    )
    media_rename = re.sub(rf"\b(?:{metadata_pattern})\b", "", media_rename, flags=re.IGNORECASE)

    # strip resolution
    if resolution:
        media_rename = re.sub(
            rf"\(?\s*{re.escape(resolution)}\s*\)?",
            "",
            media_rename,
            flags=re.IGNORECASE,
        )

    # maintain episode if stripped alongside metadata
    if episode:
        # maintain title before episode
        ep_match = re.search(
            re.escape(episode),
            media_rename,
            flags=re.IGNORECASE,
        )
        if ep_match:
            title = media_rename[: ep_match.end()].strip()
        else:
            title = media_rename
    else:
        title = media_rename

    # get rid of additional tags
    tags_match = [
        r"\b(?:PROPER|REPACK|RERIP|INTERNAL|LIMITED|COMPLETE|UNCUT)\b",
        r"\b(?:THEATRICAL|EXTENDED|UNRATED|DIRECTORS?\s+CUT)\b",
        r"\b(?:IMAX|3D)\b",
        r"\b(?:MULTI|DUAL[\s-]?AUDIO)\b",
    ]
    for pattern in tags_match:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # clean additional whitespace
    title = re.sub(r"\s+", " ", title).strip(" -")

    # replace episode marker with normalized one
    if episode:
        title_without_episode = re.sub(
            rf"\s*{re.escape(episode)}\s*$",
            "",
            title,
            flags=re.IGNORECASE,
        ).strip()
        title = f"{title_without_episode} {episode}".strip()

    # build languages (found audio and subtitle streams) part
    audio_part = ""
    for stream in audio_streams:
        audio_part += stream['language']+" "

    subtitle_part = ""
    if subtitle_streams:
        subtitle_part = "(sub "
        for stream in subtitle_streams:
            subtitle_part += stream['language']+" "
        subtitle_part = subtitle_part.rstrip()
        subtitle_part += ")"
    else:
        subtitle_part = ""

    # assemble final naming
    result = f"{title} {resolution}"
    result = result.strip()
    if audio_part:
        result += f" {audio_part}"
    result += subtitle_part + ".mkv"

    return result



def transcode_menu_quality(stdscr, config):
    """Prints simple transcode menu, takes care of media selection and ffmpeg for (S)ingle and (B)atch transcodes"""
    # clear screen, check terminal size, draw title
    stdscr.clear()
    min_qualm_h = 28
    min_qualm_w = 95
    check_terminal_size(stdscr, min_qualm_h, min_qualm_w)
    h, w = stdscr.getmaxyx()
    redraw_windows(stdscr, l_alignment="left-aligned")

    # prompt if (S)ingle or (B)atch
    stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors['header_string_color'])
    stdscr.addstr(14, 3, "'q' to quit transcode", colors['quit_search_color'])

    # prompt user input loop
    key = None
    while True:
        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `s`, `b` or `q`; (S)ingle, (B)atch or (Q)uit
        if key in [83, 115] or key in [66, 98] or key in [81, 113]:
            break

        # on `KEY_RESIZE`, check if terminal size is sufficient, and update screen's h & w for dynamic resizing
        elif key == curses.KEY_RESIZE:
            check_terminal_size(stdscr, min_qualm_h, min_qualm_w)
            h, w, = stdscr.getmaxyx()

            # draw cycle
            redraw_windows(stdscr, l_alignment="left-aligned")
            stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors['header_string_color'])
            stdscr.addstr(14, 3, "'q' to quit transcode", colors['quit_search_color'])
    # on `q`, quit and go back to main menu
    if key in [81, 113]:
        return

    # compose download path as per config
    download_path = Path(config['download_path']['value'])
    # initialize aut-aut list
    flister_list = []

    # if (S)ingle, parse download path for files into alphabetically ordered list
    if key in [83, 115]:
        n_found_files = 0
        for file in download_path.iterdir():
            if file.is_file() and file.suffix.lower() == ".mkv":
                flister_list.append(file.stem)
                n_found_files += 1
        # if no files were found, warn user and go back to main menu
        if n_found_files == 0:
            stdscr.addstr(16, 7, "No files present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)

    # if (B)atch, parse download path for folders into alphabetically ordered list
    elif key in [66, 98]:
        # parse download_path for folders into alphabetically ordered list
        n_found_folders = 0
        for folder in download_path.iterdir():
            if folder.is_dir():
                flister_list.append(folder.name)
                n_found_folders += 1
        # if no folders were found, warn user and go back to main menu
        if n_found_folders == 0:
            stdscr.addstr(16, 7, "No folder present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)


    # allow user to select flister (file/folder)
    selected_media_idx = select_from_list(stdscr, 16, (h-16)//3, flister_list)
    if selected_media_idx is None: # handling quitting during media selection
        return
    selected_media = flister_list[selected_media_idx]

    # if (S)ingle, execute ffmpeg command, move & rename once
    if key in [83, 115]:
        # get file's stream info
        audio_streams, subtitle_streams = get_streams_info(selected_media, config['wanted_languages']['value'], config['download_path']['value']) # even though we're not stripping unwanted languages here, still rename in a sane way with what we're interested in
        # parse filename to generate normalized one
        renamed = rename_media_output(selected_media, audio_streams, subtitle_streams)
        # check if resulting file is already present, if so, warn user and return to main menu
        if (Path(config['transcode_path']['value'])/renamed).is_file():
            stdscr.addstr(16, 7, "File already present!", colors['anger_emoji_color'])
            stdscr.getch()
            return

        # display initial line to show progress, including the resulting filename
        stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(16, 3, "Transcoding…", colors['unselected_entry_softer'])
        stdscr.addstr(16, 3+15, renamed, colors['unselected_entry_color'])
        stdscr.refresh()

        # get media file's number of frames, to allow the user to guesstimate time left when ffmpeg's progress fails to show speed
        n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", Path(config['download_path']['value'])/(selected_media+'.mkv')], capture_output=True, text=True, check=True).stdout.strip()
        # compose ffmpeg command
        ffmpeg_command = [
            'ffmpeg', *config['transcode_input_accel']['value'], '-i', Path(config['download_path']['value'])/(selected_media+'.mkv'), '-map', '0',
            '-c:v', *config['transcode_video_args']['value'],
            '-c:a', *config['transcode_audio_args']['value'],
            '-c:s', 'copy',
            '-progress', 'pipe:1',
            Path(config['transcode_path']['value'])/renamed
        ]

        # initialize writing output to file, if debug log is enabled in config
        if config['enable_ffmpeg_debug_log']['value'] == 'y':
            with open("ffmpeg-log", "a") as f:
                f.write('\n\n\n' + time.strftime("%Y-%m-%d_%H:%M.%S") + '\n')
        log_file = (
            open("ffmpeg-log", "a", encoding="utf-8")
            if config['enable_ffmpeg_debug_log']['value'] == 'y'
            else subprocess.DEVNULL
        )

        # start and wait for command to finish
        try:
            # run command in subprocess, while passing stderr to `log_file`
            proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)

            # assemble progress dictionary
            progress = {}
            for line in proc.stdout:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    progress[k] = v
                # print outputted progress
                if line == "progress=continue":
                    progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                    stdscr.addstr(17, 3, progress_string, colors['unselected_entry_softer'])
                    stdscr.refresh()
            proc.wait()

        # once command has terminated, close `log_file` if present, and notify user
        finally:
            if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(18, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.getch()


    # if (B)atch, execute ffmpeg command, move & rename recursively in new transcoded folder
    elif key in [66, 98]:
        # compose input folder's path
        input_folder = Path(config['download_path']['value'])/selected_media
        # get files list
        files = sorted(file for file in input_folder.iterdir() if file.is_file() and file.suffix.lower() == ".mkv")
        total = len(files)
        # get (first) file's stream info for renaming
        folder_audio_streams, folder_subtitle_streams = get_streams_info(files[0].stem, config['wanted_languages']['value'], input_folder)
        renamed_folder = rename_media_output(selected_media, folder_audio_streams, folder_subtitle_streams)
        output_folder = Path(config['transcode_path']['value'])/renamed_folder
        # check if resulting folder is already present, if so, warn user and return to main menu
       	if output_folder.is_dir():
            stdscr.addstr(16, 7, "Folder already present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        # create resulting folder with normalized name in transcode path
        output_folder.mkdir()


        # iterate ffmpeg for every file in list
        for i, file in enumerate(files, start=1):
            # get file's stream info
            audio_streams, subtitle_streams = get_streams_info(file.stem, config['wanted_languages']['value'], input_folder)
            # parse filename to generate normalized one
            renamed = rename_media_output(file.stem, audio_streams, subtitle_streams)

            # display initial line to show progress, including the resulting filename
            stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
            stdscr.addstr(16, 3, "Transcoding…", colors['unselected_entry_softer'])
            # also display amount of files to go through left
            i_progress_string = f"{i}/{total}"
            stdscr.addstr(16, 16, i_progress_string, colors['unselected_entry_softer'])
            stdscr.addstr(16, 3+20, renamed, colors['unselected_entry_color'])
            stdscr.refresh()

            # get media file's number of frames, to allow the user to guesstimate time left when ffmpeg's progress fails to show speed
            n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", file], capture_output=True, text=True, check=True).stdout.strip()
            # compose ffmpeg command
            ffmpeg_command = [
                'ffmpeg', *config['transcode_input_accel']['value'], '-i', file, '-map', '0',
                '-c:v', *config['transcode_video_args']['value'],
                '-c:a', *config['transcode_audio_args']['value'],
                '-c:s', 'copy',
                '-progress', 'pipe:1',
                output_folder/renamed
            ]

            # initialize writing output to file, if debug log is enabled in config
            if config['enable_ffmpeg_debug_log']['value'] == 'y':
                with open("ffmpeg-log", "a") as f:
                    f.write('\n\n\n' + time.strftime("%Y-%m-%d_%H:%M.%S") + '\n')
            log_file = (
                open("ffmpeg-log", "a", encoding="utf-8")
                if config['enable_ffmpeg_debug_log']['value'] == 'y'
                else subprocess.DEVNULL
            )

            # start and wait for command to finish
            try:
                # run command in subprocess, while passing stderr to `log_file`
                proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)

                # assemble progress dictionary
                progress = {}
                for line in proc.stdout:
                    line = line.strip()
                    if "=" in line: # assemble progress dictionary
                        k, v = line.split("=", 1)
                        progress[k] = v
                    # print outputted progress
                    if line == "progress=continue":
                        progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                        stdscr.addstr(17, 3, progress_string, colors['unselected_entry_softer'])
                        stdscr.refresh()
                proc.wait()

            # once command has terminated, close `log_file` if present, and notify user
            finally:
                if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(18, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.getch()



def stream_selection(stdscr, y_pos, streams_list, prompt_string):
    """Allow user to select streams from given list"""
    # prompt user for streams to keep
    h, w = stdscr.getmaxyx()
    stdscr.addstr(y_pos, 3, " "*w*(((h-16)//3)+1))
    stdscr.addstr(y_pos, 3, prompt_string, colors['header_string_color'])
    # initialize current index as first
    current_idx = 0
    # initialize indexes to be removed list
    indexes_to_remove = []

    # calculate beginning y_pos for stream entries
    starting_y = y_pos+1
    # user input loop
    while True:
        # draw cycle, printing currently selected and enbaled/disabled streams accordingly
        for idx, streams in enumerate(streams_list):
            if idx in indexes_to_remove:
                stdscr.addstr(starting_y+idx, 3, "□", colors['unselected_entry_softer'])
            else:
                stdscr.addstr(starting_y+idx, 3, "■", colors['unselected_entry_softer'])
            stream_string = str(streams_list[idx]['id']) + ': ' + streams_list[idx]['language'] + ' (' + streams_list[idx]['title'] + ')'
            if idx == current_idx:
                stdscr.addstr(starting_y+idx, 5, stream_string, colors['selected_menu_color'])
            else:
                stdscr.addstr(starting_y+idx, 5, stream_string, colors['entry_text_color'])
        stdscr.refresh()

        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `KEY_UP`, move selection up, while updating the index, and preventing the user from going out of bounds
        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1

        # on `KEY_DOWN`, move selection down, while updating the index, and preventing the user from going out of bounds
        elif key == curses.KEY_DOWN and current_idx < len(streams_list)-1:
            current_idx += 1

        # on KEY_SPACE, select/unselect stream on current index
        elif key == ord(' '): # space to (un)select
            if current_idx in indexes_to_remove:
                indexes_to_remove.remove(current_idx)
            else:
                indexes_to_remove.append(current_idx)

        # on `KEY_ENTER`, break out of selection loop
        elif key == curses.KEY_ENTER or key in [10,13]:
            break

        # on `KEY_RESIZE`, begrudgingly quit out of current menu
        #    handling this is possible, but it would involve accounting for every different stream inside this very function, which would turn out real ugly
        #    so im pretty please asking the user to just settle on a terminal size!
        elif key == curses.KEY_RESIZE:
            stdscr.clear()
            h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
            stdscr.addstr(h//2, (w-3)//2, ">:(", colors['anger_emoji_color'])
            stdscr.getch()
            return

        # on `q`, quit out of input field and current menu
        elif key in [81, 113]:
            return None

    # remove streams to remove
    selected_streams = []
    for idx, stream in enumerate(streams_list):
        if idx not in indexes_to_remove:
            selected_streams.append(streams_list[idx])

    return selected_streams

def transcode_menu_language(stdscr, config):
    """Prints transcode menu that allows merging of audio and subtitle streams. Takes care of media and streams selection, and ffmpeg for (S)ingle and (B)atch merges"""
    # clear srceen, check terminal size, draw title
    stdscr.clear()
    min_langm_h = 38
    min_langm_w = 95
    check_terminal_size(stdscr, min_langm_h, min_langm_h)
    h, w = stdscr.getmaxyx()

    # prompt user input loop
    key = None
    to_transcode = True
    while True:
        # draw cycle, reprint prompt and if to transcode accordingly
        stdscr.clear()
        redraw_windows(stdscr, l_alignment="left-aligned")
        # prompt if (S)ingle or (B)atch
        stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors['header_string_color'])
        stdscr.addstr(14, 3, "'q' to quit transcode", colors['quit_search_color'])
        if to_transcode == True:
            stdscr.addstr(13, 29, "■", colors['unselected_entry_softer'])
            stdscr.addstr(13, 31, "Transcode", colors["seeders_text_color"])
            stdscr.refresh()
        elif to_transcode == False:
            stdscr.addstr(13, 29, "□", colors['unselected_entry_softer'])
            stdscr.addstr(13, 31, "Transcode", colors["leechers_text_color"])
        stdscr.addstr(14, 28, "(E)nable/(D)", colors['unselected_entry_softer'])

        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `e`, (E)nable encoding
        if key in [69, 101]:
            to_transcode = True

        # on `d`, (D)isable encoding
        elif key in [68, 100]:
            to_transcode = False

        # on `s`, `b`, or `q``; (S)ingle, (B)atch or (Q)uit
        elif key in [83, 115] or key in [66, 98] or key in [81, 113]: # (S)ingle or (B)atch or (Q)uit
            stdscr.addstr(14, 28, " "*12) # (clear `"(E)nable/(D)"`)
            break

        # on `KEY_RESIZE`, check if terminal size is sufficient, and update screen's h & w for dynamic resizing
        elif key == curses.KEY_RESIZE:
            check_terminal_size(stdscr, min_langm_h, min_langm_h)
            h, w = stdscr.getmaxyx()
    # on `q`, quit and go back to main menu
    if key in [81, 113]:
        return

    # compose download path as per config
    download_path = Path(config['download_path']['value'])
    # initialize aut-aut list
    flister_list = []

    # if (S)ingle, parse download path for files into alphabetically ordered list
    if key in [83, 115]:
        n_found_files = 0
        for file in download_path.iterdir():
            if file.is_file() and file.suffix.lower() == ".mkv":
                flister_list.append(file.stem)
                n_found_files += 1
        # if no files were found, warn user and go back to main menu
        if n_found_files == 0:
            stdscr.addstr(16, 7, "No files present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)
        folder_or_file = 'file'

    # if (B)atch, parse download path for folders into alphabetically ordered list
    elif key in [66, 98]:
        n_found_folders = 0
        for folder in download_path.iterdir():
            if folder.is_dir():
                flister_list.append(folder.name)
                n_found_folders += 1
        # if no folders were found, warn user and go back to main menu
        if n_found_folders == 0:
            stdscr.addstr(16, 7, "No folder present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)
        folder_or_file = 'folder'


    # if (S)ingle, prompt media and streams selection for both files, and move & rename once
    if key in [83, 115]:
        # allow user to select the first file
        first_selected_media_idx = select_from_list(stdscr, 16, (h-16)//3, flister_list)
        if first_selected_media_idx is None: # handling quitting during media selection
            return
        first_selected_media = flister_list[first_selected_media_idx]

        # get first file's stream info
        first_media_audio_streams, first_media_subtitle_streams = get_streams_info(first_selected_media, config['wanted_languages']['value'], config['download_path']['value'])

        # allow first file's audio streams selection
        first_selected_audio_streams = stream_selection(stdscr, 16, first_media_audio_streams, "Select audio streams to keep:")
        if first_selected_audio_streams is None: # handling quitting during stream selection
            return

        # allow first file's subtitle streams selection
        first_selected_subtitle_streams = stream_selection(stdscr, 16, first_media_subtitle_streams, "Select subtitle streams to keep:")
       	if first_selected_subtitle_streams is None: # handling quitting during stream selection
            return

        # display selected streams

        stdscr.addstr(16, 0, " "*w*(((h-16)//3)+1))

        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_subtitle_streams)

        stdscr.addstr(16, 3, "Selected streams for first file:", colors['unselected_entry_softer'])
        stdscr.addstr(17, 3, f"Audio: {audio_selection}", colors['entry_text_color'])
        stdscr.addstr(18, 3, f"Subtitle: {subtitle_selection}", colors['entry_text_color'])
        # truncate media filename if it reaches out of bounds
        first_selected_media_display = first_selected_media
        if len(first_selected_media_display) > w-12:
            first_selected_media_display = first_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(19, 3, f"From: {first_selected_media_display}", colors['quit_search_color'])


        # allow user to select the second file
        stdscr.addstr(21, 3, "Select second file:", colors['header_string_color'])
        second_selected_media_idx = select_from_list(stdscr, 22, (h-16)//3, flister_list)
        if second_selected_media_idx is None: # handling quitting during media selection
            return
        second_selected_media = flister_list[second_selected_media_idx]

        stdscr.addstr(22, 0, " "*w*(((h-16)//3)+2))

        # get second file's stream info
        second_media_audio_streams, second_media_subtitle_streams = get_streams_info(second_selected_media, config['wanted_languages']['value'], config['download_path']['value'])

        # allow second file's audio streams selection
        second_selected_audio_streams = stream_selection(stdscr, 21, second_media_audio_streams, "Select audio streams to keep:")
       	if second_selected_audio_streams is None: # handling quitting during stream selection
            return

        # allow second file's subtitle streams selection
        second_selected_subtitle_streams = stream_selection(stdscr, 21, second_media_subtitle_streams, "Select subtitle streams to keep:")
       	if second_selected_subtitle_streams is None: # handling quitting during stream selection
            return

        # display selected streams

        stdscr.addstr(21, 0, " "*w*(((h-16)//3)+2))

        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_subtitle_streams)

        stdscr.addstr(21, 3, "Selected streams for second file:", colors['unselected_entry_softer'])
        stdscr.addstr(22, 3, f"Audio: {audio_selection}", colors['entry_text_color'])
        stdscr.addstr(23, 3, f"Subtitle: {subtitle_selection}", colors['entry_text_color'])
        # truncate media filename if it reaches out of bounds
        second_selected_media_display = second_selected_media
        if len(second_selected_media_display) > w-12:
            second_selected_media_display = second_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(24, 3, f"From: {second_selected_media_display}", colors['quit_search_color'])


        # merge selected streams into final list of streams to keep
        merge_audio_streams = first_selected_audio_streams + second_selected_audio_streams
        merge_subtitle_streams = first_selected_subtitle_streams + second_selected_subtitle_streams
        # normalize resulting media name using the kept streams
        merge_renamed = rename_media_output(first_selected_media, merge_audio_streams, merge_subtitle_streams)

        # display final resulting output, and prompt for confirmation
        stdscr.addstr(26, 3, "Merging into:", colors['unselected_entry_softer'])
        stdscr.addstr(26, 29, "Enter to confirm", colors['header_string_color'])
        stdscr.addstr(27, 3, merge_renamed, colors['entry_text_color'])
        stdscr.addstr(28, 3, "*This assumes you're merging stuff that makes sense, no checks", colors['quit_search_color'])
        stdscr.addstr(29, 3, "*Final filename and video stream is taken from the first input", colors['quit_search_color'])

        # user input loop
        while True:
            # get user's input; the loop runs each time a key is caught
            key = stdscr.getch()

            # on `KEY_ENTER`, break while loop and confirm merge
            if key == curses.KEY_ENTER or key in [10,13]:
                stdscr.addstr(26, 29, " "*16) # (clear `"Enter to confirm:"``)
                break

            # on `KEY_RESIZE`, begrudgingly quit out of current menu
            #    handling this is possible, but it would involve accounting for every different stream inside this very function, which would turn out real ugly
            #    so im pretty please asking the user to just settle on a terminal size!
            elif key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors['anger_emoji_color'])
                stdscr.getch()
                return

            # on `q`, quit and go back to main menu
            elif key in [81, 113]:
                return


        # check if resulting file is already present, if so, warn user and return to main menu
        if (Path(config['transcode_path']['value'])/merge_renamed).is_file():
            stdscr.addstr(31, 8, "File already present!", colors['anger_emoji_color'])
            stdscr.getch()
            return

        # display initial line to show progress, including the resulting filename
        stdscr.addstr(31, 3, "Transcoding…", colors['unselected_entry_softer'])
        stdscr.addstr(31, 3+15, merge_renamed, colors['unselected_entry_color'])
        stdscr.refresh()

        # compose ffmpeg command's stream mapping from selected streams
        streams_mapping = ["-map", "0:0"]
        # audio streams from first file
        for stream in first_selected_audio_streams:
            streams_mapping += ["-map", f"0:{stream['id']}"]
        # subtitle streams from first file
        for stream in first_selected_subtitle_streams:
            streams_mapping += ["-map", f"0:{stream['id']}"]
        # audio streams from second file
        for stream in second_selected_audio_streams:
            streams_mapping += ["-map", f"1:{stream['id']}"]
        # subtitle streams from second file
        for stream in second_selected_subtitle_streams:
            streams_mapping += ["-map", f"1:{stream['id']}"]

        # get media file's number of frames, to allow the user to guesstimate time left when ffmpeg's progress fails to show speed
        n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", Path(config['download_path']['value'])/(first_selected_media+'.mkv')], capture_output=True, text=True, check=True).stdout.strip()
        # compose ffmpeg command, with transcode args if to_transcode
        ffmpeg_command = []
        if to_transcode:
            ffmpeg_command = [
                'ffmpeg', *config['transcode_input_accel']['value'],
                '-i', Path(config['download_path']['value'])/(first_selected_media+'.mkv'),
                '-i', Path(config['download_path']['value'])/(second_selected_media+'.mkv'),
                '-c:v', *config['transcode_video_args']['value'],
                '-c:a', *config['transcode_audio_args']['value'],
                *streams_mapping,
                '-progress', 'pipe:1',
                Path(config['transcode_path']['value'])/merge_renamed
            ]
        else:
            ffmpeg_command = [
                'ffmpeg',
                '-i', Path(config['download_path']['value'])/(first_selected_media+'.mkv'), # could this make use of 'transcode_input_accel'? #TODO
                '-i', Path(config['download_path']['value'])/(second_selected_media+'.mkv'),
                *streams_mapping,
                '-progress', 'pipe:1',
                Path(config['transcode_path']['value'])/merge_renamed
            ]


        # initialize writing output to file, if debug log is enabled in config
        if config['enable_ffmpeg_debug_log']['value'] == 'y':
            with open("ffmpeg-log", "a") as f:
                f.write('\n\n\n' + time.strftime("%Y-%m-%d_%H:%M.%S") + '\n')
        log_file = (
            open("ffmpeg-log", "a", encoding="utf-8")
            if config['enable_ffmpeg_debug_log']['value'] == 'y'
            else subprocess.DEVNULL
        )

        # start and wait for command to finish
        try:
            # run command in subprocess, while passing stderr to `log_file`
            proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)

            # assemble progress dictionary
            progress = {}
            for line in proc.stdout:
                line = line.strip()
                if "=" in line: # assemble progress dictionary
                    k, v = line.split("=", 1)
                    progress[k] = v
                # print outputted progress
                if line == "progress=continue":
                    progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                    stdscr.addstr(32, 3, progress_string, colors['unselected_entry_softer'])
                    stdscr.refresh()
            proc.wait()

        # once command has terminated, close `log_file` if present, and notify user
        finally:
            if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(33, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.refresh()
        stdscr.getch()

    # if (B)atch, prompt media and streams selection for both folders, and move & rename once recursively in new transcoded folder
    elif key in [66, 98]:
        # allow user to select the first folder
        first_selected_media_idx = select_from_list(stdscr, 16, (h-16)//3, flister_list)
        if first_selected_media_idx is None: # handling quitting during media selection
            return
        first_selected_media = flister_list[first_selected_media_idx]

        # compose first input folder path as per config
        first_input_folder = Path(config['download_path']['value'])/first_selected_media
        # get files list
        first_files = sorted(file for file in first_input_folder.iterdir() if file.is_file() and file.suffix.lower() == ".mkv")
        first_total_files = len(first_files)

        # get first folder's (first file's) stream info
        first_folder_audio_streams, first_folder_subtitle_streams = get_streams_info(first_files[0].stem, config['wanted_languages']['value'], config['download_path']['value']+'/'+first_selected_media)

        # allow first file's (first file's) audio streams selection
        first_selected_audio_streams = stream_selection(stdscr, 16, first_folder_audio_streams, "Select audio streams to keep:")
       	if first_selected_audio_streams is None: # handling quitting during stream selection
            return

        # allow first file's subtitle streams selection
        first_selected_subtitle_streams = stream_selection(stdscr, 16, first_folder_subtitle_streams, "Select subtitle streams to keep:")
       	if first_selected_subtitle_streams is None: # handling quitting during stream selection
            return

        # display selected streams

        stdscr.addstr(16, 0, " "*w*(((h-16)//3)+2))

        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_subtitle_streams)

        stdscr.addstr(16, 3, "Selected streams for first file:", colors['unselected_entry_softer'])
        stdscr.addstr(17, 3, f"Audio: {audio_selection}", colors['entry_text_color'])
        stdscr.addstr(18, 3, f"Subtitle: {subtitle_selection}", colors['entry_text_color'])
        # truncate folder filename if it reaches out of bounds
        first_selected_media_display = first_selected_media
        if len(first_selected_media_display) > w-12:
            first_selected_media_display = first_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(19, 3, f"From: {first_selected_media_display}", colors['quit_search_color'])


        # allow user to select the second folder
        stdscr.addstr(21, 3, "Select second file:", colors['header_string_color'])
        second_selected_media_idx = select_from_list(stdscr, 22, (h-16)//3, flister_list)
        if second_selected_media_idx is None: # handling quitting during media selection
            return
        second_selected_media = flister_list[second_selected_media_idx]

        stdscr.addstr(22, 0, " "*w*(((h-16)//3)+2))

        # compose second input folder path as per config
        second_input_folder = Path(config['download_path']['value'])/second_selected_media
        # get files list
        second_files = sorted(file for file in second_input_folder.iterdir() if file.is_file() and file.suffix.lower() == ".mkv")
        second_total_files = len(second_files)

        # get the second folder's (first file's) stream info
        second_folder_audio_streams, second_folder_subtitle_streams = get_streams_info(second_files[0].stem, config['wanted_languages']['value'], config['download_path']['value']+'/'+second_selected_media)

        # allow second folder's (first file's) audio streams selection
        second_selected_audio_streams = stream_selection(stdscr, 21, second_folder_audio_streams, "Select audio streams to keep:")
       	if second_selected_audio_streams is None: # handling quitting during stream selection
            return

        # allow second folder's subtitle streams selection
        second_selected_subtitle_streams = stream_selection(stdscr, 21, second_folder_subtitle_streams, "Select subtitle streams to keep:")
       	if second_selected_subtitle_streams is None: # handling quitting during stream selection
            return

        # display selected streams

        stdscr.addstr(21, 0, " "*w*(((h-16)//3)+1))

        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_subtitle_streams)

        stdscr.addstr(21, 3, "Selected streams for second file:", colors['unselected_entry_softer'])
        stdscr.addstr(22, 3, f"Audio: {audio_selection}", colors['entry_text_color'])
        stdscr.addstr(23, 3, f"Subtitle: {subtitle_selection}", colors['entry_text_color'])
        # truncate folder filename if it reaches out of bounds
        second_selected_media_display = second_selected_media
        if len(second_selected_media_display) > w-12:
            second_selected_media_display = second_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(24, 3, f"From: {second_selected_media_display}", colors['quit_search_color'])


        # merge selected streams into final list of streams to kepp
        merge_audio_streams = first_selected_audio_streams + second_selected_audio_streams
        merge_subtitle_streams = first_selected_subtitle_streams + second_selected_subtitle_streams
        # normalize resutling media name using the kept streams
        merge_renamed_folder = rename_media_output(first_selected_media, merge_audio_streams, merge_subtitle_streams).rstrip('.mkv')

        # display final resulting output, and prompt for confirmation
        stdscr.addstr(26, 3, "Merging into:", colors['unselected_entry_softer'])
        stdscr.addstr(26, 29, "Enter to confirm", colors['header_string_color'])
        stdscr.addstr(27, 3, merge_renamed_folder, colors['entry_text_color'])
        stdscr.addstr(28, 3, "*This assumes you're merging stuff that makes sense, no checks", colors['quit_search_color'])
        stdscr.addstr(29, 3, "*Final filename and video stream is taken from the first input", colors['quit_search_color'])
        if w < 148-6: # line wrap for doctrine
            stdscr.addstr(30, 3, "*Assuming that files in both folders can be alphabetically sorted in the same order and that streams are consistent in each of them. Praise thy lord"[:w-7]+"-", colors['quit_search_color'])
            stdscr.addstr(31, 4, "*Assuming that files in both folders can be alphabetically sorted in the same order and that streams are consistent in each of them. Praise thy lord"[w-7:], colors['quit_search_color'])
        else:
            stdscr.addstr(30, 3, "*Assuming that files in both folders can be alphabetically sorted in the same order and that streams are consistent in each of them. Praise thy lord", colors['quit_search_color'])

        # user input loop
        while True:
            # get user's input; the loop runs each time a key is caught
            key = stdscr.getch()

            # on `KEY_ENTER`, break while loop and confirm merge
            if key == curses.KEY_ENTER or key in [10,13]:
                stdscr.addstr(26, 29, " "*16) # (clear `"Enter to confirm:"``)
                break

            # on `KEY_RESIZE`, begrudgingly quit out of current menu
            #    handling this is possible, but it would involve accounting for every different stream inside this very function, which would turn out real ugly
            #    so im pretty please asking the user to just settle on a terminal size!
            elif key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors['anger_emoji_color'])
                stdscr.getch()
                return

            # on `q`, quit and go back to main menu
            elif key in [81, 113]:
                return

        # compose resulting folder path
        merge_output_folder = Path(config['transcode_path']['value'])/merge_renamed_folder
        # , and check if already present, if so, warn user and return to main menu
        if merge_output_folder.is_dir():
            stdscr.addstr(31, 7, "Folder already present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        # otherwire create the folder in transcode_path
        merge_output_folder.mkdir()


        # compose ffmpeg command's stream mapping from selected streams
        streams_mapping = ["-map", "0:0"]
        # audio streams from first file
        for stream in first_selected_audio_streams:
            streams_mapping += ["-map", f"0:{stream['id']}?"] # ? --> make map optional; better to miss a stream than the entire file
        # subtitle streams from first file
        for stream in first_selected_subtitle_streams:
            streams_mapping += ["-map", f"0:{stream['id']}?"] #                          (since we're transcoding every file off the first of each folder's selection)
        # audio streams from second file
        for stream in second_selected_audio_streams:
            streams_mapping += ["-map", f"1:{stream['id']}?"] #                          told ya to make a prayer
        # subtitle streams from second file
        for stream in second_selected_subtitle_streams:
            streams_mapping += ["-map", f"1:{stream['id']}?"] #                          okay the comments are symmetric now


        # iterate ffmpeg proc for every file in first folder
        for i, file in enumerate(first_files, start=1):
            # generate normalized resutling filename
            merge_renamed = rename_media_output(file.stem, merge_audio_streams, merge_subtitle_streams)

            # display intial line to show progress, including the resulting filename
            stdscr.addstr(32, 3, " "*w*(((h-16)//3)+2))
            stdscr.addstr(32, 3, "Transcoding…", colors['unselected_entry_softer'])
            # also display amount of files to go through left
            i_progress_string = f"{i}/{first_total_files}"
            stdscr.addstr(32, 16, i_progress_string, colors['unselected_entry_softer'])
            stdscr.addstr(32, 3+20, merge_renamed, colors['unselected_entry_color'])
            stdscr.refresh()

            # get media file's number of frames, to allow the user to guesstimate time left when ffmpeg's progress fails to show speed
            n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", file], capture_output=True, text=True, check=True).stdout.strip()
            # compose ffmpeg command, with transcode ags if to_transcode
            ffmpeg_command = []
            if to_transcode:
                ffmpeg_command = [
                    'ffmpeg', *config['transcode_input_accel']['value'],
                    '-i', file,
                    '-i', second_files[i-1], # i is the human facing index for displaying progress, so gotta -1
                    '-c:v', *config['transcode_video_args']['value'],
                    '-c:a', *config['transcode_audio_args']['value'],
                    *streams_mapping,
                    '-progress', 'pipe:1',
                    merge_output_folder/merge_renamed
                 ]
            else:
                ffmpeg_command = [
                    'ffmpeg',
                    '-i', file, # could this make use of 'transcode_input_accel'? #TODO
                    '-i', second_files[i-1], # i is the human facing index for displaying progress, so gotta -1
                    *streams_mapping,
                    '-progress', 'pipe:1',
                    merge_output_folder/merge_renamed
                ]


            # initialize writing output to file, if debug log is enabled in config
            if config['enable_ffmpeg_debug_log']['value'] == 'y':
                with open("ffmpeg-log", "a") as f:
                    f.write('\n\n\n' + time.strftime("%Y-%m-%d_%H:%M.%S") + '\n')
            log_file = (
                open("ffmpeg-log", "a", encoding="utf-8")
                if config['enable_ffmpeg_debug_log']['value'] == 'y'
                else subprocess.DEVNULL
            )

            # start and wait for command to finish
            try:
                # run command in subprocess, while passing stderr to `log_file`
                proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)

                # assemble progress dictionary
                progress = {}
                for line in proc.stdout:
                    line = line.strip()
                    if "=" in line: # assemble progress dictionary
                        k, v = line.split("=", 1)
                        progress[k] = v
                        # print outputted progress
                    if line == "progress=continue":
                        progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                        stdscr.addstr(33, 3, progress_string, colors['unselected_entry_softer'])
                        stdscr.refresh()
                proc.wait()

            # once command has terminated, close `log_file` if present, and notify user
            finally:
                if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(34, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.refresh()
        stdscr.getch()



def embed_subtitle_menu(stdscr, config):
    """Prints menu to embed subtitle track into mkv file"""
    # clear screen, check terminal size, draw title
    stdscr.clear()
    min_embedm_h = 35
    min_embedm_w = 60
    check_terminal_size(stdscr, min_embedm_h, min_embedm_w)
    h, w = stdscr.getmaxyx()
    redraw_windows(stdscr, l_alignment="left-aligned")

    # prompt for file location
    stdscr.addstr(13, 3, "Select .mkv file from (D)ownload or (T)ranscode path?", colors['header_string_color'])
    stdscr.addstr(14, 3, "'q' to quit embedding", colors['quit_search_color'])
    key = None
    # prompt user input loop
    while True:
        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `d`, `t` or `q`; (D)ownload, (T)ranscode or (Q)uit
        if key in [68, 100] or key in [84, 116] or key in [81, 113]:
            break

        # on `KEY_RESIZE`, check if terminal size is sufficient, and update screen's h & w for dynamic resizing
        elif key == curses.KEY_RESIZE:
            check_terminal_size(stdscr, min_embedm_h, min_embedm_w)
            h, w, = stdscr.getmaxyx()

            # draw cycle
            stdscr.clear()
            redraw_windows(stdscr, l_alignment="left-aligned")
            stdscr.addstr(13, 3, "Select .mkv file from (D)ownload or (T)ranscode path?", colors['header_string_color'])
            stdscr.addstr(14, 3, "'q' to quit embedding", colors['quit_search_color'])

    # on `q`, quit and go back to main menu
    if key in [81, 113]: return

    # set files' path according to selection
    files_path = None
    if key in [68, 100]: # (D)ownload
        files_path = Path(config['download_path']['value'])
    elif key in [84, 116]: # (T)ranscode
        files_path = Path(config['transcode_path']['value'])

    # parse files_path for files into alphabetically ordered list
    files_list = []
    n_found_files = 0
    for file in files_path.iterdir():
        if file.is_file() and file.suffix.lower() == ".mkv":
            files_list.append(file.stem)
            n_found_files += 1
    # if no files were found, warn user and go back to main menu
    if n_found_files == 0:
        stdscr.addstr(16, 7, "No files present!", colors['anger_emoji_color'])
        stdscr.getch()
        return
    files_list = sorted(files_list)

    # allow user to select file
    selected_media_idx = select_from_list(stdscr, 16, (h-16)//3, files_list)
    if selected_media_idx is None: # handling quitting during media selection
        return
    selected_media = files_list[selected_media_idx]


    # allow user to select subtitle track
    stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
    stdscr.addstr(16, 3, "Select subtitle track to embed:", colors['header_string_color'])
    # compose subs path as per config
    subs_path = Path(config['subtitles_path']['value'])

    # parse subs path for into alphabetically ordered list
    subs_list = []
    n_found_files = 0
    for file in subs_path.iterdir():
        if file.is_file():
           subs_list.append(file.stem)
           n_found_files += 1
    # if no files were found, warn user and go back to main menu
    if n_found_files == 0:
        stdscr.addstr(18, 7, "No files present!", colors['anger_emoji_color'])
        stdscr.getch()
        return
    subs_list = sorted(subs_list)

    # allow user to select file
    selected_sub_idx = select_from_list(stdscr, 17, (h-16)//4, subs_list)
    if selected_sub_idx is None: # handling quitting during media selection
        return

    # generate and parse file list also containing file extension
    subs_ext_list = []
    for files in subs_path.iterdir():
        if file.is_file():
            subs_ext_list.append(file)
    subs_ext_list = sorted(subs_ext_list)
    selected_sub = subs_ext_list[selected_sub_idx] # that's me!


    # display selected media
    stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
    stdscr.addstr(16, 3, "Selected .mkv file:", colors['unselected_entry_softer'])
    # truncate media name if out of bounds
    selected_media_display = selected_media
    if len(selected_media_display) > w-6:
        selected_media_display = selected_media_display[:(w-9)] + "..."
    stdscr.addstr(17, 3, selected_media_display, colors['entry_text_color'])

    # display selected subtitle track
    stdscr.addstr(18, 3, "Selected subtitle track to embed:", colors['unselected_entry_softer'])
    # truncate subtitle track filename if out of bounds
    selected_sub_display = subs_list[selected_sub_idx]
    if len(selected_sub_display) > w-6:
        selected_sub_display = selected_sub_display[:(w-9)] + "..."
    stdscr.addstr(19, 3, selected_sub_display, colors['entry_text_color'])

    # prompt user for sub title // haha, get it?
    stdscr.addstr(21, 3, "Specify subtitle track title:", colors['header_string_color'])
    sub_title, d = add_input_field(stdscr, 22, 3, 28) # d for discard
    if sub_title is None: # handling quitting during input
        return

    # prompt user for subtitle language, and confirm
    stdscr.addstr(24, 3, "Specify subtitle track language to confirm:", colors['header_string_color'])
    sub_lang, d = add_input_field(stdscr, 25, 3, 3) # d for discard
    if sub_lang is None: # handling quitting during input
        return

    # rename media accordingly:
    output_mkv = selected_media
    if sub_lang != "":
        # if not normalized, just append +sub {sub_lang}
        if key in [68, 100]: # (D)ownload
            output_mkv = selected_media+ f" +sub {sub_lang}.mkv"
        # if normalized, append {sub_lang} in (+sub lang1 lang2 ...)
        elif key in [84, 116]: # (T)ranscode
            output_mkv = selected_media[:-1] + f" {sub_lang}).mkv"
    else: # if user didn't specify sub language, leave as is
        output_mkv = selected_media+".mkv"
    # check if resulting file is already present, if so, warn user and return to main menu
    if (files_path/output_mkv).is_file():
        stdscr.addstr(27, 5, "File already present!", colors['anger_emoji_color'])
        stdscr.getch()
        return

    # compose ffmpeg command (actually mkvmerge)
    #    ideally, i would've wanted to keep ffmpeg (and ffprobe) as the only command dependecy,
    #    but i could not get embedding a subtitle track working consinstently with it,
    #    while mkvmerge is much more straightforward and proper for this use case
    #
    #    still keeping my best attempt at ffmpeg for this commented here though, in case someone wants to try figure it out:
    #
    #    n_sub_streams = len(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index', '-of', 'json', files_path/selected_media], capture_output=True, text=True, check=True).stdout).get('streams', []))
    #
    #    ffmpeg_command = [
    #       'ffmpeg', '-i', files_path/selected_media, '-i', Path(config['subtitles_path']['value']/selected_sub),
    #       '-map', '0', '-map', '1:0', '-c', 'copy',
    #       '-c:s', {'.ass': 'ass', '.ssa': 'ssa', '.srt': 'subrip', '.vtt': 'webvtt'}.get(Path(selected_sub).suffix.lower()),
    #       f'-metadata:s:s:{n_sub_streams}', f'language={sub_lang}',
    #       f'-metadata:s:s:{n_sub_streams}', f'title={sub_title}',
    #       files_path/output_mkv
    #    ]

    # compose mkvmerge command
    selected_media += ".mkv"
    mkvmerge_command = [
        'mkvmerge', '-o', str(files_path/output_mkv), str(files_path/selected_media),
        '--language', f'0:{sub_lang}', '--track-name', f'0:{sub_title}',
        str(Path(config['subtitles_path']['value'])/selected_sub)
    ]

    # initialize writing output to file, if debug log is enabled in config
    if config['enable_ffmpeg_debug_log']['value'] == 'y':
        with open("ffmpeg-log", "a") as f:
            f.write('\n\n\n' + time.strftime("%Y-%m-%d_%H:%M.%S") + '\n')
    log_file = (
        open("ffmpeg-log", "a", encoding="utf-8")
        if config['enable_ffmpeg_debug_log']['value'] == 'y'
        else subprocess.DEVNULL
    )

    # start and wait for command to finish
    try:
        # run command in subprocess, while passing stdout to `log_file`
        process = subprocess.Popen(mkvmerge_command, stdout=log_file, stderr=subprocess.DEVNULL) # (ffmpeg would use stderr)

        # dottus
        dots = [".", "..", "..."]
        i = 0
        while process.poll() is None:
            stdscr.addstr(27, 5, dots[i % len(dots)], colors['unselected_entry_softer'])
            stdscr.refresh()
            i += 1
            time.sleep(0.2)
            stdscr.addstr(27, 6, " "*2)
        process.wait()

    # once command has terminated, close `log_file` if present, and notify user
    finally:
        if log_file is not subprocess.DEVNULL: log_file.close()
    stdscr.addstr(27, 5, "Done!", colors['downloaded_torrent_color'])
    stdscr.getch()



def load_indexers():
    """Loads indexers from `fingers.py`. These can be accessed by indexer['name'](search_query)"""
    # initialize indexers list
    indexers = {}
    # parse functions of `fingers.py`,
    for indexer, function in inspect.getmembers(fingers, inspect.isfunction):
        # and ignore those that start with "_", allowing the writing of helper methods
        if not indexer.startswith("_"):
            indexers[indexer] = function

    return indexers

def indexers_menu(stdscr, indexers, indexer):
    """Prints indexer selection menu, returns the user selected indexer"""
    # clear screen, check terminal size, draw title
    stdscr.clear()
    min_indexerm_h = 30
    min_indexerm_w = 60
    check_terminal_size(stdscr, min_indexerm_h, min_indexerm_w)
    h, w = stdscr.getmaxyx()
    redraw_windows(stdscr)

    # set current index as first
    current_idx = 0

    # user input loop
    while True:
        # draw cycle, printing currently selected and enabled indexers accordingly
        stdscr.clear()
        redraw_windows(stdscr)
        for idx, row in enumerate(indexers):
            x = w//2 - len(row)//2
            y = max((16+idx*2), ((h-6)//2 - len(indexers)//2 + idx*2))
            if idx == current_idx:
                stdscr.addstr(y, x, row, colors['selected_menu_color'])
            else:
                if indexers[row] == indexer:
                    stdscr.addstr(y, x, row, colors["seeders_text_color"])
                else:
                    stdscr.addstr(y, x, row, colors['leechers_text_color'])

        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `KEY_UP`, move selection up, while updating the index, and preventing the user from going out of bounds
        if key == curses.KEY_UP:
            if current_idx == -1:
                current_idx = 0
            elif current_idx > 0:
                current_idx -= 1

        # on `KEY_DOWN`, move selection DOWN, while updating the index, and preventing the user from going out of bounds
        elif key == curses.KEY_DOWN and current_idx < len(indexers)-1:
            current_idx += 1

        # on `KEY_ENTER`, return selected indexer and go back to main menu
        elif key == curses.KEY_ENTER or key in [10,13]:
            indexer = list(indexers.values())[current_idx]
            return indexer

        # on `KEY_RESIZE`, check if terminal size is sufficient, and update screen's h & w for dynamic resizing
        if key == curses.KEY_RESIZE:
            check_terminal_size(stdscr, min_indexerm_h, min_indexerm_w)
            h, w = stdscr.getmaxyx()

        # on `q`, quit and go back to main menu
        elif key in [81, 113]:
            return indexer

        # draw cycle, printing currently selected and enabled indexers accordingly
        stdscr.clear()
        redraw_windows(stdscr)
        for idx, row in enumerate(indexers):
            x = w//2 - len(row)//2
            y = max((16+idx*2), ((h-6)//2 - len(indexers)//2 + idx*2))
            if idx == current_idx:
                stdscr.addstr(y, x, row, colors['selected_menu_color'])
            else:
                if indexers[row] == indexer:
                    stdscr.addstr(y, x, row, colors["seeders_text_color"])
                else:
                    stdscr.addstr(y, x, row, colors['leechers_text_color'])



def load_config(config_file):
    """Loads config, returns dict for each parameter containing its values, definitions and example configurations"""
    # initialize list of config dicts, and load config's toml
    config = {}
    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    with open(config_file, "r", encoding="utf-8") as f:
        # initialize dict values as blank
        str_def = ""
        str_def2 = ""
        list_ex = []
        str_name = ""

        # parsing loop to discover config parameters and their values
        for line in f:
            line = line.strip()

            # if the paramater's comment begins with "@def", assign `str_def`
            if line.startswith("# @def "):
                str_def = line[7:].strip()
                continue

            # if the parameter's comment begins with "@def2", assign `str_def2`
            if line.startswith("# @def2 "):
                str_def2 = line[8:].strip()
                continue

            # if the parameter's comment begins with "@ex", append to `list_ex`
            if line.startswith("# @ex "):
                list_ex.append(line[6:].strip())
                continue

            # ignore non-defining comments
            if line.startswith("# "):
                continue

            # once value declaration has been reached, assign everything found to parameter's dict
            if "=" in line:
                str_name = line.split("=", 1)[0].strip() # i feel like this will break if the user ever needs to set an ffmpeg argument containing '='. *mmmhh*

                config[str_name] = {
                    "name": str_name,
                    "value": config[str_name],
                    "def": str_def,
                    "def2": str_def2,
                    "ex": list_ex,
                }

            # reset dict values each parsing loop
            str_def = ""
            str_def2 = ""
            list_ex = []
            str_name = ""

    return config

def edit_config_param(config_file, parameter, value):
    """Sets parameter with given value in config file"""
    # read config's toml
    with open(config_file, "r", encoding="utf-8") as f:
        config_doc = tomlkit.parse(f.read())

    # if given value is a list, split into strings
    if isinstance(config_doc[parameter], list):
        value = value.split()
    # save value to config's toml
    config_doc[parameter] = value

    # write change to config
    with open(config_file, "w", encoding="utf-8") as f:
        f.write(config_doc.as_string())

def edit_config_menu(stdscr, config, config_file):
    """Prints menu to edit config parameters from tui"""
    # clear screen, check terminal size, draw title
    stdscr.clear()
    min_confm_h = 46
    min_confm_w = 113
    if check_terminal_size(stdscr, min_confm_h, min_confm_w, ">:("):
        return # in this case, we return to main menu if size isn't sufficient, avoiding bad headaches for everyone
    h, w = stdscr.getmaxyx()
    redraw_windows(stdscr, l_alignment="left-aligned")

    # first display of current parameters; `download_path`
    stdscr.addstr(13, 0, config['download_path']['def'], colors['config_display_def'])
    stdscr.addstr(14, 0, config['download_path']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
    stdscr.addstr(15, 0, config['download_path']['ex'][0], colors['config_display_exs'])

    # first display of current parameters; `transcode_path`
    stdscr.addstr(17, 0, config['transcode_path']['def'], colors['config_display_def'])
    stdscr.addstr(18, 0, config['transcode_path']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
    stdscr.addstr(19, 0, config['transcode_path']['ex'][0], colors['config_display_exs'])

    # first display of current parameters; `subtitles_path`
    stdscr.addstr(21, 0, config['subtitles_path']['def'], colors['config_display_def'])
    stdscr.addstr(22, 0, config['subtitles_path']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
    stdscr.addstr(23, 0, config['subtitles_path']['ex'][0], colors['config_display_exs'])

    # first display of current parameters; `wanted_languages`
    stdscr.addstr(26, 0, config['wanted_languages']['def'], colors['config_display_def'])
    stdscr.addstr(27, 0, config['wanted_languages']['def2'], colors['config_display_def'])
    stdscr.addstr(28, 0, config['wanted_languages']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
    stdscr.addstr(29, 0, config['wanted_languages']['ex'][0], colors['config_display_exs'])

    stdscr.addstr(32, 0, "Transcode Options: ffmpeg arguments for video and audio codecs to transcode media files into", colors['config_display_def'])

    # first display of current parameters; `transcode_input_accel`
    stdscr.addstr(34, 0, config['transcode_input_accel']['def'], colors['config_display_def'])
    stdscr.addstr(35, 0, config['transcode_input_accel']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
    stdscr.addstr(36, 0, config['transcode_input_accel']['ex'][0], colors['config_display_exs'])

    # first display of current parameters; `transcode_video_args`
    stdscr.addstr(38, 0, config['transcode_video_args']['def'], colors['config_display_def'])
    stdscr.addstr(39, 0, config['transcode_video_args']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
    stdscr.addstr(40, 0, config['transcode_video_args']['ex'][0], colors['config_display_exs'])
    stdscr.addstr(41, 0, config['transcode_video_args']['ex'][1], colors['config_display_exs'])

    # first display of current parameters; `transcode_audio_args`
    stdscr.addstr(43, 0, config['transcode_audio_args']['def'], colors['config_display_def'])
    stdscr.addstr(44, 0, config['transcode_audio_args']['name']+' = ', colors['header_string_color'])
    stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
    stdscr.addstr(45, 0, config['transcode_audio_args']['ex'][0], colors['config_display_exs'])

    # set current index out of bounds, so no parameter is selected at first
    current_idx = -1
    # user input loop
    while True:
        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `KEY_UP`, move selection up (or set to first, if first input), while updating the index, and preventing the user from going out of bounds
        if key == curses.KEY_UP:
            if current_idx == -1:
                current_idx = 0
            elif current_idx > 0:
                current_idx -= 1

        # on `KEY_DOWN`, move selection DOWN, while updating the index, and preventing the user from going out of bounds
        elif key == curses.KEY_DOWN and current_idx < 6:
            current_idx += 1

        # on `KEY_ENTER`, allow user to modify currently selected parameter via input field. also handle aborting edit
        elif key == curses.KEY_ENTER or key in [10,13]:
            # avoid writing abort message when no parameter is selected
            if current_idx == -1:
               	continue
            stdscr.addstr(25, 45, "Don't write anything or press ESC to abort change", colors['leechers_text_color'])

            # download_path
            if current_idx == 0:
                value, esc_s = add_input_field(stdscr, 14, 16, w-16-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(14, 16, " "*(w-16))
                    stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "" or esc_s: # handling quitting edit
                    stdscr.addstr(14, 16, " "*(w-16))
                    stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'download_path', value)
                    config = load_config(config_file)
                stdscr.addstr(14, 16, " "*(w-16))
                stdscr.addstr(14, 16, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

            # transcode_path
            elif current_idx == 1:
                value, esc_s = add_input_field(stdscr, 18, 17, w-17-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(18, 17, " "*(w-17))
                    stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "": # handling quitting during edit
                    stdscr.addstr(18, 17, " "*(w-17))
                    stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'transcode_path', value)
                    config = load_config(config_file)
                stdscr.addstr(18, 17, " "*(w-17))
                stdscr.addstr(18, 17, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

            # subtitles_path
            elif current_idx == 2:
                value, esc_s = add_input_field(stdscr, 22, 17, w-17-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(22, 17, " "*(w-17))
                    stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "": # handling quitting during edit
                    stdscr.addstr(22, 17, " "*(w-17))
                    stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'wanted_languages', value)
                    config = load_config(config_file)
                stdscr.addstr(22, 17, " "*(w-17))
                stdscr.addstr(22, 17, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

            # wanted_languages
            elif current_idx == 3:
                value, esc_s = add_input_field(stdscr, 28, 19, w-19-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(28, 19, " "*(w-19))
                    stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "": # handling quitting during edit
                    stdscr.addstr(28, 19, " "*(w-19))
                    stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'wanted_languages', value)
                    config = load_config(config_file)
                stdscr.addstr(28, 19, " "*(w-19))
                stdscr.addstr(28, 19, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

            # transcode_input_accel
            elif current_idx == 4:
                value, esc_s = add_input_field(stdscr, 35, 24, w-24-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(35, 24, " "*(w-24))
                    stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "": # handling quitting during edit
                    stdscr.addstr(35, 24, " "*(w-24))
                    stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'transcode_input_accel', value)
                    config = load_config(config_file)
                stdscr.addstr(35, 24, " "*(w-24))
                stdscr.addstr(35, 24, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

            # transcode_video_args
            elif current_idx == 5:
                value, esc_s = add_input_field(stdscr, 39, 23, w-23-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(39, 23, " "*(w-23))
                    stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "": # handling quitting during edit
                    stdscr.addstr(39, 23, " "*(w-23))
                    stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'transcode_video_args', value)
                    config = load_config(config_file)
                stdscr.addstr(39, 23, " "*(w-23))
                stdscr.addstr(39, 23, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

            # transcode_audio_args
            elif current_idx == 6:
                value, esc_s = add_input_field(stdscr, 44, 23, w-23-13)
                if value is None and not esc_s: # handling resize during input
                    return
                if esc_s: # handling quitting during edit
                    stdscr.addstr(44, 23, " "*(w-23))
                    stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                if value.strip() == "": # handling quitting during edit
                    stdscr.addstr(44, 23, " "*(w-23))
                    stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
                    stdscr.addstr(25, 45, " "*(48+1))
                    continue
                else:
                    edit_config_param(config_file, 'transcode_audio_args', value)
                    config = load_config(config_file)
                stdscr.addstr(44, 23, " "*(w-23))
                stdscr.addstr(44, 23, value, colors['config_display_val'])
                stdscr.addstr(25, 45, " "*(48+1))

        # on `KEY_RESIZE`, check if terminal size is sufficient,
        elif key == curses.KEY_RESIZE:
            if check_terminal_size(stdscr, min_confm_h, min_confm_w, ">:("):
                return # and in this case, we return to main menu if size isn't sufficient, avoiding bad headaches for everyone

        # on `q`, quit and go back to main menu
        elif key in [81, 113]:
            return

        # on `ESC`, quit and go back to main menu
        elif key == ord('\x1b'):
            return None


        # i'm sorry (printing highlighted paramater)
        if current_idx == 0:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'] | curses.A_REVERSE)
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
        elif current_idx == 1:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'] | curses.A_REVERSE)
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
        elif current_idx == 2:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'] | curses.A_REVERSE)
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
        elif current_idx == 3:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'] | curses.A_REVERSE)
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
        elif current_idx == 4:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'] | curses.A_REVERSE)
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
        elif current_idx == 5:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'] | curses.A_REVERSE)
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'])
        elif current_idx == 6:
            stdscr.addstr(14, 16, config['download_path']['value'], colors['config_display_val'])
            stdscr.addstr(18, 17, config['transcode_path']['value'], colors['config_display_val'])
            stdscr.addstr(22, 17, config['subtitles_path']['value'], colors['config_display_val'])
            stdscr.addstr(28, 19, ' '.join([v for v in config['wanted_languages']['value']]), colors['config_display_val'])
            stdscr.addstr(35, 24, ' '.join([v for v in config['transcode_input_accel']['value']]), colors['config_display_val'])
            stdscr.addstr(39, 23, ' '.join([v for v in config['transcode_video_args']['value']]), colors['config_display_val'])
            stdscr.addstr(44, 23, ' '.join([v for v in config['transcode_audio_args']['value']]), colors['config_display_val'] | curses.A_REVERSE)



def check_terminal_size(stdscr, min_h, min_w, warn_string="Terminal window too small!"):
    """Checks terminal size and interrupts drawing to screen until a sufficient minimum height and width is set. Returns True if triggered. Also allows user to panic hit q"""
    # check if terminal height and width are sufficient, if so, let application continue
    h, w = stdscr.getmaxyx()
    if h >= min_h and w >= min_w:
        return

    # continuououously keep checking for terminal size changes
    while True:
        # check if terminal height and width are sufficient, if so, let application continue while signaling this function has been triggered
        h, w = stdscr.getmaxyx()
        if  h >= min_h and w >= min_w:
            stdscr.erase()
            return True

        # warn user that current terminal size is too small, while saving curses from an aneurysm by preventing it to attempt to draw characters out of bounds
        stdscr.erase()
        warn_y_pos = h // 2
        warn_x_pos = max(0, (w-len(warn_string)) // 2)
        if h > 2:
            stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
        stdscr.refresh()

        # check for terminal resize
        key = stdscr.getch()
        # allow user to panic quit by hitting q
        if key in [81, 113]:
            raise SystemExit(0)

def main(stdscr):
    # disable cursor blinking
    curses.curs_set(0)

    # specify and load config file
    config_file = "config.toml"
    config = load_config(config_file)

    # load indexers and set default one
    indexers = load_indexers()
    indexer = indexers["nyaa"]

    # declare menu entries
    menu_entries = ['Download', 'Transcode (Quality)', 'Transcode (+ Language)', 'Embed Subtitle', 'Indexer', 'Edit Config', 'Exit']

    # check terminal size, first draw
    min_mainm_h = 30
    min_mainm_w = 60
    check_terminal_size(stdscr, min_mainm_h, min_mainm_w)
    h, w = stdscr.getmaxyx()

    # set current index as first
    current_idx = 0

    # first draw cycle, printing current selected menu entry highlighted accordingly
    for idx, row in enumerate(menu_entries):
        x = w//2 - len(row)//2
        y = max((16 + idx*2), ((h-6)//2 - len(menu_entries)//2 + idx*2))
        if idx == current_idx:
            stdscr.addstr(y, x, row, colors['selected_menu_color'])
        else:
            stdscr.addstr(y, x, row, colors['entry_text_color'])
    redraw_windows(stdscr)

    # user input loop
    while True:
        # get user's input; the loop runs each time a key is caught
        key = stdscr.getch()

        # on `KEY_UP`, move selection up, while updating the index, and preventing the user from going out of bounds
        if key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1

        # on `KEY_DOWN`, move selection down, while updating the index, and preventing the user from going out of bounds
        elif key == curses.KEY_DOWN and current_idx < len(menu_entries)-1:
            current_idx += 1

        # on `KEY_ENTER`, drop user into currently selected menu entry and act accordingly
        elif key == curses.KEY_ENTER or key in [10,13]:
            # Download
            if current_idx == 0:
                # check if required config parameters have been set, if not, warn user and return to main menu
                if config['download_path']['value'].strip() == "" or config['download_path']['value'] == "/path/to/folder":
                    stdscr.clear()
                    warn_string = "`download_path` must be set!"
                    warn_y_pos = h//2
                    warn_x_pos = max(0, (w-len(warn_string))//2)
                    stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
                    continue

                download_menu(stdscr, 13, h-13-6, config, indexer)

            # Transcode (Quality)
            if current_idx == 1:
                # check if required config parameters have been set, if not, warn user and return to main menu
                if (config['download_path']['value'].strip() == "" or config['download_path']['value'] == "/path/to/folder"
                or config['transcode_path']['value'].strip() == "" or config['transcode_path']['value'] == "/path/to/folder"
                or not config['wanted_languages']['value']
                or not config['transcode_video_args']['value']
                or not config['transcode_audio_args']['value']):
                    stdscr.clear()
                    warn_string = "`download_path`, `transcode_path`, `wanted_languages`, `transcode_video_args` and `transcode_audio_args` must be set!"
                    warn_y_pos = h//2
                    warn_x_pos = max(0, (w-len(warn_string))//2)
                    stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
                    continue

                transcode_menu_quality(stdscr, config)

            # Transcode (+ Language)
            if current_idx == 2:
                # check if required config parameters have been set, if not, warn user and return to main menu
                if (config['download_path']['value'].strip() == "" or config['download_path']['value'] == "/path/to/folder"
                or config['transcode_path']['value'].strip() == "" or config['transcode_path']['value'] == "/path/to/folder"
                or not config['wanted_languages']['value']
                or not config['transcode_video_args']['value']
                or not config['transcode_audio_args']['value']):
                    stdscr.clear()
                    warn_string = "`download_path`, `transcode_path`, `wanted_languages`, `transcode_video_args` and `transcode_audio_args` must be set!"
                    warn_y_pos = h//2
                    warn_x_pos = max(0, (w-len(warn_string))//2)
                    stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
                    continue

                transcode_menu_language(stdscr, config)

            # Embed Subtitle
            if current_idx == 3:
                # check if required config parameters have been set, if not, warn user and return to main menu
                if (config['download_path']['value'].strip() == "" or config['download_path']['value'] == "/path/to/folder"
                or config['transcode_path']['value'].strip() == "" or config['transcode_path']['value'] == "/path/to/folder"
                or config['subtitles_path']['value'].strip() == "" or config['subtitles_path']['value'] == "/path/to/folder"):
                    stdscr.clear()
                    warn_string = "`download_path`, `transcode_path`, and `subtitles_path` must be set!"
                    warn_y_pos = h//2
                    warn_x_pos = max(0, (w-len(warn_string))//2)
                    stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
                    continue

                embed_subtitle_menu(stdscr, config)

            # Indexer
            if current_idx == 4:
                # reload indexers once choice has been made
                indexer = indexers_menu(stdscr, indexers, indexer)

            # Edit Config
            if current_idx == 5:
                edit_config_menu(stdscr, config, config_file)
                # reload config after editing
                config = load_config(config_file)
            stdscr.refresh()

            # Exit
            if current_idx == len(menu_entries)-1:
                break

        # on `KEY_RESIZE`, check if terminal size is sufficient, and update screen's h & w for dynamic resizing
        elif key == curses.KEY_RESIZE:
            check_terminal_size(stdscr, min_mainm_h, min_mainm_w)

        # on `q`, quit
        elif key in [81, 113]:
            break

        # draw cycle, printing current selected menu entry highlighted
        stdscr.clear()
        h, w = stdscr.getmaxyx() # this is not on `KEY_RESIZE` because then it wouldn't be able to account for when the terminal has been resized while inside another menu
        for idx, row in enumerate(menu_entries):
            x = w//2 - len(row)//2
            y = max((16 + idx*2), ((h-6)//2 - len(menu_entries)//2 + idx*2))
            if idx == current_idx:
                stdscr.addstr(y, x, row, colors['selected_menu_color'])
            else:
                stdscr.addstr(y, x, row, colors['entry_text_color'])
        redraw_windows(stdscr)

curses.wrapper(main)
