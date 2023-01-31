import os

from track import Track
from button import *
import pygame
import text
import tkinter.messagebox
import tkinter.filedialog

pygame.init()
pygame.font.init()

pygame.mixer.init()

screen = pygame.display.set_mode((318, 512))
pygame.display.set_caption("Music Player")

SUPPORTED_FORMATS = ["mp3", "wav", "ogg", "flac", "mid"]

FONTS = [
    pygame.font.SysFont("Arial", 16),
    pygame.font.SysFont("Arial", 24)
]

DEFAULT_COVER = pygame.image.load("res/cover.png")

mp = pygame.mixer.music

playlist: list[Track] = []
current_track = 0
playlist_active = False
music_loop = False

paused_flag = False

show_playlist_menu = False
panel_size = screen.get_width() - 92

# float
music_offset = 0
# millisecs
prev_play_time = 0


def resume():
    global paused_flag
    global playlist_active
    if playlist_active:
        paused_flag = False
        mp.unpause()
    elif len(playlist) > 0:
        start_music_player()


def pause():
    global paused_flag
    global playlist_active
    if playlist_active:
        paused_flag = True
        mp.pause()
    elif len(playlist) > 0:
        start_music_player()


# special check to prevent RecursionError
def prev_music(first_track_checked=False):
    global music_offset
    global prev_play_time
    global current_track
    if len(playlist) > 0:
        if current_track > 0:
            current_track -= 1
        try:
            mp.load(playlist[current_track].get_filepath())
            mp.play()
            pygame.display.set_caption(playlist[current_track].get_name() + ", " + playlist[current_track].get_artist() + " | " + "Music Player")
            music_offset = 0
            prev_play_time = 0
        except pygame.error as e:
            print(e)
            if first_track_checked:
                next_music()
            elif not current_track > 0:
                prev_music(first_track_checked=True)
            else:
                prev_music()


def load_next_music():
    global music_offset
    global prev_play_time
    if not music_loop:
        next_music()
    else:
        try:
            mp.load(playlist[current_track].get_filepath())
            mp.play()
            music_offset = 0
            prev_play_time = 0
        except pygame.error as e:
            print(e)
            next_music()


def next_music():
    global current_track
    global playlist_active
    global music_offset
    global prev_play_time
    # global paused_flag
    # check if there are tracks remaining
    if current_track < len(playlist) - 1:
        current_track += 1
        try:
            mp.load(playlist[current_track].get_filepath())
            mp.play()
            pygame.display.set_caption(playlist[current_track].get_name() + ", " + playlist[current_track].get_artist() + " | " + "Music Player")
        except pygame.error as e:
            print(e)
            next_music()
        # paused_flag = False
    else:
        flush_playlist()
        # reset window caption
        pygame.display.set_caption("Music Player")
        # paused_flag = True

    music_offset = 0
    prev_play_time = 0


def rewind():
    global music_offset
    global prev_play_time
    global paused_flag
    try:
        mp.rewind()
        mp.play()
        playpause_button.activated = True
        paused_flag = False
        music_offset = 0
        prev_play_time = 0
    except Exception as e:
        print(e)


def set_loop():
    global music_loop
    music_loop = True


def unset_loop():
    global music_loop
    music_loop = False


def show_menu():
    global show_playlist_menu
    show_playlist_menu = True


def hide_menu():
    global show_playlist_menu
    show_playlist_menu = False


def start_music_player():
    global playlist_active
    global playpause_button
    global current_track
    global paused_flag
    if len(playlist) > 0:
        playlist_active = True

        playpause_button.activated = True
        paused_flag = False

        current_track = 0
        try:
            mp.load(playlist[current_track].get_filepath())
            mp.play()
            pygame.display.set_caption(playlist[current_track].get_name() + ", " + playlist[current_track].get_artist() + " | " + "Music Player")
        except pygame.error as e:
            print(e)
            next_music()


def add_to_playlist():
    filepaths = tkinter.filedialog.askopenfilenames()
    for filepath in filepaths:
        if os.path.splitext(filepath)[1][1:] in SUPPORTED_FORMATS:
            playlist.append(Track(filepath))


def ask_flush_playlist():
    if len(playlist) > 0:
        response = tkinter.messagebox.askyesno("Confirmer", "Vider tous les titres de la playlist ?\n\nAttention: cela stoppera la lecture en cours !")
        if response:
            flush_playlist()


