import random

from .core import Dog

_compliments = (
    "Well done, {}! 👏",
    "You're awesome, {}! 🙌",
    "You nailed it champ! 🏆",
    "Keep shining, {}! ✨",
    "Incredible work, {}! Keep pushing the limits! 💪",
    "Wow, {}! Your effort truly paid off! 🌟",
    "Bravo, {}! You've outdone yourself! 🎉",
    "You're a star! 🌈",
    "You're my darling {}! ❤️",
    "You've got the magic touch, {}! 🎩",
    "Spectacular, {}! You're breaking new ground! 🚀",
    "What a masterpiece, {}! 🖼️",
    "You're on fire, {}! 🔥",
    "What a triumph! 👏👏",
    "{}, you're my hero! 🦸",
    "{}, my sunshine! ☀️",
    "Pure genius, {}! 🧠",
    "Out of this world, {}! 🌍",
    "Heart of gold, {}! 💛",
    "You're a gem, {}! 💎",
    "So proud of you, {}! 🥰",
    "You're a legend, {}! 🏰",
    "Breaking barriers, {}! ⚔️",
    "Simply the best, {}! 🥇",
    "A true friend, {}! 🤝",
    "Unstoppable force, {}! 🚄",
    "Master of challenges, {}! 🎯",
    "Change maker, {}! 💡",
    "Limitless potential, {}! 🌌",
)


def praise(dog: Dog):
    print(random.choice(_compliments).format(dog.name))
    dog.bark()
