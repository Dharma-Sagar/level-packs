from pathlib import Path

import yaml

from .corpus_segment import Tokenizer
from .google_drive import upload_to_drive, download_drive
from .generate_to_tag import generate_to_tag
from .convert2plaintxt import convert2plaintxt
from .extract_level_content import extract_content
from .onto_from_tagged import onto_from_tagged


def create_pack(
    content_path,
    drive_ids,
    lang,
    mode="local",
    subs=None,
    l_colors=None,
    pos=None,
    levels=None,
    legend=None
):
    if not subs:
        subs = [
            "1 docx-raw",
            "2 docx-text-only",
            "3 to-segment",
            "4 segmented",
            "5 to-tag",
            "6 vocabulary",
        ]

    path_ids = [(content_path / subs[i], drive_ids[content_path.stem][i]) for i in range(len(drive_ids[content_path.stem]))]
    path_ontos = (content_path.parent / 'ontos', drive_ids['ontos'])
    abort = prepare_folders(content_path, subs)  # prepare the folder structure
    if abort and mode == "local":
        print(
            'Exiting: "content" folder did not exist. Please add some files to segment and rerun.'
        )
        return

    if mode == "local":
        create_pack_local(path_ids, lang=lang, l_colors=l_colors, pos=pos, levels=levels, legend=legend, ontos=path_ontos)
    elif mode == "drive":
        create_pack_local(path_ids, lang=lang, l_colors=l_colors, pos=pos, levels=levels, legend=legend, ontos=path_ontos)
        upload_to_drive(drive_ids)
    elif mode == "download":
        download_drive(path_ids)
    elif mode == "upload":
        upload_to_drive(drive_ids)
    else:
        raise ValueError('either one of "local", "drive", "download" and "upload".')


def create_pack_local(path_ids, lang="bo", l_colors=None, pos=None, levels=None, legend=None, ontos=None):
    state, resources = current_state(path_ids)
    new_files = []
    T = Tokenizer(lang=lang)
    tok = None
    has_totag_unfinished = False

    for file, steps in state.items():
        print(file)
        cur = 1
        while cur <= 7 and cur in steps and steps[cur]:
            cur += 1

        # 1. convert raw .docx files to text only containing raw text
        if cur == 2:
            print("\tconverting to simple text...")
            in_file = steps[cur-1]
            out_file = path_ids[cur-1][0] / (in_file.stem + '_textonly.docx')
            convert2plaintxt(in_file, out_file)
            new_files.append(out_file)

        # 2. mark all text to be extracted using a given style
            print('\t--> Please apply the style to all text to be extracted.')

        # 3. extract all marked text
        out_file = None
        if cur == 3:
            print("\textracting all text and segmenting it")
            in_file = steps[cur-1]
            out_file = path_ids[cur-1][0] / (in_file.stem.split('_')[0] + '_tosegment.txt')
            extract_content(in_file, out_file)
            new_files.append(out_file)
            cur += 1  # incrementing so that segmentation happens right after

        if cur == 4:
            print("\tsegmenting...")
            in_file = steps[cur-1] if steps[cur-1] else out_file
            out_file = path_ids[cur - 1][0] / (in_file.stem.split('_')[0] + "_segmented.txt")
            if not tok:
                tok = T.set_tok()
            T.tok_file(tok, in_file, out_file)
            new_files.append(out_file)

        # 6. manually correct the segmentation
            print("\t--> Please manually correct the segmentation.")

        # 7. create the _totag.xlsx in to_tag from the segmented .txt file from segmented
        if cur == 5:
            if not has_totag_unfinished:
                print("\ncreating the file to tag...")
                in_file = steps[cur - 1]
                out_file = path_ids[cur - 1][0] / (
                    in_file.stem.split("_")[0] + "_totag.xlsx"
                )
                tmp_onto = out_file.parent.parent / '6 vocabulary' / (out_file.stem.split('_')[0] + '_partial.yaml')

                # generate partial ontos from the tagged chunks
                if out_file.is_file():
                    onto_from_tagged(out_file, tmp_onto, ontos[0], legend)

                # create totag
                finalized_ontos = ontos[0]
                current_ontos = path_ids[5][0]
                has_totag_unfinished = generate_to_tag(in_file, out_file, finalized_ontos, current_ontos, pos, levels, l_colors)

                new_files.append(out_file)
            # 8. manually POS tag the segmented text
                print(
                    "\t--> Please manually tag new words with their POS tag and level. (words not tagged will be ignored)"
                )

        # 9. create .yaml ontology files from tagged .xlsx files from to_tag
        if cur == 6:
            print("\t creating the onto from the tagged file...")
            in_file = steps[cur - 1]
            out_file = path_ids[cur - 1][0] / (
                in_file.stem.split("_")[0] + "_onto.yaml"
            )
            if not out_file.is_file():
                onto_from_tagged(in_file, out_file, ontos[0], legend)
                new_files.append(out_file)

            # removing temporary partial ontos
            tmp_onto = out_file.parent / (out_file.stem.split('_')[0] + '_partial.yaml')
            if tmp_onto.is_file():
                tmp_onto.unlink()

            # 6. manually fill in the onto
            print(
                '\t--> Please integrate new words in the onto from "to_organize" sections and add synonyms.'
            )

        # 10. merge into the level onto
        # TODO: add this st ep as 7 in state{}
        if cur == 7:
            print("\tmerging produced ontos into the level onto...")
            in_file = ''
            out_files = ''  # merge_ontos(in_file, out_file)
            new_files.append(out_files)

    write_to_upload(new_files)


def current_state(paths_ids):
    file_type = {
        "1 docx-raw": ".docx",
        "2 docx-text-only": ".docx",
        "3 to-segment": ".txt",
        "4 segmented": ".txt",
        "5 to-tag": ".xlsx",
        "6 vocabulary": ".yaml",
    }

    state = {}
    resources = {}
    for path, _ in paths_ids:
        for f in path.glob("*"):
            if f.suffix != file_type[path.stem]:
                continue
            # test chunks are all processed
            if path.stem.startswith('5'):
                chunks_conf = f.parent / (f.stem.split('_')[0] + '.config')
                if chunks_conf.is_file():
                    config = yaml.safe_load(chunks_conf.read_text())
                    if 'todo' in config.values():
                        continue

            # ignore the partial ontos
            if path.stem.startswith('6'):
                if f.stem.endswith('partial'):
                    continue

            # add file to state
            stem = f.stem.split("_")[0]
            if stem not in state:
                state[stem] = {i: None for i in range(1, len(paths_ids) + 1)}
            step = int(f.parts[-2][0])
            state[stem][step] = f

            # add onto files to resources

    return state, resources


def write_to_upload(files):
    file = Path("to_upload.txt")
    if not file.is_file():
        file.write_text("")

    content = file.read_text().strip().split("\n")
    files = [str(f) for f in files]
    for f in files:
        if f not in content:
            content.append(f)

    file.write_text("\n".join(content))


def prepare_folders(content_path, sub_folders):
    missing = False
    if not content_path.is_dir():
        missing = True
        print(f'folder "{content_path}" does not exist. Creating it...')
        content_path.mkdir()
    for sub in sub_folders:
        if not (content_path / sub).is_dir():
            print(f'folder "{(content_path / sub)}" does not exist. Creating it...')
            (content_path / sub).mkdir()
    return missing
