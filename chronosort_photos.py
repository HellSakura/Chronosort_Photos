import os
import datetime
import sys
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS
import ctypes

def allocate_console():
    """Dynamically allocates a console window for the GUI app."""
    if sys.platform == "win32":
        try:
            # Check if we are running as a bundled exe
            if hasattr(sys, 'frozen'):
                # Allocate a console for our process
                ctypes.windll.kernel32.AllocConsole()
                
                # Redirect stdout and stderr to the new console
                sys.stdout = open('CONOUT$', 'w')
                sys.stderr = open('CONOUT$', 'w')
        except Exception as e:
            # In case of any error, we just proceed without a console.
            print(f"Could not allocate console: {e}")


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
    Scans a directory and renames image files, printing progress to the console.
    """
    if not os.path.isdir(directory):
        print(f"错误：目录 '{directory}' 不存在或无效。")
        return

    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
    
    files_to_rename = [f for f in os.listdir(directory) if f.lower().endswith(image_extensions)]

    if not files_to_rename:
        print("在该目录中没有找到支持的图片文件。")
        return

    if dry_run:
        print(f"\n在 '{os.path.basename(directory)}' 中找到 {len(files_to_rename)} 个图片文件。预览如下：")
        print("="*50)

    total_renamed = 0
    for filename in files_to_rename:
        if is_already_renamed(filename):
            if dry_run:
                print(f"'{filename}' -> [跳过]")
            continue

        old_filepath = os.path.join(directory, filename)
        
        try:
            date_to_use = None
            source = ""

            exif_date = get_exif_date(old_filepath)
            if exif_date:
                date_to_use = exif_date
                source = "拍摄日期"
            else:
                try:
                    mod_timestamp = os.path.getmtime(old_filepath)
                    date_to_use = datetime.datetime.fromtimestamp(mod_timestamp)
                    source = "修改日期"
                except OSError:
                    creation_timestamp = os.path.getctime(old_filepath)
                    date_to_use = datetime.datetime.fromtimestamp(creation_timestamp)
                    source = "创建日期"

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
                if dry_run:
                    print(f"'{filename}'\n  -> '{new_filename}' (来源: {source})")
                else:
                    os.rename(old_filepath, new_filepath)
                total_renamed += 1
            
        except Exception as e:
            print(f"处理 '{filename}' 时出错: {e}")
    
    if not dry_run:
        print(f"\n操作完成。总共重命名了 {total_renamed} 个文件。")


if __name__ == '__main__':
    # This MUST be one of the first things to run
    allocate_console()

    try:
        if sys.platform == "win32":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    root.withdraw()
    
    print("ChronoSort Photos - 日志窗口")
    print("请勿关闭此窗口，操作信息将在这里显示。")
    print("-" * 50)

    target_directory = filedialog.askdirectory(title="请选择要重命名图片的文件夹")

    if not target_directory:
        print("\n没有选择文件夹，程序退出。")
    else:
        # Preview run
        rename_images_in_directory(target_directory, dry_run=True)
        print("="*50)
        print("预览完成。")
        
        # Confirmation
        confirm = messagebox.askyesno(
            title="确认操作",
            message="预览已在日志窗口中显示。\n\n您要执行真正的重命名吗？"
        )
        
        if confirm:
            print("\n正在执行重命名...")
            rename_images_in_directory(target_directory, dry_run=False)
            messagebox.showinfo("操作完成", "所有文件已成功重命名！\n详情请见日志窗口。")
        else:
            print("\n操作已取消，没有文件被修改。")
            messagebox.showinfo("操作取消", "没有文件被修改。")
    
    print("-" * 50)
    print("所有操作已完成。")
    # Use a messagebox to pause at the end, as input() can be unreliable.
    messagebox.showinfo("ChronoSort Photos", "所有操作已完成。\n日志窗口可以关闭了。")