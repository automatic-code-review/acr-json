import hashlib
import json
import os
from json import JSONDecodeError

import automatic_code_review_commons as commons


def generate_md5(path):
    hash_md5 = hashlib.md5()

    try:
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)

        return hash_md5.hexdigest()
    except FileNotFoundError as _:
        return None


def review(config):
    path_source = config['path_source']
    changes = config['merge']['changes']
    message_error = config['messageError']
    message_ident = config['messageIdent']

    comments = []

    for change in changes:
        new_path = change['new_path']

        if not new_path.endswith(".json"):
            continue

        path = os.path.join(path_source, new_path)

        try:
            with open(path, 'r') as content_data:
                data = json.load(content_data)

        except JSONDecodeError as _:

            comment_path = new_path
            comment_description = message_error
            comment_description = comment_description.replace("${FILE_PATH}", comment_path)

            print(comment_description)

            comments.append(commons.comment_create(
                comment_id=commons.comment_generate_id(comment_path),
                comment_path=comment_path,
                comment_description=comment_description,
                comment_snipset=False,
                comment_end_line=1,
                comment_start_line=1,
                comment_language="json",
            ))
        else:
            path_tmp = "/tmp/acr_json.json"
            with open(path_tmp, 'w') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            if generate_md5(path) != generate_md5(path_tmp):
                json_formatted = json.dumps(data, indent=4, ensure_ascii=False)

                comment_path = new_path
                comment_description = message_ident
                comment_description = comment_description.replace("${FILE_PATH}", comment_path)
                comment_description = comment_description.replace("${JSON_FORMATTED}", json_formatted)

                print(comment_description)

                comments.append(commons.comment_create(
                    comment_id=commons.comment_generate_id(comment_path),
                    comment_path=comment_path,
                    comment_description=comment_description,
                    comment_snipset=False,
                    comment_end_line=1,
                    comment_start_line=1,
                    comment_language="json",
                ))

    return comments