def flush_playlist():
    global playlist
    global current_track
    global paused_flag
    global playpause_button
    global playlist_active
    global music_offset
    global prev_play_time
    # mp.stop()
    paused_flag = True
    playpause_button.activated = False
    mp.unload()
    playlist = []
    playlist_active = False
    current_track = 0
    music_offset = 0
    prev_play_time = 0
    player_slider.set_scroll_pos(0)


def set_time_with_slider():
    global music_offset
    global prev_play_time
    if playlist_active:
        percent = player_slider.get_scroll_pos()
        tmp_old = prev_play_time
        prev_play_time = mp.get_pos()
        if percent >= 1.0:
            load_next_music()
        else:
            # if set_pos is not supported (.wav, .mid)
            try:
                mp.set_pos(playlist[current_track].get_length() * percent)
                music_offset = percent
            except pygame.error as e:
                prev_play_time = tmp_old
                print(e)


def render_playlist_menu():
    rect_over = pygame.Surface((screen.get_width(), screen.get_height()))
    rect_over.set_alpha(200)
    rect_over.fill((0, 0, 0))
    screen.blit(rect_over, (0, 0))
    screen.fill((50, 50, 50), (0, 0, panel_size, screen.get_height()))
    text.draw_aligned_text("Playlist", panel_size / 2, 6, screen, FONTS[1])


def render_cover():
    cover = DEFAULT_COVER
    if playlist_active:
        if playlist[current_track].get_cover() is not None:
            cover = playlist[current_track].get_cover()
    cover = pygame.transform.scale(cover, (222, 222))
    screen.blit(cover, (screen.get_width()/2 - 111, 48), (0, 0, cover.get_width(), cover.get_height()))


# player buttons
playpause_button = TrueFalseButton(
    screen.get_width()/2 - 24, screen.get_height() - 116, 48,
    pygame.image.load("res/play.png"), pygame.image.load("res/pause.png"),
    true_command=lambda: resume(), false_command=lambda: pause()
)
prev_button = ButtonIcon(
    screen.get_width()/2 - 128, screen.get_height() - 108, 32,
    pygame.image.load("res/prev.png"), command=lambda: prev_music()
)
next_button = ButtonIcon(
    screen.get_width()/2 + 92, screen.get_height() - 108, 32,
    pygame.image.load("res/next.png"), command=lambda: next_music()
)


rewind_button = ButtonIcon(
    screen.get_width()/2 - 76, screen.get_height() - 44, 32,
    pygame.image.load("res/rewind.png"), command=lambda: rewind()
)
loop_button = TrueFalseButton(
    screen.get_width()/2 + 42, screen.get_height() - 44, 32,
    pygame.image.load("res/loop_disabled.png"), pygame.image.load("res/loop_enabled.png"),
    true_command=lambda: set_loop(), false_command=lambda: unset_loop()
)

show_playlist_button = TrueFalseButton(
    4, 4, 32, pygame.image.load("res/burger.png"), pygame.image.load("res/cross.png"),
    true_command=lambda: show_menu(), false_command=lambda: hide_menu()
)

player_slider = ButtonSlider(
    16, screen.get_height() - 144, screen.get_width()-32, 4,
    release_command=lambda: set_time_with_slider()
)

# playlist menu buttons
add_track_button = ButtonIcon(
    panel_size / 2 - 72, screen.get_height() - 36, 32,
    pygame.image.load("res/add.png"), command=lambda: add_to_playlist()
)
flush_playlist_button = ButtonIcon(
    panel_size / 2 + 40, screen.get_height() - 36, 32,
    pygame.image.load("res/trash.png"), command=lambda: ask_flush_playlist()
)
start_music_player_button = ButtonLabel(
    "Lecture", panel_size / 2 - 36, screen.get_height() - 84, 72, 24,
    FONTS[1], command=lambda: start_music_player()
)

player_buttons = [playpause_button, prev_button, next_button, rewind_button, loop_button]
playlist_menu_buttons = [add_track_button, flush_playlist_button, start_music_player_button]

running = True

while running:

    # update playlist
    if playlist_active:
        # update slider
        if not player_slider.mouse_focus:
            # milliseconds
            player_slider.set_scroll_pos((mp.get_pos() - prev_play_time) / (playlist[current_track].get_length() * 1000) + music_offset)
        if not mp.get_busy() and not paused_flag:
            load_next_music()

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

    # labels
    if playlist_active:
        text.draw_centered_text(playlist[current_track].get_name(), screen.get_width()/2, 48 + 248, screen, FONTS[0])
        text.draw_centered_text(playlist[current_track].get_artist(), screen.get_width() / 2, 48 + 248 + 28, screen, FONTS[0])

    render_cover()

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
