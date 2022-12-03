from typing import *
from datetime import datetime

from ghunt.helpers.utils import get_datetime_utc
from ghunt.objects.apis import Parser


class DriveFile(Parser):
	def __init__(self):
		self.kind: str = ""
		self.id: str = ""
		self.thumbnail_version: str = ""
		self.title: str = ""
		self.mime_type: str = ""
		self.labels: DriveLabels = DriveLabels()
		self.created_date: datetime = None
		self.modified_date: datetime = None
		self.last_viewed_by_me_date: datetime = None
		self.marked_viewed_by_me_date: datetime = None
		self.shared_with_me_date: datetime = None
		self.recency: datetime = None
		self.recency_reason: str = ""
		self.version: str = ""
		self.parents: List[DriveParentReference] = []
		self.user_permission: DrivePermission = DrivePermission()
		self.file_extension: str = ""
		self.file_size: str = ""
		self.quota_bytes_used: str = ""
		self.owners: List[DriveUser] = []
		self.last_modifying_user: DriveUser = DriveUser()
		self.capabilities: DriveCapabilities = DriveCapabilities()
		self.copyable: bool = False
		self.shared: bool = False
		self.explicitly_trashed: bool = False
		self.authorized_app_ids: List[str] = []
		self.primary_sync_parent_id: str = ""
		self.subscribed: bool = False
		self.passively_subscribed: bool = False
		self.flagged_for_abuse: bool = False
		self.abuse_is_appealable: bool = False
		self.source_app_id: str = ""
		self.spaces: List[str] = []
		self.has_thumbnail: bool = False
		self.contains_unsubscribed_children: bool = False
		self.alternate_link: str = ""
		self.icon_link: str = ""
		self.copy_requires_writer_permission: bool = False
		self.permissions: List[DrivePermission] = []
		self.head_revision_id: str = ""
		self.video_media_metadata: DriveVideoMediaMetadata = DriveVideoMediaMetadata()
		self.has_legacy_blob_comments: bool = False
		self.label_info: DriveLabelInfo = DriveLabelInfo()
		self.web_content_link: str = ""
		self.thumbnail_link: str = ""
		self.description: str = ""
		self.original_filename: str = ""
		self.permissions_summary: DrivePermissionsSummary = DrivePermissionsSummary()
		self.full_file_extension: str = ""
		self.md5_checksum: str = ""
		self.owned_by_me: bool = False
		self.writers_can_share: bool = False
		self.image_media_metadata: DriveImageMediaMetadata = DriveImageMediaMetadata()
		self.is_app_authorized: bool = False
		self.link_share_metadata: DriveLinkShareMetadata = DriveLinkShareMetadata()
		self.etag: str = ""
		self.self_link: str = ""
		self.embed_link: str = ""
		self.open_with_links: DriveOpenWithLinks = DriveOpenWithLinks()
		self.default_open_with_link: str = ""
		self.has_child_folders: bool = False
		self.owner_names: List[str] = []
		self.last_modifying_user_name: str = ""
		self.editable: bool = False
		self.app_data_contents: bool = False
		self.drive_source: DriveSource = DriveSource()
		self.source: DriveSource = DriveSource()
		self.descendant_of_root: bool = False
		self.folder_color: str = ""
		self.folder_properties: DriveFolderProperties = DriveFolderProperties()
		self.resource_key: str = ""
		self.has_augmented_permissions: bool = False
		self.ancestor_has_augmented_permissions: bool = False
		self.has_visitor_permissions: bool = False
		self.primary_domain_name: str = ""
		self.organization_display_name: str = ""
		self.customer_id: str = ""
		self.team_drive_id: str = ""
		self.folder_color_rgb: str = ""

	def _scrape(self, file_data: Dict[str, any]):
		self.kind = file_data.get('kind')
		self.id = file_data.get('id')
		self.thumbnail_version = file_data.get('thumbnailVersion')
		self.title = file_data.get('title')
		self.mime_type = file_data.get('mimeType')
		if (labels_data := file_data.get('labels')):
			self.labels._scrape(labels_data)
		if (isodate := file_data.get("createdDate")):
			self.created_date = get_datetime_utc(isodate)
		if (isodate := file_data.get("modifiedDate")):
			self.modified_date = get_datetime_utc(isodate)
		if (isodate := file_data.get("lastViewedByMeDate")):
			self.last_viewed_by_me_date = get_datetime_utc(isodate)
		if (isodate := file_data.get("markedViewedByMeDate")):
			self.marked_viewed_by_me_date = get_datetime_utc(isodate)
		if (isodate := file_data.get("sharedWithMeDate")):
			self.shared_with_me_date = get_datetime_utc(isodate)
		if (isodate := file_data.get("recency")):
			self.recency = get_datetime_utc(isodate)
		self.recency_reason = file_data.get('recencyReason')
		self.version = file_data.get('version')
		if (parents_data := file_data.get('parents')):
			for parents_data_item in parents_data:
				parents_item = DriveParentReference()
				parents_item._scrape(parents_data_item)
				self.parents.append(parents_item)
		if (user_permission_data := file_data.get('userPermission')):
			self.user_permission._scrape(user_permission_data)
		self.file_extension = file_data.get('fileExtension')
		self.file_size = file_data.get('fileSize')
		self.quota_bytes_used = file_data.get('quotaBytesUsed')
		if (owners_data := file_data.get('owners')):
			for owners_data_item in owners_data:
				owners_item = DriveUser()
				owners_item._scrape(owners_data_item)
				self.owners.append(owners_item)
		if (last_modifying_user_data := file_data.get('lastModifyingUser')):
			self.last_modifying_user._scrape(last_modifying_user_data)
		if (capabilities_data := file_data.get('capabilities')):
			self.capabilities._scrape(capabilities_data)
		self.copyable = file_data.get('copyable')
		self.shared = file_data.get('shared')
		self.explicitly_trashed = file_data.get('explicitlyTrashed')
		self.authorized_app_ids = file_data.get('authorizedAppIds')
		self.primary_sync_parent_id = file_data.get('primarySyncParentId')
		self.subscribed = file_data.get('subscribed')
		self.passively_subscribed = file_data.get('passivelySubscribed')
		self.flagged_for_abuse = file_data.get('flaggedForAbuse')
		self.abuse_is_appealable = file_data.get('abuseIsAppealable')
		self.source_app_id = file_data.get('sourceAppId')
		self.spaces = file_data.get('spaces')
		self.has_thumbnail = file_data.get('hasThumbnail')
		self.contains_unsubscribed_children = file_data.get('containsUnsubscribedChildren')
		self.alternate_link = file_data.get('alternateLink')
		self.icon_link = file_data.get('iconLink')
		self.copy_requires_writer_permission = file_data.get('copyRequiresWriterPermission')
		if (permissions_data := file_data.get('permissions')):
			for permissions_data_item in permissions_data:
				permissions_item = DrivePermission()
				permissions_item._scrape(permissions_data_item)
				self.permissions.append(permissions_item)
		self.head_revision_id = file_data.get('headRevisionId')
		if (video_media_metadata_data := file_data.get('videoMediaMetadata')):
			self.video_media_metadata._scrape(video_media_metadata_data)
		self.has_legacy_blob_comments = file_data.get('hasLegacyBlobComments')
		if (label_info_data := file_data.get('labelInfo')):
			self.label_info._scrape(label_info_data)
		self.web_content_link = file_data.get('webContentLink')
		self.thumbnail_link = file_data.get('thumbnailLink')
		self.description = file_data.get('description')
		self.original_filename = file_data.get('originalFilename')
		if (permissions_summary_data := file_data.get('permissionsSummary')):
			self.permissions_summary._scrape(permissions_summary_data)
		self.full_file_extension = file_data.get('fullFileExtension')
		self.md5_checksum = file_data.get('md5Checksum')
		self.owned_by_me = file_data.get('ownedByMe')
		self.writers_can_share = file_data.get('writersCanShare')
		if (image_media_metadata_data := file_data.get('imageMediaMetadata')):
			self.image_media_metadata._scrape(image_media_metadata_data)
		self.is_app_authorized = file_data.get('isAppAuthorized')
		if (link_share_metadata_data := file_data.get('linkShareMetadata')):
			self.link_share_metadata._scrape(link_share_metadata_data)
		self.etag = file_data.get('etag')
		self.self_link = file_data.get('selfLink')
		self.embed_link = file_data.get('embedLink')
		if (open_with_links_data := file_data.get('openWithLinks')):
			self.open_with_links._scrape(open_with_links_data)
		self.default_open_with_link = file_data.get('defaultOpenWithLink')
		self.has_child_folders = file_data.get('hasChildFolders')
		self.owner_names = file_data.get('ownerNames')
		self.last_modifying_user_name = file_data.get('lastModifyingUserName')
		self.editable = file_data.get('editable')
		self.app_data_contents = file_data.get('appDataContents')
		if (drive_source_data := file_data.get('driveSource')):
			self.drive_source._scrape(drive_source_data)
		if (source_data := file_data.get('source')):
			self.source._scrape(source_data)
		self.descendant_of_root = file_data.get('descendantOfRoot')
		self.folder_color = file_data.get('folderColor')
		if (folder_properties_data := file_data.get('folderProperties')):
			self.folder_properties._scrape(folder_properties_data)
		self.resource_key = file_data.get('resourceKey')
		self.has_augmented_permissions = file_data.get('hasAugmentedPermissions')
		self.ancestor_has_augmented_permissions = file_data.get('ancestorHasAugmentedPermissions')
		self.has_visitor_permissions = file_data.get('hasVisitorPermissions')
		self.primary_domain_name = file_data.get('primaryDomainName')
		self.organization_display_name = file_data.get('organizationDisplayName')
		self.customer_id = file_data.get('customerId')
		self.team_drive_id = file_data.get('teamDriveId')
		self.folder_color_rgb = file_data.get('folderColorRgb')

