from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, TCON, TDRC, TCOM, TPE2,COMM
from pydub import AudioSegment
import os, warnings, re, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FolderWatcher(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.observer = Observer()

    def start(self):
        self.observer.schedule(self, path=self.folder_path, recursive=False)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.flac', '.ogg', '.wav', '.mp3')):
            print(f"New file created: {event.src_path}")
            main(target_folder)

def find_music_files(folder_path):
    music_extensions = ['.mp3', '.flac', '.ogg', '.wav']
    music_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in music_extensions):
                music_files.append(os.path.join(root, file))
    return music_files

def convert_to_mp3(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format='mp3', bitrate='320k')
        os.remove(input_file)
    except Exception as e:
        print(f"Error converting {input_file} to mp3: {str(e)}")

def change_music_file_name(file_path):
    new_file_name = re.sub(r"^\d+\.\s*|\d+\s+", "", os.path.basename(file_path))
    new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
    os.rename(file_path, new_file_path)
    return new_file_path

def edit_audio_file(file_path):
    new_file_path = change_music_file_name(file_path)
    change_music_info(new_file_path)
    remove_album_art(new_file_path)

def change_music_info(file_path):
    try:
        # ID3 タグを新規作成
        audio = ID3(file_path)
        # タイトル情報を設定
        audio['TIT2'] = TIT2(text=["Privacy Protection"])
        # アルバム情報を設定
        audio['TALB'] = TALB(text=["Privacy Protection"])
        # アーティスト情報を設定
        audio['TPE1'] = TPE1(text=["Privacy Protection"])
        # ジャンル情報を設定
        audio['TCON'] = TCON(text=["Privacy Protection"])
        # アルバムアーティスト情報を設定
        audio['TPE2'] = TPE2(text=["Privacy Protection"])
        # 作曲者情報を設定
        audio['TCOM'] = TCOM(text=["Privacy Protection"])
        # コメント情報を設定
        audio['COMM::eng'] = COMM(encoding=3, desc='Privacy Protection', text=["Privacy Protection"])
        # 製作年情報を設定  
        audio['TDRC'] = TDRC(text=["9999"])
        # 保存
        audio.save(file_path)
        return True
    except Exception as e:
        print(f"Error changing music info and artwork for {file_path}: {str(e)}")
        return False

def remove_album_art(file_path):
    try:
        audio = ID3(file_path)
        audio.delall("APIC")
        audio.save()
        return True
    except Exception as e:
        print(f"Error removing album art from {file_path}: {str(e)}")
        return False

# メイン処理
def main(folder_path):
    music_files = find_music_files(folder_path)
    for file_path in music_files:
        if file_path.lower().endswith(('.flac', '.ogg', '.wav')):
            mp3_output_path = os.path.splitext(file_path)[0] + '.mp3'
            convert_to_mp3(file_path, mp3_output_path)
            edit_audio_file(mp3_output_path)
        else : 
            edit_audio_file(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/folder")
        sys.exit(1)
    target_folder = sys.argv[1]
    if not os.path.exists(target_folder):
        print("Folder does not exist.")
        sys.exit(1)

    folder_watcher = FolderWatcher(target_folder)
    folder_watcher.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        folder_watcher.stop()
