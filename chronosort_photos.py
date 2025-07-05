import os
import datetime
import sys
import re
import tkinter as tk
from tkinter import filedialog
from PIL import Image
from PIL.ExifTags import TAGS
import ctypes

def get_exif_date(filepath):
    """Tries to get the original 'Date Taken' from image EXIF data."""
    try:
        with Image.open(filepath) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'DateTimeOriginal':
                        return datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        return None
    return None

def is_already_renamed(filename):
    """Checks if a filename already matches the target format."""
    pattern = r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(_\d+)?\..+$'
    return re.match(pattern, filename) is not None

def rename_images_in_directory(directory, dry_run=True):
    """
    Renames images, skipping files that already match the target format.
    Uses a three-tier fallback for date source:
    1. EXIF 'Date Taken'
    2. File 'Date Modified'
    3. File 'Date Created'
    """
    if not os.path.isdir(directory):
        print(f"错误：目录 '{directory}' 不存在或无效。")
        return

    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    
    print(f"\n正在扫描目录: {directory}")
    if dry_run:
        print("--- 预览模式 --- (不会修改任何文件)")
    else:
        print("--- 执行模式 --- (将重命名文件)")

    for filename in os.listdir(directory):
        if filename.lower().endswith(image_extensions):
            
            if is_already_renamed(filename):
                print(f"'{filename}' -> [跳过] (已是目标格式)")
                continue

            old_filepath = os.path.join(directory, filename)
            
            try:
                date_to_use = None
                source = ""

                exif_date = get_exif_date(old_filepath)
                if exif_date:
                    date_to_use = exif_date
                    source = "拍摄日期 (EXIF)"
                else:
                    try:
                        mod_timestamp = os.path.getmtime(old_filepath)
                        date_to_use = datetime.datetime.fromtimestamp(mod_timestamp)
                        source = "文件修改日期"
                    except OSError:
                        creation_timestamp = os.path.getctime(old_filepath)
                        date_to_use = datetime.datetime.fromtimestamp(creation_timestamp)
                        source = "文件创建日期"

                new_filename_base = date_to_use.strftime('%Y-%m-%d_%H-%M-%S')
                file_extension = os.path.splitext(filename)[1]
                
                new_filename = f"{new_filename_base}{file_extension}"
                new_filepath = os.path.join(directory, new_filename)
                
                counter = 1
                while os.path.exists(new_filepath):
                    new_filename = f"{new_filename_base}_{counter}{file_extension}"
                    new_filepath = os.path.join(directory, new_filename)
                    counter += 1

                if old_filepath != new_filepath:
                    print(f"'{filename}' -> '{new_filename}' (来源: {source})")
                    if not dry_run:
                        os.rename(old_filepath, new_filepath)
                
            except Exception as e:
                print(f"处理 '{filename}' 时出错: {e}")

if __name__ == '__main__':
    # --- 主程序 ---
    
    # 解决高分屏下tkinter对话框模糊的问题 (仅限Windows)
    try:
        if sys.platform == "win32":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass # 在非Windows或旧版Windows上可能会失败，但程序仍可继续

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    print("请在弹出的对话框中选择一个图片文件夹...")
    
    # 打开文件夹选择对话框
    target_directory = filedialog.askdirectory(title="请选择要重命名图片的文件夹")

    if not target_directory:
        print("没有选择文件夹，程序退出。")
    else:
        # 第一次运行：预览模式
        rename_images_in_directory(target_directory, dry_run=True)
        
        # 询问用户是否执行
        print("\n" + "="*50)
        print("预览完成。请检查上面的列表。")
        confirm = input("要执行真正的重命名吗？请输入 'yes' 确认: ")
        
        if confirm.lower() == 'yes':
            # 第二次运行：执行模式
            rename_images_in_directory(target_directory, dry_run=False)
            print("\n重命名操作已完成！")
        else:
            print("\n操作已取消。")
