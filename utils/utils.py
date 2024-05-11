import os
import datetime
import json
from pydantic import BaseModel


PREFIX_OUTPUT_PATH =  "output/"
PREFFIX_ASSETS_PATH = "assets/"
PREFIX_CACHE_PATH = "assets/cache/"
FULL_EMOJI_FONT_PATH = "/Users/paulius/Library/Fonts/NotoColorEmoji-Regular.ttf"


class Path:
    def __init__(self, raw_name = "_", lower_video_name = "_", output_name = "_") -> None:
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
        os.makedirs(PREFFIX_ASSETS_PATH, exist_ok=True)
        return os.path.join(PREFFIX_ASSETS_PATH, file_name)

    def get_output_path(self, file_name):
        os.makedirs(PREFIX_OUTPUT_PATH, exist_ok=True)
        return os.path.join(PREFIX_OUTPUT_PATH, f"{self.get_timestamp()}_{file_name}.mp4")
    
    @staticmethod
    def get_cache_path(file_name):
        os.makedirs(PREFIX_CACHE_PATH, exist_ok=True)
        return os.path.join(PREFIX_CACHE_PATH, file_name)

class Loader:

    @staticmethod
    def save_to_json(model: BaseModel, file_path: str) -> None:
        with open(file_path, 'w') as file:
            json.dump(model.dict(), file)

    @staticmethod
    def load_from_json(model_class, file_path: str) -> BaseModel:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
        with open(file_path, 'r') as file:
            data = json.load(file)
        return model_class(**data)


class User(BaseModel):
    name: str
    age: int
    is_active: bool


if __name__ == "__main__":
    p = Path()
    print(p.get_timestamp())
    print(p.get_assets_path("test.mp4"))

    user = User(name="John Doe", age=30, is_active=True)
    file_path = 'user_data.json'
    
    l = Loader()
    l.save_to_json(user, file_path)
    
    # Load the user object from the JSON file
    loaded_user = l.load_from_json(User, file_path)
    print(loaded_user)
