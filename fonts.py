""" Module initializing fonts. """

import os

import pygame

pygame.font.init()

path = os.path.join("misc", "chalk.ttf")
title_font = pygame.font.Font(path, 200)
message_font = pygame.font.Font(path, 72)
regular_font = pygame.font.Font(path, 48)
