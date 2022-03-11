import yaml
from pathlib import Path

from .create_pack import create_pack
from .vocab_report import gen_vocab_report


def create_packs():
    mode, lang, content, driver_folders, level_colors, pos, levels, legend, line_mode = read_config()
    content = Path(content)
    create_pack(
        content,
        driver_folders,
        lang,
        mode=mode,
        l_colors=level_colors,
        pos=pos,
        levels=levels,
        legend=legend,
        line_mode=line_mode
    )


def read_config():
    default = """# "local", "drive" or "upload"
mode: local
# "bo" and "en" are currently supported 
lang: bo
# the relative path to the folder containing the 5 folders of the data
input: content
# lines are either sentences ("sentence") or chunks of syllables ("chunk")
line_mode: sentence
# Google Drive folder ids.
# add the ids right after each "- ". keep the order from 1 to 5 from the drive folders
# to find the id, open the folder, take everything following the last "/" in the url
drive_folders: 
- 
- 
- 
- 
- """
    in_file = Path("config.yaml")
    if not in_file.is_file():
        print("No config file, creating it.\n" 'Please review "config.yaml"\n')
        in_file.write_text(default)

    struct = yaml.safe_load(in_file.read_text())
    return (
        struct["mode"],
        struct["lang"],
        struct["input"],
        struct["drive_folders"],
        struct["level_colors"],
        struct["pos"],
        struct["levels"],
        struct["legend_template"],
        struct["line_mode"],
    )


__all__ = {create_packs}