class DriveLabels(Parser):
	def __init__(self):
		self.starred: bool = False
		self.trashed: bool = False
		self.restricted: bool = False
		self.viewed: bool = False
		self.hidden: bool = False
		self.modified: bool = False

	def _scrape(self, labels_data: Dict[str, bool]):
		self.starred = labels_data.get('starred')
		self.trashed = labels_data.get('trashed')
		self.restricted = labels_data.get('restricted')
		self.viewed = labels_data.get('viewed')
		self.hidden = labels_data.get('hidden')
		self.modified = labels_data.get('modified')

class DriveUserPermission(Parser):
	def __init__(self):
		self.role: str = ""
		self.id: str = ""
		self.type: str = ""

	def _scrape(self, user_permission_data: Dict[str, str]):
		self.role = user_permission_data.get('role')
		self.id = user_permission_data.get('id')
		self.type = user_permission_data.get('type')

class DriveUser(Parser):
	def __init__(self):
		self.kind: str = ""
		self.id: str = ""
		self.permission_id: str = ""
		self.email_address_from_account: str = ""
		self.display_name: str = ""
		self.picture: DrivePicture = DrivePicture()
		self.is_authenticated_user: bool = False
		self.email_address: str = ""

	def _scrape(self, user_data: Dict[str, any]):
		self.kind = user_data.get('kind')
		self.id = user_data.get('id')
		self.permission_id = user_data.get('permissionId')
		self.email_address_from_account = user_data.get('emailAddressFromAccount')
		self.display_name = user_data.get('displayName')
		if (picture_data := user_data.get('picture')):
			self.picture._scrape(picture_data)
		self.is_authenticated_user = user_data.get('isAuthenticatedUser')
		self.email_address = user_data.get('emailAddress')

