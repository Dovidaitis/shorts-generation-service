import os
import datetime
import json
from pydantic import BaseModel


OUTPUT_PATH = "assets/output/"
ASSETS_PATH = "assets/"
DOWNLOADS_PATH = "assets/downloads/"
STORAGE_PATH = "assets/storage/"
CACHE_PATH = "assets/cache/"
FULL_EMOJI_FONT_PATH = "/Users/paulius/Library/Fonts/NotoColorEmoji-Regular.ttf"
IOS_EMOJI_PATH = "assets/ios_emoji"


class Path:
    def __init__(self, raw_name="_", lower_video_name="_", output_name="_") -> None:
        self.raw_name = raw_name
        self.main_video_name = f"{raw_name}.mp4"
        self.lower_video_name = f"{lower_video_name}.mp4"
        self.output_name = f"{output_name}.mp4"
        self.main_video_path = self.get_assets_path(self.main_video_name)
        self.lower_video_path = self.get_assets_path(self.lower_video_name)
        self.output_path = f"{self.get_output_path(output_name)}"
        self.subtitle_audio_name = f"{raw_name}.mp3"
        self.subtitle_audio_path = self.get_assets_path(self.subtitle_audio_name)
        self.subtitle_json_path = self.get_cache_path(raw_name + ".json")
        if raw_name != "_":
            print(f"Path created: {json.dumps(self.__dict__, indent=4)}")

    @staticmethod
    def get_timestamp():
        return datetime.datetime.now().strftime("%m%d_%H%M%S")

    @staticmethod
    def get_emoji_font_path():
        if not os.path.exists(FULL_EMOJI_FONT_PATH):
            raise FileNotFoundError(f"Emoji font not found at {FULL_EMOJI_FONT_PATH}")
        return FULL_EMOJI_FONT_PATH

    @staticmethod
    def get_assets_path(file_name):
        os.makedirs(ASSETS_PATH, exist_ok=True)
        return os.path.join(ASSETS_PATH, file_name)

    def get_output_path(self, file_name):
        os.makedirs(OUTPUT_PATH, exist_ok=True)
        return os.path.join(
            OUTPUT_PATH, f"{self.get_timestamp()}_{file_name}.mp4"
        )

    @staticmethod
    def get_cache_path(file_name):
        os.makedirs(CACHE_PATH, exist_ok=True)
        return os.path.join(CACHE_PATH, file_name)

    @staticmethod
    def get_downloads_path(file_name):
        os.makedirs(DOWNLOADS_PATH, exist_ok=True)
        return os.path.join(DOWNLOADS_PATH, file_name)

    
    @staticmethod
    def get_emoji_path_from_unicode(unicode:str):
        return f"{IOS_EMOJI_PATH}/{unicode}.png"

    @staticmethod
    def path_to_unicode(path: str):
        file_name_w_extension = path.split("/")[-1]
        file_name = file_name_w_extension.split(".")[0]
        unicode_str = file_name.split("_")[1]
        unicode_str = unicode_str.split("-")[0]
        return unicode_str
        # print(f"file_name_w_extension: {file_name_w_extension} file_name: {file_name} unicode_str: \t\t*{unicode_str}*")
        



class Loader:
    @staticmethod
    def save_to_json(model: BaseModel, file_path: str) -> None:
        if not os.path.exists(file_path):
            # os.makedirs(os.path.dirname(file_path), exist_ok=True)
            pass
        with open(file_path, "w") as file:
            json.dump(model.dict(), file)

    @staticmethod
    def load_from_json(model_class, file_path: str) -> BaseModel:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
        with open(file_path, "r") as file:
            data = json.load(file)
        return model_class(**data)


class User(BaseModel):
    name: str
    age: int
    is_active: bool


def test_path():
    p = Path()
    print(p.get_timestamp())
    print(p.get_assets_path("test.mp4"))

    user = User(name="John Doe", age=30, is_active=True)
    file_path = "user_data.json"

    l = Loader()
    l.save_to_json(user, file_path)

    # Load the user object from the JSON file
    loaded_user = l.load_from_json(User, file_path)
    print(loaded_user)

if __name__ == "__main__":
    items = os.listdir(IOS_EMOJI_PATH)
    for item in items:
        unicode_name = f"{Path.path_to_unicode(item)}.png"
        length = len(unicode_name.split(".png")[0]) 
        if length > 5 or length < 4:
            print(f"{unicode_name} < {item}")
        os.rename(f"{IOS_EMOJI_PATH}/{item}", f"{IOS_EMOJI_PATH}/{unicode_name}")
