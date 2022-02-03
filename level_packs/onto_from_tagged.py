from .onto.leavedonto import OntoManager


def onto_from_tagged(in_file, out_file, onto_path, legend):
    om = OntoManager()
    folders = sorted([f for f in onto_path.glob('*') if f.is_dir()])
    for folder in folders:
        om.batch_merge_to_onto(ontos=folder)
    if not om.onto1.ont.legend:
        om.onto1.ont.legend = legend
    om.onto_from_tagged(in_file, out_file)
