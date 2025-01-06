import os
import subprocess
import shutil
import time
import select
import sys
from PIL import Image
import tempfile
import cv2
import json

temp_dir = tempfile.gettempdir()
current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

with open("config.json", "r") as f:
    config = json.load(f)

class Bash:
    time_sleep = 0.1
    def __init__(self) -> None:
        # Créer un fichier temporaire pour rediriger stdout et stderr
        self.temp_fileOut = tempfile.NamedTemporaryFile(mode='w+', delete=False, dir=temp_dir)
        self.temp_fileOut_name = self.temp_fileOut.name  # Obtenir le nom du fichier temporaire
        self.temp_fileErr = tempfile.NamedTemporaryFile(mode='w+', delete=False, dir=temp_dir)
        self.temp_fileErr_name = self.temp_fileErr.name  # Obtenir le nom du fichier temporaire

        
        # Lancer le processus bash
        self.process = subprocess.Popen(
            ['bash','--posix'],  # Démarrer un shell bash
            stdin=subprocess.PIPE,  # Pour envoyer des commandes
            stdout=self.temp_fileOut,    # Rediriger stdout vers le fichier temporaire
            stderr=self.temp_fileErr,    # Rediriger stderr vers le fichier temporaire
            text=True                  # Pour gérer les chaînes de caractères
        )
        self.incOut = 0
        self.incErr = 0

    def SendCommand(self, command: str):
        time.sleep(Bash.time_sleep)
        """Envoyer une commande au shell."""
        if self.process.stdin and self.process.poll() is None:  # Vérifier si le stdin est ouvert
            self.process.stdin.write(command + '\n')  # Écrire la commande
            self.process.stdin.flush()  # Assurer que la commande est envoyée
        time.sleep(Bash.time_sleep)

    def ReadAllOutput(self):
        time.sleep(Bash.time_sleep)
        """Lire tout le contenu du fichier temporaire."""
        with open(self.temp_fileOut_name, 'r') as f:
            f.seek(self.incOut)
            output = f.read()  # Lire tout le contenu
            self.incOut = f.tell()
        return output
    
    def ReadAllError(self):
        time.sleep(Bash.time_sleep)
        """Lire tout le contenu du fichier temporaire."""
        with open(self.temp_fileErr_name, 'r') as f:
            f.seek(self.incErr)
            output = f.read()
            self.incErr = f.tell()
        return output

    def close(self):
        """Fermer le processus et le fichier temporaire."""
        self.process.stdin.close()  # Fermer l'entrée standard
        self.process.wait()  # Attendre que le processus se termine
        self.temp_fileOut.close()  # Fermer le fichier temporaire
        self.temp_fileErr.close()
    
    def __del__(self):
        self.close()
        # Supprimer les fichiers temporaires
        os.remove(self.temp_fileOut_name)
        os.remove(self.temp_fileErr_name)
bash = Bash()


PROGRAM_NAME = __file__

def is_pixel_or_percent(value):
    return value.isdigit() or (value.endswith('%') and value[:-1].isdigit())

def is_valid_x(x):
    return is_pixel_or_percent(x) or x in ["left", "center", "right"]

def is_valid_y(y):
    return is_pixel_or_percent(y) or y in ["top", "center", "bottom"]

def is_valid_size(size):
    return is_pixel_or_percent(size)

def validate_parameters(media, x=None, y=None, width=None, height=None):
    if not os.path.isfile(media) or not os.access(media, os.R_OK):
        print(f"{PROGRAM_NAME}: {media}: No such file or Permission denied")
        exit(1)

    if x and not is_valid_x(x):
        print(f"{PROGRAM_NAME}: {x}: Invalid argument")
        exit(1)

    if y and not is_valid_y(y):
        print(f"{PROGRAM_NAME}: {y}: Invalid argument")
        exit(1)

    if width and not is_valid_size(width):
        print(f"{PROGRAM_NAME}: {width}: Invalid argument")
        exit(1)

    if height and not is_valid_size(height):
        print(f"{PROGRAM_NAME}: {height}: Invalid argument")
        exit(1)

def get_screen_size():
    bash.SendCommand("xrandr | grep '*' | awk '{print $1}'")
    output = bash.ReadAllOutput()
    return map(int, output.splitlines()[0].split('x'))

def get_video_dimensions(file_path):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise ValueError("Could not open the video file.")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height
    
def get_media_size(media):
    bash.ReadAllOutput()
    #can be png, jpg, gif, mp4, webm
    if media.endswith(".gif") or media.endswith(".png") or media.endswith(".jpg"):
        img = Image.open(media)
        return img.size
    elif media.endswith(".mp4") or media.endswith(".webm"):
        #bash.SendCommand(f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {media}")
        #output = bash.ReadAllOutput()
        #res = output.strip().lower().split('x')
        #return int(res[0]), int(res[1])
        return get_video_dimensions(media)

def parse_parameters(media, x=None, y=None, width=None, height=None):
    validate_parameters(media, x, y, width, height)
    bash.ReadAllOutput()
    s_width, s_height = get_screen_size()
    m_width, m_height = get_media_size(media)

    w_width = convert_size(width or f"{s_width // 10}", s_width)
    w_height = convert_size(height or f"{(w_width * m_height) // m_width}", s_height)

    pos_x = convert_pos(x or "center", s_width, w_width)
    pos_y = convert_pos(y or "center", s_height, w_height)

    return media, pos_x, pos_y, w_width, w_height

