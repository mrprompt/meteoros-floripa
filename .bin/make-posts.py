#!/usr/bin/env python3
# -*- coding: utf8 -*-
import os
import sqlite3
import boto3
from typing import List


S3_BUCKET = 'meteoros'
PATH = os.path.dirname(__file__)
PATH_OF_SITE_POSTS = "{}/../_posts/".format(PATH)


def get_matching_s3_objects(bucket, prefix="", suffix=""):
    """
    Generate objects in an S3 bucket.

    From: https://alexwlchan.net/2019/07/listing-s3-keys/

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")

    kwargs = {'Bucket': bucket}

    # We can pass the prefix directly to the S3 API.  If the user has passed
    # a tuple or list of prefixes, we go through them one by one.
    if isinstance(prefix, str):
        prefixes = (prefix,)
    else:
        prefixes = prefix

    for key_prefix in prefixes:
        kwargs["Prefix"] = key_prefix

        for page in paginator.paginate(**kwargs):
            try:
                contents = page["Contents"]
            except KeyError:
                return

            for obj in contents:
                key = obj["Key"]
                if key.endswith(suffix):
                    yield obj


def get_matching_s3_keys(bucket, prefix="", suffix=""):
    """
    Generate the keys in an S3 bucket.

    From: https://alexwlchan.net/2019/07/listing-s3-keys/

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj["Key"]


def cleanup_dir(directory: str) -> bool:
    """
    Remove posts and captures before recreate then.

    :param directory: Name of directory to cleanup md files.
    :returns: bool
    """
    file_list = [f for f in os.listdir(directory) if f.endswith(".md")]

    for f in file_list:
        file_to_delete = os.path.join(directory, f)

        os.remove(file_to_delete)

    return True


def organize_captures(stations_captures: List) -> List:
    """
    Organize captures to be inserted into database with
    correct params organized into a tuple.

    :param stations_captures: The array all captures
    :returns: List
    """
    captures_organized = []

    for capture in stations_captures:
        capture_spliced = capture.split('/')
        station = capture_spliced[0]
        capture_date = capture_spliced[3]
        post = (capture_date, station, capture)

        captures_organized.append(post)

    return captures_organized


def populate_tables(connection: object, captures_list: List) -> bool:
    """
    Insert posts into table

    :param connection: The database connection
    :param captures_list: Array of posts
    :returns: bool
    """
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    CREATE TABLE IF NOT EXISTS captures (
        id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT,
        night_start DATE NOT NULL,
        station VARCHAR(20) NOT NULL,
        files TEXT
    );
    """)

    connection_cursor.executemany("""
    INSERT INTO captures (night_start, station, files)
    VALUES (?, ?, ?)
    """, captures_list)

    connection.commit()

    return True


def generate_pages(connection: object) -> bool:
    """
    Generate captures collections and pages from every station captures.

    :param connection: The database connection
    :return: bool
    """
    connection_cursor = connection.cursor()

    connection_cursor.execute("""
    SELECT COUNT(files) AS captures, night_start
    FROM captures
    GROUP BY night_start
    """)

    for data in connection_cursor.fetchall():
        captures = int(data[0])
        night_start = str(data[1])
        day = str(night_start[6:8])
        month = str(night_start[4:6])
        year = str(night_start[0:4])
        post_filename = PATH_OF_SITE_POSTS + "{}-{}-{}-captures.md".format(year, month, day)

        filehandle = open(post_filename, "w+")
        filehandle.write("---\n")
        filehandle.write("layout: post\n")
        filehandle.write("title: {}/{}/{}\n".format(day, month, year))
        filehandle.write("date: {}-{}-{} 00:00:00+00:00\n".format(year, month, day))
        filehandle.write("captures: {}\n".format(captures))
        filehandle.write("---\n")
        filehandle.close()

    return True


if __name__ == '__main__':
    print("- Cleaning {}".format(PATH_OF_SITE_POSTS))
    cleanup_dir(PATH_OF_SITE_POSTS)

    print('- Reading captures from S3 bucket')
    captures = get_matching_s3_keys(S3_BUCKET, suffix=('.mp4', '.MP4'), prefix='TLP')

    print("- Organizing captures")
    posts = organize_captures(captures)

    print("- Connecting to database")
    conn = sqlite3.connect(':memory:')

    print("- Creating temporary table and populating...")
    populate_tables(conn, posts)

    print("- Creating pages")
    generate_pages(conn)

    print("- Closing database connection")
    conn.close()

    print("- Done :)")