class DriveCapabilities(Parser):
	def __init__(self):
		self.can_add_children: bool = False
		self.can_add_my_drive_parent: bool = False
		self.can_block_owner: bool = False
		self.can_change_security_update_enabled: bool = False
		self.can_copy: bool = False
		self.can_delete: bool = False
		self.can_download: bool = False
		self.can_edit: bool = False
		self.can_edit_category_metadata: bool = False
		self.can_request_approval: bool = False
		self.can_move_children_within_drive: bool = False
		self.can_move_item_into_team_drive: bool = False
		self.can_move_item_within_drive: bool = False
		self.can_read: bool = False
		self.can_read_category_metadata: bool = False
		self.can_remove_children: bool = False
		self.can_remove_my_drive_parent: bool = False
		self.can_rename: bool = False
		self.can_share: bool = False
		self.can_share_child_files: bool = False
		self.can_share_child_folders: bool = False
		self.can_trash: bool = False
		self.can_untrash: bool = False
		self.can_comment: bool = False
		self.can_move_item_out_of_drive: bool = False
		self.can_add_as_owner: bool = False
		self.can_add_as_organizer: bool = False
		self.can_add_as_file_organizer: bool = False
		self.can_add_as_writer: bool = False
		self.can_add_as_commenter: bool = False
		self.can_add_as_reader: bool = False
		self.can_change_to_owner: bool = False
		self.can_change_to_organizer: bool = False
		self.can_change_to_file_organizer: bool = False
		self.can_change_to_writer: bool = False
		self.can_change_to_commenter: bool = False
		self.can_change_to_reader: bool = False
		self.can_change_to_reader_on_published_view: bool = False
		self.can_remove: bool = False
		self.can_accept_ownership: bool = False
		self.can_add_encrypted_children: bool = False
		self.can_change_copy_requires_writer_permission: bool = False
		self.can_change_permission_expiration: bool = False
		self.can_change_restricted_download: bool = False
		self.can_change_writers_can_share: bool = False
		self.can_create_decrypted_copy: bool = False
		self.can_create_encrypted_copy: bool = False
		self.can_list_children: bool = False
		self.can_manage_members: bool = False
		self.can_manage_visitors: bool = False
		self.can_modify_content: bool = False
		self.can_modify_content_restriction: bool = False
		self.can_modify_labels: bool = False
		self.can_print: bool = False
		self.can_read_all_permissions: bool = False
		self.can_read_labels: bool = False
		self.can_read_revisions: bool = False
		self.can_set_missing_required_fields: bool = False
		self.can_share_as_commenter: bool = False
		self.can_share_as_file_organizer: bool = False
		self.can_share_as_organizer: bool = False
		self.can_share_as_owner: bool = False
		self.can_share_as_reader: bool = False
		self.can_share_as_writer: bool = False
		self.can_share_published_view_as_reader: bool = False
		self.can_share_to_all_users: bool = False
		self.can_add_folder_from_another_drive: bool = False
		self.can_delete_children: bool = False
		self.can_move_item_out_of_team_drive: bool = False
		self.can_move_item_within_team_drive: bool = False
		self.can_move_team_drive_item: bool = False
		self.can_read_team_drive: bool = False
		self.can_trash_children: bool = False

	def _scrape(self, capabilities_data: Dict[str, bool]):
		self.can_add_children = capabilities_data.get('canAddChildren')
		self.can_add_my_drive_parent = capabilities_data.get('canAddMyDriveParent')
		self.can_block_owner = capabilities_data.get('canBlockOwner')
		self.can_change_security_update_enabled = capabilities_data.get('canChangeSecurityUpdateEnabled')
		self.can_copy = capabilities_data.get('canCopy')
		self.can_delete = capabilities_data.get('canDelete')
		self.can_download = capabilities_data.get('canDownload')
		self.can_edit = capabilities_data.get('canEdit')
		self.can_edit_category_metadata = capabilities_data.get('canEditCategoryMetadata')
		self.can_request_approval = capabilities_data.get('canRequestApproval')
		self.can_move_children_within_drive = capabilities_data.get('canMoveChildrenWithinDrive')
		self.can_move_item_into_team_drive = capabilities_data.get('canMoveItemIntoTeamDrive')
		self.can_move_item_within_drive = capabilities_data.get('canMoveItemWithinDrive')
		self.can_read = capabilities_data.get('canRead')
		self.can_read_category_metadata = capabilities_data.get('canReadCategoryMetadata')
		self.can_remove_children = capabilities_data.get('canRemoveChildren')
		self.can_remove_my_drive_parent = capabilities_data.get('canRemoveMyDriveParent')
		self.can_rename = capabilities_data.get('canRename')
		self.can_share = capabilities_data.get('canShare')
		self.can_share_child_files = capabilities_data.get('canShareChildFiles')
		self.can_share_child_folders = capabilities_data.get('canShareChildFolders')
		self.can_trash = capabilities_data.get('canTrash')
		self.can_untrash = capabilities_data.get('canUntrash')
		self.can_comment = capabilities_data.get('canComment')
		self.can_move_item_out_of_drive = capabilities_data.get('canMoveItemOutOfDrive')
		self.can_add_as_owner = capabilities_data.get('canAddAsOwner')
		self.can_add_as_organizer = capabilities_data.get('canAddAsOrganizer')
		self.can_add_as_file_organizer = capabilities_data.get('canAddAsFileOrganizer')
		self.can_add_as_writer = capabilities_data.get('canAddAsWriter')
		self.can_add_as_commenter = capabilities_data.get('canAddAsCommenter')
		self.can_add_as_reader = capabilities_data.get('canAddAsReader')
		self.can_change_to_owner = capabilities_data.get('canChangeToOwner')
		self.can_change_to_organizer = capabilities_data.get('canChangeToOrganizer')
		self.can_change_to_file_organizer = capabilities_data.get('canChangeToFileOrganizer')
		self.can_change_to_writer = capabilities_data.get('canChangeToWriter')
		self.can_change_to_commenter = capabilities_data.get('canChangeToCommenter')
		self.can_change_to_reader = capabilities_data.get('canChangeToReader')
		self.can_change_to_reader_on_published_view = capabilities_data.get('canChangeToReaderOnPublishedView')
		self.can_remove = capabilities_data.get('canRemove')
		self.can_accept_ownership = capabilities_data.get('canAcceptOwnership')
		self.can_add_encrypted_children = capabilities_data.get('canAddEncryptedChildren')
		self.can_change_copy_requires_writer_permission = capabilities_data.get('canChangeCopyRequiresWriterPermission')
		self.can_change_permission_expiration = capabilities_data.get('canChangePermissionExpiration')
		self.can_change_restricted_download = capabilities_data.get('canChangeRestrictedDownload')
		self.can_change_writers_can_share = capabilities_data.get('canChangeWritersCanShare')
		self.can_create_decrypted_copy = capabilities_data.get('canCreateDecryptedCopy')
		self.can_create_encrypted_copy = capabilities_data.get('canCreateEncryptedCopy')
		self.can_list_children = capabilities_data.get('canListChildren')
		self.can_manage_members = capabilities_data.get('canManageMembers')
		self.can_manage_visitors = capabilities_data.get('canManageVisitors')
		self.can_modify_content = capabilities_data.get('canModifyContent')
		self.can_modify_content_restriction = capabilities_data.get('canModifyContentRestriction')
		self.can_modify_labels = capabilities_data.get('canModifyLabels')
		self.can_print = capabilities_data.get('canPrint')
		self.can_read_all_permissions = capabilities_data.get('canReadAllPermissions')
		self.can_read_labels = capabilities_data.get('canReadLabels')
		self.can_read_revisions = capabilities_data.get('canReadRevisions')
		self.can_set_missing_required_fields = capabilities_data.get('canSetMissingRequiredFields')
		self.can_share_as_commenter = capabilities_data.get('canShareAsCommenter')
		self.can_share_as_file_organizer = capabilities_data.get('canShareAsFileOrganizer')
		self.can_share_as_organizer = capabilities_data.get('canShareAsOrganizer')
		self.can_share_as_owner = capabilities_data.get('canShareAsOwner')
		self.can_share_as_reader = capabilities_data.get('canShareAsReader')
		self.can_share_as_writer = capabilities_data.get('canShareAsWriter')
		self.can_share_published_view_as_reader = capabilities_data.get('canSharePublishedViewAsReader')
		self.can_share_to_all_users = capabilities_data.get('canShareToAllUsers')
		self.can_add_folder_from_another_drive = capabilities_data.get('canAddFolderFromAnotherDrive')
		self.can_delete_children = capabilities_data.get('canDeleteChildren')
		self.can_move_item_out_of_team_drive = capabilities_data.get('canMoveItemOutOfTeamDrive')
		self.can_move_item_within_team_drive = capabilities_data.get('canMoveItemWithinTeamDrive')
		self.can_move_team_drive_item = capabilities_data.get('canMoveTeamDriveItem')
		self.can_read_team_drive = capabilities_data.get('canReadTeamDrive')
		self.can_trash_children = capabilities_data.get('canTrashChildren')

