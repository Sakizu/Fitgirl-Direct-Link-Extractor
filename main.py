import requests
import os
import sys
import re
import pyperclip
from bs4 import BeautifulSoup
from datetime import datetime
from colorama import Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed


class console:
    def __init__(self) -> None:
        self.colors = {
            "green": Fore.GREEN,
            "red": Fore.RED,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
            "black": Fore.BLACK,
            "reset": Style.RESET_ALL,
            "lightblack": Fore.LIGHTBLACK_EX,
            "lightred": Fore.LIGHTRED_EX,
            "lightgreen": Fore.LIGHTGREEN_EX,
            "lightyellow": Fore.LIGHTYELLOW_EX,
            "lightblue": Fore.LIGHTBLUE_EX,
            "lightmagenta": Fore.LIGHTMAGENTA_EX,
            "lightcyan": Fore.LIGHTCYAN_EX,
            "lightwhite": Fore.LIGHTWHITE_EX,
        }

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def success(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightgreen']}SUCC {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightgreen']}{obj}{self.colors['reset']}")

    def error(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightred']}ERRR {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightred']}{obj}{self.colors['reset']}")

    def done(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightmagenta']}DONE {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightmagenta']}{obj}{self.colors['reset']}")

    def warning(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightyellow']}WARN {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightyellow']}{obj}{self.colors['reset']}")

    def info(self, message, obj):
        print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightblue']}INFO {self.colors['lightblack']}• {self.colors['white']}{message} : {self.colors['lightblue']}{obj}{self.colors['reset']}")

    def input(self, message):
        return input(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightcyan']}INPUT • {self.colors['white']}{message}{self.colors['reset']}")


log = console()
log.clear()

url = log.input("Enter Fitgirl Game Link : ")

try:
    r = requests.get(url, timeout=30)
except Exception as e:
    log.error("Request Failed", e)
    sys.exit()

soup = BeautifulSoup(r.text, "html.parser")

text_span = soup.find(
    "span",
    string=lambda s: s and "REALLY Fucking Fast" in s
)

if not text_span:
    log.error("Text Not Found", "REALLY Fucking Fast")
    sys.exit()

spoiler = text_span.find_next(
    "div",
    class_="su-spoiler"
)

if not spoiler:
    log.error("Spoiler Container Not Found", "su-spoiler")
    sys.exit()

links = [
    a["href"]
    for a in spoiler.find_all("a", href=True)
    if a["href"].startswith("https://fuckingfast.co/")
]

if not links:
    log.error("No Matching URLs Found", "Retry")
    sys.exit()

log.success("Found FuckingFast Links", len(links))


def get_direct_link(url):
    try:
        r = requests.get(url, timeout=30)

        match = re.search(
            r'window\.open\("(https://fuckingfast\.co/dl/[^"]+)"',
            r.text
        )

        if match:
            return match.group(1)

    except Exception:
        return None

    return None


direct_links = []
total = len(links)

log.info("Resolving Direct Links", total)

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(get_direct_link, link): link for link in links}

    for i, future in enumerate(as_completed(futures), 1):

        result = future.result()

        if result:
            direct_links.append(result)
            log.success("Direct Link", result)
        else:
            log.warning("Failed", futures[future])

        log.info("Progress", f"{i}/{total}")


if direct_links:

    output = "\n".join(direct_links)

    print("\n🔗 Direct Download Links:\n")
    print(output)

    with open("direct.txt", "w", encoding="utf-8") as f:
        f.write(output)

    log.success("Saved To File", "direct.txt")

    pyperclip.copy(output)

    log.done("Links Copied To Clipboard", len(direct_links))

else:
    log.error("No Direct Links Extracted", "Retry")
