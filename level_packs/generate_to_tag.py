import yaml

from .onto.leavedonto import OntoManager


def generate_to_tag(in_file, out_file, finalized_ontos, current_ontos, pos, levels, line_mode, l_colors):
    om = OntoManager()
    folders = sorted([f for f in finalized_ontos.glob('*') if f.is_dir() and f.parts[-1] != current_ontos.parts[-1]])
    # if a level onto is created, use it instead
    level_ontos = []
    for n, f in enumerate(folders):
        l_onto = f.parent / (f.stem + '_onto.yaml')
        if l_onto.is_file():
            folders[n] = None  # remove onto path without shortening list
            level_ontos.append(l_onto)

    # merge finalized ontos
    for folder in folders:
        if folder:
            om.batch_merge_to_onto(ontos=folder)
    for onto in level_ontos:
        om.merge_to_onto(onto)

    # merge current ontos
    om.batch_merge_to_onto(ontos=current_ontos)

    level = in_file.parts[1]
    has_remaining_chunks = om.tag_segmented_chunks(in_file, out_file, line_mode, fields={'level': level, 'pos': pos, 'levels': levels, 'l_colors': l_colors})
    return has_remaining_chunks
