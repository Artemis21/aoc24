"""Utils for getting puzzle inputs and submitting solutions."""
from __future__ import annotations

import json
import pathlib
import re
import os
import time
import webbrowser
from typing import Literal, TypedDict, Any

import bs4
import rich
import requests
import dotenv


class _SubmissionCacheEntry(TypedDict):
    """A cache entry for a submission."""

    message: str
    colour: str
    is_correct: bool


class _Cache(TypedDict):
    """A local JSON cache for puzzle inputs and submission responses."""

    inputs: dict[str, str]
    submissions: dict[str, dict[str, _SubmissionCacheEntry]]


_ROOT_PATH = pathlib.Path(__file__).parent
_CACHE_FILE = _ROOT_PATH / "cache.json"

_cache: _Cache
try:
    with open(_CACHE_FILE) as f:
        _cache = json.load(f)
except FileNotFoundError:
    _cache = {"inputs": {}, "submissions": {}}

_input_cache = _cache["inputs"]
_submission_cache = _cache["submissions"]

dotenv.load_dotenv(_ROOT_PATH / ".env")
_SESSION_TOKEN = os.getenv("AOC_TOKEN")
if not _SESSION_TOKEN:
    raise ValueError("Missing AOC_TOKEN environment variable.")

_URL = "https://adventofcode.com/2016/day/{day}{endpoint}"


def get_input(day: int) -> str:
    """Get the raw input for a given day.

    Inputs are cached in the INPUTS_FILE.
    """
    if (day_key := str(day)) in _input_cache:
        return _input_cache[day_key]
    input = _request("GET", day, "/input").strip("\n")
    _input_cache[day_key] = input
    _commit_cache()
    return input


def submit(day: int, part: int, solution: object):
    """Interactively submit a solution to a given part."""
    part_key = f"{day}-{part}"
    if part_key not in _submission_cache:
        _submission_cache[part_key] = {}
    part_cache = _submission_cache[part_key]
    soln_key = str(solution)
    if soln_key in part_cache:
        _SubmissionResponse.from_cache(part_cache[soln_key]).display()
        return
    if not _sanity_check(solution, part_cache):
        return
    while True:
        rich.print(f"Submitting {soln_key} as solution to day {day} part {part}:")
        response = _request("POST", day, "/answer", {"level": str(part), "answer": soln_key})
        message = _SubmissionResponse.parse(response)
        if isinstance(message, _SubmissionRatelimitResponse):
            message.display()
            continue
        break
    part_cache[soln_key] = message.as_cache_entry()
    _commit_cache()
    message.display()
    if part == 1 and message.correct and message.fresh:
        part_2_url = _URL.format(day=day, endpoint="#part2")
        webbrowser.open(part_2_url)


def _commit_cache():
    """Commit the cache to the cache file."""
    with open(_CACHE_FILE, "w") as f:
        json.dump(_cache, f, indent=4)


def _request(
    method: Literal["GET", "POST"],
    day: int,
    endpoint: str,
    data: dict[str, Any] | None = None
) -> str:
    """Make a request to a given endpoint for a given day."""
    response = requests.request(
        method=method,
        url=_URL.format(day=day, endpoint=endpoint),
        cookies={"session": _SESSION_TOKEN},
        data=data,
    )
    if not response.ok:
        raise ValueError(f"Bad server response code: {response.text}.")
    return response.text


def _sanity_check(solution: object, part_cache: dict[str, _SubmissionCacheEntry]) -> bool:
    if isinstance(solution, str) and len(solution) < 5:
        confirmed = _confirm_solution(solution, "short string")
    elif isinstance(solution, int) and -50 < solution < 50:
        confirmed = _confirm_solution(solution, "small integer")
    elif not isinstance(solution, (str, int)):
        confirmed = _confirm_solution(solution, "not str or int")
    elif any(submission["is_correct"] for submission in part_cache.values()):
        confirmed = _confirm_solution(solution, "already solved")
    else:
        confirmed = True
    if not confirmed:
        rich.print("[red]Submission cancelled.")
        return False
    return True


def _confirm_solution(solution: object, reason: str) -> bool:
    """Confirm the submission of a solution."""
    rich.print(f"[yellow]Are you sure you want to submit '{solution}' ({reason})?", end=" [Y/n] ")
    return not input().lower().startswith("n")


class _SubmissionResponse:
    """A response from a submission request."""

    @classmethod
    def parse(cls, response: str) -> _SubmissionResponse:
        """Parse a server response to a submission."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        if not soup.article:
            raise ValueError(f"Failed to parse server response: {response}.")
        message = soup.article.text.replace("\n", "").strip()
        if message.startswith("You gave"):
            wait_re = r"You have (?:(\d+)m )?(\d+)s left to wait."
            (minutes, seconds), = re.findall(wait_re, message)
            return _SubmissionRatelimitResponse(message, minutes, seconds)
        if message.startswith("That's the"):
            return cls("green", message, correct=True, fresh=True)
        elif message.startswith("You don't"):
            return cls("yellow", message, correct=False, fresh=True)
        elif message.startswith("That's not"):
            return cls("red", message, correct=False, fresh=True)
        else:
            raise ValueError(f"Failed to parse server message: {message}.")

    @classmethod
    def from_cache(cls, cache_entry: _SubmissionCacheEntry) -> _SubmissionResponse:
        """Return a submission response from a cache entry."""
        return cls(
            cache_entry["colour"],
            cache_entry["message"],
            cache_entry["is_correct"],
            fresh=False,
        )

    def __init__(self, colour: str, message: str, correct: bool, fresh: bool):
        """Store the message for the response."""
        self.colour = colour
        self.message = message
        self.correct = correct
        self.fresh = fresh

    def display(self):
        """Print the message."""
        prefix = "" if self.fresh else "[italic]Cached response: [/]"
        rich.print(f"{prefix}[bold {self.colour}]{self.message}")

    def as_cache_entry(self) -> _SubmissionCacheEntry:
        """Return the response as a cache entry."""
        return {
            "colour": self.colour,
            "message": self.message,
            "is_correct": self.correct,
        }


class _SubmissionRatelimitResponse(_SubmissionResponse):
    """A response indicating we should retry after a give time period."""

    def __init__(self, message: str, minutes: str, seconds: str):
        """Store the data for the response."""
        self.minutes = int(minutes or "0")
        self.seconds = int(seconds)
        super().__init__("yellow", message, correct=False, fresh=True)

    def display(self):
        """Wait the given time after printing the message."""
        super().display()
        rich.print(f"Waiting {self.minutes}m {self.seconds}s seconds to retry...")
        time.sleep(self.minutes * 60 + self.seconds)
