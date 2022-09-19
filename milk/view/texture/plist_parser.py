import plistlib
from pprint import pprint
import re
from os.path import exists


class PlistParser:
    class FileNotFoundException(ValueError):
        pass

    class InvalidFileException(ValueError):
        pass

    class InvalidFormatException(ValueError):
        pass

    class FloatNotSupportException(ValueError):
        pass

    @staticmethod
    def parse(plist_path):
        if not exists(plist_path):
            raise PlistParser.FileNotFoundException("No such file: {0}".format(plist_path))

        try:
            with open(plist_path, 'rb') as f:
                plist_dict = plistlib.load(f)
        except plistlib.InvalidFileException:
            raise PlistParser.InvalidFileException("Invalid plist file: {0}".format(plist_path))

        try:
            if isinstance(plist_dict, dict) and plist_dict.get("frames") and plist_dict.get(
                    "metadata"):
                metadata = plist_dict.get("metadata")
                plist_format = metadata.get("format")
                texture_name = metadata.get("textureFileName")
                plist_frames = plist_dict.get("frames")

                if plist_format not in (0, 1, 2, 3):
                    raise PlistParser.InvalidFormatException("Invalid plist format: {0}".format(plist_format))

                result = {
                    "frames": [],
                    "texture": texture_name
                }

                if plist_format == 0:
                    PlistParser.__parse_format_0(result, plist_frames)
                elif plist_format == 1 or plist_format == 2:
                    PlistParser.__parse_format_1x2(result, plist_frames)
                elif plist_format == 3:
                    PlistParser.__parse_format_3(result, plist_frames)

                return result
            else:
                raise PlistParser.InvalidFileException("Invalid plist file: {0}".format(plist_path))
        except ValueError:
            raise PlistParser.FloatNotSupportException("Not support float value in frame")

    @staticmethod
    def __parse_format_0(result: dict, plist_frames: dict):
        for (name, config) in plist_frames.items():
            try:
                ow = int(config.get("originalWidth", 0))
                oh = int(config.get("originalHeight", 0))
                sx = int(config.get("x", 0))
                sy = int(config.get("y", 0))
                ox = int(config.get("offsetX", 0))
                oy = int(config.get("offsetY", 0))
                result["frames"].append({
                    "name": name,
                    "rotated": False,
                    "source_size": (ow, oh),
                    "offset": (ox, oy),
                    "frame_rect": (sx, sy, ow, oh),
                    "crop_rect": (sx, sy, sx + ow, sy + oh)
                })
            except Exception as e:
                print("parse format 0: ", e)

    @staticmethod
    def __parse_format_1x2(result: dict, plist_frames: dict):
        for (name, config) in plist_frames.items():
            fx, fy, fw, fh = PlistParser.__extract_frame_field(config.get("frame"))
            cx, cy = PlistParser.__extract_frame_field(config.get("offset"))
            sw, sh = PlistParser.__extract_frame_field(config.get("sourceSize"))
            rotated = config.get("rotated", False)
            frame = PlistParser.__get_format1x2x3(name, rotated, fx, fy, fw, fh, cx, cy, sw, sh)
            result["frames"].append(frame)

    @staticmethod
    def __parse_format_3(result: dict, plist_frames: dict):
        for (name, config) in plist_frames.items():
            fx, fy, fw, fh = PlistParser.__extract_frame_field(config.get("textureRect"))
            cx, cy = PlistParser.__extract_frame_field(config.get("spriteOffset"))
            sw, sh = PlistParser.__extract_frame_field(config.get("spriteSourceSize"))
            rotated = config.get("textureRotated", False)
            frame = PlistParser.__get_format1x2x3(name, rotated, fx, fy, fw, fh, cx, cy, sw, sh)
            result["frames"].append(frame)
        pprint("__parse_format_3: ")
        pprint(result)

    @staticmethod
    def __get_format1x2x3(name, rotated, fx, fy, fw, fh, cx, cy, sw, sh):
        ow, oh = (fh, fw) if rotated else (fw, fh)

        return {
            "name": name,
            "rotated": rotated,
            "source_size": (sw, sh),
            "offset": (int(sw / 2 + cx - fw / 2), int(sh / 2 - cy - fh / 2)),
            "frame_rect": (fx, fy, ow, oh),
            "crop_rect": (fx, fy, fx + ow, fy + oh)
        }

    @staticmethod
    def __extract_frame_field(text):
        try:
            return (int(x) for x in re.sub(r"[{}]", "", text).split(','))
        except Exception as e:
            print("Fuck!", e)
