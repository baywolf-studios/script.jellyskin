import xml.etree.ElementTree as ET
import json
import os
import xbmc
import xbmcaddon
import xbmcvfs
import xbmcgui
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')


def walk_path(root_path, relative_path, all_files):
    files = xbmcvfs.listdir(root_path)
    found_paths = files[0]
    found_files = files[1]

    for item in found_files:
        rel_path = os.path.join(relative_path, item)
        all_files.append(rel_path)

    for item in found_paths:
        new_path = os.path.join(root_path, item)
        rel_path = os.path.join(relative_path, item)
        all_files.append(rel_path)
        walk_path(new_path, rel_path, all_files)


def clone_skin():
    xbmc.log("Cloning Estuary Skin")

    kodi_path = xbmcvfs.translatePath("special://xbmc")
    kodi_skin_source = os.path.join(kodi_path, "addons", "skin.estuary")
    xbmc.log("Kodi Skin Source: {0}".format(kodi_skin_source))

    pdialog = xbmcgui.DialogProgress()
    pdialog.create(addonname, "")

    all_files = []
    walk_path(kodi_skin_source, "", all_files)
    for found in all_files:
        xbmc.log("Found Path: {0}".format(found))

    kodi_home_path = xbmcvfs.translatePath("special://home")
    kodi_skin_destination = os.path.join(
        kodi_home_path, "addons", "skin.jellyskin"
    )
    xbmc.log("Kodi Skin Destination: {0}".format(kodi_skin_destination))

    # copy all skin files (clone)
    count = 0
    total = len(all_files)
    for skin_file in all_files:
        percentage_done = int(float(count) / float(total) * 100.0)
        pdialog.update(percentage_done, skin_file)

        source = os.path.join(kodi_skin_source, skin_file)
        destination = os.path.join(kodi_skin_destination, skin_file)
        xbmcvfs.copy(source, destination)

        count += 1

    addon_xml_path = os.path.join(kodi_skin_destination, "addon.xml")
    addon_tree = ET.parse(addon_xml_path)
    addon_root = addon_tree.getroot()

    addon_root.attrib['id'] = 'skin.jellyskin'
    addon_root.attrib['name'] = 'Jellyskin'

    addon_tree.write(addon_xml_path)

    # skin modifications
    home_xml_path = os.path.join(kodi_skin_destination, "xml", "home.xml")
    home_tree = ET.parse(home_xml_path)

    # Parse the XML
    home_tree = ET.parse(home_xml_path)
    home_root = home_tree.getroot()

    # Create the new home main menu item 
    home_item = ET.Element("item")
    ET.SubElement(home_item, "label").text = "Home"
    ET.SubElement(home_item, "property", name="menu_id").text = "$NUMBER[3000]"
    ET.SubElement(home_item, "thumb").text = "home.png"
    ET.SubElement(home_item, "property", name="id").text = "home"

    # Create the new widgets for the home main menu item
    home_widgets_3000 = ET.Element("control", {"type": "group", "id": "3000"})
    ET.SubElement(home_widgets_3000, "visible").text = "String.IsEqual(Container(9000).ListItem.Property(id),home)"
    include_visible = ET.SubElement(home_widgets_3000, "include", {"content": "Visible_Right_Delayed"})
    ET.SubElement(include_visible, "param", {"name": "id", "value": "home"})
    home_widgets_3001 = ET.SubElement(home_widgets_3000, "control", {"type": "grouplist", "id": "3001"})
    ET.SubElement(home_widgets_3001, "include").text = "WidgetGroupListCommon"
    ET.SubElement(home_widgets_3001, "pagecontrol").text = "3010"

    # My Media
    home_widget_my_media = ET.SubElement(home_widgets_3001, "include", {"content": "WidgetListEpisodes"})
    ET.SubElement(home_widget_my_media, "param", {"name": "content_path", "value": "favourites://"})
    ET.SubElement(home_widget_my_media, "param", {"name": "widget_header", "value": "My Media"})
    ET.SubElement(home_widget_my_media, "param", {"name": "main_label", "value": "$INFO[ListItem.Label]"})
    ET.SubElement(home_widget_my_media, "param", {"name": "list_id", "value": "3100"})

    # Continue Watching
    home_widget_continue_watching = ET.SubElement(home_widgets_3001, "include", {"content": "WidgetListEpisodes"})
    ET.SubElement(home_widget_continue_watching, "param", {
        "name": "content_path",
        "value": (
            "plugin://plugin.video.jellycon/?media_type=mixed&mode=GET_CONTENT&sort=none"
            "&reload=$INFO[Window(Home).Property(plugin.video.jellycon-jellycon_widget_reload)]"
            "&url=%2FUsers%2F%7Buserid%7D%2FItems%2FResume%3FFields%3D%7Bfield_filters%7D%26Limit%3D24"
        )
    })
    ET.SubElement(home_widget_continue_watching, "param", {"name": "widget_header", "value": "Continue Watching"})
    ET.SubElement(home_widget_continue_watching, "param", {"name": "widget_target", "value": "videos"})
    ET.SubElement(home_widget_continue_watching, "param", {"name": "widget_limit", "value": "24"})
    ET.SubElement(home_widget_continue_watching, "param", {"name": "browse_mode", "value": "never"})
    ET.SubElement(home_widget_continue_watching, "param", {"name": "list_id", "value": "3200"})

    # Next Up
    home_widget_next_up = ET.SubElement(home_widgets_3001, "include", {"content": "WidgetListEpisodes"})
    ET.SubElement(home_widget_next_up, "param", {
        "name": "content_path",
        "value": (
            "plugin://plugin.video.jellycon/?media_type=mixed&mode=GET_CONTENT&sort=none"
            "&reload=$INFO[Window(Home).Property(plugin.video.jellycon-jellycon_widget_reload)]"
            "&url=%2FShows%2FNextUp%3Fuserid%3D%7Buserid%7D%26Fields%3D%7Bfield_filters%7D%26EnableResumable%3Dfalse%26EnableRewatching%3Dfalse%26Limit%3D24"
        )
    })
    ET.SubElement(home_widget_next_up, "param", {"name": "widget_header", "value": "Next Up"})
    ET.SubElement(home_widget_next_up, "param", {"name": "widget_target", "value": "videos"})
    ET.SubElement(home_widget_next_up, "param", {"name": "widget_limit", "value": "24"})
    ET.SubElement(home_widget_next_up, "param", {"name": "browse_mode", "value": "never"})
    ET.SubElement(home_widget_next_up, "param", {"name": "list_id", "value": "3400"})

    # Final include: WidgetScrollbar
    include_scrollbar = ET.SubElement(home_widgets_3000, "include", {
        "content": "WidgetScrollbar",
        "condition": "Skin.HasSetting(touchmode)"
    })
    ET.SubElement(include_scrollbar, "param", {"name": "scrollbar_id", "value": "5010"})


    # Find controls
    main_menu_control = None
    main_menu_widgets_control = None
    for control in home_root.findall(".//control"):
        if control.attrib.get("id") == "9000":
            main_menu_control = control
        if control.attrib.get("id") == "2000":
            main_menu_widgets_control = control

    if main_menu_control is not None:
        content = main_menu_control.find("content")
        if content is not None:
            content.insert(0, home_item)
            xbmc.log("Item inserted inside <content>.")
        else:
            xbmc.log("<content> element not found inside <control>.")
    else:
        xbmc.log("<control type='fixedlist' id='9000'> not found.")

    if main_menu_widgets_control is not None:
        main_menu_widgets_control.append(home_widgets_3000)
            
    # Save the modified file
    home_tree.write(home_xml_path)

    xbmc.executebuiltin("UpdateLocalAddons")

    enable_json_params = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "Addons.SetAddonEnabled",
        "params": 
            {
                "addonid": "skin.jellyskin", 
                "enabled": True
            }
    }
    xbmc.executeJSONRPC(json.dumps(enable_json_params))

    pdialog.close()
    del pdialog

    response = xbmcgui.Dialog().yesno(
        addonname,
        "Do you want to switch to the new cloned skin?"
    )
    if response:
        use_json_params = {
            "jsonrpc": "2.0",
            "method": "Settings.SetSettingValue",
            "id": 1,
            "params":{
                "setting": "lookandfeel.skin",
                "value": "skin.jellyskin"
                }
            }
        xbmc.executeJSONRPC(json.dumps(use_json_params))
        
        

response = xbmcgui.Dialog().yesno(
    addonname,
    "This will clone the default Estuary Kodi skin and add JellyCon functionality to it. Do you want to continue?")
if response:
    clone_skin()
