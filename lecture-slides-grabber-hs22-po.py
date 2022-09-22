# Author: Renato Farruggio

import urllib.request
import os

debug = False

def get_settings() -> (str, str, str):
    website_link = ""
    screen_or_printer = ""
    with open(filename_settings, "rt") as f:
        for line in f.readlines():
            line = line.strip()

            try:
                (key, value) = line.split(": ")
            except ValueError:
                continue
            if key == "dmi-link":
                website_link = value
            elif key == "screen-or-printer":
                screen_or_printer = value
            else:
                print("Unknown key in", filename_settings + ". Unknown key:", key)

    global debug
    if debug:
        print("Loaded settings:")
        print("dmi_link =", website_link)
        print("[SCREEN / PRINTER] =", screen_or_printer)
        print("===================================")

    if website_link == "":
        return exit("ERROR: No link specified for dmi slides! Please make an entry in " + filename_settings + " called 'dmi-link'.")
    if screen_or_printer == "":
        return exit("ERROR: Please specify whether you want the 'screen' or 'printer' version of the slides! Please make an entry in " + filename_settings + " called 'screen-or-printer'.")

    return (website_link, screen_or_printer)

def get_example_download_link_prefix(webContent) -> str:
    keywords = ['No', 'Topic', 'Date', 'Slides']
    link = webContent
    for keyword in keywords:
        link = link.split(keyword, 1)[1]

    # Link now: </th></tr></thead><tbody><tr><td>0</td><td>Organizational Matters</td><td>17.2.</td><td>
    # <a href="http://ai.dmi.unibas.ch/_files/teaching/fs20/ai/slides/ai00.pdf" title="screen version" target="_blank"

    link = link.split('"', 2)[1]
    # Now: http://ai.dmi.unibas.ch/_files/teaching/fs20/ai/slides/ai00.pdf

    link = link.rsplit("/", 1)[0] + '/'
    # Now: http://ai.dmi.unibas.ch/_files/teaching/fs20/ai/slides/

    global debug
    if debug:
        print("Found this prefix of a link to slides: ", link)
    return link

def find_all(a_str, sub):
    # Iterable version of str.find().
    # Taken from https://stackoverflow.com/a/4665027
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)

def extract_links(a_str: str, indices: []) -> [str]:
    all_links = []
    for i in indices:
        all_links.append(a_str[i:].split('"')[0])


    # Filter by pdf type
    array_to_return = all_links
    if screen_or_printer.lower() == "screen":
        array_to_return = [a for a in all_links if "handout" not in a]
    elif screen_or_printer.lower() == "printer":
        array_to_return = [a for a in all_links if "handout" in a.rsplit("/", 1)[1]]
    return array_to_return

def extract_titles(website_source, links) -> [str]:
    array_to_return = []
    for link in links:
        link_short = link.rsplit("/", 1)[0] + "/" + link.rsplit("/", 1)[1][:-4]  # http://ai.dmi.unibas.ch/_files/teaching/fs21/ai/slides/ai00
        index = website_source.find(link_short)
        # title first line:
        # le="printer version" target="_blank">printer</a></td></tr><tr><td rowspan="1">5</td><td rowspan="1"><span>State-Space Search: State Spaces</span></td><td rowspan="1">8.3.</td><td rowspan="1"><a href="

        # title second line:
        # rowspan="1"><span>State-Space Search: State Spaces</span></

        # title third line:
        # rowspan="1">State-Space Search: State Spaces</

        # title forth line:
        # State-Space Search: State Spaces

        title = website_source[index-200:index]\
            .split("td")[-5]\
            .replace("<span>", "").replace("</span>", "")\
            .rsplit(">")[1].split("<")[0]
            
        if debug:
            print("Title in website:", website_source[index-200:index].split("td")[-5])
            print("Title so far:", title)

        # Clean document name
        title = title\
            .replace(":", "")\
            .replace(" ", "_")\
            .replace("&amp;", "&")\
            .replace('\\xe2\\x88\\x97', '*')\
            .replace('*', '_star_')\
            .replace(',', '-')\
            .replace('__', '_')\
            .replace('?', '')\
            .rstrip('_')
        
        if debug:
            print("Title after cleaning:", title)

        array_to_return.append(link.rsplit("/", 1)[1][:-4] + "_" + title)
    return array_to_return

def download_file(download_url, filename):
    downloaded_file = urllib.request.urlopen(download_url)
    with open(filename + ".pdf", "wb") as f:
        f.write(downloaded_file.read())

# LOAD SETTINGS
filename_settings = "settings.txt"
keyword_screen = ".pdf"
keyword_printer = "-handout.pdf"
(url, screen_or_printer) = get_settings()

# LOAD WEBSITE
response = urllib.request.urlopen(url)
webContent = str(response.read())

# FIND url_search
url_search = get_example_download_link_prefix(webContent)

# FIND ALL OCCURENCES OF WEBSITES OF THE FORM url_search
indices = list(find_all(webContent, url_search))
if debug:
    print("Indices:", indices)

# FIND LINKS
links_to_download = extract_links(webContent, indices)
if debug:
    for link in links_to_download:
        print("Download link:", link)
    print("============================")

# FIND TITLES
titles = extract_titles(webContent, links_to_download)
if debug:
    print("============================")
    print("List of all titles found:")
    for title in titles:
        print(title)
    print("============================")

# DOWNLOAD AND RENAME FILES
for (download_url, filename) in zip(links_to_download, titles):
    if filename + ".pdf" not in os.listdir():
        print("Downloading:", filename)
        download_file(download_url, filename)
    else:
        print("File already downloaded:", filename)

print("Done.")
