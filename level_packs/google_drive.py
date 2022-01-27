from pathlib import Path
import shutil

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def download_drive(path_ids):
    get = RetrieveDriveFiles()

    for sub, id_ in path_ids:
        get.download_folder(sub, id_)


def upload_to_drive(driver_folders):
    to_upload_file = Path("to_upload.txt")
    if not to_upload_file.is_file():
        print('Exiting: there is no "to_upload.txt" file.')
        return

    files_list = to_upload_file.read_text().strip().split("\n")
    files_list = [Path(f) for f in files_list]
    to_upload = []
    for f in files_list:
        idx = int(f.parts[1].split(" ")[0]) - 1
        to_upload.append((driver_folders[idx], f))

    pf = PushDriveFiles()
    pf.push_files(to_upload)
    to_upload_file.unlink()


class RetrieveDriveFiles:
    def __init__(self):
        self.drive = self.__login()

    @staticmethod
    def __login():
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script
        return GoogleDrive(gauth)

    def download_content(self, name, id_):
        c_path = Path(name)
        if c_path.is_dir():
            shutil.rmtree(c_path)
        if not c_path.is_dir():
            c_path.mkdir()

        file_list = self.drive.ListFile(
            {"q": f"'{id_}' in parents and trashed=false"}
        ).GetList()
        for file in file_list:
            if "spreadsheet" in file.attr["metadata"]["mimeType"]:
                file.GetContentFile(
                    f'{name}/{file["title"]}.tsv', mimetype="text/tab-separated-values"
                )
            else:
                file.GetContentFile(
                    f'{name}/{file["title"]}.txt', mimetype="text/plain"
                )

    def download_folder(self, name, id_):
        file_type = {
            "1 to_segment": (".txt", "text/plain"),
            "2 segmented": (".txt", "text/plain"),
            "3 to_tag": (
                ".xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            "4 vocabulary": ("", "text/plain"),
            "5 to_simplify": (
                ".xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            "6 simplified": (
                ".xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            "7 versions": (
                ".docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        }
        c_path = Path(name)
        if c_path.is_dir():
            shutil.rmtree(c_path)
        if not c_path.is_dir():
            c_path.mkdir(parents=True, exist_ok=True)

        file_list = self.drive.ListFile(
            {"q": f"'{id_}' in parents and trashed=false"}
        ).GetList()
        for file in file_list:
            print(f'downloading {file["title"]}')
            file.GetContentFile(
                c_path / (file["title"] + file_type[name.stem][0]),
                mimetype=file_type[name.stem][1],
            )


class PushDriveFiles:
    def __init__(self):
        self.drive = self.__login()

    @staticmethod
    def __login():
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script
        return GoogleDrive(gauth)

    def push_files(self, files_list):
        for folder, file in files_list:
            print(f"uploading {file}")
            title = file.name if file.suffix == ".yaml" else file.stem
            params = {"title": title}

            if file.suffix == ".xlsx":
                params[
                    "mimeType"
                ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file.suffix == ".txt":
                params["mimeType"] = "text/plain"
            elif file.suffix == ".yaml":
                params["mimeType"] = "text/plain"
            elif file.suffix == ".docx":
                params[
                    "mimeType"
                ] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                print(f"{file}\nfile format not supported for upload.")
                continue

            docs_list = self.drive.ListFile(
                {"q": f"'{folder}' in parents and trashed=false"}
            ).GetList()
            for f in docs_list:
                if f["title"] == file.stem:
                    params["id"] = f["id"]

            if "id" not in params:
                params["parents"] = [{"id": folder}]

            drive_file = self.drive.CreateFile(params)
            drive_file.SetContentFile(file)
            convert = False if file.suffix == ".yaml" else True
            drive_file.Upload(param={"convert": convert})
