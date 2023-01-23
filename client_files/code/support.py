from csv import reader
from os import walk
import pygame


def import_csv_layout(path: str) -> list[list[str]]:
    """
    Loads layout from csv file
    :return: 2D list of numbers representing layout
    """
    # Output
    tiles: list[list[str]] = []

    with open(path) as file:
        # Read lines of csv file
        layout = reader(file, delimiter=',')

        for row in layout:
            tiles.append(list(row))

    return tiles


def import_folder(path: str) -> dict[str: pygame.Surface]:
    """
    Loads all tiles from a folder
    :return: dictionary of id to surfaces of the tiles
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