class DriveVideoMediaMetadata(Parser):
	def __init__(self):
		self.width: int = 0
		self.height: int = 0
		self.duration_millis: str = ""

	def _scrape(self, video_media_metadata_data: Dict[str, any]):
		self.width = video_media_metadata_data.get('width')
		self.height = video_media_metadata_data.get('height')
		self.duration_millis = video_media_metadata_data.get('durationMillis')

class DriveLabelInfo(Parser):
	def __init__(self):
		self.label_count: int = 0
		self.incomplete: bool = False

	def _scrape(self, label_info_data: Dict[str, any]):
		self.label_count = label_info_data.get('labelCount')
		self.incomplete = label_info_data.get('incomplete')

class DrivePermission(Parser):
	def __init__(self):
		self.kind: str = ""
		self.id: str = ""
		self.self_link: str = ""
		self.role: str = ""
		self.additional_roles: List[str] = []
		self.type: str = ""
		self.selectable_roles: List[list] = []
		self.pending_owner: bool = False
		self.with_link: bool = False
		self.capabilities: DriveCapabilities = DriveCapabilities()
		self.user_id: str = ""
		self.name: str = ""
		self.email_address: str = ""
		self.domain: str = ""
		self.photo_link: str = ""
		self.deleted: bool = False
		self.is_collaborator_account: bool = False

	def _scrape(self, permission_data: Dict[str, any]):
		self.kind = permission_data.get('kind')
		self.id = permission_data.get('id')
		self.self_link = permission_data.get('selfLink')
		self.role = permission_data.get('role')
		self.additional_roles = permission_data.get('additionalRoles', [])
		self.type = permission_data.get('type')
		self.selectable_roles = permission_data.get('selectableRoles')
		self.pending_owner = permission_data.get('pendingOwner')
		self.with_link = permission_data.get('withLink')
		if (capabilities_data := permission_data.get('capabilities')):
			self.capabilities._scrape(capabilities_data)
		self.user_id = permission_data.get('userId')
		self.name = permission_data.get('name')
		self.email_address = permission_data.get('emailAddress')
		self.domain = permission_data.get('domain')
		self.photo_link = permission_data.get('photoLink')
		self.deleted = permission_data.get('deleted')
		self.is_collaborator_account = permission_data.get('isCollaboratorAccount')

