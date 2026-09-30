import libtorrent as lt
import time

def format_speed(kbs_download_rate):
    """formats kB/s speeds up to 999 GB/s"""
    units = ["kB/s", "MB/s"] # + GB/s

    speed = float(kbs_download_rate)

    for unit in units:
        if speed < 1000:
            return f"{speed:6.2f}{unit}"
        speed /= 1000
    return f"{speed:6.2f}GB/s" # congrats if you manage more than 999 GB/s, you've broken the program!

def download_torrent(infohash, download_path, callback):
    """downloads a torrent given infohash and a download path, expects a function to handle callback status as its third argument"""
    # initialize libretorrent session
    settings = {
        "enable_dht": True, # peer finding
        "enable_lsd": True, # local device sharing
        "enable_upnp": True, # auto-opening ports fuckery
        "enable_natpmp": True # auto-forwarding ports fuckery #2
    }
    session = lt.session(settings)

    # turn infohash into sha1 to pass to libretorrent
    infohash = lt.sha1_hash(bytes.fromhex(infohash))

    # set torrent's infohash and download path
    params = lt.add_torrent_params()
    params.info_hashes = lt.info_hash_t(infohash)
    params.save_path = download_path
    # add torrent to session
    torrent = session.add_torrent(params)

    # get torrent status as it downloads
    while True:
        status = torrent.status()

        progress = status.progress * 100
        download_rate = status.download_rate / 1000
        peers = status.num_peers
        formatted_speed = format_speed(download_rate)

        # pass each new dictionary to callback function // get_progress(status): print(status['progress'], status['download_speed'], status['peers'])
        callback({
            "progress": f"{progress:6.2f}%",
            "download_speed": f"{formatted_speed}",
            "peers": f"{peers:2.0f}"
        })
#        time.sleep(0.1)

        # once done, exit and remove torrent
        if status.is_seeding:
            break

    session.remove_torrent(torrent)
