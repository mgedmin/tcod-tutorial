#!/usr/bin/python3
from setuptools import setup

setup(
    name="tcod-tutorial",
    version="0.1",
    author="Marius Gedminas",
    author_email="marius@gedmin.as",
    url="http://rogueliketutorials.com/tutorials/tcod/part-0/",
    description="Following along the roguelike tutorial`",
    long_description="Go read the website",
    keywords="roguelike tcod",
    classifiers=[
        "Private"
    ],
    python_requires=">=3.6",

    py_modules=[
        "engine",
        "entity",
        "fov_functions",
        "game_map",
        "game_states",
        "input_handlers",
        "map_objects",
        "render_functions",
    ],
    install_requires=["tcod"],
    entry_points={
        "console_scripts": [
            "engine = engine:main",
        ],
    },
)
