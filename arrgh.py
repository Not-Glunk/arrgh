import curses
import time
import threading
from wcwidth import wcswidth
import subprocess
import json
from pathlib import Path
import tomllib
import re
import tomlkit
import os

import fingers
import inspect
from pioggerella import download_torrent
from coloring import init_colors

# since we aren't using any character sequences, have esc instantly quit out of input fields
os.environ.setdefault('ESCDELAY', '1')
# init colors
colors = init_colors()

def print_title(stdscr, h_alignment=None):
    """Prints title, centered at y 11 by default, 'left-aligned' can be passed. Returns a `curses.newwin()`, which has to be drawn after everything else on stdscr"""
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

    # get main stdscr size to center title_window
    h, w = stdscr.getmaxyx()
    # title h, w --> 10, 51
    if not h_alignment:
        title_window = curses.newwin(11, 51, 5, max(0, (w-51)//2))
    elif h_alignment == "left-aligned":
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

def redraw_windows(stdscr, h_alignment=None):
    """Correctly redraw windows. 'left-aligned' can be passed for title"""
    # correctly draw windows
    stdscr.noutrefresh() # prime base screen for update
    title_window = print_title(stdscr, h_alignment) # draw title
    title_window.noutrefresh() # prime title_window for update
    curses.doupdate() # update entire physical screen

def print_menu(stdscr, menu_entries, current_idx):
    """Prints menu entries given a list of strings, centered below the title's default location. Current selected index must be passed for highlighting"""
    stdscr.clear()

    # get main stdscr size to center entries
    h, w = stdscr.getmaxyx()

    # printing menu entries (including selected one)
    for idx, row in enumerate(menu_entries):
        x = w//2 - len(row)//2
        y = max((16 + idx*2), ((h-6)//2 - len(menu_entries)//2 + idx*2))
        if idx == current_idx:
            stdscr.addstr(y, x, row, colors['selected_menu_color'])
        else:
            stdscr.addstr(y, x, row, colors['entry_text_color'])

    redraw_windows(stdscr)

def add_input_field(stdscr, input_y, input_x, width):
    """Adds a text input field of given width at the specified stdscr coordinates. Returns inputted data on `curses.KEY_ENTER`"""
    input_y, input_x
    width
    cursor_x = 0
    text = ""
    curses.echo()
    curses.curs_set(1)
    while True:
        stdscr.addstr(input_y, input_x, "_" * width, colors['input_text_background'])
        stdscr.addstr(input_y, input_x, text, colors['input_text_foreground'])

        stdscr.move(input_y, input_x + cursor_x)
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_ENTER or key in (10, 13):
            inputted_data = stdscr.instr(input_y, input_x, width).decode().rstrip()
            inputted_data = inputted_data.rstrip('_')
            curses.noecho()
            curses.curs_set(0)
            break

        elif key == curses.KEY_LEFT:
            cursor_x = max(0, cursor_x - 1)

        elif key == curses.KEY_RIGHT:
            cursor_x = min(len(text), cursor_x + 1)

        elif 32 <= key <= 126:
            if len(text) < width:
                text = text[:cursor_x] + chr(key) + text[cursor_x:]
                if cursor_x < width-1:
                    cursor_x += 1

        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if cursor_x > 0:
                text = text[:cursor_x - 1] + text[cursor_x:]
                cursor_x -= 1

        elif key == curses.KEY_RESIZE:
            stdscr.clear()
            h, w = stdscr.getmaxyx() # sorry, i am NOT handling that
            curses.noecho()
            curses.curs_set(0)
            stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
            stdscr.getch()
            return None

        elif key == ord('\x1b'): # if esc, quit
            curses.noecho()
            curses.curs_set(0)
            return None

    return inputted_data

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

    redraw_windows(stdscr, h_alignment="left-aligned")

def create_torrent_status(): # callback factory
    """Generates callbacks to be passed to the `download_torrent` function in order to receive torrent status updates"""
    torrent_status = {
        "progress": "0.00%",
        "download_speed": "0kB/s",
        "peers": "0"
    }
    def get_torrent_status(status):
        torrent_status.update(status)

    return torrent_status, get_torrent_status

pause_thread = threading.Event()
pause_thread.set()
page_n = 0
def download_torrent_print_status(infohash, download_path, stdscr, y, x, downloading_torrent, stop_torrent_status_printing):
    """Starts a thread which initiates torrent download and prints live status data on the correct entries table page. Printing thread can be stopped by setting and passing `stop_torrent_status_printing`. The torrent will continue downloading until app is quit"""
    global page_n
    h, w = stdscr.getmaxyx()

    spinner_frames = "⠂⠒⠲⠴⠤⠄⠄⠤⢤⣠⣀⡀⡀⣀⢀⢀⣀⣄⡤⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒"
    spinner_i = 0

    torrent_status, get_torrent_status = create_torrent_status()

    torrent_status_thread = threading.Thread(
        target=download_torrent,
        args=(infohash, download_path, get_torrent_status),
        daemon=True
    )
    torrent_status_thread.start()

    while torrent_status_thread.is_alive() and not stop_torrent_status_printing.is_set():
        if downloading_torrent['page_n'] == page_n:
            pause_thread.wait()
            spinner_frame = spinner_frames[spinner_i % len(spinner_frames)]
            spinner_i += 1
            stdscr.addstr(y, x, " "*24)
            stdscr.addstr(y, x, spinner_frame, colors['downloading_torrent_color'])
            stdscr.addstr(y, x+2, torrent_status['progress'], colors['downloading_torrent_color'])
            stdscr.addstr(y, x+2+8, torrent_status['download_speed'], colors['downloading_torrent_color'])
            stdscr.addstr(y, x+2+8+11, torrent_status['peers']+"ጰ", colors['downloading_torrent_color'])
            redraw_windows(stdscr, h_alignment="left-aligned")
            time.sleep(0.1)
    downloading_torrent['completed'] = True

def download_menu(stdscr, y_pos, max_y, config, indexer):
    """Prints download menu at specified stdscr coordinates; takes care of search field, search results table and starting download threads. `max_y` has to be of at least 12"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    global page_n

    redraw_windows(stdscr, h_alignment="left-aligned")

    # input field
    stdscr.addstr(y_pos, 3, "Search: ", colors['entry_text_color'])
    stdscr.addstr(y_pos+1, 11, "'q' to quit search", colors['quit_search_color'])
    search_query = add_input_field(stdscr, y_pos, 11, 48)
    if search_query is None: # handling quitting during search
        return
    search_results = indexer(search_query)
    if search_results is None:
        stdscr.addstr(16, 15, "No results found :(", colors['anger_emoji_color'])
        stdscr.getch()
        return

    # printing search results table
    # ~ 4 selector; 23 date; x title; 4 seeders; 4 leechers; 5 completed; 8 size
    title_max_length = (min(max(wcswidth(item["title"]) for item in search_results)+1,w-58)) # i think i found out for once why the code needs a random +1, but la scala looks nice so
    seeders_max_length = (min(max(len(item["seeders"]) for item in search_results),w-58))
    leechers_max_length = (min(max(len(item["leechers"]) for item in search_results),w-58))
    completed_max_length = (min(max(len(item["completed"]) for item in search_results),w-58))

    max_fit_entries = max_y-11
    downloading_torrents = []
    torrent_status_printing_threads = []
    stop_torrent_status_printing = threading.Event()
    stop_torrent_status_printing.clear()
    if max_fit_entries > len(search_results):
        print_entries_table(stdscr, search_results, title_max_length, seeders_max_length, leechers_max_length, completed_max_length)
        current_idx = 0
        selected_string = "Selected: " + search_results[current_idx]['title']
        # selected entry full title line wrap
        if len(selected_string) > w-6:
            lines = []
            while selected_string:
                lines.append(selected_string[:w-6])
                selected_string = selected_string[w-6:]
            i = 0
            for line in lines:
                stdscr.addstr(y_pos+max_y-3+i, 3, line, colors['selected_full_entry'])
                i += 1
        else:
     	     stdscr.addstr(y_pos+max_y-3, 3, selected_string, colors['selected_full_entry'])
        # handling user input for selecting entry
        while True:
            key = stdscr.getch()
            pause_thread.clear() # pause torrent status printing

            if key == curses.KEY_RESIZE:
                check_terminal_size(stdscr, max_y+18, 60)
                curses.update_lines_cols()
                h, w = stdscr.getmaxyx()
                max_y = h - y_pos - 6 # this kinda makes passing max_y useless, but eh that was for another use im not implenting anymore so eh
            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
                if downloading_torrents: # avoid selecting downloading torrents
                    for downloading in downloading_torrents:
                        if downloading['page_index'] == current_idx and current_idx > 0:
                            current_idx -= 1
                        elif downloading['page_index'] == current_idx and current_idx == 0:
                            current_idx += 1
            if key == curses.KEY_DOWN and current_idx < len(search_results)-1:
                current_idx += 1
                if downloading_torrents: # avoid selecting downloading torrents
                    for downloading in downloading_torrents:
                        if downloading['page_index'] == current_idx and len(search_results)-1 > 0:
                            current_idx += 1
                        elif downloading['page_index'] == current_idx and len(search_results)-1 == 0:
                            current_idx -= 1
            if key == 81 or key == 113: # q to quit and go back to main menu
                stop_torrent_status_printing.set()
                for thread in torrent_status_printing_threads:
                    thread.join(timeout=1)
                break
            if key == curses.KEY_ENTER or key in [10,13]:
                infohash = search_results[current_idx]['infoHash']

                downloading_torrent = {
                   "page_index": current_idx, # for printing multiple page correctly
                   "page_n": 0,
                   "completed": False
                }

                torrent_download_thread = threading.Thread(
                    target=download_torrent_print_status,
                    args=(infohash, config['download_path']['value'], stdscr, 18+current_idx, 4, downloading_torrent, stop_torrent_status_printing),
                    daemon=True
                )
                torrent_download_thread.start()
                torrent_status_printing_threads.append(torrent_download_thread)
                downloading_torrents.append(downloading_torrent)

            # redraw srceen
            stdscr.clear()

            # live resizing for entries table
            title_max_length = (min(max(wcswidth(item["title"]) for item in search_results)+1,w-58)) # i think i found out for once why the code needs a random +1, but la scala looks nice so
            seeders_max_length = (min(max(len(item["seeders"]) for item in search_results),w-58))
            leechers_max_length = (min(max(len(item["leechers"]) for item in search_results),w-58))
            completed_max_length = (min(max(len(item["completed"]) for item in search_results),w-58))
            print_entries_table(stdscr, search_results, title_max_length, seeders_max_length, leechers_max_length, completed_max_length, current_idx, downloading_torrents)

            selected_string = "Selected: " + search_results[current_idx]['title']
            # selected entry full title line wrap
            if len(selected_string) > w-6:
                lines = []
                while selected_string:
                    lines.append(selected_string[:w-6])
                    selected_string = selected_string[w-6:]
                i = 0
                for line in lines:
                    stdscr.addstr(y_pos+max_y-3+i, 3, line, colors['selected_full_entry'])
                    i += 1
            else:
                stdscr.addstr(y_pos+max_y-3, 3, selected_string, colors['selected_full_entry'])

            stdscr.addstr(y_pos, 3, "Search: ", colors['entry_text_color'])
            stdscr.addstr(y_pos, 11, "_" * 48, colors['input_text_background'])
            stdscr.addstr(y_pos, 11, search_query, colors['input_text_foreground'])
            stdscr.addstr(y_pos+1, 11, "'q' to quit search", colors['quit_search_color'])
            redraw_windows(stdscr, h_alignment="left-aligned")
            pause_thread.set() # unpause torrent status printing

    elif max_fit_entries < len(search_results):
        # split entries into multiple pages
        fitted_search_results = []
        for i in range(0, len(search_results), max_fit_entries):
       	    single_page = search_results[i:i + max_fit_entries]
            fitted_search_results.append(single_page)

        print_entries_table(stdscr, fitted_search_results[0], title_max_length, seeders_max_length, leechers_max_length, completed_max_length)
        current_idx = 0
        #page_n = 0
        pages_indicator = "< " + str(page_n+1) + " / " + str(len(fitted_search_results)) + " >"
        stdscr.addstr(y_pos+max_y-5, (4+title_max_length+seeders_max_length+leechers_max_length+completed_max_length+33)//2, pages_indicator)
        search_results_actual_index = current_idx + max_fit_entries*page_n
        selected_string = "Selected: " + search_results[search_results_actual_index]['title']
        # selected entry full title line wrap
       	if len(selected_string) > w-6:
            lines = []
            while selected_string:
                lines.append(selected_string[:w-6])
               	selected_string = selected_string[w-6:]
            i = 0
            for	line in lines:
               	stdscr.addstr(y_pos+max_y-3+i, 3, line, colors['selected_full_entry'])
               	i += 1
       	else:
            stdscr.addstr(y_pos+max_y-3, 3, selected_string, colors['selected_full_entry'])
        while True:
            key = stdscr.getch()
            pause_thread.clear() # pause torrent status printing

            if key == curses.KEY_RESIZE:
                check_terminal_size(stdscr, max_y+18, 60)
                curses.update_lines_cols()
                h, w = stdscr.getmaxyx()
                curses.update_lines_cols()
            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
                if downloading_torrents: # avoid selecting downloading torrents
                    for downloading in downloading_torrents:
                        if downloading['page_n'] == page_n and downloading['page_index'] == current_idx and current_idx > 0:
                            current_idx -= 1
                        elif downloading['page_n'] == page_n and downloading['page_index'] == current_idx and current_idx == 0:
                            current_idx += 1
            if key == curses.KEY_DOWN and current_idx < len(fitted_search_results[0])-1:
                current_idx += 1
                if page_n == len(fitted_search_results)-1 and current_idx == len(fitted_search_results[-1]): # avoid going below number of entries on last page
                    current_idx -= 1
                if downloading_torrents: # avoid selecting downloading torrents
                    for downloading in downloading_torrents:
                        if downloading['page_n'] == page_n and downloading['page_index'] == current_idx and len(fitted_search_results)-1 > 0:
                            current_idx += 1
                        elif downloading['page_n'] == page_n and downloading['page_index'] == current_idx and len(fitted_search_results)-1 == 0:
                            current_idx -= 1
            if key == curses.KEY_LEFT and page_n > 0:
                page_n -= 1
            if key == curses.KEY_RIGHT and page_n < len(fitted_search_results)-1:
                page_n += 1
                if page_n == len(fitted_search_results)-1 and current_idx > len(fitted_search_results[-1])-1:
                    current_idx = len(fitted_search_results[-1])-1
            if key == 81 or key == 113: # q to quit and go back to main menu
                stop_torrent_status_printing.set()
                for thread in torrent_status_printing_threads:
                    thread.join(timeout=1)
                break
            if key == curses.KEY_ENTER or key in [10,13]:
                infohash = search_results[search_results_actual_index]['infoHash']

                downloading_torrent = {
                    "page_index": current_idx,
                    "page_n": page_n,
                    "completed": False
                }

                torrent_download_thread = threading.Thread(
                    target=download_torrent_print_status,
                    args=(infohash, config['download_path']['value'], stdscr, 18+current_idx, 4, downloading_torrent, stop_torrent_status_printing),
                    daemon=True
                )
                torrent_download_thread.start()
                torrent_status_printing_threads.append(torrent_download_thread)
                downloading_torrents.append(downloading_torrent)

            # redraw screen
            stdscr.clear()

            stdscr.addstr(y_pos, 3, "Search: ", colors['entry_text_color'])
            stdscr.addstr(y_pos, 11, "_" * 48, colors['input_text_background'])
            stdscr.addstr(y_pos, 11, search_query, colors['input_text_foreground'])
            stdscr.addstr(y_pos+1, 11, "'q' to quit search", colors['quit_search_color'])

            # live resizing for entries table
            title_max_length = (min(max(wcswidth(item["title"]) for item in search_results)+1,w-58)) # i think i found out for once why the code needs a random +1, but la scala looks nice so
            seeders_max_length = (min(max(len(item["seeders"]) for item in search_results),w-58))
            leechers_max_length = (min(max(len(item["leechers"]) for item in search_results),w-58))
            completed_max_length = (min(max(len(item["completed"]) for item in search_results),w-58))
            print_entries_table(stdscr, fitted_search_results[page_n], title_max_length, seeders_max_length, leechers_max_length, completed_max_length, current_idx, downloading_torrents)

            pages_indicator = "< " + str(page_n+1) + " / " + str(len(fitted_search_results)) + " >"
            stdscr.addstr(y_pos+max_y-5, (4+title_max_length+seeders_max_length+leechers_max_length+completed_max_length+33)//2, pages_indicator)
            search_results_actual_index = current_idx + max_fit_entries*page_n
            selected_string = "Selected: " + search_results[search_results_actual_index]['title']
            # selected entry full title line wrap
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

            redraw_windows(stdscr, h_alignment="left-aligned")
            pause_thread.set() # unpause torrent status printing

def check_terminal_size(stdscr, min_h, min_w, warn_string="Terminal window too small!"):
    """Checks terminal size and interrupts drawing to screen until a sufficient minimum height and width is set. Returns True if triggered. Also allows user to panic hit q"""
    h, w = stdscr.getmaxyx()
    if h >= min_h and w >= min_w:
        return
    while True:
        h, w = stdscr.getmaxyx()
        if  h >= min_h and w >= min_w:
            stdscr.erase()
            return True

        stdscr.erase()
        warn_y_pos = h // 2
        warn_x_pos = max(0, (w-len(warn_string)) // 2)
        if h > 2:
            stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
        stdscr.refresh()

        key = stdscr.getch() # (also checks for KEY_RESIZE updates)
        if key == 81 or key == 113: # q to exit
            raise SystemExit(0)

def load_config(config_file):
    """Loads config, returns dict for each parameter containg its values, definitions and example configurations"""
    config = {}
    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    with open(config_file, "r", encoding="utf-8") as f:
        str_def = ""
        str_def2 = ""
        list_ex = []
        str_name = ""

        for line in f:
            line = line.strip()

            if line.startswith("# @def "):
                str_def = line[7:].strip()
                continue

            if line.startswith("# @def2 "):
                str_def2 = line[8:].strip()
                continue

            if line.startswith("# @ex "):
                list_ex.append(line[6:].strip())
                continue

            if line.startswith("# "):
                continue

            if "=" in line:
                str_name = line.split("=", 1)[0].strip()

                config[str_name] = {
                    "name": str_name,
                    "value": config[str_name],
                    "def": str_def,
                    "def2": str_def2,
                    "ex": list_ex,
                }

            str_def = ""
            str_def2 = ""
            list_ex = []
            str_name = ""

    return config

def get_streams_info(media_file, wanted_languages, media_file_path):
    """Parses given file's media streams and returns two lists of dictionaries containing audio and subtitle id's and titles of those that match wanted_languages"""
    ffprobe_command = [
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=index,codec_type,codec_name:stream_tags=language,title', '-of', 'json', media_file_path+'/'+media_file+'.mkv'
    ]
    found_streams = subprocess.run(ffprobe_command, capture_output=True, text=True) #check=True)
    found_streams = json.loads(found_streams.stdout)

#    video_stream_codec = None
    audio_streams = []
    subtitle_streams = []

    for stream in found_streams["streams"]:
        stream_type = stream.get("codec_type")

 #       if stream_type == "video":
 #           video_stream_codec = stream.get("codec_name")
 #           continue

        tags = stream.get("tags", {})
        language = tags.get("language", "").lower()
        if language not in wanted_languages:
            continue

        stream_metadata = {
            "id": stream["index"],
            "language": language,
            "title": tags.get("title", "")
        }
        if stream_type == "audio":
            stream_metadata["codec"] = stream.get("codec_name")
            audio_streams.append(stream_metadata)
        elif stream_type == "subtitle":
            subtitle_streams.append(stream_metadata)

    return audio_streams, subtitle_streams # video_stream_codec, audio_streams, subtitle_streams

def select_media(stdscr, y_pos, max_y, media_list):
    """Prints scrollable menu from a given list at specified `y_pos`, returns selected index of such list. `max_y` must be at least 3, i think"""
    selected_idx = 0
    scroll_offset = 0

    max_entries = max_y - 2
    h, w = stdscr.getmaxyx()

    while True:
        entry_max_length = min(max(len(entry) for entry in media_list), w-6)
        stdscr.addstr(y_pos, 0, " "*w)
        stdscr.addstr(y_pos, (entry_max_length+6)//2, "^")

        # split list into visible entries
        visible_entries = media_list[scroll_offset:scroll_offset+max_entries]

        for visible_i, entry in enumerate(visible_entries):
            actual_visible_i = scroll_offset + visible_i

            if len(entry) > w-6:
                entry = entry[:(w-9)] + "..."

            stdscr.addstr(y_pos+1+visible_i, 0, " "*w)
            if actual_visible_i == selected_idx:
                stdscr.addstr(y_pos+1+visible_i, 3, entry, colors["selected_entry_color"])
            else:
                stdscr.addstr(y_pos+1+visible_i, 3, entry, colors["unselected_entry_color"])

        stdscr.addstr(y_pos+max_y, 0, " "*w)
        stdscr.addstr(y_pos+max_y, (entry_max_length+6)//2, "v")

        stdscr.refresh()


        key = stdscr.getch()

        if key == curses.KEY_RESIZE:
            stdscr.clear()
            h, w = stdscr.getmaxyx() # sorry, i am NOT handling that
            stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
            stdscr.getch()
            return None
        elif key == ord('\x1b'): # if esc, quit
            return None
        elif key == curses.KEY_UP:
            if selected_idx > 0:
                selected_idx -= 1
            if selected_idx < scroll_offset:
                scroll_offset = selected_idx
        elif key == curses.KEY_DOWN:
            if selected_idx < len(media_list)-1:
                selected_idx += 1
            if selected_idx >= scroll_offset+max_entries:
                scroll_offset = selected_idx-max_entries+1
        if key in [81, 113]: # q to quit and go back to main menu
            return None
            break
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return selected_idx

def rename_media_output(media_input, audio_streams, subtitle_streams):
    """Given an input media file name and found wanted_languages streams; strips release groups, quality tags and the such to format it as following: `{Title} - {SxxExx} {Quality} {audio_streams} (sub {subtitle_streams}).mkv`"""
    media_rename = media_input

    # strip release group (first [])
    media_rename = re.sub(r"^\s*\[[^\]]+\]\s*", "", media_rename, count=1)
    # get resolution
    resolution_match = re.search(r"(?:\(\s*)?(2160p|1440p|1080p|900p|720p|576p|480p|360p)(?:\s*\))?", media_rename, flags=re.IGNORECASE)
    resolution = resolution_match.group(1).lower() if resolution_match else ""
    # strip '.' separators
    media_rename = re.sub(r"[._]+", " ", media_rename)
    media_rename = re.sub(r"\s+", " ", media_rename).strip()
    # strip hases or trailing release groups
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
    # build languages (audio and subtitles) part
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

    return result.strip()

def transcode_menu_quality(stdscr, config):
    """Prints simple transcode menu, takes care of media selection and ffmpeg for (S)ingle and (B)atch transcodes"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    min_qualm_h = 28
    min_qualm_w = 95
    check_terminal_size(stdscr, min_qualm_h, min_qualm_w)
    redraw_windows(stdscr, h_alignment="left-aligned")

    stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors["header_string_color"])
    stdscr.addstr(14, 3, "'q' to quit transcode", colors["quit_search_color"])
    stdscr.refresh()
    key = None
    while True:
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            check_terminal_size(stdscr, min_qualm_h, min_qualm_w)
        if key in [83, 115] or key in [66, 98] or key in [81, 113]: # (S)ingle or (B)atch or (Q)uit
            break

        redraw_windows(stdscr, h_alignment="left-aligned")
        stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors["header_string_color"])
        stdscr.addstr(14, 3, "'q' to quit transcode", colors["quit_search_color"])
    if key in [81, 113]: return # (Q)uit to main menu

    flister_list = []
    download_path = Path(config['download_path']['value'])
    folder_or_file = ''
    if key in [83, 115]: # (S)ingle
        # parse download_path for files into alphabetically ordered list
        n_found_files = 0
        for file in download_path.iterdir():
            if file.is_file() and file.suffix.lower() == ".mkv":
                flister_list.append(file.stem)
                n_found_files += 1
        if n_found_files == 0:
            stdscr.addstr(16, 7, "No files present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)
        folder_or_file = 'file'
    else:
        # parse download_path for folders into alphabetically ordered list
        n_found_folders = 0
        for folder in download_path.iterdir():
            if folder.is_dir():
                flister_list.append(folder.name)
                n_found_folders += 1
        if n_found_folders == 0:
            stdscr.addstr(16, 7, "No folder present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)
        folder_or_file = 'folder'

    selected_media_idx = select_media(stdscr, 16, (h-16)//3, flister_list)
    if selected_media_idx is None: # handling quitting during media selection
        return
    selected_media = flister_list[selected_media_idx]

    # (S)ingle
    if folder_or_file == "file": # execute ffmpeg command, move&rename once
        audio_streams, subtitle_streams = get_streams_info(selected_media, config['wanted_languages']['value'], config['download_path']['value']) # even though we're not stripping unwanted languages here, still rename in a sane way with what we're interested in
        renamed = rename_media_output(selected_media, audio_streams, subtitle_streams)
        # check if file already present in transcode_path
        if Path(config['transcode_path']['value']+'/'+renamed).is_file():
            stdscr.addstr(16, 7, "File already present!", colors['anger_emoji_color'])
            stdscr.refresh()
            stdscr.getch()
            return

        stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(16, 3, "Transcoding…", colors['unselected_entry_softer'])
        stdscr.addstr(16, 3+15, renamed, colors['unselected_entry_color'])
        stdscr.refresh()
        n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", config['download_path']['value']+'/'+selected_media+'.mkv'], capture_output=True, text=True, check=True).stdout.strip()
        ffmpeg_command = [
            'ffmpeg', *config['transcode_input_accel']['value'], '-i', config['download_path']['value']+'/'+selected_media+'.mkv', '-map', '0',
            '-c:v', *config['transcode_video_args']['value'],
            '-c:a', *config['transcode_audio_args']['value'],
            '-c:s', 'copy',
            '-progress', 'pipe:1',
            config['transcode_path']['value']+'/'+renamed
        ]
        log_file = (
            open("ffmpeg-log", "a", encoding="utf-8")
            if config['enable_ffmpeg_debug_log']['value'] == 'y'
            else subprocess.DEVNULL
        )
        try:
            proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)
            progress = {}
            for line in proc.stdout:
                line = line.strip()
                if "=" in line: # assemble progress dictionary
                    k, v = line.split("=", 1)
                    progress[k] = v
                if line == "progress=continue":
                    progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                    stdscr.addstr(17, 3, progress_string, colors['unselected_entry_softer'])
                    stdscr.refresh()
            proc.wait()
        finally:
            if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(18, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.refresh()
        stdscr.getch()

    # (B)atch
    elif folder_or_file == "folder": # execute ffmpeg command, move&rename recursively in new remuxed folder
        input_folder = config['download_path']['value']+'/'+selected_media
        p_input_folder = Path(input_folder)
        # get files list
        files = sorted(file for file in p_input_folder.iterdir() if file.is_file() and file.suffix.lower() == ".mkv")
        total = len(files)
        # create output folder with formatted name
        folder_audio_streams, folder_subtitle_streams = get_streams_info(files[0].stem, config['wanted_languages']['value'], input_folder)
        renamed_folder = rename_media_output(selected_media, folder_audio_streams, folder_subtitle_streams)
        output_folder = config['transcode_path']['value']+'/'+renamed_folder
        p_output_folder = Path(output_folder)
        # check if file already present	in transcode_path
       	if p_output_folder.is_dir():
            stdscr.addstr(16, 7, "Folder already present!", colors['anger_emoji_color'])
            stdscr.refresh()
            stdscr.getch()
            return
        p_output_folder.mkdir()

        # iterate ffmpeg proc over every file
        for i, file in enumerate(files, start=1):
            audio_streams, subtitle_streams = get_streams_info(file.stem, config['wanted_languages']['value'], input_folder)
            renamed = rename_media_output(file.stem, audio_streams, subtitle_streams)

            stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
            stdscr.addstr(16, 3, "Transcoding…", colors['unselected_entry_softer'])
            i_progress_string = f"{i}/{total}"
            stdscr.addstr(16, 16, i_progress_string, colors['unselected_entry_softer'])
            stdscr.addstr(16, 3+20, renamed, colors['unselected_entry_color'])
            stdscr.refresh()

            n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", file], capture_output=True, text=True, check=True).stdout.strip()
            ffmpeg_command = [
                'ffmpeg', *config['transcode_input_accel']['value'], '-i', file, '-map', '0',
                '-c:v', *config['transcode_video_args']['value'],
                '-c:a', *config['transcode_audio_args']['value'],
                '-c:s', 'copy',
                '-progress', 'pipe:1',
                output_folder+'/'+renamed
            ]
            log_file = (
                open("ffmpeg-log", "a", encoding="utf-8")
                if config['enable_ffmpeg_debug_log']['value'] == 'y'
                else subprocess.DEVNULL
            )
            try:
                proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)
                progress = {}
                for line in proc.stdout:
                    line = line.strip()
                    if "=" in line: # assemble progress dictionary
                        k, v = line.split("=", 1)
                        progress[k] = v
                    if line == "progress=continue":
                        progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                        stdscr.addstr(17, 3, progress_string, colors['unselected_entry_softer'])
                        stdscr.refresh()
                proc.wait()
            finally:
                if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(18, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.refresh()
        stdscr.getch()

def transcode_menu_language(stdscr, config):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    min_langm_h = 38
    min_langm_w = 95
    check_terminal_size(stdscr, min_langm_h, min_langm_h)
    redraw_windows(stdscr, h_alignment="left-aligned")

    stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors["header_string_color"])
    stdscr.addstr(14, 3, "'q' to quit transcode", colors["quit_search_color"])
    stdscr.addstr(13, 29, "■", colors["unselected_entry_softer"])
    stdscr.addstr(13, 31, "Transcode", colors["seeders_text_color"])
    to_transcode = True
    stdscr.addstr(14, 28, "(E)nable/(D)", colors["unselected_entry_softer"])
    stdscr.refresh()
    key = None
    while True:
        key = stdscr.getch()

        stdscr.clear()

        if key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            check_terminal_size(stdscr, min_langm_h, min_langm_h)
        if key in [69, 101]: # (E)nable encoding
            stdscr.refresh()
            to_transcode = True
        if key in [68, 100]: # (D)isable encoding
            stdscr.refresh
            to_transcode = False

        redraw_windows(stdscr, h_alignment="left-aligned")

        stdscr.addstr(13, 3, "(S)ingle or (B)atch?", colors["header_string_color"])
        stdscr.addstr(14, 3, "'q' to quit transcode", colors["quit_search_color"])
        if to_transcode == True:
            stdscr.addstr(13, 29, "■", colors["unselected_entry_softer"])
            stdscr.addstr(13, 31, "Transcode", colors["seeders_text_color"])
            stdscr.refresh()
        elif to_transcode == False:
            stdscr.addstr(13, 29, "□", colors["unselected_entry_softer"])
            stdscr.addstr(13, 31, "Transcode", colors["leechers_text_color"])
        stdscr.addstr(14, 28, "(E)nable/(D)", colors["unselected_entry_softer"])

        if key in [83, 115] or key in [66, 98] or key in [81, 113]: # (S)ingle or (B)atch or (Q)uit
            stdscr.addstr(14, 28, " "*12)
            stdscr.refresh()
            break
    if key in [81, 113]: return # (Q)uit to main menu

    flister_list = []
    download_path = Path(config['download_path']['value'])
    folder_or_file = ''
    if key in [83, 115]: # (S)ingle
        # parse download_path for files into alphabetically ordered list
        n_found_files = 0
        for file in download_path.iterdir():
            if file.is_file() and file.suffix.lower() == ".mkv":
                flister_list.append(file.stem)
                n_found_files += 1
        if n_found_files == 0:
            stdscr.addstr(16, 7, "No files present!", colors['anger_emoji_color'])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)
        folder_or_file = 'file'
    else: # (B)atch
        # parse download_path for folders into alphabetically ordered list
        n_found_folders = 0
        for folder in download_path.iterdir():
            if folder.is_dir():
                flister_list.append(folder.name)
                n_found_folders += 1
        if n_found_folders == 0:
            stdscr.addstr(16, 7, "No folder present!", colors["anger_emoji_color"])
            stdscr.getch()
            return
        flister_list = sorted(flister_list)
        folder_or_file = 'folder'

    # (S)ingle
    if folder_or_file == "file":
        ### first file
        first_selected_media_idx = select_media(stdscr, 16, (h-16)//3, flister_list)
        if first_selected_media_idx is None: # handling quitting during media selection
            return
        first_selected_media = flister_list[first_selected_media_idx]
        first_media_audio_streams, first_media_subtitle_streams = get_streams_info(first_selected_media, config['wanted_languages']['value'], config['download_path']['value'])

        # allow audio stream selection
        stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(16, 3, "Select audio streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 17
            for idx, streams in enumerate(first_media_audio_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(first_media_audio_streams[idx]['id']) + ': ' + first_media_audio_streams[idx]['language'] + '(' + first_media_audio_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(first_media_audio_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        first_selected_audio_streams = []
        # remove streams to remove
        for idx, stream in enumerate(first_media_audio_streams):
            if idx not in indexes_to_remove:
                first_selected_audio_streams.append(first_media_audio_streams[idx])

        # allow subtitle stream selection
        stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(16, 3, "Select subtitle streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 17
            for idx, streams in enumerate(first_media_subtitle_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(first_media_subtitle_streams[idx]['id']) + ': ' + first_media_subtitle_streams[idx]['language'] + '(' + first_media_subtitle_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(first_media_subtitle_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        first_selected_subtitle_streams = []
        # remove streams to remove
        for idx, stream in enumerate(first_media_subtitle_streams):
            if idx not in indexes_to_remove:
                first_selected_subtitle_streams.append(first_media_subtitle_streams[idx])

        stdscr.addstr(16, 0, " "*w*(((h-16)//3)+1))
        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_subtitle_streams)
        stdscr.addstr(16, 3, "Selected streams for first file:", colors["unselected_entry_softer"])
        stdscr.addstr(17, 3, f"Audio: {audio_selection}", colors["entry_text_color"])
        stdscr.addstr(18, 3, f"Subtitle: {subtitle_selection}", colors["entry_text_color"])
        first_selected_media_display = first_selected_media
        if len(first_selected_media_display) > w-12:
            first_selected_media_display = first_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(19, 3, f"From: {first_selected_media_display}", colors["quit_search_color"])

        ### second file // yes yes, most 'second_' variables are redundant
        stdscr.addstr(21, 3, "Select second file:", colors["header_string_color"])
        second_selected_media_idx = select_media(stdscr, 22, (h-16)//3, flister_list)
        if second_selected_media_idx is None: # handling quitting during media selection
            return
        second_selected_media = flister_list[second_selected_media_idx]
        second_media_audio_streams, second_media_subtitle_streams = get_streams_info(second_selected_media, config['wanted_languages']['value'], config['download_path']['value'])

        # allow audio stream selection
        stdscr.addstr(21, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(21, 3, "Select audio streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 22
            for idx, streams in enumerate(second_media_audio_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(second_media_audio_streams[idx]['id']) + ': ' + second_media_audio_streams[idx]['language'] + '('  + second_media_audio_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(second_media_audio_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        second_selected_audio_streams = []
        # remove streams to remove
        for idx, stream in enumerate(second_media_audio_streams):
            if idx not in indexes_to_remove:
                second_selected_audio_streams.append(second_media_audio_streams[idx])

        # allow subtitle stream selection
        stdscr.addstr(21, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(21, 3, "Select subtitle streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 22
            for idx, streams in enumerate(second_media_subtitle_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(second_media_subtitle_streams[idx]['id']) + ': ' + second_media_subtitle_streams[idx]['language'] + '(' + second_media_subtitle_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(second_media_subtitle_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        second_selected_subtitle_streams = []
        # remove streams to remove
        for idx, stream in enumerate(second_media_subtitle_streams):
            if idx not in indexes_to_remove:
                second_selected_subtitle_streams.append(second_media_subtitle_streams[idx])

        stdscr.addstr(21, 0, " "*w*(((h-16)//3)+2))
        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_subtitle_streams)
        stdscr.addstr(21, 3, "Selected streams for second file:", colors["unselected_entry_softer"])
        stdscr.addstr(22, 3, f"Audio: {audio_selection}", colors["entry_text_color"])
        stdscr.addstr(23, 3, f"Subtitle: {subtitle_selection}", colors["entry_text_color"])
        second_selected_media_display = second_selected_media
        if len(second_selected_media_display) > w-12:
            second_selected_media_display = second_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(24, 3, f"From: {second_selected_media_display}", colors["quit_search_color"])

        merge_audio_streams = first_selected_audio_streams + second_selected_audio_streams
        merge_subtitle_streams = first_selected_subtitle_streams + second_selected_subtitle_streams
        merge_renamed = rename_media_output(first_selected_media, merge_audio_streams, merge_subtitle_streams)

        stdscr.addstr(26, 3, "Merging into:", colors["unselected_entry_softer"])
        stdscr.addstr(26, 29, "Enter to confirm", colors["header_string_color"])
        stdscr.addstr(27, 3, merge_renamed, colors["entry_text_color"])
        stdscr.addstr(28, 3, "*This assumes you're merging stuff that makes sense, no checks", colors["quit_search_color"])
        stdscr.addstr(29, 3, "*Final filename and video stream is taken from the first input", colors["quit_search_color"])

        while True:
            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_ENTER or key in [10,13]:
                stdscr.addstr(26, 29, " "*16)
                break
            elif key in [81, 113]: return # (Q)uit to main menu

        if Path(config['transcode_path']['value']+'/'+merge_renamed).is_file():
            stdscr.addstr(31, 8, "File already present!", colors['anger_emoji_color'])
            stdscr.refresh()
            stdscr.getch()
            return

        stdscr.addstr(31, 3, "Transcoding…", colors['unselected_entry_softer'])
        stdscr.addstr(31, 3+15, merge_renamed, colors['unselected_entry_color'])
        stdscr.refresh()

        ### compose ffmpeg command
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

        ffmpeg_command = []
        if to_transcode:
            ffmpeg_command = [
                'ffmpeg', *config['transcode_input_accel']['value'],
                '-i', config['download_path']['value']+'/'+first_selected_media+'.mkv',
                '-i', config['download_path']['value']+'/'+second_selected_media+'.mkv',
                '-c:v', *config['transcode_video_args']['value'],
                '-c:a', *config['transcode_audio_args']['value'],
                *streams_mapping,
                '-progress', 'pipe:1',
                config['transcode_path']['value']+'/'+merge_renamed
            ]
        else:
            ffmpeg_command = [
                'ffmpeg',
                '-i', config['download_path']['value']+'/'+first_selected_media+'.mkv', # could this make use of 'transcode_input_accel'? #TODO
                '-i', config['download_path']['value']+'/'+second_selected_media+'.mkv',
                *streams_mapping,
                '-progress', 'pipe:1',
                config['transcode_path']['value']+'/'+merge_renamed
            ]

        n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", config['download_path']['value']+'/'+first_selected_media+'.mkv'], capture_output=True, text=True, check=True).stdout.strip()
        log_file = (
            open("ffmpeg-log", "a", encoding="utf-8")
            if config['enable_ffmpeg_debug_log']['value'] == 'y'
            else subprocess.DEVNULL
        )
        try:
            proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)
            progress = {}
            for line in proc.stdout:
                line = line.strip()
                if "=" in line: # assemble progress dictionary
                    k, v = line.split("=", 1)
                    progress[k] = v
                if line == "progress=continue":
                    progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                    stdscr.addstr(32, 3, progress_string, colors['unselected_entry_softer'])
                    stdscr.refresh()
            proc.wait()
        finally:
            if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(33, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.refresh()
        stdscr.getch()

    elif folder_or_file == "folder":
        ### first folder
        first_selected_media_idx = select_media(stdscr, 16, (h-16)//3, flister_list)
        if first_selected_media_idx is None: # handling quitting during media selection
            return
        first_selected_media = flister_list[first_selected_media_idx]

        first_input_folder = config['download_path']['value']+'/'+first_selected_media
        p_first_input_folder = Path(first_input_folder)
        # get files list
        first_files = sorted(file for file in p_first_input_folder.iterdir() if file.is_file() and file.suffix.lower() == ".mkv")
        first_total_files = len(first_files)
        first_folder_audio_streams, first_folder_subtitle_streams = get_streams_info(first_files[0].stem, config['wanted_languages']['value'], first_input_folder)

        # allow audio stream selection
        stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(16, 3, "Select audio streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 17
            for idx, streams in enumerate(first_folder_audio_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(first_folder_audio_streams[idx]['id']) + ': ' + first_folder_audio_streams[idx]['language'] + '(' + first_folder_audio_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(first_folder_audio_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        first_selected_audio_streams = []
        for idx, stream in enumerate(first_folder_audio_streams):
            if idx not in indexes_to_remove:
                first_selected_audio_streams.append(first_folder_audio_streams[idx])

        # allow subtitle stream selection
        stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(16, 3, "Select subtitle streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 17
            for idx, streams in enumerate(first_folder_subtitle_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(first_folder_subtitle_streams[idx]['id']) + ': ' + first_folder_subtitle_streams[idx]['language'] + '(' + first_folder_subtitle_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(first_folder_subtitle_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        first_selected_subtitle_streams = []
        # remove streams to remove
        for idx, stream in enumerate(first_folder_subtitle_streams):
            if idx not in indexes_to_remove:
                first_selected_subtitle_streams.append(first_folder_subtitle_streams[idx])

        stdscr.addstr(16, 0, " "*w*(((h-16)//3)+1))
        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in first_selected_subtitle_streams)
        stdscr.addstr(16, 3, "Selected streams for first file:", colors["unselected_entry_softer"])
        stdscr.addstr(17, 3, f"Audio: {audio_selection}", colors["entry_text_color"])
        stdscr.addstr(18, 3, f"Subtitle: {subtitle_selection}", colors["entry_text_color"])
        first_selected_media_display = first_selected_media
        if len(first_selected_media_display) > w-12:
            first_selected_media_display = first_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(19, 3, f"From: {first_selected_media_display}", colors["quit_search_color"])

        ### second file // yes yes, most 'second_' variables are redundant
        stdscr.addstr(21, 3, "Select second file:", colors["header_string_color"])
        second_selected_media_idx = select_media(stdscr, 22, (h-16)//3, flister_list)
        if second_selected_media_idx is None: # handling quitting during media selection
            return
        second_selected_media = flister_list[second_selected_media_idx]

        second_input_folder = config['download_path']['value']+'/'+second_selected_media
        p_second_input_folder = Path(second_input_folder)
        # get files list
        second_files = sorted(file for file in p_second_input_folder.iterdir() if file.is_file() and file.suffix.lower() == ".mkv")
        second_total_files = len(second_files)
        second_folder_audio_streams, second_folder_subtitle_streams = get_streams_info(second_files[0].stem, config['wanted_languages']['value'], second_input_folder)

        # allow audio stream selection
        stdscr.addstr(21, 3, " "*w*(((h-16)//3)+2))
        stdscr.addstr(21, 3, "Select audio streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 22
            for idx, streams in enumerate(second_folder_audio_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(second_folder_audio_streams[idx]['id']) + ': ' + second_folder_audio_streams[idx]['language'] + '(' + second_folder_audio_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(second_folder_audio_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        second_selected_audio_streams = []
        for idx, stream in enumerate(second_folder_audio_streams):
            if idx not in indexes_to_remove:
                second_selected_audio_streams.append(second_folder_audio_streams[idx])

        # allow subtitle stream selection
        stdscr.addstr(21, 3, " "*w*(((h-16)//3)+1))
        stdscr.addstr(21, 3, "Select subtitle streams to keep:", colors["header_string_color"])
        stdscr.refresh()
        current_idx = 0
        indexes_to_remove = []
        while True:
            starting_y = 22
            for idx, streams in enumerate(second_folder_subtitle_streams):
                if idx in indexes_to_remove:
                    stdscr.addstr(starting_y+idx, 3, "□", colors["unselected_entry_softer"])
                else:
                    stdscr.addstr(starting_y+idx, 3, "■", colors["unselected_entry_softer"])
                stream_string = str(second_folder_subtitle_streams[idx]['id']) + ': ' + second_folder_subtitle_streams[idx]['language'] + '(' + second_folder_subtitle_streams[idx]['title'] + ')'
                if idx == current_idx:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["selected_menu_color"]) # temp color
                else:
                    stdscr.addstr(starting_y+idx, 5, stream_string, colors["entry_text_color"])
            stdscr.refresh()

            key = stdscr.getch()

            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(second_folder_subtitle_streams)-1:
                current_idx += 1
            elif key == ord(' '): # space to (un)select
                if current_idx in indexes_to_remove:
                    indexes_to_remove.remove(current_idx)
                else:
                    indexes_to_remove.append(current_idx)
            elif key == curses.KEY_ENTER or key in [10,13]:
                break
            elif key in [81, 113]: return # (Q)uit to main menu
        second_selected_subtitle_streams = []
        # remove streams to remove
        for idx, stream in enumerate(second_folder_subtitle_streams):
            if idx not in indexes_to_remove:
                second_selected_subtitle_streams.append(second_folder_subtitle_streams[idx])

        stdscr.addstr(21, 0, " "*w*(((h-16)//3)+1))
        audio_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_audio_streams)
        subtitle_selection = ", ".join(f'{stream["language"]} ({stream["title"]})' for stream in second_selected_subtitle_streams)
        stdscr.addstr(21, 3, "Selected streams for second file:", colors["unselected_entry_softer"])
        stdscr.addstr(22, 3, f"Audio: {audio_selection}", colors["entry_text_color"])
        stdscr.addstr(23, 3, f"Subtitle: {subtitle_selection}", colors["entry_text_color"])
        second_selected_media_display = second_selected_media
        if len(second_selected_media_display) > w-12:
            second_selected_media_display = second_selected_media_display[:(w-15)] + "..."
        stdscr.addstr(24, 3, f"From: {second_selected_media_display}", colors["quit_search_color"])

        merge_audio_streams = first_selected_audio_streams + second_selected_audio_streams
        merge_subtitle_streams = first_selected_subtitle_streams + second_selected_subtitle_streams
        merge_renamed_folder = rename_media_output(first_selected_media, merge_audio_streams, merge_subtitle_streams).rstrip('.mkv')

        stdscr.addstr(26, 3, "Merging into:", colors["unselected_entry_softer"])
        stdscr.addstr(26, 29, "Enter to confirm", colors["header_string_color"])
        stdscr.addstr(27, 3, merge_renamed_folder, colors["entry_text_color"])
        stdscr.addstr(28, 3, "*This assumes you're merging stuff that makes sense, no checks", colors["quit_search_color"])
        stdscr.addstr(29, 3, "*Final filename and video stream is taken from the first input", colors["quit_search_color"])
        if w < 148-6:
            stdscr.addstr(30, 3, "*Assuming that files in both folders can be alphabetically sorted in the same order and that streams are consistent in each of them. Praise thy lord"[:w-7]+"-", colors["quit_search_color"])
            stdscr.addstr(31, 4, "*Assuming that files in both folders can be alphabetically sorted in the same order and that streams are consistent in each of them. Praise thy lord"[w-7:], colors["quit_search_color"])
        else:
            stdscr.addstr(30, 3, "*Assuming that files in both folders can be alphabetically sorted in the same order and that streams are consistent in each of them. Praise thy lord", colors["quit_search_color"])

        while True:
            key = stdscr.getch()
            if key == curses.KEY_RESIZE:
                stdscr.clear()
                h, w = stdscr.getmaxyx() # sorry, i am NOT handling this (could, but way ugly)
                stdscr.addstr(h//2, (w-3)//2, ">:(", colors["anger_emoji_color"])
                stdscr.getch()
                return
            elif key == curses.KEY_ENTER or key in [10,13]:
                stdscr.addstr(26, 29, " "*16)
                break
            elif key in [81, 113]: return # (Q)uit to main menu

        merge_output_folder = config['transcode_path']['value']+'/'+merge_renamed_folder
        p_merge_output_folder = Path(merge_output_folder)
        # check if folder already present in transcode_path
        if p_merge_output_folder.is_dir():
            stdscr.addstr(31, 7, "Folder already present!", colors['anger_emoji_color'])
            stdscr.refresh()
            stdscr.getch()
            return
        p_merge_output_folder.mkdir()

        # compose stream mapping args
        streams_mapping = ["-map", "0:0"]
        # audio streams from first file
        for stream in first_selected_audio_streams:
            streams_mapping += ["-map", f"0:{stream['id']}?"] # ? --> make map optional; better to miss a stream than the entire file
        # subtitle streams from first file
        for stream in first_selected_subtitle_streams:
            streams_mapping += ["-map", f"0:{stream['id']}?"]
        # audio streams from second file
        for stream in second_selected_audio_streams:
            streams_mapping += ["-map", f"1:{stream['id']}?"]
        # subtitle streams from second file
        for stream in second_selected_subtitle_streams:
            streams_mapping += ["-map", f"1:{stream['id']}?"]


        # iterate ffmpeg proc over every file
        for i, file in enumerate(first_files, start=1):
            merge_renamed = rename_media_output(file.stem, merge_audio_streams, merge_subtitle_streams)

            stdscr.addstr(32, 3, " "*w*(((h-16)//3)+2))
            stdscr.addstr(32, 3, "Transcoding…", colors['unselected_entry_softer'])
            i_progress_string = f"{i}/{first_total_files}"
            stdscr.addstr(32, 16, i_progress_string, colors['unselected_entry_softer'])
            stdscr.addstr(32, 3+20, merge_renamed, colors['unselected_entry_color'])
            stdscr.refresh()

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
                    merge_output_folder+'/'+merge_renamed
                 ]
            else:
                ffmpeg_command = [
                    'ffmpeg',
                    '-i', file, # could this make use of 'transcode_input_accel'? #TODO
                    '-i', second_files[i-1], # i is the human facing index for displaying progress, so gotta -1
                    *streams_mapping,
                    '-progress', 'pipe:1',
                    merge_output_folder+'/'+merge_renamed
                ]
            n_frames = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", file], capture_output=True, text=True, check=True).stdout.strip()
            log_file = (
                open("ffmpeg-log", "a", encoding="utf-8")
                if config['enable_ffmpeg_debug_log']['value'] == 'y'
                else subprocess.DEVNULL
            )
            try:
                proc = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=log_file,  text=True, bufsize=1)
                progress = {}
                for line in proc.stdout:
                    line = line.strip()
                    if "=" in line: # assemble progress dictionary
                        k, v = line.split("=", 1)
                        progress[k] = v
                    if line == "progress=continue":
                        progress_string = f"Media Time: {progress.get('out_time')}   nFrame: {progress.get('frame')}/{n_frames}   fps: {progress.get('fps')}   Speed: {progress.get('speed')}"
                        stdscr.addstr(33, 3, progress_string, colors['unselected_entry_softer'])
                        stdscr.refresh()
                proc.wait()
            finally:
                if log_file is not subprocess.DEVNULL: log_file.close()
        stdscr.addstr(34, (w//2)-10, "Done!", colors['downloaded_torrent_color'])
        stdscr.refresh()
        stdscr.getch()

def embed_subtitle_menu(stdscr, config):
    """Prints menu to embed subtitle track into mkv file"""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    min_embedm_h = 35
    min_embedm_w = 60
    check_terminal_size(stdscr, min_embedm_h, min_embedm_w)
    redraw_windows(stdscr, h_alignment="left-aligned")

    stdscr.addstr(13, 3, "Select .mkv file from (D)ownload or (T)ranscode path?", colors["header_string_color"])
    stdscr.addstr(14, 3, "'q' to quit embedding", colors["quit_search_color"])
    key = None
    while True:
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            h, w, = stdscr.getmaxyx()
            check_terminal_size(stdscr, min_embedm_h, min_embedm_w)
        if key in [68, 100] or key in [84, 116] or key in [81, 113]: # (D)ownload or (T)ranscode or (Q)uit
            break

        stdscr.clear()
        redraw_windows(stdscr, h_alignment="left-aligned")
        stdscr.addstr(13, 3, "Select .mkv file from (D)ownload or (T)ranscode path?", colors["header_string_color"])
        stdscr.addstr(14, 3, "'q' to quit embedding", colors["quit_search_color"])
    if key in [81, 113]: return # (Q)uit to main menu

    files_path = None
    if key in [68, 100]: # (D)ownload
        files_path = Path(config['download_path']['value'])
    elif key in [84, 116]: # (T)ranscode
        files_path = Path(config['transcode_path']['value'])
    files_list = []

    # parse files_path for files into alphabetically ordered list
    n_found_files = 0
    for file in files_path.iterdir():
        if file.is_file() and file.suffix.lower() == ".mkv":
            files_list.append(file.stem)
            n_found_files += 1
    if n_found_files == 0:
        stdscr.addstr(16, 7, "No files present!", colors['anger_emoji_color'])
        stdscr.getch()
        return
    files_list = sorted(files_list)

    selected_media_idx = select_media(stdscr, 16, (h-16)//3, files_list)
    if selected_media_idx is None: # handling quitting during media selection
        return
    selected_media = files_list[selected_media_idx]

    stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
    stdscr.addstr(16, 3, "Select subtitle track to embed:", colors["header_string_color"])
    subs_path = Path(config['subtitles_path']['value'])
    subs_list = []
    n_found_files = 0
    for file in subs_path.iterdir():
        if file.is_file():
           subs_list.append(file.stem)
           n_found_files += 1
    if n_found_files == 0:
        stdscr.addstr(18, 7, "No files present!", colors['anger_emoji_color'])
        stdscr.getch()
        return
    subs_list = sorted(subs_list)
    selected_sub_idx = select_media(stdscr, 17, (h-16)//4, subs_list)
    if selected_sub_idx is None: # handling quitting during media selection
        return
    subs_ext_list = []
    for files in subs_path.iterdir():
        if file.is_file():
            subs_ext_list.append(file)
    subs_ext_list = sorted(subs_ext_list)
    selected_sub = subs_ext_list[selected_sub_idx] # that's me!

    stdscr.addstr(16, 3, " "*w*(((h-16)//3)+1))
    stdscr.addstr(16, 3, "Selected .mkv file:", colors["unselected_entry_softer"])
    selected_media_display = selected_media
    if len(selected_media_display) > w-6:
        selected_media_display = selected_media_display[:(w-9)] + "..."
    stdscr.addstr(17, 3, selected_media_display, colors["entry_text_color"])
    stdscr.addstr(18, 3, "Selected subtitle track to embed:", colors["unselected_entry_softer"])
    selected_sub_display = subs_list[selected_sub_idx]
    if len(selected_sub_display) > w-6:
        selected_sub_display = selected_sub_display[:(w-9)] + "..."
    stdscr.addstr(19, 3, selected_sub_display, colors["entry_text_color"])

    stdscr.addstr(21, 3, "Specify subtitle track title:", colors["header_string_color"])
    sub_title = add_input_field(stdscr, 22, 3, 28)
    if sub_title is None: # handling quitting during input
        return

    stdscr.addstr(24, 3, "Specify subtitle track language to confirm:", colors["header_string_color"])
    sub_lang = add_input_field(stdscr, 25, 3, 3)
    if sub_lang is None: # handling quitting during input
        return
    output_mkv = selected_media
    if sub_lang != "":
        if key in [68, 100]: # (D)ownload
            output_mkv = selected_media+ f" +sub {sub_lang}.mkv"
        elif key in [84, 116]: # (T)ranscode
            output_mkv = selected_media[:-1] + f" {sub_lang}).mkv"
    else:
        output_mkv = selected_media+".mkv"
    if (files_path/output_mkv).is_file():
        stdscr.addstr(27, 5, "File already present!", colors["anger_emoji_color"])
        stdscr.getch()
        return

    selected_media += ".mkv"
#    n_sub_streams = len(json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 's', '-show_entries', 'stream=index', '-of', 'json', files_path/selected_media], capture_output=True, text=True, check=True).stdout).get('streams', []))
    mkvmerge_command = [
        'mkvmerge', '-o', str(files_path/output_mkv), str(files_path/selected_media),
        '--language', f'0:{sub_lang}', '--track-name', f'0:{sub_title}',
        str(Path(config['subtitles_path']['value']/selected_sub))
    ]
#    ffmpeg_command = [
#        'ffmpeg', '-i', files_path/selected_media, '-i', Path(config['subtitles_path']['value']/selected_sub),
#        '-map', '0', '-map', '1:0', '-c', 'copy',
#        '-c:s', {'.ass': 'ass', '.ssa': 'ssa', '.srt': 'subrip', '.vtt': 'webvtt'}.get(Path(selected_sub).suffix.lower()),
#        f'-metadata:s:s:{n_sub_streams}', f'language={sub_lang}',
#        f'-metadata:s:s:{n_sub_streams}', f'title={sub_title}',
#        files_path/output_mkv
#    ]
    log_file = (
        open("ffmpeg-log", "a", encoding="utf-8")
        if config['enable_ffmpeg_debug_log']['value'] == 'y'
        else subprocess.DEVNULL
    )
    try:
        process = subprocess.Popen(mkvmerge_command, stdout=log_file, stderr=subprocess.DEVNULL) # (ffmpeg would use stderr), but it buggy with sub streams so
        dots = [".", "..", "..."]
        i = 0
        while process.poll() is None:
            stdscr.addstr(27, 5, dots[i % len(dots)], colors["unselected_entry_softer"])
            stdscr.refresh()
            i += 1
            time.sleep(0.2)
            stdscr.addstr(27, 6, " "*2)
        process.wait()
    finally:
        if log_file is not subprocess.DEVNULL: log_file.close()
    stdscr.addstr(27, 5, "Done!", colors['downloaded_torrent_color'])
    stdscr.refresh()
    stdscr.getch()

def load_indexers():
    indexers = {}
    for indexer, function in inspect.getmembers(fingers, inspect.isfunction):
        if not indexer.startswith("_"):
            indexers[indexer] = function

    return indexers

def indexers_menu(stdscr, indexers, indexer):
    stdscr.clear()
    min_indexerm_h = 30
    min_indexerm_w = 60
    check_terminal_size(stdscr, min_indexerm_h, min_indexerm_w)
    redraw_windows(stdscr)

    current_idx = 0
    h, w = stdscr.getmaxyx()

    for idx, row in enumerate(indexers):
        x = w//2 - len(row)//2
        y = max((16+idx*2), ((h-6)//2 - len(indexers)//2 + idx*2))
        if idx == current_idx:
            stdscr.addstr(y, x, row, colors["selected_menu_color"])
        else:
            if indexers[row] == indexer:
                stdscr.addstr(y, x, row, colors["seeders_text_color"])
            else:
                stdscr.addstr(y, x, row, colors["leechers_text_color"])
    while True:
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            check_terminal_size(stdscr, min_indexerm_h, min_indexerm_w)
        elif key == curses.KEY_UP:
            if current_idx == -1:
                current_idx = 0
            elif current_idx > 0:
                current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < len(indexers)-1:
            current_idx += 1
        elif key == curses.KEY_ENTER or key in [10,13]:
            indexer = list(indexers.values())[current_idx]
            return indexer
        elif key in [81, 113]: return indexer # (Q)uit to main menu

        stdscr.clear()
        redraw_windows(stdscr)
        for idx, row in enumerate(indexers):
            x = w//2 - len(row)//2
            y = max((16+idx*2), ((h-6)//2 - len(indexers)//2 + idx*2))
            if idx == current_idx:
                stdscr.addstr(y, x, row, colors["selected_menu_color"])
            else:
                if indexers[row] == indexer:
                    stdscr.addstr(y, x, row, colors["seeders_text_color"])
                else:
                    stdscr.addstr(y, x, row, colors["leechers_text_color"])

    return indexer

def edit_config_param(config_file, parameter, value):
    """Sets parameter with given value in config file"""
    with open(config_file, "r", encoding="utf-8") as f:
        document = tomlkit.parse(f.read())

    if isinstance(document[parameter], list):
        value = value.split()

    document[parameter] = value

    with open(config_file, "w", encoding="utf-8") as f:
        f.write(document.as_string())

def edit_config_menu(stdscr, config, config_file):
    stdscr.clear()
    min_confm_h = 46
    min_confm_w = 113
    if check_terminal_size(stdscr, min_confm_h, min_confm_w, ">:("):
        return
    redraw_windows(stdscr, h_alignment="left-aligned")

    stdscr.addstr(13, 0, config["download_path"]["def"], colors["config_display_def"])
    stdscr.addstr(14, 0, config["download_path"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
    stdscr.addstr(15, 0, config["download_path"]["ex"][0], colors["config_display_exs"])

    stdscr.addstr(17, 0, config["transcode_path"]["def"], colors["config_display_def"])
    stdscr.addstr(18, 0, config["transcode_path"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
    stdscr.addstr(19, 0, config["transcode_path"]["ex"][0], colors["config_display_exs"])

    stdscr.addstr(21, 0, config["subtitles_path"]["def"], colors["config_display_def"])
    stdscr.addstr(22, 0, config["subtitles_path"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
    stdscr.addstr(23, 0, config["subtitles_path"]["ex"][0], colors["config_display_exs"])

    stdscr.addstr(26, 0, config["wanted_languages"]["def"], colors["config_display_def"])
    stdscr.addstr(27, 0, config["wanted_languages"]["def2"], colors["config_display_def"])
    stdscr.addstr(28, 0, config["wanted_languages"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
    stdscr.addstr(29, 0, config["wanted_languages"]["ex"][0], colors["config_display_exs"])

    stdscr.addstr(32, 0, "Transcode Options: ffmpeg arguments for video and audio codecs to transcode media files into", colors["config_display_def"])

    stdscr.addstr(34, 0, config["transcode_input_accel"]["def"], colors["config_display_def"])
    stdscr.addstr(35, 0, config["transcode_input_accel"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
    stdscr.addstr(36, 0, config["transcode_input_accel"]["ex"][0], colors["config_display_exs"])

    stdscr.addstr(38, 0, config["transcode_video_args"]["def"], colors["config_display_def"])
    stdscr.addstr(39, 0, config["transcode_video_args"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
    stdscr.addstr(40, 0, config["transcode_video_args"]["ex"][0], colors["config_display_exs"])
    stdscr.addstr(41, 0, config["transcode_video_args"]["ex"][1], colors["config_display_exs"])

    stdscr.addstr(43, 0, config["transcode_audio_args"]["def"], colors["config_display_def"])
    stdscr.addstr(44, 0, config["transcode_audio_args"]["name"]+' = ', colors["header_string_color"])
    stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
    stdscr.addstr(45, 0, config["transcode_audio_args"]["ex"][0], colors["config_display_exs"])

    current_idx = -1
    h, w = stdscr.getmaxyx()
    while True:
        key = stdscr.getch()


        if key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            if check_terminal_size(stdscr, min_confm_h,	min_confm_w):
                return
        elif key == curses.KEY_UP:
            if current_idx == -1:
                current_idx = 0
            elif current_idx > 0:
                current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < 6:
            current_idx += 1
        elif key == curses.KEY_ENTER or key in [10,13]:
            stdscr.addstr(25, 45, "Don't write anything to abort change", colors["leechers_text_color"])
            if current_idx == 0: # download_path
                value = add_input_field(stdscr, 14, 16, w-16-13)
                if value is None: # handling quitting during input
                    return
                if value.strip() == "": # handling quitting edit
                    stdscr.addstr(14, 16, " "*(w-16))
                    stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "download_path", value)
                    config = load_config(config_file)
                stdscr.addstr(14, 16, " "*(w-16))
                stdscr.addstr(14, 16, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
            elif current_idx == 1: # transcode_path
                value = add_input_field(stdscr, 18, 17, w-17-13)
                if value is None: # handling quitting during input
                    return
                if value.strip() == "":
                    stdscr.addstr(18, 17, " "*(w-17))
                    stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "transcode_path", value)
                    config = load_config(config_file)
                stdscr.addstr(18, 17, " "*(w-17))
                stdscr.addstr(18, 17, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
            elif current_idx == 2: # subtitles_languages
                value = add_input_field(stdscr, 22, 17, w-17-13)
                if value is None: # handling quitting during input
                    return
                if value.strip() == "":
                    stdscr.addstr(22, 17, " "*(w-17))
                    stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "wanted_languages", value)
                    config = load_config(config_file)
                stdscr.addstr(22, 17, " "*(w-17))
                stdscr.addstr(22, 17, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
            elif current_idx == 3: # wanted_languages
                value = add_input_field(stdscr, 28, 19, w-19-13)
                if value is None: # handling quitting during input
                    return
                if value.strip() == "":
                    stdscr.addstr(28, 19, " "*(w-19))
                    stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "wanted_languages", value)
                    config = load_config(config_file)
                stdscr.addstr(28, 19, " "*(w-19))
                stdscr.addstr(28, 19, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
            elif current_idx == 4: # transcode_input_accel
                value = add_input_field(stdscr, 35, 24, w-24-13)
                if value is None: # handling quitting during input
                    return
                if value == "":
                    stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
                    stdscr.addstr(35, 24, " "*(w-24))
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "transcode_input_accel", value)
                    config = load_config(config_file)
                stdscr.addstr(35, 24, " "*(w-24))
                stdscr.addstr(35, 24, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
            elif current_idx == 5: # transcode_video_args
                value = add_input_field(stdscr, 39, 23, w-23-13)
                if value is None: # handling quitting during input
                    return
                if value.strip() == "":
                    stdscr.addstr(39, 23, " "*(w-23))
                    stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "transcode_video_args", value)
                    config = load_config(config_file)
                stdscr.addstr(39, 23, " "*(w-23))
                stdscr.addstr(39, 23, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
            elif current_idx == 6: # transcode_audio_args
                value = add_input_field(stdscr, 44, 23, w-23-13)
                if value is None: # handling quitting during input
                    return
                if value.strip() == "":
                    stdscr.addstr(44, 23, " "*(w-23))
                    stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
                    stdscr.addstr(25, 45, " "*36)
                    stdscr.refresh()
                    continue
                else:
                    edit_config_param(config_file, "transcode_audio_args", value)
                    config = load_config(config_file)
                stdscr.addstr(44, 23, " "*(w-23))
                stdscr.addstr(44, 23, value, colors["config_display_val"])
                stdscr.addstr(25, 45, " "*36)
                stdscr.refresh()
        elif key in [81, 113]: return # (Q)uit to main menu

        # i'm sorry
        if current_idx == 0:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"] | curses.A_REVERSE)
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
        elif current_idx == 1:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"] | curses.A_REVERSE)
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
        elif current_idx == 2:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"] | curses.A_REVERSE)
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
        elif current_idx == 3:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"] | curses.A_REVERSE)
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
        elif current_idx == 4:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"] | curses.A_REVERSE)
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
        elif current_idx == 5:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"] | curses.A_REVERSE)
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"])
        elif current_idx == 6:
            stdscr.addstr(14, 16, config["download_path"]["value"], colors["config_display_val"])
            stdscr.addstr(18, 17, config["transcode_path"]["value"], colors["config_display_val"])
            stdscr.addstr(22, 17, config["subtitles_path"]["value"], colors["config_display_val"])
            stdscr.addstr(28, 19, ' '.join([v for v in config["wanted_languages"]["value"]]), colors["config_display_val"])
            stdscr.addstr(35, 24, ' '.join([v for v in config["transcode_input_accel"]["value"]]), colors["config_display_val"])
            stdscr.addstr(39, 23, ' '.join([v for v in config["transcode_video_args"]["value"]]), colors["config_display_val"])
            stdscr.addstr(44, 23, ' '.join([v for v in config["transcode_audio_args"]["value"]]), colors["config_display_val"] | curses.A_REVERSE)
        stdscr.refresh()


#TODO: refactor
#      - curses draw pipeline: call `redraw_windows` only when key `RESIZE` is triggered,, and always have menu contents reprinted each While True loop
#      - elif key == ord('\x1b'): # if esc, quit
#      - normalize to draw-loop-template
def main(stdscr):
    curses.curs_set(0) # disable cursor blinking

    config_file = "config2.toml"
    config = load_config(config_file)

    indexers = load_indexers()
    indexer = indexers["nyaa"]

    menu_entries = ['Download', 'Transcode (Quality)', 'Transcode (+ Language)', 'Embed Subtitle', 'Indexer', 'Edit Config', 'Exit']
    current_idx = 0
    h, w = stdscr.getmaxyx()
    min_mainm_h = 30
    min_mainm_w = 60
    check_terminal_size(stdscr, min_mainm_h, min_mainm_w)
    print_menu(stdscr, menu_entries, current_idx)

    # handle user input for navigating main menu
    while True:
        key = stdscr.getch()
        stdscr.clear()

        if key == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            check_terminal_size(stdscr, min_mainm_h, min_mainm_w)
        elif key == curses.KEY_UP and current_idx > 0:
            current_idx -= 1
        elif key == curses.KEY_DOWN and current_idx < len(menu_entries)-1:
            current_idx += 1
        elif key == curses.KEY_ENTER or key in [10,13]:
            if current_idx == 0: # Download
                if config['download_path']['value'].strip() == "" or config['download_path']['value'] == "/path/to/folder":
                    stdscr.clear()
                    warn_string = "`download_path` must be set!"
                    warn_y_pos = h//2
                    warn_x_pos = max(0, (w-len(warn_string))//2)
                    stdscr.addstr(warn_y_pos, warn_x_pos, warn_string, colors['anger_emoji_color'])
                    continue
                download_menu(stdscr, 13, h-13-6, config, indexer)
            if current_idx == 1: # Transcode (Quality)
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
            if current_idx == 2: # Transcode (+Language)
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
            if current_idx == 3: # Embed Subtitle
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
            if current_idx == 4: # Indexer
                indexer = indexers_menu(stdscr, indexers, indexer)
            if current_idx == 5: # Edit Config
                edit_config_menu(stdscr, config, config_file)
                config = load_config(config_file)
            stdscr.refresh()
            if current_idx == len(menu_entries)-1: # exit
                break
        elif key == 81 or key == 113: # q to exit
            break

        check_terminal_size(stdscr, min_mainm_h, min_mainm_w)
        print_menu(stdscr, menu_entries, current_idx)
        stdscr.refresh()

curses.wrapper(main)