class DrivePermissionsSummary(Parser):
	def __init__(self):
		self.entry_count: int = 0
		self.visibility: List[DriveMiniPermission] = []
		self.select_permissions: List[DrivePermission] = []

	def _scrape(self, permissions_summary_data: Dict[str, any]):
		self.entry_count = permissions_summary_data.get('entryCount')
		if (visibility_data := permissions_summary_data.get('visibility')):
			for visibility_data_item in visibility_data:
				visibility_item = DriveMiniPermission()
				visibility_item._scrape(visibility_data_item)
				self.visibility.append(visibility_item)
		if (select_permissions_data := permissions_summary_data.get('selectPermissions')):
			for select_permissions_data_item in select_permissions_data:
				select_permissions_item = DrivePermission()
				select_permissions_item._scrape(select_permissions_data_item)
				self.select_permissions.append(select_permissions_item)

class DriveMiniPermission(Parser):
	def __init__(self):
		self.permission_id: str = ""
		self.role: str = ""
		self.type: str = ""
		self.with_link: bool = False

	def _scrape(self, unknown_model4_data: Dict[str, any]):
		self.permission_id = unknown_model4_data.get('permissionId')
		self.role = unknown_model4_data.get('role')
		self.type = unknown_model4_data.get('type')
		self.with_link = unknown_model4_data.get('withLink')

