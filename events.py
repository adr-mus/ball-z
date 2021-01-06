# pylint: disable=no-member
""" Module contating user-defined events. """

import pygame


BONUS_DROPPED = pygame.USEREVENT + 1  # attributes: bonus
BONUS_COLLECTED = pygame.USEREVENT + 2  # attributes: bonus
POINTS = pygame.USEREVENT + 3  # attributes: points
EXPLOSION = pygame.USEREVENT + 4 # attributes: where
DEATH = pygame.USEREVENT + 5
GAME_OVER = pygame.USEREVENT + 6  # attributes: won
