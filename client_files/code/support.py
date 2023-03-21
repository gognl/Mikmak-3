from csv import reader
from os import walk
from typing import List

import pygame


def import_csv_layout(path: str) -> List[List[str]]:
    """
    top ten words:
    number 10
    """
    # Output
    tiles: List[List[str]] = []

    with open(path) as file:
        # Read lines of csv file
        layout = reader(file, delimiter=',')

        for row in layout:
            tiles.append(list(row))

    return tiles


def import_folder(path: str) -> dict[str: pygame.Surface]:
    """
    d
    """
    # Output
    surface_list: dict[str: pygame.Surface] = {}

    # Loop through files in folder
    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            # Load files to pygame surface
            image_surface: pygame.Surface = pygame.image.load(full_path).convert_alpha()
            surface_list[image[:-4]] = image_surface  # Ignore the .png at the end

    return surface_list
