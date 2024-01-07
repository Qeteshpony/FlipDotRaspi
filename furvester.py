import time
from datetime import timedelta, datetime
from random import randint
from asciiconverter import converter

from flipdot.framebuf import FrameBuffer
import flipdot
from requests_cache import CachedSession

URL_LEADS = "https://convention.api.furvester.org/game/leaderboard"
URL_STATS = "https://convention.api.furvester.org/game/bloop-statistics"
ACHIEVEMENT = "2764518326123855"

NEW_YEAR = datetime(2024,1,1,0,0,0)

class Furvester:
    def __init__(self, display: "flipdot.FlipDot"):
        self.session = CachedSession(
            cache_control=True,
            expire_after=timedelta(seconds=60),
            backend="memory",
        )
        self.display = display
        self.pageWaitTime = 5
        self.pageNextTime = 0
        self.page = 0
        self.achievementtimermin = 50
        self.achievementtimermax = 100
        self.achievementtimer = randint(self.achievementtimermin, self.achievementtimermax)

        # calculate statistics
        seconds = 0.0
        pages = self.get_pages()
        for page in pages:
            seconds += page[1]
        ppm = 60 / seconds * len(pages)
        print(f"Displaying {len(pages)} pages in {seconds:0.1f} seconds. "
              f"That is ~{ppm:0.1f} pages per minute")
        print(f"The achievement-code will be visible every {self.achievementtimermin/ppm*60:0.0f} "
              f"to {self.achievementtimermax/ppm*60:0.0f} seconds.")

    def get_leaders(self, place: int = 0, limit: int = 3) -> tuple[str, int]:
        response = self.session.get(URL_LEADS + "?limit=" + str(limit))
        result = response.json()
        data = result.get("data")
        if data:
            try:
                entry = data[place]
            except IndexError:
                entry = None
            if entry is not None:
                identity = entry.get("identity")
                if identity:
                    name = converter(identity.get("nickname"))
                else:
                    name = "Anonymous"
                points = entry.get("points")
                return name, points
        return "N/A", 0

    def get_stats(self, stat: str) -> int:
        response = self.session.get(URL_STATS)
        result = response.json()
        data = result.get("data")
        if data:
            return data.get(stat)
        else:
            return 0

    def screen(self):
        if self.pageNextTime < time.time():
            pages = self.get_pages()
            self.achievementtimer -= 1
            if self.achievementtimer == 0:
                self.achievementtimer = randint(self.achievementtimermin, self.achievementtimermax)
                self.achievementcode()
            text, seconds = pages[self.page]
            self.display.text(text, show=False, cutoff=True)
            self.display.transition_scroll()
            self.pageNextTime = time.time() + seconds
            self.page += 1
            if self.page >= len(pages):
                self.page = 0

    def get_pages(self):
        pages = [
            ("1st Place:", 1),
            (f"{self.get_leaders(0)[0]}", 2),
            (f"{self.get_leaders(0)[1]} Points", 2),
            (" ", 0),
            ("2nd Place:", 1),
            (f"{self.get_leaders(1)[0]}", 2),
            (f"{self.get_leaders(1)[1]} Points", 2),
            (" ", 0),
            ("3rd Place:", 1),
            (f"{self.get_leaders(2)[0]}", 2),
            (f"{self.get_leaders(2)[1]} Points", 2),
            (" ", 0),
            (f"Total:", 1),
            (f"{self.get_stats('totalGlobalBloops')} Boops", 2),
            (" ", 0),
            (f"Last 24 hours:", 1),
            (f"{self.get_stats('bloopsLastDay')} Boops", 2),
            (" ", 0),
            (f"Last hour:", 1),
            (f"{self.get_stats('bloopsLastHour')} Boops", 2),
            (" ", 0),
            (f"Dragon = PQRS", .2),
            (" ", 0),
            (time.strftime("%a %d. %b %H:%M"), 5),
            (" ", 0),
        ]
        if datetime.now() > NEW_YEAR:
            pages += [
                ("HAPPY NEW YEAR!!!", 5),
                (" ", 0),
            ]

        return pages

    def achievementcode(self):
        buffer = FrameBuffer(self.display.width, self.display.height)
        buffer.copy_buffer(self.display, 0, 0)
        self.display.text(ACHIEVEMENT)
        self.display.copy_buffer(buffer, 0, 0)
        self.display.show()

