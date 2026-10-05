<img width="38%" src="https://github.com/user-attachments/assets/488ade72-dc5f-407a-82d0-29007754753f" />

Fancy pyCurses TUI to facilitate media archiving by semi-automating downloading and transcoding

Fueled by the frustration of ideal releases never being available on public trackers browsed through the \*arr stack <sup>(thus, **arr**gh)</sup>

\> "I'll make my own releases then"<br />
\> how is there not a simple, straightforward tool for that?<br />
\> I'll make my own then!

Initially, I had planned to implement automatic fetching, downloading and merging of audio & subs tracks, but relying on unpredictable parsers has never sat right with me, so I rather go with a semi automated approach, that allows curating a library how one prefers it.

---

<details>
<summary>Main Features</summary>

### Download

<img width="69%" src="https://github.com/user-attachments/assets/dee2f770-2127-4ecc-8185-8cf77c2fdc60" />

### Transcode & Merge

<img width="69%" src="https://github.com/user-attachments/assets/c9d73ce3-1a01-4ed6-9dcc-03a8b76f1950" />


### Indexers
Currently only Nyaa.si is supported by default, but you can implement your own! <sup>and contributions are appreciated!</sup>
You can do so by following the template in the [indexers file](https://github.com/Not-Glunk/arrgh/blob/main/fingers.py#L48) and writing a function which given a search query as input, returns a list of dictionaries containing the torrents' info structured as follows:
<sup>I will likely be implementing ext.to, but it'll be janky</sup>
```py
"title": "Made in Abyss S01"
"pubDate": "Wed 2026-09-30, 15:37"
"seeders": "48"
"leechers": "5"
"completed": "420"
"infoHash": "ac5463f76633fb3906d4a129e96a766a4b19be7b"
"size": "505.3 MiB"
```
</details>

---

<details>
<summary>Installation</summary>

To install, just `pip install -r requirements.txt`, and make sure to have ffmpeg & ffprobe <sup>and mkvmerge</sup> in your path, then run `python3 arrgh.py`

</details>

---

<details>
<summary>Known bugs</summary>
  
- smaaall chance for short lived torrents, such as small or already completed ones, to just completely freeze your terminal window or blurt out randomly colored character sequences :D
      known reason? no

- asian (or otherwise of non-standard monospace width) unicode characters have been handled, but they still sometimes break truncation or line-wrap, just a cosmetic issue though

</details>
