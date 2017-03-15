from urllib import quote_plus

import os
import csv

resource_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../resources"))


def get_space_key():
    space_keys = get_entries_as_list("spaces/spaceKeys.csv")
    return space_keys[0]["space_key"] if len(space_keys) > 0 else "ds"


def get_pages_by_title():
    return get_entries_as_list("pages/pagesByTitle.csv")


def get_pages_not_found():
    return get_entries_as_list("pages/pagesNotFound.csv")


def get_space_actions():
    return get_entries_as_list("spaces/spaces.csv")


def get_rss_feed_types():
    return get_entries_as_list("spaces/rss.csv")


def get_oc_pages():
    return get_entries_as_list("pages/pagesOC.csv")


def get_search_keywords():
    return get_entries_as_list("search/keywords.csv")


def get_labels():
    return get_entries_as_list("search/labels.csv")


def get_quick_nav_keywords():
    return get_entries_as_list("search/quicknavkeywords.csv")


def get_pages_to_comment():
    return get_entries_as_list("pages/pagesToComment.csv")


def get_sample_comments():
    return get_entries_as_list("comments/comments.csv")


def url_encode(string):
    return quote_plus(string)


def get_entries_as_list(file_name):
    csv_file_path = os.path.abspath(os.path.join(resource_directory, file_name))
    with open(csv_file_path) as csv_file:
        entries = csv.DictReader(csv_file)
        return list(entries)



