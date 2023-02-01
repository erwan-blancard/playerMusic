import pygame
import text
from button import ButtonSliderVertical
from track import Track


class ScrollingList:

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.scroll_bar = ButtonSliderVertical(self.x + self.width - 4, self.y, self.height, 4)

    def render(self, screen: pygame.Surface, playlist: list, font: pygame.font.Font, list_index=-1):
        screen.fill((60, 60, 60), (self.x, self.y, self.width, self.height))

        y_offset = font.size("A")[1]
        # create a Surface based of the length of the playlist
        board = pygame.Surface((self.width - 8, y_offset * len(playlist)))
        board.fill((60, 60, 60))
        for i in range(len(playlist)):
            text_color = text.DEFAULT_COLOR
            if i == list_index:
                text_color = (0, 155, 255)
            else:
                if type(playlist[i]) == Track:
                    if playlist[i].is_broken():
                        text_color = (255, 40, 40)
            text.draw_text(str(playlist[i]), 2, y_offset*i, board, font, color=text_color)
        scroll_offset = 0
        if y_offset * len(playlist) > self.height:
            scroll_offset = (board.get_height() - self.height) * self.scroll_bar.get_scroll_pos()
        screen.blit(board, (self.x, self.y), (0, scroll_offset, self.width, self.height))
        self.scroll_bar.render(screen)

    def mouse_input(self, event: pygame.event.Event):
        self.scroll_bar.mouse_input(event)