def convert_size(size, max_size):
    if size.endswith('%'):
        size = int(size[:-1])
        return (size * max_size) // 100
    return int(size)

def convert_pos(pos, screen_size, window_size):
    if pos in ["left", "top"]:
        pos = 0
    elif pos == "center":
        pos = "50%"
    elif pos in ["right", "bottom"]:
        pos = "100%"

    if pos.endswith('%'):
        pos = int(pos[:-1])
        return ((screen_size - window_size) * pos) // 100
    return int(pos)

def wait_for_window_id_from_pid(pid):
    win_id = None
    while not win_id:
        bash.SendCommand(f"wmctrl -l -p | awk '{{if ($3 == {pid}) print $1}}'")
        win_id = bash.ReadAllOutput().strip()
        time.sleep(1)
    return win_id

def start_media(media, x, y, width, height):
    font = config.get("font", "Arial")
    bash.SendCommand(f"mpv {media} --no-input-terminal --geometry=\"{width}x{height}+{x}+{y}\" --loop --osd-font=\"{font}\" --osd-font-size=70 --osd-align-x=center --osd-align-y=center --script=osd_update.lua > /dev/null 2>&1 & pid=$!")
    bash.ReadAllOutput().strip()
    bash.SendCommand("echo $!")
    pid = bash.ReadAllOutput().strip()
    window_id = wait_for_window_id_from_pid(pid)
    return window_id, pid

def bring_window_to_top(window_id):
    bash.SendCommand(f"xdotool set_window --overrideredirect 1 {window_id}")
    bash.SendCommand(f"xdotool windowunmap --sync {window_id}")
    bash.SendCommand(f"xdotool windowmap --sync {window_id}")
    bash.SendCommand(f"xdotool windowraise {window_id}")
    
def resize_window(window_id, width, height):
    bash.SendCommand(f"xdotool windowsize --sync {window_id} {width} {height}")

def move_window(window_id, x, y):
    time.sleep(1)
    bash.SendCommand(f"xdotool windowmove --sync {window_id} {x} {y}")
    
def ft_lock():
    bash.SendCommand("ft_lock -n pimp_my_lock -t 0 -d 0 -c 0 -p 0 -b 0 -o 0")

def wait_for_ft_lock():
    while subprocess.call("xwininfo -name ft_lock 2> /dev/null | grep \"IsViewable\" > /dev/null 2>&1", shell=True) != 0:
        time.sleep(0.1)

def wait_for_ft_lock_end():
    while subprocess.call("xwininfo -name ft_lock 2> /dev/null | grep \"IsViewable\" > /dev/null 2>&1", shell=True) == 0:
        subprocess.call(["xdotool", "click", "1"])
        time.sleep(0.1)

def check_dependencies():
    dependencies = ['ft_lock', 'mpv', 'xwininfo', 'grep', 'awk', 'wmctrl', 'xdotool']
    for dep in dependencies:
        if shutil.which(dep) is None:
            print(f"{dep} is not installed!")
            exit(1)

check_dependencies()
args = ["path", "center", "center", "100%", "100%"]

media_lst = config.get("wallpapers", {})


if len(list(media_lst.keys())) == 0:
    print("No wallpapers found in config.json")
    exit(1)

message = ""

args[0] = list(media_lst.keys())[0]

args_sys = sys.argv[1:]
while len(args_sys) > 0:
    if args_sys[0] == "--list":
        count = 0
        for k, v in media_lst.items():
            print(f"{count}: {v}")
            count += 1
        exit(0)
    elif args_sys[0] == "--media":
        if len(args_sys) < 2:
            print("Invalid argument --media")
            exit(1)
        args[0] = args_sys[1]
        args_sys = args_sys[2:]
    elif args_sys[0] == "--msg":
        if len(args_sys) < 2:
            print("Invalid argument --msg")
            exit(1)
        message = args_sys[1].replace("\\n", "\n").replace('"', '\\"')+ "\n"
        args_sys = args_sys[2:]
    else:
        print("Invalid argument", args_sys[0])
        exit(1)

bash.SendCommand(f"export MSG_LOCK=\"{message}\"")
bash.ReadAllOutput()

#check extension of media, if not mp4, webm, gif, png, jpg, exit
if not any([args[0].endswith(ext) for ext in [".mp4", ".webm", ".gif", ".png", ".jpg"]]):
    print("Invalid media file extension")
    exit(1)

media, pos_x, pos_y, w_width, w_height = parse_parameters(*args)
#print(media, pos_x, pos_y, w_width, w_height)

ft_lock()
wait_for_ft_lock()
window_id, pid = start_media(media, pos_x, pos_y, w_width, w_height)

bring_window_to_top(window_id)
resize_window(window_id, w_width, w_height)
move_window(window_id, pos_x, pos_y)

#time.sleep(3)
wait_for_ft_lock_end()
os.kill(int(pid), 9)

bash.close()