class DrivePicture(Parser):
	def __init__(self):
		self.url: str = ""

	def _scrape(self, picture_data: Dict[str, str]):
		self.url = picture_data.get('url')

class DriveImageMediaMetadata(Parser):
	def __init__(self):
		self.width: int = 0
		self.height: int = 0
		self.rotation: int = 0

	def _scrape(self, image_media_metadata_data: Dict[str, int]):
		self.width = image_media_metadata_data.get('width')
		self.height = image_media_metadata_data.get('height')
		self.rotation = image_media_metadata_data.get('rotation')

class DriveLinkShareMetadata(Parser):
	def __init__(self):
		self.security_update_eligible: bool = False
		self.security_update_enabled: bool = False
		self.security_update_change_disabled_reason: str = ""
		self.security_update_explicitly_set: bool = False

	def _scrape(self, link_share_metadata_data: Dict[str, any]):
		self.security_update_eligible = link_share_metadata_data.get('securityUpdateEligible')
		self.security_update_enabled = link_share_metadata_data.get('securityUpdateEnabled')
		self.security_update_change_disabled_reason = link_share_metadata_data.get('securityUpdateChangeDisabledReason')
		self.security_update_explicitly_set = link_share_metadata_data.get('securityUpdateExplicitlySet')

class DriveChildList(Parser):
	def __init__(self):
		self.kind: str = ""
		self.etag: str = ""
		self.self_link: str = ""
		self.items: List[DriveChildReference] = []

	def _scrape(self, child_list_data: Dict[str, any]):
		self.kind = child_list_data.get('kind')
		self.etag = child_list_data.get('etag')
		self.self_link = child_list_data.get('selfLink')
		if (items_data := child_list_data.get('items')):
			for items_data_item in items_data:
				items_item = DriveChildReference()
				items_item._scrape(items_data_item)
				self.items.append(items_item)

