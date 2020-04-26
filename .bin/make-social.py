#!/usr/bin/env python3
# -*- coding: utf8 -*-
import os
import sqlite3
import boto3
import facebook
from datetime import date, timedelta
from typing import List

PATH = os.path.dirname(__file__)
S3_BUCKET = 'meteoros'
PATH_OF_STATS = "{}/..".format(PATH)
YESTERDAY = str(date.today() - timedelta(days=1)).replace('-', '')


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

        if capture_date == YESTERDAY:
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
        capture_month VARCHAR(6) NOT NULL,
        station VARCHAR(20) NOT NULL,
        files TEXT
    );
    """)

    connection_cursor.executemany("INSERT INTO captures (capture_month, station, files) VALUES (?, ?, ?)",
                                  captures_list)

    connection.commit()

    return True


def generate_stats(connection: object) -> bool:
    """
    Generate captures collections and pages from every station captures.

    :param connection: The database connection
    :return: bool
    """
    connection_cursor = connection.cursor()
    connection_cursor.execute("""
    SELECT COUNT(files) AS captures, capture_month, station 
    FROM captures 
    GROUP BY capture_month, station
    ORDER BY station, capture_month
    """)

    for data in connection_cursor.fetchall():
        captures = str(data[0])
        station = str(data[2])

        print(station, captures)

    return True


def main():
    cfg = {
        "page_id": "351699955744024",  # Step 1
        "access_token": "EAADzAYhStkcBANaITmPk00KYAer9jw0JCqWhc0zU9ZBG8ixeBdMZCSz9zMS5pcnMxd0WAB6VpdlZAjLQf1ZBneTVKVz2QdWDWsKVRonz4LmyfVEhYyZBBPAPqZCe4uXWt4aU6v5ZBGkDp2EJAAlp4EZA4rZCY4FwZAlcut8zj0MOmQtaFg3XzPviTo"  # Step 3
    }

    api = get_api(cfg)
    msg = "Hello, world!"
    status = api.put_wall_post(msg)


def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])
    resp = graph.get_object('me/accounts')
    page_access_token = None

    for page in resp['data']:
        if page['id'] == cfg['page_id']:
            page_access_token = page['access_token']
    graph = facebook.GraphAPI(page_access_token)
    return graph


if __name__ == '__main__':
    # print('- Reading captures from S3 bucket')
    # captures = get_matching_s3_keys(S3_BUCKET, suffix='.mp4', prefix='TLP')
    #
    # print("- Organizing captures")
    # posts = organize_captures(captures)
    #
    # print("- Connecting to database")
    # conn = sqlite3.connect(':memory:')
    #
    # print("- Creating temporary table and populating...")
    # populate_tables(conn, posts)
    #
    # print("- Creating stats")
    # generate_stats(conn)
    #
    # print("- Closing database connection")
    # conn.close()
    #
    # print("- Done :)")
    main()