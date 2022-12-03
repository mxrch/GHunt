from typing import *

from ghunt.parsers.drive import DriveComment, DriveCommentList, DriveCommentReply, DriveFile
from ghunt.objects.base import DriveExtractedUser
from ghunt.helpers.utils import oprint # TEMP


def get_users_from_file(file: DriveFile) -> List[DriveExtractedUser]:
    """
        Extracts the users from the permissions of a Drive file,
        and the last modifying user.
    """
    
    users: Dict[str, DriveExtractedUser] = {}
    for perms in [file.permissions, file.permissions_summary.select_permissions]:
        for perm in perms:
            if not perm.email_address:
                continue
            #oprint(perm)
            user = DriveExtractedUser()
            user.email_address = perm.email_address
            user.gaia_id = perm.user_id
            user.name = perm.name
            user.role = perm.role
            users[perm.email_address] = user

    # Last modifying user
    target_user = file.last_modifying_user
    if target_user.id:
        email = target_user.email_address
        if not email:
            email = target_user.email_address_from_account
        if not email:
            return users

        if email in users:
            users[email].is_last_modifying_user = True

    return list(users.values())

def get_comments_from_file(comments: DriveCommentList) -> List[Tuple[str, Dict[str, any]]]:
    """
        Extracts the comments and replies of a Drive file.
    """

    def update_stats(authors: List[Dict[str, Dict[str, any]]], comment: DriveComment|DriveCommentReply):
        name = comment.author.display_name
        pic_url = comment.author.picture.url
        key = f"{name}${pic_url}" # Two users can have the same name, not the same picture URL (I hope so)
                                  # So we do this to make users "unique"
        if key not in authors:
            authors[key] = {
                "name": name,
                "pic_url": pic_url,
                "count": 0
            }
        authors[key]["count"] += 1

    authors: Dict[str, Dict[str, any]] = {}
    for comment in comments.items:
        update_stats(authors, comment)
        for reply in comment.replies:
            update_stats(authors, reply)

    return sorted(authors.items(), key=lambda k_v: k_v[1]['count'], reverse=True)