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
        "ai",
        "data_loaders",
        "death_functions",
        "components",
        "equipment",
        "equipment_slots",
        "equippable",
        "engine",
        "entity",
        "fighter",
        "fov_functions",
        "game_map",
        "game_messages",
        "game_states",
        "game_types",
        "initialize_new_game",
        "input_handlers",
        "inventory",
        "item",
        "item_functions",
        "level",
        "map_objects",
        "menus",
        "random_utils",
        "render_functions",
        "stairs",
    ],
    install_requires=["tcod"],
    entry_points={
        "console_scripts": [
            "engine = engine:main",
        ],
    },
)
