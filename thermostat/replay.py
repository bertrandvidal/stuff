import json
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
        for line in f.readlines():
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
