EVENT_FOR_UNSAFE = {
    "project": {"id": 1, "path_with_namespace": "test_event"},
    "object_attributes": {"last_commit": {"id": "test_sha"}},
    "event_type": "merge_request"
}

DIFF_IN_IGNORE_DIR = [
    {
        "old_path": "",
        "new_path": "ignore/test/dir/a.java",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": True,
        "renamed_file": False,
        "deleted_file": False,
        "diff": "Public void main(String[] args{})",
    }
]

DIFF_SAFE_FILE_CONTENT = [
    {
        "old_path": "something/text.txt",
        "new_path": "something/text.txt",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": False,
        "renamed_file": False,
        "deleted_file": False,
        "diff": "@@ -1,33 +1,21 @@\n+ Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem \n+ Ipsum has been the industry's standard dummy text ever since the 1500s, when an \n+ unknown printer took a galley of type and scrambled it to make a type specimen book. \n+\n+ It was popularised in the 1960s with the release of Letraset sheets containing \n+ Lorem Ipsum passages, and more recently with desktop publishing software like Aldus \n+ PageMaker including versions of Lorem Ipsum.",
    }
]

DIFF_UNSAFE_FILE_CONTENT = [
    {
        "old_path": "something/text.txt",
        "new_path": "something/text.txt",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": False,
        "renamed_file": False,
        "deleted_file": False,
        "diff": "@@ -1,33 +1,21 @@\n+ Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem \n+ Ipsum has been the industry's standard dummy text ever since the 1500s, when an \n++-----BEGIN RSA PRIVATE KEY----\n++Some fake RSA ID KEYADFADF\n+NVJtV3JB83faCtSbiP7nn1ooLOY27yfKaKjlNJWgJMKUu853DkcniExXf1\n+-----END OPENSSH PRIVATE KEY-----\n+\n+ It was popularised in the 1960s with the release of Letraset sheets containing \n+ Lorem Ipsum passages, and more recently with desktop publishing software like Aldus \n+ PageMaker including versions of Lorem Ipsum.",
    }
]

DIFF_UNSAFE_FILENAME = [
    {
        "old_path": "something/text.txt",
        "new_path": "something/filezilla.xml",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": False,
        "renamed_file": False,
        "deleted_file": False,
        "diff": "",
    }
]

DIFF_UNSAFE_FILE_EXTENSION = [
    {
        "old_path": "",
        "new_path": "something/fake_cert.pem",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": True,
        "renamed_file": False,
        "deleted_file": False,
        "diff": "",
    }
]

DIFF_FILE_BLACKLIST = [
    {
        "old_path": "",
        "new_path": "send/nudes.jpg",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": True,
        "renamed_file": False,
        "deleted_file": False,
        "diff": "",
    }
]

DIFF_DELETED_FILE = [
    {
        "old_path": "",
        "new_path": "send/nudes.jpg",
        "a_mode": "100644",
        "b_mode": "100644",
        "new_file": True,
        "renamed_file": False,
        "deleted_file": True,
        "diff": "",
    }
]
