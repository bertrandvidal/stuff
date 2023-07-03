#!/usr/bin/env python

import argparse
import datetime
import json
import pathlib
import sys
import zipfile


def get_thermostat_attribute(thermostat_data, attribute):
    """Retrieve 'attribute' from 'thermostat_data' if it is present, None otherwise.

    :param thermostat_data: dict containing thermostat data
    :param attribute: name of the attribute to return, if present
    :return: the value associate with 'attribute' if present, None otherwise.
    """
    return thermostat_data.get(attribute)


def get_thermostat_data(file_path):
    """Yield json objects as read from 'file_path', file is expected to be jsonl format.

    :param file_path: path to a jsonl file - http://jsonlines.org/
    :return: yield json objects from the given file path
    """
    with open(file_path, "r") as f:
        for line in f:
            yield json.loads(line.strip("\n"))


def get_file_path(file_path):
    """Get the path of the unzipped file containing the thermostat data. If the path points to a zipped file it is
    unzipped, and it belongs to the caller to do any necessary clean up.

    :param file_path: path to a zipped or unzipped file
    :return: path to an unzipped file
    """
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path) as zf:
            zip_files = zf.namelist()
            assert len(zip_files) == 1
            filename = zip_files[0]
            zf.extractall()
            return filename
    else:
        return file_path


def get_attribute_from_file(file_path, attribute, search_timestamp):
    """Reading from the file, return the value for the 'attribute' at the given 'timestamp'

    :param file_path: path of a jsonl file containing the data
    :param attribute: name of the thermostat attribute
    :param search_timestamp: datetime at which we want to read the attribute
    :return: value of the thermostat attribute at
    the given timestamp or None if that attribute isn't present or the file does not contain data for the given
    timestamp.
    """
    current_data = {}
    for thermostat_data in get_thermostat_data(file_path):
        update_time = datetime.datetime.fromisoformat(thermostat_data["updateTime"])
        if current_data == {} and update_time and search_timestamp < update_time:
            # handle a search_timestamp that's before the start of the file
            return None
        current_data.update(thermostat_data["update"])
        if update_time >= search_timestamp:
            return get_thermostat_attribute(current_data, attribute)
    return get_thermostat_attribute(current_data, attribute)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="replay", description="Infer the state of a field at a point in time")
    parser.add_argument("attribute")
    parser.add_argument("file_path", type=pathlib.Path)
    parser.add_argument("timestamp", type=datetime.datetime.fromisoformat)
    args = parser.parse_args(sys.argv[1:])
    value = get_attribute_from_file(args.file_path, args.attribute, args.timestamp)
    if value is None:
        print(f"Could not find '{args.attribute}' in '{args.file_path}': attribute unknown or timestamp is too early")
    else:
        print(f"Thermostat[{args.attribute}] = {value} at {args.timestamp}")
