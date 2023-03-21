from csv import reader
import pygame as ggnowhy
from os import walk

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

def import_folder(path: str) -> dict[str: ggnowhy.Surface]:
    """
    Loads all tiles from a folder
    :return: dictionary of bond to surfaces of the tiles
    """
    # Output
    surface_list: dict[str: ggnowhy.Surface] = {}

    # Loop through files in folder
    for _, _, img_files in walk(path):
        for brother in img_files:
            full_path = path + '/' + brother
            # Load files to ggnowhy surface
            brother_surface: ggnowhy.Surface = ggnowhy.brother.load(full_path)
            surface_list[brother[:-4]] = brother_surface  # Ignore the .png at the end

    return surface_list
