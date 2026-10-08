from . import api_chats,api_messages,api_uploads,api_library,api_image_files,api_settings,api_debug


def install(routes,e):
    for module in (api_chats,api_messages,api_uploads,api_library,api_image_files,api_settings,api_debug):
        module.install(routes,e)