class DriveChildReference(Parser):
	def __init__(self):
		self.id: str = ""
		self.self_link: str = ""
		self.kind: str = ""
		self.child_link: str = ""

	def _scrape(self, child_reference_data: Dict[str, str]):
		self.id = child_reference_data.get('id')
		self.self_link = child_reference_data.get('selfLink')
		self.kind = child_reference_data.get('kind')
		self.child_link = child_reference_data.get('childLink')

class DriveApp(Parser):
	def __init__(self):
		self.kind: str = ""
		self.id: str = ""
		self.name: str = ""
		self.type: str = ""
		self.short_description: str = ""
		self.long_description: str = ""
		self.supports_create: bool = False
		self.supports_import: bool = False
		self.supports_multi_open: bool = False
		self.supports_offline_create: bool = False
		self.supports_mobile_browser: bool = False
		self.installed: bool = False
		self.authorized: bool = False
		self.drive_branded_app: bool = False
		self.drive_branded: bool = False
		self.hidden: bool = False
		self.removable: bool = False
		self.has_drive_wide_scope: bool = False
		self.use_by_default: bool = False
		self.primary_mime_types: List[str] = []
		self.requires_authorization_before_open_with: bool = False
		self.supports_team_drives: bool = False
		self.supports_all_drives: bool = False

	def _scrape(self, app_data: Dict[str, any]):
		self.kind = app_data.get('kind')
		self.id = app_data.get('id')
		self.name = app_data.get('name')
		self.type = app_data.get('type')
		self.short_description = app_data.get('shortDescription')
		self.long_description = app_data.get('longDescription')
		self.supports_create = app_data.get('supportsCreate')
		self.supports_import = app_data.get('supportsImport')
		self.supports_multi_open = app_data.get('supportsMultiOpen')
		self.supports_offline_create = app_data.get('supportsOfflineCreate')
		self.supports_mobile_browser = app_data.get('supportsMobileBrowser')
		self.installed = app_data.get('installed')
		self.authorized = app_data.get('authorized')
		self.drive_branded_app = app_data.get('driveBrandedApp')
		self.drive_branded = app_data.get('driveBranded')
		self.hidden = app_data.get('hidden')
		self.removable = app_data.get('removable')
		self.has_drive_wide_scope = app_data.get('hasDriveWideScope')
		self.use_by_default = app_data.get('useByDefault')
		self.primary_mime_types = app_data.get('primaryMimeTypes')
		self.requires_authorization_before_open_with = app_data.get('requiresAuthorizationBeforeOpenWith')
		self.supports_team_drives = app_data.get('supportsTeamDrives')
		self.supports_all_drives = app_data.get('supportsAllDrives')

class DriveOpenWithLinks(Parser):
	def __init__(self):
		self.digitsfield: str = ""

	def _scrape(self, open_with_links_data: Dict[str, str]):
		self.digitsfield = open_with_links_data.get('digits_field')

class DriveParentReference(Parser):
	def __init__(self):
		self.kind: str = ""
		self.id: str = ""
		self.self_link: str = ""
		self.parent_link: str = ""
		self.is_root: bool = False

	def _scrape(self, parent_reference_data: Dict[str, any]):
		self.kind = parent_reference_data.get('kind')
		self.id = parent_reference_data.get('id')
		self.self_link = parent_reference_data.get('selfLink')
		self.parent_link = parent_reference_data.get('parentLink')
		self.is_root = parent_reference_data.get('isRoot')

