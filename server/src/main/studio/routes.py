from . import api_chats,api_messages,api_uploads,api_library,api_image_files,api_settings,api_debug
from . import api_branches,api_search,api_export,api_storage,api_edits,api_documents,api_backup


def install(routes,e):
    for module in (api_chats,api_messages,api_uploads,api_library,api_image_files,api_settings,api_debug,
                   api_branches,api_search,api_export,api_storage,api_edits,api_documents,api_backup):
        module.install(routes,e)
