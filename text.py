import pygame


def draw_text(text, x, y, screen: pygame.Surface, font: pygame.font.Font, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), (x, y))


def draw_aligned_text(text, center_x, y, screen: pygame.Surface, font: pygame.font.Font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (center_x - (text_surface.get_width() / 2), y))


def draw_centered_text(text, center_x, center_y, screen: pygame.Surface, font: pygame.font.Font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (center_x - (text_surface.get_width() / 2), center_y - (text_surface.get_height() / 2)))


def draw_aligned_spaced_text(text, center_x, y, x_spacing, screen: pygame.Surface, font: pygame.font.Font, color=(255, 255, 255)):
    width = font.size(text)[0] + (x_spacing*len(text))
    i = 0
    while i < len(text):
        draw_text(text[i], center_x-(width/2) + width/len(text)*i, y, screen, font, color)
        i += 1
