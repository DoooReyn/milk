import json
import os
import subprocess

CUR_DIR = os.path.dirname(__file__)
QRC_CONFIG = os.path.join(CUR_DIR, 'resources.json')
QRC_ENCODING = 'utf-8'
QRC_HEADER = u'<!DOCTYPE RCC>\n<RCC version="1.0">\n<qresource>\n'
QRC_FOOTER = u'</qresource>\n</RCC>'
QRC_FILE_FMT = '<file alias="{0}/{1}">{2}/{0}/{1}</file>\n'
QRC_CMD_FMT = r'pyrcc5 -o {0} {1}'
QRC_MAP_HEADER = "class ResMap:\n"
QRC_MAP_ITEM_FMT = "\t{1}_{0} = \":/{1}/{2}\"\n"

if __name__ == '__main__':
    os.chdir(CUR_DIR)
    try:
        with open(QRC_CONFIG, 'r') as f_conf:
            config = json.loads(f_conf.read())
            qrc = config.get("qrc")
            out = config.get("out")
            root = config.get("root")
            dirs = config.get("dirs")
            map = config.get("map")
            if not qrc or not out or not root or not dirs or not map:
                raise json.JSONDecodeError

        map_class = [QRC_MAP_HEADER]
        with open(qrc, 'w') as f_qrc:
            f_qrc.write(QRC_HEADER)

            for d in dirs:
                for item in os.listdir(os.path.join(CUR_DIR, root, d)):
                    f_qrc.write(QRC_FILE_FMT.format(d, item, root))
                    name = str(os.path.splitext(item)[0])
                    name = name.replace("-", "_")
                    map_class.append(QRC_MAP_ITEM_FMT.format(name, d, item))

            f_qrc.write(QRC_FOOTER)

        with open(out, 'w') as f_out:
            cmd = QRC_CMD_FMT.format(out, qrc)
            subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             cwd=os.getcwd())

        with open(map, 'w') as f_map:
            f_map.write("".join(map_class))

        print("OK!")
    except Exception as e:
        print("Config read/parse Failed!", e)