class DriveSource(Parser):
	def __init__(self):
		self.client_service_id: str = ""
		self.value: str = ""

	def _scrape(self, source_data: Dict[str, str]):
		self.client_service_id = source_data.get('clientServiceId')
		self.value = source_data.get('value')

class DriveFolderProperties(Parser):
	def __init__(self):
		self.psyncho_root: bool = False
		self.psyncho_folder: bool = False
		self.machine_root: bool = False
		self.arbitrary_sync_folder: bool = False
		self.external_media: bool = False
		self.photos_and_videos_only: bool = False

	def _scrape(self, folder_properties_data: Dict[str, bool]):
		self.psyncho_root = folder_properties_data.get('psynchoRoot')
		self.psyncho_folder = folder_properties_data.get('psynchoFolder')
		self.machine_root = folder_properties_data.get('machineRoot')
		self.arbitrary_sync_folder = folder_properties_data.get('arbitrarySyncFolder')
		self.external_media = folder_properties_data.get('externalMedia')
		self.photos_and_videos_only = folder_properties_data.get('photosAndVideosOnly')

class DriveCommentList(Parser):
	def __init__(self):
		self.kind: str = ""
		self.self_link: str = ""
		self.items: List[DriveComment] = []

	def _scrape(self, comment_list_data: Dict[str, any]):
		self.kind = comment_list_data.get('kind')
		self.self_link = comment_list_data.get('selfLink')
		if (items_data := comment_list_data.get('items')):
			for items_data_item in items_data:
				items_item = DriveComment()
				items_item._scrape(items_data_item)
				self.items.append(items_item)

class DriveComment(Parser):
	def __init__(self):
		self.comment_id: str = ""
		self.kind: str = ""
		self.created_date: str = ""
		self.modified_date: str = ""
		self.file_id: str = ""
		self.status: str = ""
		self.anchor: str = ""
		self.replies: List[DriveCommentReply] = []
		self.author: DriveUser = DriveUser()
		self.deleted: bool = False
		self.html_content: str = ""
		self.content: str = ""
		self.context: DriveCommentContext = DriveCommentContext()
		self.file_title: str = ""

	def _scrape(self, comment_data: Dict[str, any]):
		self.comment_id = comment_data.get('commentId')
		self.kind = comment_data.get('kind')
		self.created_date = comment_data.get('createdDate')
		self.modified_date = comment_data.get('modifiedDate')
		self.file_id = comment_data.get('fileId')
		self.status = comment_data.get('status')
		self.anchor = comment_data.get('anchor')
		if (replies_data := comment_data.get('replies')):
			for replies_data_item in replies_data:
				replies_item = DriveCommentReply()
				replies_item._scrape(replies_data_item)
				self.replies.append(replies_item)
		if (author_data := comment_data.get('author')):
			self.author._scrape(author_data)
		self.deleted = comment_data.get('deleted')
		self.html_content = comment_data.get('htmlContent')
		self.content = comment_data.get('content')
		if (context_data := comment_data.get('context')):
			self.context._scrape(context_data)
		self.file_title = comment_data.get('fileTitle')

class DriveCommentContext(Parser):
	def __init__(self):
		self.type: str = ""
		self.value: str = ""

	def _scrape(self, context_data: Dict[str, str]):
		self.type = context_data.get('type')
		self.value = context_data.get('value')

class DriveCommentReply(Parser):
	def __init__(self):
		self.reply_id: str = ""
		self.kind: str = ""
		self.created_date: str = ""
		self.modified_date: str = ""
		self.author: DriveUser = DriveUser()
		self.deleted: bool = False
		self.html_content: str = ""
		self.content: str = ""

	def _scrape(self, comment_reply_data: Dict[str, any]):
		self.reply_id = comment_reply_data.get('replyId')
		self.kind = comment_reply_data.get('kind')
		self.created_date = comment_reply_data.get('createdDate')
		self.modified_date = comment_reply_data.get('modifiedDate')
		if (author_data := comment_reply_data.get('author')):
			self.author._scrape(author_data)
		self.deleted = comment_reply_data.get('deleted')
		self.html_content = comment_reply_data.get('htmlContent')
		self.content = comment_reply_data.get('content')