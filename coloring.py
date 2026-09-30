import curses

def init_colors():
    """Initializes app's color pairs by returning a dictionary containing them"""
    curses.initscr()
    curses.start_color()

    # title
    curses.init_pair(1, 33, curses.COLOR_BLACK) # title text color --> xterm 33
    curses.init_pair(2, 160, curses.COLOR_BLACK) # :anger: emoji color --> xterm 160
    curses.init_pair(3, 124, curses.COLOR_BLACK) # fire color first --> xterm 124
    curses.init_pair(4, 166, curses.COLOR_BLACK) # fire color second --> xterm 166
    curses.init_pair(5, 94, curses.COLOR_BLACK) # fire color third --> xterm 94
    curses.init_pair(6, 237, curses.COLOR_BLACK) # smoke color first --> xterm 237

    # menu
    curses.init_pair(10, 39, curses.COLOR_BLACK) # entry text color --> xterm 39
    curses.init_pair(11, curses.COLOR_BLACK, 45) # selected menu color --> xterm 45

    # search field
    curses.init_pair(20, 45, curses.COLOR_BLACK) # input text foreground --> xterm 45, 238
    curses.init_pair(21, 239, curses.COLOR_BLACK) # input text background --> xterm 238
    curses.init_pair(30, 237, curses.COLOR_BLACK) # quit search color --> xterm 237

    # search_results entries table
    curses.init_pair(22, 235, curses.COLOR_BLACK) # borderline color --> xterm 235
    curses.init_pair(23, 72, curses.COLOR_BLACK) # header string color --> xterm 72
    curses.init_pair(24, 66, curses.COLOR_BLACK) # unselected entry color --> xterm 66
    curses.init_pair(25, 52, curses.COLOR_BLACK) # leechers text color --> xterm 52
    curses.init_pair(26, 22, curses.COLOR_BLACK) # seeders text color --> xterm 22
    curses.init_pair(27, 23, curses.COLOR_BLACK) # unselected entry softer --> xterm 23
    curses.init_pair(28, curses.COLOR_BLACK, 38) # selected entry color --> xterm 38
    curses.init_pair(29, 24, curses.COLOR_BLACK) # selected full entry --> xterm 24
    curses.init_pair(31, 167, curses.COLOR_BLACK) # downloaded torrent color --> xterm 167
    curses.init_pair(32, 131, curses.COLOR_BLACK) # downloading torrent color --> xterm 131

    # config display
    curses.init_pair(40, 32, curses.COLOR_BLACK) # config display defs --> xterm 26
    curses.init_pair(41, 25, curses.COLOR_BLACK) # config display exs --> xterm 25
    curses.init_pair(42, 67, curses.COLOR_BLACK) # config display val --> xterm 67
    curses.init_pair(43, 68, curses.COLOR_BLACK) # config display input --> xterm 68

    return { # colors = init_colors()
        # title
        "title_text_color": curses.color_pair(1), # colors["title_text_color"]
        "anger_emoji_color": curses.color_pair(2),
        "fire_color_first": curses.color_pair(3),
        "fire_color_second": curses.color_pair(4),
        "fire_color_third": curses.color_pair(5),
        "smoke_color_first": curses.color_pair(6),

        # menu
        "entry_text_color": curses.color_pair(10),
        "selected_menu_color": curses.color_pair(11),

        # search field
        "input_text_foreground": curses.color_pair(20),
        "input_text_background": curses.color_pair(21),
        "quit_search_color": curses.color_pair(30),

        # search_results entries table
        "border_line_color": curses.color_pair(22),
        "header_string_color": curses.color_pair(23),
        "unselected_entry_color": curses.color_pair(24),
        "leechers_text_color": curses.color_pair(25),
        "seeders_text_color": curses.color_pair(26),
        "unselected_entry_softer": curses.color_pair(27),
        "selected_entry_color": curses.color_pair(28),
        "selected_full_entry": curses.color_pair(29),
        "downloaded_torrent_color": curses.color_pair(31),
        "downloading_torrent_color": curses.color_pair(32),

        # config display
        "config_display_def": curses.color_pair(40),
        "config_display_exs": curses.color_pair(41),
        "config_display_val": curses.color_pair(42)
    }
