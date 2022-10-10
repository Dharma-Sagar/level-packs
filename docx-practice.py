import docx

doc = docx.Document('A0.01-vocab.docx')
paragraph = doc.add_paragraph()
out_file = paragraph.style.name
print(out_file)