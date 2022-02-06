from .onto.leavedonto import OntoManager


def merge_ontos(ontos_path, out_file):
    if out_file.is_file():
        om = OntoManager(out_file)
    else:
        om = OntoManager()
        om.onto1.ont_path = out_file

    om.batch_merge_to_onto(ontos_path)
    om.onto1.convert2yaml()
