# ViNov
Vision Novel Generator

## Instruction
Please copy and rename `vnov/configs/config.yaml` to `vnov/configs/config2.yaml`, and add relevant keys and information to `config2.yaml`.


## Datasets Preparation

In `datasets`, create a folder for the novel, and put the novel text file, `chapters_info.json` and `info.json` in the `datasets/<novel_name>/original` folder.

```
from vnov.data import Novel
novel = Novel("datasets/<novel_name>", main_character="main_character_name")
```

### Folder Structure
```
datasets/<novel_name>
├── original/
│   ├── <novel_name>.txt
│   ├── chapters_info.json
│   └── info.json
├── <sub_dir>/
│   ├── script/
│   ├── refined_script/
│   ├── storyboard/
│   ├── prompts/
│   ├── scene_images/
│   ├── mj_char_images/
│   ├── characters_info.json
│   └── midjourney_char_info.json
```
