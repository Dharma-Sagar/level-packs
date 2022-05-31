from pathlib import Path

from botok import WordTokenizer, Config
#from spacy.lang.en import English
#from spacy.lang.pt import Portuguese


class Tokenizer:
    def __init__(self, lang="bo"):
        self.set_tok = None
        self.tokenize = None
        self.set_lang(lang)

    def set_lang(self, lang):
        if lang == "bo":
            self.set_tok = set_tok_bo
            self.tokenize = tokenize_bo
        #if lang == "en":
            #self.set_tok = set_tok_en
            #self.tokenize = tokenize_en
        #if lang == "pt":
           # self.set_tok = set_tok_pt
            #self.tokenize = tokenize_en

    def tok_file(self, tok, in_file, out_file):
        dump = in_file.read_text()
        out = self.tokenize(tok, dump)
        out_file.write_text(out)


#def set_tok_en():
    #nlp = English()
    #nlp.add_pipe("sentencizer")
    #return nlp


#def set_tok_pt():
    #nlp = Portuguese()
    #nlp.add_pipe("sentencizer")
    #return nlp


#def tokenize_en(tok, string):
    #sents = []
    #for sent in tok(string).sents:
        #tokens = [str(s).replace(" ", "_") for s in sent]
        #sents.append(" ".join(tokens))
    #return "\n".join(sents)


def set_tok_bo():
    c = Config(dialect_name="general", base_path=Path("../content/tok_data"))
    return WordTokenizer(config=c)


def tokenize_bo(tok, string):
    lemmatization_exceptions = ["བཅས་", "མཁས་"]
    lines = []
    for line in string.split("\n"):
        tokens = tok.tokenize(line)
        words = []
        for t in tokens:
            if t.chunk_type == "TEXT":
                if not t.lemma:
                    text = t.text
                else:
                    if t.pos == "PART":
                        if t.affix:
                            text = "-" + t.text
                        else:
                            text = t.text
                    else:
                        # Hack because of botok limitation:
                        if (
                            t.text_cleaned not in lemmatization_exceptions
                            and t.affixation
                            and "aa" in t.affixation
                            and t.affixation["aa"]
                        ):
                            text = t.lemma
                        else:
                            text = t.text
                text = text.strip().replace("༌", "་")
                if not text.endswith("་"):
                    text += "་"

                if t.pos == "NON_WORD":
                    text += "#"
                words.append(text)

            else:
                t = t.text.replace(" ", "_")
                words.append(t)

        tokenized = " ".join(words)

        # do replacements
        repl_path = (
            Path("../content/tok_data")
            / "general"
            / "adjustments"
            / "rules"
            / "replacements.txt"
        )
        if not repl_path.is_file():
            repl_path.write_text("")
        for Line in repl_path.read_text().split("\n"):
            if "—" in Line:
                orig, repl = Line.split("—")
                tokenized = tokenized.replace(orig, repl)
        lines.append(tokenized)

    return "\n".join(lines)