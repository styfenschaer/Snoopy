import shutil
import sys
import threading
import time
from dataclasses import dataclass, field

from .terminal import Commands

elapsed_template = "Elapsed [sec]: {:.1f}\r"

dots_template = (
    "\033[KWorking on it\r",
    "Working on it.\r",
    "Working on it..\r",
    "Working on it...\r",
)

rotate_template = (
    "\033[KWorking on it |\r",
    "Working on it /\r",
    "Working on it -\r",
    "Working on it \\\r",
)


def dog_string(position: int = 0):
    lines = f"""       {Commands.CLEAR_LINE}
             .--~~,__  {Commands.CLEAR_LINE}
:-....,-------`~~'._.' {Commands.CLEAR_LINE}
 `-,,,  ,_      ;'~U'  {Commands.CLEAR_LINE}
  _,-' ,'`-__; '--.    {Commands.CLEAR_LINE}
 (_/'~~      ''''(;    {Commands.CLEAR_LINE}{Commands.MOVE_UP * 4}
""".splitlines()
    return "\n".join(" " * position + line for line in lines[1:])


def make_dog_template(niter: int):
    longest = max(dog_string().splitlines(), key=len)
    stop = shutil.get_terminal_size()[0] - len(longest)
    return tuple(dog_string(n) for n in range(0, stop, stop // niter))


dog_template = make_dog_template(niter=30)


class _ProgressTemplate:
    def __init__(self, tempalte: str):
        if isinstance(tempalte, str):
            tempalte = (tempalte,)

        self.count = -1
        self.tmpl = tempalte
        self.n = len(self.tmpl)

    def reset(self):
        self.count = -1
        self._move_to_template_end()

    def _move_to_template_end(self):
        n = len(self.tmpl[0].splitlines())
        sys.stdout.write(Commands.MOVE_DOWN * n + "\n")

    def format(self, *args):
        self.count += 1
        return self.tmpl[self.count % self.n].format(*args)


class _ThreadTimer(threading.Thread):
    def __init__(self, tmpl: _ProgressTemplate, time_sleep: float):
        super().__init__()
        self.event = threading.Event()
        self.tmpl = tmpl
        self.time_sleep = time_sleep

    def run(self):
        self.tic = time.time()
        while not self.event.is_set():
            elapsed = time.time() - self.tic
            sys.stdout.write(self.tmpl.format(elapsed))
            time.sleep(self.time_sleep)

    def stop(self):
        self.event.set()
        sys.stdout.write("\n")


@dataclass
class _Progress:
    strings: str | tuple[str, ...] = field(default=elapsed_template)
    time_sleep: float = field(default=0.1, kw_only=True)

    def __post_init__(self):
        self.tmpl = _ProgressTemplate(self.strings)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()

    def start(self):
        self.tmpl.reset()
        self.timer = _ThreadTimer(self.tmpl, self.time_sleep)
        self.timer.start()

    def stop(self):
        self.timer.stop()
        self.tmpl.reset()


def dog(time_sleep: float = 0.15):
    return _Progress(dog_template, time_sleep=time_sleep)


def elapsed(time_sleep: float = 0.1):
    return _Progress(elapsed_template, time_sleep=time_sleep)


def dots(time_sleep: float = 0.35):
    return _Progress(dots_template, time_sleep=time_sleep)


def rotate(time_sleep: float = 0.35):
    return _Progress(rotate_template, time_sleep=time_sleep)
