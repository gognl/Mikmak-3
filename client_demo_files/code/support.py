from csv import reader
from os import walk
import pygame


def import_csv_layout(path: str) -> list[list[int]]:
    """
    Loads layout from csv file
    :return: 2D list of numbers represeting layout
    """
    # Output
    tiles = []

    with open(path) as file:
        # Read lines of csv file
        layout = reader(file, delimiter=',')

        for row in layout:
            tiles.append(list(row))

    return tiles


def import_folder(path: str) -> list[pygame.Surface]:
    """
    Loads all tiles from a folder
    :return: list of surfaces of the tiles
    """
    # Output
    surface_list = []

    # Loop through files in folder
    for _, _, img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            # Load files to pygame surface
            image_surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surface)

    return surface_list
