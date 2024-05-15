# 🎥 Convert YouTube videos (links) into multiple shorts with subtitles and emojis 🎉

![example.gif](readme_assets/example.gif)

## Setup

- Install `poetry`
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

- Install packages with `poetry install`
- Enable venv with `poetry shell`
- Run `poetry run python setup.py` 

## Usage

### Download youtube video with `yt/main` package
- will be saved at `assets/downloads`
```python
    vm = VideoManger()
    print(vm.download_video("https://www.youtube.com/watch?v=KDiEIqD4MJ8"))
```

### Create shorts with `editor/main` package
- output assets will be saved at `assets/output`
`raw_name`: the name of the video in `assets/downloads`
`lower_video_name`: the name of the video in `assets`
`ouput_name`: the name of the video that will be produced

```python
  path = Path(
    raw_name="Joe_Rogan_Is_Steven_Seagal_Legit_",
    lower_video_name="parkour_big",
    output_name="joe_seagal",
  )
  build(resize_video=True, path=path)
```
