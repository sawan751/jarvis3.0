import os
import shutil

def open_file(file_path):
    """
    Opens a file with the default application.
    """
    try:
        abs_path = os.path.abspath(file_path)
        os.startfile(abs_path)
        return f"Opened {file_path}"
    except Exception as e:
        return f"Error opening {file_path}: {str(e)}"

def create_folder(folder_path):
    """
    Creates a new folder.
    """
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Created folder {folder_path}"
    except Exception as e:
        return f"Error creating folder {folder_path}: {str(e)}"

def delete_file(file_path):
    """
    Deletes a file.
    """
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            return f"Deleted file {file_path}"
        else:
            return f"{file_path} is not a file"
    except Exception as e:
        return f"Error deleting {file_path}: {str(e)}"

def delete_folder(folder_path):
    """
    Deletes a folder (and contents).
    """
    try:
        if os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
            return f"Deleted folder {folder_path}"
        else:
            return f"{folder_path} is not a folder"
    except Exception as e:
        return f"Error deleting {folder_path}: {str(e)}"

def modify_file(file_path, new_content):
    """
    Modifies a file by overwriting with new content.
    Note: This is basic; for editing, use more advanced methods.
    """
    try:
        with open(file_path, 'w') as f:
            f.write(new_content)
        return f"Modified {file_path}"
    except Exception as e:
        return f"Error modifying {file_path}: {str(e)}"