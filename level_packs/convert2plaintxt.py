from collections import defaultdict

import pypandoc
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import RGBColor


def convert2plaintxt(in_file, out_file):
    # download pandoc if missing
    try:
        pypandoc.get_pandoc_path()
    except OSError:
        print('pandoc is not installed. Installing pandoc...')
        pypandoc.download_pandoc()

    dump = pypandoc.convert_file(str(in_file), 'plain', format='docx')
    txt = parse_md(dump)
    # create new document
    style_content = {
        'name': 'ནང་དོན།',
        'font': 'Jomolhari',
        'rgb': [0xff, 0x99, 0xcc]
    }
    doc = Document()
    for line in txt:
        par = doc.add_paragraph(line)
        par.style.font.name = 'Jomolhari'
    add_content_style(doc, style_content)
    doc.save(out_file)


def add_content_style(doc, new):
    try:
        style = doc.styles.add_style(new['name'], WD_STYLE_TYPE.CHARACTER)
    except ValueError:
        print('\tStyle already exists. Passing...')
        return

    font = style.font
    font.name = new['font']
    r, g, b = new['rgb']
    lavender = RGBColor(r, g, b)
    font.color.rgb = lavender


def parse_md(string):
    parsed_text = []
    chunks = separate_tables(string)
    for n, chunk in enumerate(chunks):
        type_, el = chunk
        if type_ == 'table':
            # table content is cleaned in parse_table()
            txt = parse_table(el)
            parsed_text.extend(txt)
        else:
            txt = []
            for e in el:
                e = e.replace('-', '').replace('[', '').replace(']', '').replace('|', '').replace('/', '').replace('“', '').replace('”', '').strip()
                txt.append(e)
            parsed_text.extend(txt)

    return parsed_text


def parse_table(table):
    def get_sections(table):
        sections = []
        section = []
        for line in table:
            if line.startswith('+'):
                if section:
                    sections.append(section)
                    section = []

                    section.append(line)
                else:
                    section.append(line)
            else:
                section.append(line)
        return sections

    def parse_header(header):
        parts = []
        prev, cur = 0, 0
        for n, s in enumerate(header):
            if s == '+':
                if cur == 0:
                    cur += 1
                    continue
                parts.append((prev + 1, cur))
                prev = cur
            else:
                cur += 1
        return parts

    sections = get_sections(table)
    txt = []
    for section in sections:
        header, body = section[0], section[1:]
        parts = parse_header(header)
        # join column contents
        strings = defaultdict(list)
        for line in body:
            for n, idx in enumerate(parts):
                start, end = idx
                # extract and cleanup part
                part = line[start:end].replace('-', '').replace('[', '').replace(']', '').replace('|', '').replace('/', '').replace('“', '').replace('”', '').strip()
                # add it to strings
                strings[n].append(part)

        # add to txt
        for string in strings.values():
            txt.append(''.join(string))
    return txt


def separate_tables(string):
    chunks = []
    lines = string.split('\n')
    non_table = []
    table = []
    for line in lines:
        if line.startswith('+') or line.startswith('|'):
            # add non-table
            if non_table:
                chunks.append(('non_table', non_table))
                non_table = []

            table.append(line)
        else:
            if table:
                chunks.append(('table', table))
                table = []
            non_table.append(line)
    if non_table:
        chunks.append(('non_table', non_table))
    if table:
        chunks.append(('table', table))
    return chunks
