import pygame

import text
import track
from button import *

pygame.init()
pygame.font.init()

pygame.mixer.init()

screen = pygame.display.set_mode((318, 416))
pygame.display.set_caption("Music Player")

FONTS = [
    pygame.font.SysFont("Arial", 16),
    pygame.font.SysFont("Arial", 24)
]

mp = pygame.mixer.music

playlist: list[track.Track] = []
current_track = 0
playlist_active = False

show_playlist_menu = False
panel_size = screen.get_width() - 92


# button functions
def resume():
    mp.unpause()


def pause():
    mp.pause()


def prev_music():
    pass


def next_music():
    pass


def rewind():
    try:
        mp.play()   # not rewind() to work with unsupported types (WAV)
    except Exception as e:
        print(e)


def set_loop():
    pass


def unset_loop():
    pass


def show_menu():
    global show_playlist_menu
    show_playlist_menu = True


def hide_menu():
    global show_playlist_menu
    show_playlist_menu = False


def add_to_playlist():
    pass


def flush_playlist():
    global playlist
    playlist = []


def set_time_with_slider():
    percent = player_slider.scroll_pos
    # mp.set_pos(percent)


def render_playlist_menu():
    rect_over = pygame.Surface((screen.get_width(), screen.get_height()))
    rect_over.set_alpha(200)
    rect_over.fill((0, 0, 0))
    screen.blit(rect_over, (0, 0))
    screen.fill((50, 50, 50), (0, 0, panel_size, screen.get_height()))
    text.draw_aligned_text("Playlist", panel_size / 2, 4, screen, FONTS[1])


# player buttons
playpause_button = TrueFalseButton(
    screen.get_width()/2 - 24, screen.get_height()/2+92, 48,
    pygame.image.load("res/play.png"), pygame.image.load("res/pause.png"),
    true_command=lambda: resume(), false_command=lambda: pause()
)
prev_button = ButtonIcon(
    screen.get_width()/2 - 128, screen.get_height()/2+100, 32,
    pygame.image.load("res/prev.png"), command=lambda: prev_music()
)
next_button = ButtonIcon(
    screen.get_width()/2 + 92, screen.get_height()/2+100, 32,
    pygame.image.load("res/next.png"), command=lambda: next_music()
)


rewind_button = ButtonIcon(
    screen.get_width()/2 - 72, screen.get_height()/2+164, 32,
    pygame.image.load("res/rewind.png"), command=lambda: rewind()
)
loop_button = TrueFalseButton(
    screen.get_width()/2 + 48, screen.get_height()/2+164, 32,
    pygame.image.load("res/loop_disabled.png"), pygame.image.load("res/loop_enabled.png"),
    true_command=lambda: set_loop(), false_command=lambda: unset_loop()
)

show_playlist_button = TrueFalseButton(
    4, 4, 24, pygame.image.load("res/burger.png"), pygame.image.load("res/cross.png"),
    true_command=lambda: show_menu(), false_command=lambda: hide_menu()
)

player_slider = ButtonSlider(16, screen.get_height()/2+64, screen.get_width()-32, 4, release_command=lambda: set_time_with_slider())

# playlist menu buttons
add_track_button = ButtonLabel("Ajouter", panel_size / 2 - 72, screen.get_height() - 32, 64, 24, FONTS[1], lambda: add_to_playlist())
flush_playlist_button = ButtonIcon(
    panel_size / 2 + 32, screen.get_height() - 36, 32,
    pygame.image.load("res/trash.png"), command=flush_playlist()
)

player_buttons = [playpause_button, prev_button, next_button, rewind_button, loop_button]
playlist_menu_buttons = [add_track_button, flush_playlist_button]

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        show_playlist_button.mouse_input(event)
        if show_playlist_menu:
            for button in playlist_menu_buttons:
                button.mouse_input(event)
        else:
            if playlist_active:
                player_slider.mouse_input(event)
            for button in player_buttons:
                button.mouse_input(event)

    screen.fill((40, 40, 40))

    player_slider.render(screen)
    for button in player_buttons:
        if isinstance(type(button), type(BaseButton)):
            button.render(screen)

    if show_playlist_menu:
        render_playlist_menu()
        for button in playlist_menu_buttons:
            button.render(screen)

    show_playlist_button.render(screen)

    pygame.display.flip()
