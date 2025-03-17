#!/usr/bin/env python3
# -*- coding: utf8 -*-
import datetime
import glob
import os
import re
import sqlite3
import subprocess
import yaml
from xml.dom import minidom
from typing import List
from git import Repo
from PIL import ImageChops, Image
from robocopy import robocopy

PATH = os.path.dirname(__file__)
PATH_OF_GIT_REPO = "{}/../".format(PATH)
CONFIG_FILE = "{}/../_config.yml".format(PATH)
PATH_OF_SITE_POSTS = "{}/../_posts/".format(PATH)
PATH_OF_SITE_CAPTURES = "{}/../_captures/".format(PATH)
PATH_OF_WATCH_CAPTURES = "{}/../_watches/".format(PATH)
PATH_OF_ANALYZERS = "{}/../_data/".format(PATH)
PATH_OF_STATIONS = "{}/../_stations/".format(PATH)


def load_config():
    with open(CONFIG_FILE, "r") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def organize_captures(stations_captures):
    def populate_tables(captures_list: List):
        connection_cursor = connection.cursor()
        connection_cursor.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
            night_start DATE NOT NULL,
            station VARCHAR(20) NOT NULL,
            files TEXT,
            files_full_path TEXT
        );
        """)

        connection_cursor.executemany("""
        INSERT INTO captures (night_start, station, files, files_full_path)
        VALUES (?, ?, ?, ?)
        """, captures_list)

        connection.commit()

    captures_organized = []

    for capture in stations_captures:
        base = re.findall("\w{3,5}\d{1,2}.+P\.jpg$", capture)
        capture_spliced = base[0].split('/')
        station = capture_spliced[0]
        capture_date = capture_spliced[3]
        post = (capture_date, station, base[0], capture)

        captures_organized.append(post)

    populate_tables(captures_organized)


def generate_stations(stations: list):
    for index, station in enumerate(stations, start=1):
        station_filename = PATH_OF_STATIONS + "{}.md".format(station)

        filehandle = open(station_filename, "w")
        filehandle.write("---\n")
        filehandle.write("layout: station\n")
        filehandle.write("title: Capturas da esta&ccedil;&atilde;o {}\n".format(station))
        filehandle.write("station: {}\n".format(station))
        filehandle.write("navigation_weight: {}\n".format(index))
        filehandle.write("---\n")


def generate_captures():
    def stack_captures(data, output_file):
        try:
            stack = Image.open(data[0])

            for i in range(1, len(data)):
                current_image = Image.open(data[i])
                stack = ImageChops.lighter(stack, current_image)

            stack.save(output_file, "JPEG")
        except:
            pass

    connection_cursor = connection.cursor()
    connection_cursor.execute("""
    SELECT night_start, station
    FROM captures
    GROUP BY night_start, station
    """)

    for data in connection_cursor.fetchall():
        stack = []
        stack_output_dir = "./"
        night_start = str(data[0])
        station = str(data[1])
        capture_filename = PATH_OF_SITE_CAPTURES + "{}_{}.md".format(station, night_start)

        connection_cursor.execute("""
            SELECT id, night_start, station, files, files_full_path
            FROM captures
            WHERE night_start = ?
            AND station = ?
            ORDER BY station
            """, (night_start, station))

        for capture in connection_cursor.fetchall():
            stack.append(capture[4])
            stack_output_dir = os.path.dirname(capture[4])

            file = capture[3]

            capture_spliced = file.split('/')
            capture_base_filename = capture_spliced[-1]
            capture_data_spliced = capture_base_filename.split('_')

            capture_date = capture_data_spliced[0]
            capture_day = capture_date[7:9]
            capture_month = capture_date[5:7]
            capture_year = capture_date[1:5]

            capture_time = capture_data_spliced[1]
            capture_hour = capture_time[0:2]
            capture_minute = capture_time[2:4]
            capture_second = capture_time[4:6]

            if not os.path.exists(capture_filename):
                filehandle = open(capture_filename, "w+")
                filehandle.write("---\n")
                filehandle.write("layout: capture\n")
                filehandle.write("label: {}\n".format(night_start))
                filehandle.write("title: Capturas da esta&ccedil;&atilde;o {}\n".format(station))
                filehandle.write("station: {}\n".format(station))
                filehandle.write("date: {}-{}-{} {}:{}:{}\n".format(capture_year, capture_month, capture_day, capture_hour, capture_minute, capture_second))
                filehandle.write("preview: {}/stack.jpg\n".format(os.path.dirname(file)))
                filehandle.write("capturas:\n")
            else:
                filehandle = open(capture_filename, "a")

            filehandle.write("  - imagem: {}\n".format(file))
            filehandle.close()

        filehandle = open(capture_filename, "a")
        filehandle.write("---\n")
        filehandle.close()

        stack_captures(stack, "{}/stack.jpg".format(stack_output_dir))


def generate_posts():
    connection_cursor = connection.cursor()
    connection_cursor.execute("""
    SELECT night_start, files
    FROM captures
    GROUP BY night_start
    """)

    for data in connection_cursor.fetchall():
        night_start = str(data[0])
        day = str(night_start[6:8])
        month = str(night_start[4:6])
        year = str(night_start[0:4])
        file_preview = str(data[1])
        post_filename = PATH_OF_SITE_POSTS + "{}-{}-{}-captures.md".format(year, month, day)

        filehandle = open(post_filename, "w+")
        filehandle.write("---\n")
        filehandle.write("layout: post\n")
        filehandle.write("title: {}/{}/{}\n".format(day, month, year))
        filehandle.write("date: {}-{}-{} 10:00:00\n".format(year, month, day))
        filehandle.write("preview: {}/stack.jpg\n".format(os.path.dirname(file_preview)))
        filehandle.write("---\n")
        filehandle.close()


def generate_watches(converter_path: str, converter_options: str):
    def convert_video(video_input: str, video_output: str, converter_path: str, converter_options: str):
        convert_command = [
            converter_path,
            '-n',
            '-i',
            video_input,
            '-c:v',
            'libx264',
            '-profile:v',
            'baseline',
            '-level',
            '3.0',
            '-pix_fmt',
            'yuv420p',
            video_output
        ]

        subprocess.Popen(convert_command)

    connection_cursor = connection.cursor()
    connection_cursor.execute("""
    SELECT night_start, station, files, files_full_path
    FROM captures
    """)

    for data in connection_cursor.fetchall():
        station = str(data[1])
        file = str(data[2])
        file_input = data[3].replace('P.jpg', '.avi')
        file_output = data[3].replace('P.jpg', '.mp4')
        capture_spliced = file.split('/')
        capture_base_filename = capture_spliced[-1]
        capture_base_filename_spliced = capture_base_filename.split('_')
        day = capture_base_filename_spliced[0][7:9]
        month = capture_base_filename_spliced[0][5:7]
        year = capture_base_filename_spliced[0][1:5]
        hour = capture_base_filename_spliced[1][0:2]
        minute = capture_base_filename_spliced[1][2:4]
        second = capture_base_filename_spliced[1][4:6]

        if os.path.exists(file_input) and not os.path.exists(file_output):
            convert_video(file_input, file_output, converter_path, converter_options)

        post_filename = PATH_OF_WATCH_CAPTURES + "{}.md".format(capture_base_filename.replace('P.jpg', ''))

        filehandle = open(post_filename, "w+")
        filehandle.write("---\n")
        filehandle.write("layout: watch\n")
        filehandle.write("title: {} - {}/{}/{} - {}\n".format(station, day, month, year, capture_base_filename.replace('P.jpg', 'T.jpg')))
        filehandle.write("date: {}-{}-{} {}:{}:{}\n".format(year, month, day, hour, minute, second))
        filehandle.write("permalink: /{}/{}/{}/watch/{}\n".format(year, month, day, capture_base_filename.replace('P.jpg', '')))
        filehandle.write("capture: {}\n".format(file.replace('P.jpg', 'T.jpg')))
        filehandle.write("---\n")
        filehandle.close()


def generate_analyzers():
    connection_cursor = connection.cursor()
    connection_cursor.execute("""
    SELECT night_start, station
    FROM captures
    GROUP BY night_start, station
    """)

    for data in connection_cursor.fetchall():
        night_start = str(data[0])
        station = str(data[1])
        capture_filename = PATH_OF_ANALYZERS + "analyzers.yaml"

        connection_cursor.execute("""
            SELECT id, night_start, station, files, files_full_path
            FROM captures
            WHERE night_start = ?
            AND station = ?
            ORDER BY station
            """, (night_start, station))

        for capture in connection_cursor.fetchall():
            file = capture[4].replace('P.jpg', 'A.XML')

            if not os.path.exists(file):
                continue

            try:
                xmldoc = minidom.parse(file)
                itemlist = xmldoc.getElementsByTagName('ua2_object')
                classe = itemlist[0].attributes['class'].value
                magnitude = itemlist[0].attributes['mag'].value
                duration = itemlist[0].attributes['sec'].value
                latitude_start = itemlist[0].attributes['lat1'].value
                latitude_final = itemlist[0].attributes['lat2'].value
                longitude_start = itemlist[0].attributes['lng1'].value
                longitude_final = itemlist[0].attributes['lng2'].value
                velocity = itemlist[0].attributes['Vo'].value
                azimute_start = itemlist[0].attributes['az1'].value
                azimute_final = itemlist[0].attributes['az2'].value
                elevation_start = itemlist[0].attributes['ev1'].value
                elevation_final = itemlist[0].attributes['ev2'].value
                altitude_start = itemlist[0].attributes['h1'].value
                altitude_final = itemlist[0].attributes['h2'].value
            except IndexError:
                classe = "__unknown__"
                magnitude = velocity = duration = "__unknown__"
                latitude_start = latitude_final = "__unknown__"
                longitude_start = longitude_final = "__unknown__"
                azimute_start = azimute_final = "__unknown__"
                elevation_start = elevation_final = "__unknown__"
                altitude_start = altitude_final = "__unknown__"
            except Exception:
                classe = magnitude = duration = velocity = "__none__"
                latitude_start = latitude_final = "__none__"
                longitude_start = longitude_final = "__none__"
                azimute_start = azimute_final = "__none__"
                elevation_start = elevation_final = "__none__"
                altitude_start = altitude_final = "__none__"

            base = re.findall("\w{3}\d{1,2}.+", capture[3])

            filehandle = open(capture_filename, "a")
            filehandle.write("{}:\n".format(base[0]))
            filehandle.write("  station: {}\n".format(station))
            filehandle.write("  class: {}\n".format(classe))
            filehandle.write("  magnitude: {}\n".format(magnitude))
            filehandle.write("  duration: {}\n".format(duration))
            filehandle.write("  latitude_start: {}\n".format(latitude_start))
            filehandle.write("  longitude_start: {}\n".format(longitude_start))
            filehandle.write("  latitude_final: {}\n".format(latitude_final))
            filehandle.write("  longitude_final: {}\n".format(longitude_final))
            filehandle.write("  velocity: {}\n".format(velocity))
            filehandle.write("  azimute_start: {}\n".format(azimute_start))
            filehandle.write("  azimute_final: {}\n".format(azimute_final))
            filehandle.write("  elevation_start: {}\n".format(elevation_start))
            filehandle.write("  elevation_final: {}\n".format(elevation_final))
            filehandle.write("  altitude_start: {}\n".format(altitude_start))
            filehandle.write("  altitude_final: {}\n".format(altitude_final))
            filehandle.close()


def get_date_list(days: int, date_format: str = '%Y%m%d'):
    return [(datetime.date.today() - datetime.timedelta(days=x)).strftime(date_format) for x in range(0, days)]


def get_matching_captures(captures_dir: list, days: int):
    result = []
    date_list = get_date_list(days)

    for directory in captures_dir:
        for date in date_list:
            files = glob.glob("{}/**/{}/*P.jpg".format(directory, date), recursive=True)

            result.extend(files)

    return fix_path_delimiter(result)


def fix_path_delimiter(captures_list: list):
    result = []

    for path in captures_list:
        path_fixed = path.replace("\\", "/")

        result.append(path_fixed)

    return result


def cleanup():
    def delete_files(files_to_delete):
        fix_paths = fix_path_delimiter(files_to_delete)

        for file_to_delete in fix_paths:
            os.remove(file_to_delete)

    def cleanup_captures(days: int):
        result = []
        date_list = get_date_list(days, '%Y%m%d')

        for date in date_list:
            files = glob.glob("{}/*_{}.md".format(PATH_OF_SITE_CAPTURES, date))

            result.extend(files)

        delete_files(result)

    cleanup_captures(days_back)


def git_push():
    try:
        today = datetime.date.today()

        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(update=True)
        repo.git.add(PATH_OF_SITE_CAPTURES)
        repo.git.add(PATH_OF_SITE_POSTS)
        repo.git.add(PATH_OF_WATCH_CAPTURES)
        repo.git.add(PATH_OF_ANALYZERS)
        repo.git.add(PATH_OF_STATIONS)
        repo.index.commit("Captures of {}".format(today))

        origin = repo.remote(name='origin')
        origin.push()
    except:
        print('Some error occurred while pushing the code')


def upload_captures(sources: list, captures_dest: str, videos_dest: str):
    for source in sources:
        try:
            print("  - uploading captures")
            robocopy.copy(source, captures_dest, "/xf *.mp4 /xo")

            print("  - uploading videos")
            robocopy.copy(source, videos_dest, "*.mp4 /xo")
        except Exception as e:
            print('Some error occurred while pushing the code: ' + str(e))


if __name__ == '__main__':
    print("- Connecting to database")
    connection = sqlite3.connect(':memory:')

    print("- Loading site configuration")
    config = load_config()
    days_back = config['build']['days']
    captures_dir = config['build']['captures']
    stations = config['build']['stations']

    print('- Reading captures')
    captures = get_matching_captures(captures_dir, days_back)

    if len(captures) == 0:
        print("- Nothing to do")
        exit(0)

    print("- Organizing captures")
    organize_captures(captures)

    print("- Creating stations files")
    generate_stations(stations)

    print("- Creating captures")
    generate_captures()

    print("- Creating pages")
    generate_posts()

    print("- Creating watches")
    generate_watches(config['build']['converter']['path'], config['build']['converter']['options'])

    print("- Creating analyzers")
    generate_analyzers()

    print("- Uploading captures")
    upload_captures(config['build']['captures'], config['storage']['captures'], config['storage']['videos'])

    print("- Push to git")
    git_push()

    print("- Closing database connection")
    connection.close()

    print("- Done :)")
