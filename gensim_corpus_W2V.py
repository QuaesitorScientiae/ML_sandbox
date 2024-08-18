
def remove_chars_from_text(text, chars):
    # return "".join([ch for ch in text if ch not in chars])
    content = ''
    for ch in text:
        if ch not in chars:
            content = content + ''.join(ch)
        else:
            content = content + ''.join(' ')
    return content

def get_text_from_fb2(file_path):
    """Работаем с fb2-файлом"""
    from bs4 import BeautifulSoup  # pip3 install bs4
    import string
    import re
    from tokenizer_exceptions import normalizer_exc_rus
    with open(file_path, "rb") as file:
        data = file.read()
    bs_data = BeautifulSoup(data, "xml")
    paragraphs = bs_data.find_all("p")
    p_temp = []
    stop_title = ['библиография', 'краткая библиография', 'источники', 'литература', 'примечания', 'указатель имен', 'рекомендуемая литература','иллюстрации', 'избранная библиография']
    for p in paragraphs:
        if p.text.lower() in stop_title:
            print(p.text)
            break
        p_temp.append(p)
    content = " ".join([p.text for p in p_temp])
    print(len(content))
    content = normalizer_exc_rus(content).lower()
    print(len(content))
    spec_chars = string.punctuation + '\xa0«»\t—…'
    content = re.sub('\n', ' ', content)
    content = re.sub('\r', ' ', content)
    content = remove_chars_from_text(content, spec_chars)
    content = remove_chars_from_text(content, string.digits)
    content = " ".join(content.split())
    print(content[:200])
    return content

def make_text_from_txt(file_path):
    from charset_normalizer import from_path
    import string
    """Работаем с txt-файлом"""
    spec_chars = string.punctuation + '\r' + '\n\xa0«»\t—…'
    content = str(from_path(file_path).best()).lower()
    content = remove_chars_from_text(content, spec_chars)
    content = remove_chars_from_text(content, string.digits)
    return content

def make_text_from_pdf(file_path):
    from pdfminer.pdfinterp import PDFResourceManager, process_pdf
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from io import StringIO
    from io import open
    import string
    import re
    with open(file_path, "rb") as pdfFile:
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        process_pdf(rsrcmgr, device, pdfFile)
        device.close()
        content = retstr.getvalue()
        retstr.close()
    spec_chars = string.punctuation + '\xa0«»\t—…'
    content.lower()
    content = re.sub('\n', ' ', content)
    content = re.sub('\r', ' ', content)
    content = remove_chars_from_text(content, spec_chars)
    content = remove_chars_from_text(content, string.digits)
    content = " ".join(content.split())
    return content

def text_generator_bigram(tokens):

    '''Этот код на большом корпусе будет выполняться довольно долго, но зато в результате получится словарь биграмм, который можно использовать, применяя
к потоку текстов bigram_transformer. Вот так можно построить генератор для текстов с биграммами:'''
    bigram_transformer = []
    for text in tokens:
        yield bigram_transformer[ [ word for word in text ] ]

def text_generator_trigram(tokens):
    bigram_transformer = text_generator_bigram(tokens)
    trigram_transformer = []
    for text in tokens:
        return trigram_transformer[ bigram_transformer [ [ word for word in text ] ] ]

def main():
    import os
    from gensim.models.phrases import Phrases, Phraser

    corpus = []
    #get current directory, you may also provide an absolute path
    path = os.getcwd() + '/Corpus/'
    #walk recursivly through all folders and gather information
    for root, dirs, files in os.walk(path):
        #check if file is of correct type
        check_fb2 = [f for f in files if f.find(".fb2") != -1]
        if check_fb2 != []:
            print(root, check_fb2)
            corpus = [get_text_from_fb2(root+'/'+file_path) for file_path in check_fb2]
        check_txt = [f for f in files if f.find(".txt") != -1]
        if check_txt != []:
            print(root, check_txt)
            [corpus.append(make_text_from_txt(root+'/'+file_path)) for file_path in check_txt]
        check_pdf = [f for f in files if f.find(".pdf") != -1]
        if check_pdf != []:
            print(root, check_pdf)
            print(root+'/' + check_pdf[0])
            [corpus.append(make_text_from_pdf(root+'/'+file_path)) for file_path in check_pdf]
    # print(len(corpus))
    # print(corpus[2][-500:])
    tokens = [doc.split(" ") for doc in corpus]
    # print(len(tokens[1]))
    bigram = Phrases(tokens)
    # print(bigram.scoring)
    bigram_transformer = Phraser(bigram)
    # print(bigram_transformer)
    tokens_ = []
    for sent in tokens:
        # print(sent[:600])
        # print(len(sent))
        tokens_.append(bigram_transformer[sent])
    # print(tokens_)
    # print(len(tokens_[1]))
    # print(bigram)
    # print(bigram_transformer)
    trigram = Phrases(tokens_)
    trigram_transformer = Phraser(trigram)
    tokens_trigram = []
    for sent in tokens_:
        tokens_trigram.append(trigram_transformer[sent])
        # print(tokens_trigram[:100])
    print(trigram)
    print(trigram_transformer)
    # trigram_sort = sorted(trigram.vocab.items(), key=lambda x: x[1], reverse=True)
    # print([iter[0] for iter in trigram_sort])
    from gensim.models.word2vec import Word2Vec
    model = Word2Vec( vector_size=200, window=14, min_count=5, workers=10)

    model.build_vocab(tokens_trigram)
    # for index, word in enumerate(model.wv.index_to_key):
    #     if index == 500:
    #         break
    #     print(f"word #{index}/{len(model.wv.index_to_key)} is {word}")
    #     if index in range(200, 500):
    #         print(model.wv.most_similar(word))
    print(sorted(model.wv.key_to_index.items(), key=lambda x: x[1], reverse=True)[:300])
    print(len(model.wv.key_to_index))

            # model.load('new_model')
    model.train(tokens_trigram, epochs=500,
                total_examples=model.corpus_count,
                start_alpha=(model.min_alpha + (53/200 * (model.alpha - model.min_alpha))))

    print(sorted(model.wv.key_to_index.items(), key=lambda x: x[1], reverse=True)[:300])
    print(len(model.wv.key_to_index))

    for index, word in enumerate(model.wv.index_to_key):
        if index == 500:
            break
        print(f"word #{index}/{len(model.wv.index_to_key)} is {word}")
        if index in range(200, 500):
            print(model.wv.most_similar(word))


    model.save('fb2_rus_model')

if __name__ == '__main__':
    main()