from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, TCON, TDRC, TCOM,TPE2
import os
import warnings
import re
import sys
import shutil
from pydub import AudioSegment

# 指定したフォーマットの音楽ファイルを検出
def find_music_files(folder_path):
    music_extensions = ['.mp3', '.flac', '.ogg', '.wav']
    music_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in music_extensions):
                music_files.append(os.path.join(root, file))
    return music_files

# 楽曲情報とアルバムアートを変更
def change_music_info_and_artwork(file_path):
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
        # 製作年情報を設定  
        audio['TDRC'] = TDRC(text=["9999"])
        audio.save(file_path)
        return True
    except Exception as e:
        print(f"Error changing music info and artwork for {file_path}: {str(e)}")
        return False

# 音楽ファイルを変換
def convert_to_mp3(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format='mp3', bitrate='320k')

# アルバムアートを削除
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
        # ファイル名から "XX. "（Xは0から9の数字）を削除
        new_file_name = re.sub(r"^\d+\.\s+", "", os.path.basename(file_path))
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        # 楽曲情報を変更
        if change_music_info_and_artwork(file_path):
            print(f"Changed music info and artwork for {file_path}")
        # アルバムアート削除
        if remove_album_art(file_path):
            print(f"Removed album art from {file_path}")
        # flac/ogg/wavファイルをmp3に変換
        if file_path.lower().endswith(('.flac', '.ogg', '.wav')):
            mp3_output_path = os.path.splitext(new_file_path)[0] + '.mp3'
            convert_to_mp3(file_path, mp3_output_path)
            print(f"Converted {file_path} to {mp3_output_path}")
        else : 
            os.rename(file_path, new_file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/folder")
        sys.exit(1)
    target_folder = sys.argv[1]
    if not os.path.exists(target_folder):
        print("Folder does not exist.")
        sys.exit(1)
    main(target_folder)
