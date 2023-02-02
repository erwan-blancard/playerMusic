import os

from button import *
import tkinter.messagebox
import tkinter.filedialog
from scrolling_list import *
import pygame
import text
from track import Track
import random

pygame.init()
pygame.font.init()

pygame.mixer.init()

screen = pygame.display.set_mode((318, 512))
pygame.display.set_caption("Music Player")

SUPPORTED_FORMATS = ["mp3", "wav", "ogg", "flac", "mid", "opus"]

FONTS = [
    pygame.font.SysFont("Arial", 16),
    pygame.font.SysFont("Arial", 24)
]

DEFAULT_COVER = pygame.image.load("res/cover.png")

SPEAKER_STATES = []
for state in range(5):
    img = pygame.image.load("res/speaker/state_" + str(state) + ".png")
    img = pygame.transform.scale(img, (36, 36))
    SPEAKER_STATES.append(img)

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

# prevent mouse input when other windows pop up
window_focus = True


def set_track(track):
    global music_offset
    global prev_play_time
    global paused_flag
    mp.load(track.get_filepath())
    mp.play()
    pygame.display.set_caption(str(playlist[current_track]) + " | " + "Music Player")
    music_offset = 0
    prev_play_time = 0
    playpause_button.activated = True
    paused_flag = False


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
    global current_track
    if len(playlist) > 0:
        if current_track > 0:
            current_track -= 1
        try:
            set_track(playlist[current_track])
        except pygame.error as e:
            print(e)
            playlist[current_track].broken_flag = True
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
            set_track(playlist[current_track])
        except pygame.error as e:
            print(e)
            playlist[current_track].broken_flag = True
            next_music()


# special check to prevent RecursionError
def next_music(already_cycled_once=False):
    global current_track
    global playlist_active
    global music_offset
    global prev_play_time
    # check if there are tracks remaining
    if current_track < len(playlist) - 1:
        current_track += 1
        try:
            set_track(playlist[current_track])
        except pygame.error as e:
            print(e)
            playlist[current_track].broken_flag = True
            if already_cycled_once:
                # finds the nearest track that isn't broken
                all_broken = True
                for i in range(len(playlist)):
                    if not playlist[i].is_broken():
                        all_broken = False
                        current_track = i
                        set_track(playlist[current_track])
                        break
                if all_broken:
                    flush_playlist()

            else:
                next_music()
    elif len(playlist) > 0:
        # if end of playlist, go to first track
        current_track = -1
        next_music(already_cycled_once=True)


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
            set_track(playlist[current_track])
        except pygame.error as e:
            print(e)
            playlist[current_track].broken_flag = True
            next_music()


def add_to_playlist():
    global window_focus
    window_focus = False
    filepaths = tkinter.filedialog.askopenfilenames()
    for filepath in filepaths:
        if os.path.splitext(filepath)[1][1:].lower() in SUPPORTED_FORMATS:
            playlist.append(Track(filepath))
    window_focus = True


def ask_flush_playlist():
    global window_focus
    window_focus = False
    if len(playlist) > 0:
        response = tkinter.messagebox.askyesno("Confirmer", "Vider tous les titres de la playlist ?\n\nAttention: cela stoppera la lecture en cours !")
        if response:
            flush_playlist()
    window_focus = True


def flush_playlist():
    global playlist
    global current_track
    global paused_flag
    global playpause_button
    global playlist_active
    global music_offset
    global prev_play_time
    paused_flag = True
    playpause_button.activated = False
    mp.unload()
    playlist = []
    playlist_active = False
    current_track = 0
    music_offset = 0
    prev_play_time = 0
    player_slider.set_scroll_pos(0)
    playlist_scrolling_list.scroll_bar.set_scroll_pos(0)
    # reset window caption
    pygame.display.set_caption("Music Player")


def shuffle_playlist():
    global window_focus
    global paused_flag
    global current_track
    global prev_play_time
    global music_offset
    global playlist_active
    window_focus = False
    if len(playlist) > 0:
        response = tkinter.messagebox.askyesno("Mélanger les titres ?", "Mélanger l'ordre des titres de la playlist ?\n\nAttention: cela stoppera la lecture en cours !")
        if response:
            paused_flag = True
            playpause_button.activated = False
            mp.unload()
            playlist_active = False
            current_track = 0
            music_offset = 0
            prev_play_time = 0
            player_slider.set_scroll_pos(0)
            playlist_scrolling_list.scroll_bar.set_scroll_pos(0)
            # reset window caption
            pygame.display.set_caption("Music Player")
            random.shuffle(playlist)
    window_focus = True


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


def render_speaker():
    speaker_state = 0
    if mp.get_volume() > 0:
        if mp.get_volume() <= 0.2:
            speaker_state = 1
        elif mp.get_volume() <= 0.4:
            speaker_state = 2
        elif mp.get_volume() <= 0.8:
            speaker_state = 3
        elif mp.get_volume() > 0.8:
            speaker_state = 4
    screen.blit(SPEAKER_STATES[speaker_state], (screen.get_width() - 44, 64))


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
volume_slider = ButtonSliderVertical(
    screen.get_width() - 26, 48 + 64, 111, 4
)
# set volume to 1.0 - 0.3 = 0.7
volume_slider.set_scroll_pos(0.35)

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
shuffle_playlist_button = ButtonIcon(
    panel_size / 2 - 16, screen.get_height() - 36, 32, pygame.image.load("res/shuffle.png"), command=lambda: shuffle_playlist()
)

player_buttons = [playpause_button, prev_button, next_button, rewind_button, loop_button]
playlist_menu_buttons = [add_track_button, flush_playlist_button, start_music_player_button, shuffle_playlist_button]

playlist_scrolling_list = ScrollingList(8, 48, panel_size - 16, screen.get_height() - 140)

running = True

while running:

    # update mp volume with volume slider
    mp.set_volume(1.0 - volume_slider.get_scroll_pos())

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
        if window_focus:
            show_playlist_button.mouse_input(event)
            if show_playlist_menu:
                if len(playlist) > 0:
                    playlist_scrolling_list.mouse_input(event)
                for button in playlist_menu_buttons:
                    button.mouse_input(event)
            else:
                volume_slider.mouse_input(event)
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
    volume_slider.render(screen)

    str_volume = str(int(mp.get_volume()*100))
    text.draw_centered_text(str_volume, screen.get_width() - 24, 48 + 56 + 111 + 32, screen, FONTS[0])

    render_speaker()

    for button in player_buttons:
        if isinstance(type(button), type(BaseButton)):
            button.render(screen)

    if show_playlist_menu:
        render_playlist_menu()
        if playlist_active:
            playlist_scrolling_list.render(screen, playlist, FONTS[0], list_index=current_track)
        else:
            playlist_scrolling_list.render(screen, playlist, FONTS[0])
        for button in playlist_menu_buttons:
            button.render(screen)

    show_playlist_button.render(screen)

    pygame.display.flip()
