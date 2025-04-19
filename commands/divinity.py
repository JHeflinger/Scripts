"""
author: Jason Heflinger
description: Features several helper commands to easily manage the divinity project, ranging
             from creation of scenes, ui, to editing levels and auditing syntax.
"""

import sys
import os
import re

def intstr(myint):
    if myint < 10:
        return "00" + str(myint)
    if myint < 100:
        return "0" + str(myint)
    return str(myint)

if (len(sys.argv) <= 1):
    print("Available syntax:")
    print("\tall                                | lists all available commands and their variations extensively")
    print("\tdivinity bake                      | Analyzes assets and bakes them into \"src/assets/pack.h\" accordingly")
    print("\tdivinity new <type>                | Creates a new integration into the project, such as a level or an asset")
    exit()

if sys.argv[1] == 'all':
    print("Extensive commands:")
    print("\tdivinity all")
    print("\tdivinity bake")
    print("\tdivinity new scene")
    print("\tdivinity new ui")
    print("\tdivinity new card")
    print("\tdivinity new object")
    exit()

def handle():
    precursor = sys.argv[1]
    if (precursor == "new"):
        if (len(sys.argv) != 3):
            return False
        newtype = sys.argv[2]
        if (newtype == "scene"):
            scenename = input("What would you like this scene to be called? ")
            if os.path.exists(os.path.join("src/scenes/trunk/", scenename + ".h")):
                print("This scene already exists")
                return True
            num_scenes = 0
            for root, dirs, files in os.walk("src/scenes/trunk"):
                for file in files:
                    filepath = os.path.join(root, file)
                    if ".h" in filepath:
                        num_scenes += 1
            scenes_content = []
            with open("src/scenes/trunk/scenes.h", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    scenes_content = lines[:-3]
                else:
                    scenes_content = lines[:-2]
            scenes_content.append("#include \"scenes/trunk/" + scenename + ".h\"")
            scenes_content.append("")
            scenes_content.append("#endif")
            new_scene_content = ""
            new_scene_content += "#ifndef " + scenename.upper() + "_SCENE_H\n"
            new_scene_content += "#define " + scenename.upper() + "_SCENE_H\n"
            new_scene_content += "\n"
            new_scene_content += "#include \"scenes/scene.h\"\n"
            new_scene_content += "\n"
            new_scene_content += "Scene* Generate" + scenename[0].upper() + scenename[1:] + "Scene();\n"
            new_scene_content += "\n"
            new_scene_content += "#endif"
            new_source_content = ""
            new_source_content += "#include \"" + scenename + ".h\"\n"
            new_source_content += "\n"
            new_source_content += "Scene* Generate" + scenename[0].upper() + scenename[1:] + "Scene() {\n"
            new_source_content += "    Scene* scene = GenerateDefaultScene();\n"
            new_source_content += "    scene->id = " + str(num_scenes) + ";\n"
            new_source_content += "    \n"
            new_source_content += "    return scene;\n"
            new_source_content += "}\n"
            config_content = []
            with open("src/scenes/scene.c", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    config_content = lines[:-5]
                else:
                    config_content = lines[:-4]
            config_content.append("        case " + str(num_scenes) + ":")
            config_content.append("            return Generate" + scenename[0].upper() + scenename[1:] + "Scene();")
            config_content.append("        default: LOG_ASSERT(0, \"Unable to generate a scene with this ID\");")
            config_content.append("    }")
            config_content.append("    return NULL;")
            config_content.append("}")
            scenes_content_str = ""
            for line in scenes_content:
                scenes_content_str += line + "\n"
            scenes_content_str = scenes_content_str[:-1]
            config_content_str = ""
            for line in config_content:
                config_content_str += line + "\n"
            config_content_str = config_content_str[:-1]
            with open("src/scenes/trunk/scenes.h", "w") as f:
                f.write(scenes_content_str)
            with open(os.path.join("src/scenes/trunk/", scenename + ".h"), "w") as f:
                f.write(new_scene_content)
            with open(os.path.join("src/scenes/trunk/", scenename + ".c"), "w") as f:
                f.write(new_source_content)
            with open("src/scenes/scene.c", "w") as f:
                f.write(config_content_str)
            print("Created and integrated new scene file into " + str(os.path.join("src/scenes/trunk/", scenename + ".h")))
            return True
        if (newtype == "ui"):
            uiname = input("What would you like this component to be called? ")
            if os.path.exists(os.path.join("src/ui/trunk/", uiname + ".h")):
                print("This component already exists")
                return True
            num_ui = 0
            for root, dirs, files in os.walk("src/ui/trunk"):
                for file in files:
                    filepath = os.path.join(root, file)
                    if ".h" in filepath:
                        num_ui += 1
            uis_content = []
            with open("src/ui/trunk/uis.h", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    uis_content = lines[:-3]
                else:
                    uis_content = lines[:-2]
            uis_content.append("#include \"ui/trunk/" + uiname + ".h\"")
            uis_content.append("")
            uis_content.append("#endif")
            new_ui_content = ""
            new_ui_content += "#ifndef " + uiname.upper() + "_UI_H\n"
            new_ui_content += "#define " + uiname.upper() + "_UI_H\n"
            new_ui_content += "\n"
            new_ui_content += "#include \"ui/ui.h\"\n"
            new_ui_content += "\n"
            new_ui_content += "UI* Generate" + uiname[0].upper() + uiname[1:] + "UI();\n"
            new_ui_content += "\n"
            new_ui_content += "#endif"
            new_source_content = ""
            new_source_content += "#include \"" + uiname + ".h\"\n"
            new_source_content += "\n"
            new_source_content += "UI* Generate" + uiname[0].upper() + uiname[1:] + "UI() {\n"
            new_source_content += "    UI* ui = GenerateDefaultUI();\n"
            new_source_content += "    ui->id = " + str(num_ui) + ";\n"
            new_source_content += "    \n"
            new_source_content += "    return ui;\n"
            new_source_content += "}\n"
            config_content = []
            with open("src/ui/ui.c", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    config_content = lines[:-5]
                else:
                    config_content = lines[:-4]
            config_content.append("        case " + str(num_ui) + ":")
            config_content.append("            return Generate" + uiname[0].upper() + uiname[1:] + "UI();")
            config_content.append("        default: LOG_ASSERT(0, \"Unable to generate a ui with this ID\");")
            config_content.append("    }")
            config_content.append("    return NULL;")
            config_content.append("}")
            uis_content_str = ""
            for line in uis_content:
                uis_content_str += line + "\n"
            uis_content_str = uis_content_str[:-1]
            config_content_str = ""
            for line in config_content:
                config_content_str += line + "\n"
            config_content_str = config_content_str[:-1]
            with open("src/ui/trunk/uis.h", "w") as f:
                f.write(uis_content_str)
            with open(os.path.join("src/ui/trunk/", uiname + ".h"), "w") as f:
                f.write(new_ui_content)
            with open(os.path.join("src/ui/trunk/", uiname + ".c"), "w") as f:
                f.write(new_source_content)
            with open("src/ui/ui.c", "w") as f:
                f.write(config_content_str)
            print("Created and integrated new ui file into " + str(os.path.join("src/ui/trunk/", uiname + ".h")))
            return True
        if (newtype == "card"):
            cardname = input("What would you like this card to be called? ")
            oldname = cardname
            cardname = cardname.replace(" ", "_")
            cardname = cardname.lower()
            num_card = 0
            for root, dirs, files in os.walk("src/cards/trunk"):
                for file in files:
                    filepath = os.path.join(root, file)
                    if ".h" in filepath:
                        num_card += 1
            if (num_card < 10):
                cardname = "00" + str(num_card) + "_" + cardname
            elif (num_card < 100):
                cardname = "0" + str(num_card) + "_" + cardname
            elif (num_card < 1000):
                cardname = str(num_card) + "_" + cardname
            else:
                print("Reached limit for number of cards that can be created")
                return False
            cards_content = []
            with open("src/cards/trunk/cards.h", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    cards_content = lines[:-3]
                else:
                    cards_content = lines[:-2]
            cards_content.append("#include \"cards/trunk/" + cardname + ".h\"")
            cards_content.append("")
            cards_content.append("#endif")
            new_card_content = ""
            new_card_content += "#ifndef CARD_" + cardname.upper() + "_H\n"
            new_card_content += "#define CARD_" + cardname.upper() + "_H\n"
            new_card_content += "\n"
            new_card_content += "#include \"cards/card.h\"\n"
            new_card_content += "\n"
            new_card_content += "Card* GenerateCard" + cardname[0:3] + "();\n"
            new_card_content += "\n"
            new_card_content += "#endif"
            new_source_content = ""
            new_source_content += "#include \"" + cardname + ".h\"\n"
            new_source_content += "\n"
            new_source_content += "BOOL card_" + cardname[0:3] + "_behavior(CastInfo* info) {\n"
            new_source_content += "    return TRUE;\n"
            new_source_content += "}\n"
            new_source_content += "\n"
            new_source_content += "Card* GenerateCard" + cardname[0:3] + "() {\n"
            new_source_content += "    Card* card = GenerateDefaultCard();\n"
            new_source_content += "    card->id = " + str(num_card) + ";\n"
            new_source_content += "    card->behavior = card_" + cardname[0:3] + "_behavior;\n"
            new_source_content += "    strcpy(card->name, \"" + oldname + "\");\n"
            new_source_content += "    \n"
            new_source_content += "    return card;\n"
            new_source_content += "}\n"
            config_content = []
            with open("src/cards/card.c", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    config_content = lines[:-5]
                else:
                    config_content = lines[:-4]
            config_content.append("        case " + str(num_card) + ":")
            config_content.append("            return GenerateCard" + cardname[0:3] + "();")
            config_content.append("        default: LOG_ASSERT(0, \"Unable to generate a card with this ID\");")
            config_content.append("    }")
            config_content.append("    return NULL;")
            config_content.append("}")
            cards_content_str = ""
            for line in cards_content:
                cards_content_str += line + "\n"
            cards_content_str = cards_content_str[:-1]
            config_content_str = ""
            for line in config_content:
                config_content_str += line + "\n"
            config_content_str = config_content_str[:-1]
            with open("src/cards/trunk/cards.h", "w") as f:
                f.write(cards_content_str)
            with open(os.path.join("src/cards/trunk/", cardname + ".h"), "w") as f:
                f.write(new_card_content)
            with open(os.path.join("src/cards/trunk/", cardname + ".c"), "w") as f:
                f.write(new_source_content)
            with open("src/cards/card.c", "w") as f:
                f.write(config_content_str)
            print("Created and integrated new card file into " + str(os.path.join("src/cards/trunk/", cardname + ".h")))
            return True
        if (newtype == "object"):
            objname = input("What would you like this object to be called? ")
            oldname = objname
            objname = objname.replace(" ", "_")
            objname = objname.lower()
            num_object = 0
            for root, dirs, files in os.walk("src/objects/trunk"):
                for file in files:
                    filepath = os.path.join(root, file)
                    if ".h" in filepath:
                        num_object += 1
            if (num_object < 10):
                objname = "00" + str(num_object) + "_" + objname
            elif (num_object < 100):
                objname = "0" + str(num_object) + "_" + objname
            elif (num_object < 1000):
                objname = str(num_object) + "_" + objname
            else:
                print("Reached limit for number of objects that can be created")
                return False
            objects_content = []
            with open("src/objects/trunk/objects.h", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    objects_content = lines[:-3]
                else:
                    objects_content = lines[:-2]
            objects_content.append("#include \"objects/trunk/" + objname + ".h\"")
            objects_content.append("")
            objects_content.append("#endif")
            new_object_content = ""
            new_object_content += "#ifndef OBJECT_" + objname.upper() + "_H\n"
            new_object_content += "#define OBJECT_" + objname.upper() + "_H\n"
            new_object_content += "\n"
            new_object_content += "#include \"objects/object.h\"\n"
            new_object_content += "\n"
            new_object_content += "Object* GenerateObject" + objname[0:3] + "();\n"
            new_object_content += "\n"
            new_object_content += "#endif"
            new_source_content = ""
            new_source_content += "#include \"" + objname + ".h\"\n"
            new_source_content += "\n"
            new_source_content += "void object_" + objname[0:3] + "_behavior(void* raw_object) {\n"
            new_source_content += "    Object* obj = (Object*)raw_object;\n"
            new_source_content += "}\n"
            new_source_content += "\n"
            new_source_content += "void object_" + objname[0:3] + "_update(void* raw_object) {\n"
            new_source_content += "    Object* obj = (Object*)raw_object;\n"
            new_source_content += "}\n"
            new_source_content += "\n"
            new_source_content += "void object_" + objname[0:3] + "_destroy(void* raw_object) {\n"
            new_source_content += "    Object* obj = (Object*)raw_object;\n"
            new_source_content += "}\n"
            new_source_content += "\n"
            new_source_content += "Object* GenerateObject" + objname[0:3] + "() {\n"
            new_source_content += "    Object* object = GenerateDefaultObject();\n"
            new_source_content += "    object->id = " + str(num_object) + ";\n"
            new_source_content += "    object->behavior = object_" + objname[0:3] + "_behavior;\n"
            new_source_content += "    object->update = object_" + objname[0:3] + "_update;\n"
            new_source_content += "    object->destroy = object_" + objname[0:3] + "_destroy;\n"
            new_source_content += "    strcpy(object->name, \"" + oldname + "\");\n"
            new_source_content += "    \n"
            new_source_content += "    return object;\n"
            new_source_content += "}\n"
            config_content = []
            with open("src/objects/object.c", "r") as f:
                lines = f.read().split("\n")
                if lines[-1].strip() == "":
                    config_content = lines[:-5]
                else:
                    config_content = lines[:-4]
            config_content.append("        case " + str(num_object) + ":")
            config_content.append("            return GenerateObject" + objname[0:3] + "();")
            config_content.append("        default: LOG_ASSERT(0, \"Unable to generate an object with this ID\");")
            config_content.append("    }")
            config_content.append("    return NULL;")
            config_content.append("}")
            objects_content_str = ""
            for line in objects_content:
                objects_content_str += line + "\n"
            objects_content_str = objects_content_str[:-1]
            config_content_str = ""
            for line in config_content:
                config_content_str += line + "\n"
            config_content_str = config_content_str[:-1]
            with open("src/objects/trunk/objects.h", "w") as f:
                f.write(objects_content_str)
            with open(os.path.join("src/objects/trunk/", objname + ".h"), "w") as f:
                f.write(new_object_content)
            with open(os.path.join("src/objects/trunk/", objname + ".c"), "w") as f:
                f.write(new_source_content)
            with open("src/objects/object.c", "w") as f:
                f.write(config_content_str)
            print("Created and integrated new object file into " + str(os.path.join("src/objects/trunk/", objname + ".h")))
            return True
        return False
    if (precursor == "bake"):
        bake_required = False
        num_tiles = 0

        # get tile stats
        for root, dirs, files in os.walk("assets/tiles"):
            for file in files:
                filepath = os.path.join(root, file)
                if ".png" in filepath:
                    num_tiles += 1

        # construct pack
        pack_str  = "#ifndef PACK_H\n"
        pack_str += "#define PACK_H\n"
        pack_str += "\n"
        pack_str += f"#define TILE_ASSET_COUNT {num_tiles}\n"
        pack_str += "\n"
        pack_str += "#endif"

        if os.path.exists("src/assets/pack.h"):
            with open("src/assets/pack.h", 'r') as f:
                src = f.read()
                bake_required = src != pack_str
        else:
            bake_required = True

        if bake_required:
            print("Assets were detected to be out of date... baking assets now")
            with open("src/assets/pack.h", 'w') as f:
                f.write(pack_str)
            print("Assets \033[32msuccessfully\033[0m baked!")
        else:
            print("Assets are currently \033[32mup to date\033[0m - no baking needed!")
        return True
    return False

if (handle() == False):
    print("Invalid command detected - please use help command with no args for a list of available commands")
