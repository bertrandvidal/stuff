import os
import random


def get_movies(top_directory):
    """Return the list of all found movies in the given directory.

    Args:
        - top_directory: the directory to explore to find movie files
    """
    movies = []
    for (dir_path, _, filenames) in os.walk(top_directory):
        for filename in filenames:
            (__, extension) = os.path.splitext(filename)
            if extension in [".avi", ".mkv", ".mpg", ".AVI", ".wmv", ".mp4"]:
                movies.append(os.path.join(dir_path, filename))
    random.shuffle(movies)
    return movies


def get_start_time(min_start=0, max_start=90):
    """Return a time in seconds between 0 and 90 minutes in seconds.

    Note that if the movie file is shorter than start time it will be skipped.

    Args:
        - min_start: the smallest minute at which the movie can start
        - max_start: the biggest minute at which the movie can start
    """
    return random.randint(min_start, max_start) * random.randint(10, 60)


def get_run_time(min_run_time=1, max_run_time=10):
    """Return the number of seconds the movie file will be played.

    Args:
        - min_run_time: the min amount of minutes the video will be played
        - max_run_time: the max amount of minutes the video will be played
    """
    return random.randint(min_run_time, max_run_time) * random.randint(10, 60)


def get_playlist_entry(movie_file):
    """Return the entry to add to the playlist for the given movie_file.

    Args:
        - movie_file: absolute path to the movie file
    """
    return """#EXTVLCOPT:start-time=%d
#EXTVLCOPT:run-time=%d
%s
""" % (get_start_time(), get_run_time(), movie_file)


def generate_playlist(top_directory, playlist):
    """Generate a playlist file from the given directory.

    Args:
        - top_directory: the directory containing movie files
        - playlist: full path to the playlist file
    """
    with open(playlist, "w") as playlist_file:
        for m in get_movies(top_directory):
            playlist_file.write(get_playlist_entry(m))


generate_playlist("/media/bvidal/Elements/Films", "playlist_random.vlc")

