import yaml

from .onto.leavedonto import OntoManager


def generate_to_tag(in_file, out_file, finalized_ontos, current_ontos, pos, levels, l_colors):
    om = OntoManager()
    folders = sorted([f for f in finalized_ontos.glob('*') if f.is_dir()])
    for folder in folders:
        om.batch_merge_to_onto(ontos=folder)
    om.batch_merge_to_onto(ontos=current_ontos)
    level = in_file.parts[1]
    has_remaining_chunks = om.tag_segmented_chunks(in_file, out_file, fields={'level': level, 'pos': pos, 'levels': levels, 'l_colors': l_colors})
    return has_remaining_chunks
