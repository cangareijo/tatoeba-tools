# pip install janome jieba konlpy
# aspell -d en dump master | aspell -l en expand > eng.txt

from janome.tokenizer import Tokenizer
from jieba import cut
from konlpy.tag import Kkma
from os import makedirs, scandir
from os.path import getsize
from random import choice, randint, sample, shuffle
from re import findall, I, search, sub
from regex import findall as find
from unicodedata import normalize

def cleanupforhashing(text):
  text = normalize("NFKC", text)
  text = sub(r"\W", "", text)
  text = cleanupforsorting(text)
  return text

def cleanupforsorting(word):
  word = word.lower()
  word = sub(r"[àáâãäāåă]", "a", word)
  word = sub(r"[æ]", "ae", word)
  word = sub(r"[çćĉčℂ]", "c", word)
  word = sub(r"[đḍď]", "d", word)
  word = sub(r"[èéêẽëēěė]", "e", word)
  word = sub(r"[ﬁ]", "fi", word)
  word = sub(r"[ﬂ]", "fl", word)
  word = sub(r"[ĝ]", "g", word)
  word = sub(r"[ḥĥ]", "h", word)
  word = sub(r"[ìíîĩïī]", "i", word)
  word = sub(r"[ĵ]", "j", word)
  word = sub(r"[łľĺ]", "l", word)
  word = sub(r"[ñńň]", "n", word)
  word = sub(r"[òóôõöōø]", "o", word)
  word = sub(r"[œ]", "oe", word)
  word = sub(r"[ℚ]", "q", word)
  word = sub(r"[řṛŕℝ]", "r", word)
  word = sub(r"[ŝšşșṣ]", "s", word)
  word = sub(r"[ß]", "ss", word)
  word = sub(r"[ţṭť]", "t", word)
  word = sub(r"[ùúûũüūŭ]", "u", word)
  word = sub(r"[𝑥]", "x", word)
  word = sub(r"[ý]", "y", word)
  word = sub(r"[žż]", "z", word)
  return word

def gettokens(text):
  return findall(
    r"""[^\s\u200B\u200E\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*·•●▲➔][^\s\u200B\uFEFF—―…]*"""
    r"""[^\s\u200B\u200E\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*·•●▲➔]|"""
    r"""[^\s\u200B\u200E\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*·•●▲➔]|"""
    r"""[\s\u200B\u200E\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*·•●▲➔]+""",
    text)

def gettokensinlanguage(janome, kkma, language, text):
  words = set()
  if language in ("cmn", "lzh", "wuu", "yue"):
    for token in cut(text):
      words.update(gettokens(token))
  elif language == "jpn":
    for token in janome.tokenize(text):
      words.update(gettokens(token))
  elif language == "kor":
    for token in kkma.morphs(text):
      words.update(gettokens(token))
  else:
    words.update(gettokens(text))
  return words

def partitionsentences():
  print("Partitioning sentences...")
  write = {}
  makedirs("temporary/sentences", exist_ok = True)
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] != "\\N":
      makedirs("temporary/sentences/" + fields[1], exist_ok = True)
      if fields[1] not in write:
        write[fields[1]] = {}
      if fields[3] not in write[fields[1]]:
        write[fields[1]][fields[3]] = open("temporary/sentences/" + fields[1] + "/" + fields[3], "w", encoding = "utf-8")
      print(line, end = "", file = write[fields[1]][fields[3]])
  read.close()
  for language in write:
    for user in write[language]:
      write[language][user].close()

def partitionlinks():
  print("Partitioning links...")
  print("Reading languages...")
  languages = {}
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    languages[int(fields[0])] = fields[1]
  read.close()

  print("Writing links...")
  write = {}
  makedirs("temporary/links", exist_ok = True)
  read = open("links.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if int(fields[0]) in languages and languages[int(fields[0])] != "\\N" and int(fields[1]) in languages and languages[int(fields[1])] != "\\N":
      makedirs("temporary/links/" + languages[int(fields[0])], exist_ok = True)
      if languages[int(fields[0])] not in write:
        write[languages[int(fields[0])]] = {}
      if languages[int(fields[1])] not in write[languages[int(fields[0])]]:
        write[languages[int(fields[0])]][languages[int(fields[1])]] = open("temporary/links/" + languages[int(fields[0])] + "/" + languages[int(fields[1])], "w", encoding = "utf-8")
      print(fields[0], fields[1], sep = "\t", file = write[languages[int(fields[0])]][languages[int(fields[1])]])
  read.close()
  for language in write:
    for tongue in write[language]:
      write[language][tongue].close()

def listlanguages():
  print("Listing languages...")
  frequencies = {}
  sentences = {}

  print("Reading languages...")
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] not in frequencies:
      frequencies[fields[1]] = {}
      sentences[fields[1]] = {}
    if fields[3] not in frequencies[fields[1]]:
      frequencies[fields[1]][fields[3]] = 0
      sentences[fields[1]][fields[3]] = line
    frequencies[fields[1]][fields[3]] += 1
    if randint(1, frequencies[fields[1]][fields[3]]) == 1:
      sentences[fields[1]][fields[3]] = line
  read.close()

  for language in frequencies:
    frequencies[language] = sum(frequencies[language][user] for user in frequencies[language])
    sentences[language] = choice([sentences[language][user] for user in sentences[language]])

  languages = list(frequencies)
  shuffle(languages)
  languages.sort(key = lambda language: frequencies[language], reverse = True)

  print("Writing languages...")
  write = open("languages.txt", "w", encoding = "utf-8")
  for language in languages:
    print(language, frequencies[language], sentences[language], sep = "\t", end = "", file = write)
  write.close()

def listusers():
  print("Listing users...")
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  for entry in scandir("temporary/sentences"):
    if entry.is_dir():
      print("Reading users (" + entry.name + ")...")
      frequencies = {}
      distinct = {}
      sentences = {}
      for subentry in scandir("temporary/sentences/" + entry.name):
        frequencies[subentry.name] = 0
        distinct[subentry.name] = set()
        read = open("temporary/sentences/" + entry.name + "/" + subentry.name, "r", encoding = "utf-8")
        for line in read:
          fields = findall(r"[^\t\n]+", line)
          frequencies[subentry.name] += 1
          distinct[subentry.name].update(gettokensinlanguage(janome, kkma, entry.name, fields[2]))
          if randint(1, frequencies[subentry.name]) == 1:
            sentences[subentry.name] = line
        read.close()
        distinct[subentry.name] = len(distinct[subentry.name])
      users = list(frequencies)
      shuffle(users)
      users.sort(key = lambda user: frequencies[user], reverse = True)
      print("Writing users (" + entry.name + ")...")
      write = open("users/users-" + entry.name + ".txt", "w", encoding = "utf-8")
      for user in users:
        print(user, frequencies[user], distinct[user], sentences[user], sep = "\t", end = "", file = write)
      write.close()

def listcharacters():
  makedirs("characters", exist_ok = True)
  for entry in scandir("temporary/sentences"):
    if entry.is_dir():
      print("Listing characters (" + entry.name + ")...")
      frequencies = {}
      sentences = {}

      for subentry in scandir("temporary/sentences/" + entry.name):
        file = open("temporary/sentences/" + entry.name + "/" + subentry.name, "r", encoding = "utf-8")
        for line in file:
          fields = findall(r"[^\t\n]+", line)
          for character in set(fields[2]):
            if character not in frequencies:
              frequencies[character] = {}
              sentences[character] = {}
            if fields[3] not in frequencies[character]:
              frequencies[character][fields[3]] = 0
            frequencies[character][fields[3]] += 1
            if randint(1, frequencies[character][fields[3]]) == 1:
              sentences[character][fields[3]] = line
        file.close()

      characters = list(frequencies)
      characters.sort()
      for character in characters:
        frequencies[character] = sum(frequencies[character][user] for user in frequencies[character])
        sentences[character] = choice([sentences[character][user] for user in sentences[character]])

      write = open("characters/characters-" + entry.name + ".txt", "w", encoding = "utf-8")
      for character in characters:
        print(hex(ord(character)), character, frequencies[character], sentences[character], sep = "\t", end = "", file = write)
      write.close()

def listwords():
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  makedirs("words", exist_ok = True)
  for entry in scandir("temporary/sentences"):
    if entry.is_dir():
      print("Listing words (" + entry.name + ")...")
      frequencies = {}
      sentences = {}
      for subentry in scandir("temporary/sentences/" + entry.name):
        file = open("temporary/sentences/" + entry.name + "/" + subentry.name, "r", encoding = "utf-8")
        for line in file:
          fields = findall(r"[^\t\n]+", line)
          sentence = gettokensinlanguage(janome, kkma, entry.name, fields[2])
          for word in sentence:
            if word not in frequencies:
              frequencies[word] = {}
              sentences[word] = {}
            if fields[3] not in frequencies[word]:
              frequencies[word][fields[3]] = 0
            frequencies[word][fields[3]] += 1
            if randint(1, frequencies[word][fields[3]]) == 1:
              sentences[word][fields[3]] = line
        file.close()

      words = list(frequencies)
      words.sort()
      words.sort(key = lambda word: cleanupforsorting(word))
      for word in words:
        frequencies[word] = sum(frequencies[word][user] for user in frequencies[word])
        sentences[word] = choice([sentences[word][user] for user in sentences[word]])

      file = open("words/words-" + entry.name + ".txt", "w", encoding = "utf-8")
      for word in words:
        print(word, frequencies[word], sentences[word], sep = "\t", end = "", file = file)
      file.close()

def counttranslations():
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  for entry in scandir("temporary/links"):
    if entry.is_dir():
      print("Counting translations (" + entry.name + ")...")
      sentencewords = {}
      for subentry in scandir("temporary/sentences/" + entry.name):
        file = open("temporary/sentences/" + entry.name + "/" + subentry.name, "r", encoding = "utf-8")
        for line in file:
          fields = findall(r"[^\t\n]+", line)
          sentencewords[int(fields[0])] = gettokensinlanguage(janome, kkma, entry.name, fields[2])
        file.close()

      makedirs("translations/" + entry.name, exist_ok = True)
      for subentry in scandir("temporary/links/" + entry.name):
        if subentry.name != entry.name:
          translations = {}
          file = open("temporary/links/" + entry.name + "/" + subentry.name, "r", encoding = "utf-8")
          for line in file:
            fields = findall(r"[^\t\n]+", line)
            if int(fields[0]) in sentencewords:
              for word in sentencewords[int(fields[0])]:
                if word not in translations:
                  translations[word] = 0
                translations[word] += 1
          file.close()

          words = list(translations)
          words.sort()
          words.sort(key = lambda word: cleanupforsorting(word))

          write = open("translations/" + entry.name + "/translations-" + entry.name + "-" + subentry.name + ".txt", "w", encoding = "utf-8")
          for word in words:
            print(word, translations[word], sep = "\t", file = write)
          write.close()

def selectsentences():
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  makedirs("sentences", exist_ok = True)
  for entry in scandir("temporary/sentences"):
    if entry.is_dir():
      print("Selecting sentences (" + entry.name + ")...")
      sentences = {}

      for subentry in scandir("temporary/sentences/" + entry.name):
        file = open("temporary/sentences/" + entry.name + "/" + subentry.name, "r", encoding = "utf-8")
        for line in file:
          fields = findall(r"[^\t\n]+", line)
          sentence = gettokensinlanguage(janome, kkma, entry.name, fields[2])
          for token in sentence:
            if token not in sentences:
              sentences[token] = {}
            if fields[3] not in sentences[token]:
              sentences[token][fields[3]] = []
            sentences[token][fields[3]].append(line)
        file.close()

      for token in sentences:
        sentences[token] = [choice(sentences[token][user]) for user in sentences[token]]
        sentences[token] = sample(sentences[token], min(5, len(sentences[token])))
      sentences = [(token, sentence) for token in sentences for sentence in sentences[token]]
      shuffle(sentences)

      file = open("sentences/sentences-" + entry.name + ".txt", "w", encoding = "utf-8")
      for word, sentence in sentences:
        print(word, sentence, sep = "\t", end = "", file = file)

def breaksrulesofidenticalwrappingmarks(name, mark, text):
  messages = []
  if findall(r"""\w""" + mark + r"""\w""", text):
    messages.append(name + ": preceeded and succeeded by letter or digit")
  if findall(r"""(\s|^)""" + mark + r"""(\s|$)""", text):
    messages.append(name + ": preceeded and succeeded by space")
  if findall(r"""^([^""" + mark + r"""]*""" + mark + r"""[^""" + mark + r"""]*""" + mark + r""")*[^""" + mark + r"""]*""" + mark + r"""[^""" + mark + r"""]*$""", text):
    messages.append(name + ": odd number")
  return messages

def breaksrulesofsymmetricwrappingmarks(name, opening, closing, text):
  messages = []
  if findall(r"""\w""" + opening, text):
    messages.append(name + ": opening mark preceeded by letter or digit")
  if findall(opening + r"""\s""", text):
    messages.append(name + ": opening mark succeeded by space")
  if findall(r"""\s""" + closing, text):
    messages.append(name + ": closing mark preceeded by space")
  if findall(closing + r"""\w""", text):
    messages.append(name + ": closing mark succeeded by letter or digit")
  if findall(opening + r"""[^""" + opening + closing + r"""]*$""", text):
    messages.append(name + ": unclosed opening mark")
  if findall(r"""^[^""" + opening + closing + r"""]*""" + closing, text):
    messages.append(name + ": unopened closing mark")
  if findall(opening + r"""[^""" + opening + closing + r"""]*""" + opening, text):
    messages.append(name + ": unbalanced opening marks")
  if findall(closing + r"""[^""" + opening + closing + r"""]*""" + closing, text):
    messages.append(name + ": unbalanced closing marks")
  return messages

def breaksrulesoffinnishguillemets(text):
  messages = breaksrulesofidenticalwrappingmarks("Guillemets", r"»", text)
  if findall(r"""«""", text):
    messages.append("Guillemets: left-pointing not used")
  return messages

def breaksrulesoffrenchguillemets(text):
  messages = []
  if findall(r"""\w«""", text):
    messages.append("Guillemets: opening mark preceeded by letter or digit")
  if findall(r"""«\S""", text):
    messages.append("Guillemets: opening mark not succeeded by space")
  if findall(r"""\S»""", text):
    messages.append("Guillemets: closing mark not preceeded by space")
  if findall(r"""»\w""", text):
    messages.append("Guillemets: closing mark succeeded by letter or digit")
  if findall(r"""«[^«»]*$""", text):
    messages.append("Guillemets: unclosed opening mark")
  if findall(r"""^[^«»]*»""", text):
    messages.append("Guillemets: unopened closing mark")
  if findall(r"""«[^«»]*«""", text):
    messages.append("Guillemets: unbalanced opening marks")
  if findall(r"""»[^«»]*»""", text):
    messages.append("Guillemets: unbalanced closing marks")
  return messages

def breaksrulesofenglishquotationmarks(text):
  messages = breaksrulesofsymmetricwrappingmarks("English quotation marks", r"“", r"”", text)
  if findall(r"""„""", text):
    messages.append("Low quotation mark: not used")
  return messages

def breaksrulesoffinnishquotationmarks(text):
  messages = breaksrulesofidenticalwrappingmarks("Finnish quotation marks", r"”", text)
  if findall(r"""“""", text):
    messages.append("Left quotation mark: not used")
  if findall(r"""„""", text):
    messages.append("Low quotation mark: not used")
  return messages

def breaksrulesofgermanquotationmarks(text):
  messages = breaksrulesofsymmetricwrappingmarks("German quotation marks", r"„", r"“", text)
  if findall(r"""”""", text):
    messages.append("Right quotation mark: not used")
  if findall(r"""["]""", text):
    messages.append("Straight quotation marks: not used")
  return messages

def breaksrulesofpolishquotationmarks(text):
  messages = breaksrulesofsymmetricwrappingmarks("Polish quotation marks", r"„", r"”", text)
  if findall(r"""“""", text):
    messages.append("Left quotation mark: not used")
  if findall(r"""["]""", text):
    messages.append("Straight quotation marks: not used")
  return messages

def breaksrulesofstraightquotationmarks(text):
  messages = breaksrulesofidenticalwrappingmarks("Straight quotation marks", "\"", text)
  if findall(r"""„""", text):
    messages.append("Low quotation mark: not used")
  return messages

def findproblematic():
  print("Finding problematic...")
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  makedirs("problematic", exist_ok = True)
  for language in ("ber", "cat", "ces", "cmn", "dan", "deu", "eng", "epo", "est", "fin", "fra", "gle", "glg", "hun", "isl", "ita", "jpn", "kab", "kor", "lat", "lit", "lvs", "nld", "nob", "pol", "por", "ron", "slk", "spa", "swe", "tgl", "tok", "tur", "vie"):
    misspelled = {}
    try:
      file = open("misspelled/misspelled-" + language + ".txt", "r", encoding = "utf-8")
    except:
      pass
    else:
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        misspelled[fields[0]] = fields[1]
        misspelled[fields[0].upper()] = fields[1].upper()
        misspelled[fields[0][: 1].upper() + fields[0][1 :]] = fields[1][: 1].upper() + fields[1][1 :]
      file.close()
    try:
      file = open("misspelled/case-" + language + ".txt", "r", encoding = "utf-8")
    except:
      pass
    else:
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        misspelled[fields[0]] = fields[1]
      file.close()

    foreign = {}
    try:
      file = open("foreign/foreign-" + language + ".txt", "r", encoding = "utf-8")
    except:
      pass
    else:
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        foreign[fields[0]] = fields[1]
        foreign[fields[0].upper()] = fields[1].upper()
        foreign[fields[0][: 1].upper() + fields[0][1 :]] = fields[1][: 1].upper() + fields[1][1 :]
      file.close()

    sensitive = set()
    try:
      file = open("sensitive/sensitive-" + language + ".txt", "r", encoding = "utf-8")
    except:
      pass
    else:
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        sensitive.add(fields[0])
        sensitive.add(fields[0].upper())
        sensitive.add(fields[0][: 1].upper() + fields[0][1 :])
      file.close()

    print("Writing sentences (" + language + ")...")
    write = open("problematic/problematic-" + language + ".txt", "w", encoding = "utf-8")
    for entry in scandir("temporary/sentences/" + language):
      read = open("temporary/sentences/" + language + "/" + entry.name, "r", encoding = "utf-8")
      for line in read:
        fields = findall(r"[^\t\n]+", line)

        for message in breaksrulesofsymmetricwrappingmarks("Braces", r"\{", r"\}", fields[2]):
          print(message, line, sep = "\t", end = "", file = write)

        for message in breaksrulesofsymmetricwrappingmarks("Brackets", r"\[", r"\]", fields[2]):
          print(message, line, sep = "\t", end = "", file = write)

        if language in ("nld",) and find(r"""^((?!\.\.\.)(?!…)\W)*\p{Ll}(?<!'s\b)(?<!'t\b)""", fields[2]):
          print("Capitalization", line, sep = "\t", end = "", file = write)
        if language not in ("nld", "tok") and find(r"""^((?!\.\.\.)(?!…)\W)*\p{Ll}""", fields[2]):
          print("Capitalization", line, sep = "\t", end = "", file = write)

        if language in ("por",) and findall(r"""ç[ei]""", fields[2], flags = I):
          print("Cedilla: followed by e or i", line, sep = "\t", end = "", file = write)
        if language in ("ron",) and findall(r"""[şţ]""", fields[2], flags = I):
          print("Cedilla: possible homoglyph", line, sep = "\t", end = "", file = write)

        if findall(r"""\D:\d""", fields[2], flags = I):
          print("Colon: not preceeded by digit", line, sep = "\t", end = "", file = write)
        if language in ("ber", "fra", "kab") and findall(r"""[^\s\d]:""", fields[2], flags = I):
          print("Colon: preceeded by letter or punctuation", line, sep = "\t", end = "", file = write)
        if language not in ("ber", "fra", "kab") and findall(r"""\s:""", fields[2], flags = I):
          print("Colon: preceeded by space", line, sep = "\t", end = "", file = write)
        if language in ("fin", "swe") and findall(r""":[^\w\s]""", fields[2], flags = I):
          print("Colon: succeeded by punctuation", line, sep = "\t", end = "", file = write)
        if language not in ("fin", "swe") and findall(r""":[^\d\s]""", fields[2], flags = I):
          print("Colon: succeeded by letter or punctuation", line, sep = "\t", end = "", file = write)
        if language in ("ber", "fra", "kab") and findall(r"""\d:\D""", fields[2], flags = I):
          print("Colon: not succeeded by digit", line, sep = "\t", end = "", file = write)

        if findall(r"""\s,""", fields[2], flags = I):
          print("Comma: preceeded by space", line, sep = "\t", end = "", file = write)
        if findall(r"""\D,\d""", fields[2], flags = I):
          print("Comma: not preceeded by digit", line, sep = "\t", end = "", file = write)
        if findall(r""",[^\W\d]""", fields[2], flags = I):
          print("Comma: succeeded by letter", line, sep = "\t", end = "", file = write)

        if findall(r"""[a-z][\u0430-\u044F]|[\u0430-\u044F][a-z]""", fields[2], flags = I):
          print("Cyrillic characters: possible homoglyphs", line, sep = "\t", end = "", file = write)

        if language in ("por",) and findall(r"""ü""", fields[2], flags = I):
          print("Dieresis: not used", line, sep = "\t", end = "", file = write)

        if language not in ("cmn", "jpn") and findall(r"""[０-９]""", fields[2], flags = I):
          print("Digits: full-width digits", line, sep = "\t", end = "", file = write)
        if findall(r"""[0-9].*[０-９]|[０-９].*[0-9]""", fields[2], flags = I):
          print("Digits: mixed regular and full-width digits", line, sep = "\t", end = "", file = write)

        if findall(r"""\u2033""", fields[2], flags = I):
          print("Double prime: possible homoglyph", line, sep = "\t", end = "", file = write)

        if findall(r"""([^.]|^)\.\.([^.]|$)""", fields[2], flags = I):
          print("Ellipsis: too short", line, sep = "\t", end = "", file = write)

        # if findall(r"""--|(\s|^)-(\s|$)""", fields[2], flags = I):
        #   print("Em dash: homoglyph", line, sep = "\t", end = "", file = write)

        # if findall(r"""\d-\d""", fields[2], flags = I):
        #   print("En dash or figure dash: possible homoglyph", line, sep = "\t", end = "", file = write)

        if language in ("fra",) and findall(r"""\w[!]""", fields[2], flags = I):
          print("Exclamation mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
        if language not in ("fra",) and findall(r"""\s[!]""", fields[2], flags = I):
          print("Exclamation mark: preceeded by space", line, sep = "\t", end = "", file = write)
        if findall(r"""[!]\w""", fields[2], flags = I):
          print("Exclamation mark: succeeded by letter or digit", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""\w[¡]""", fields[2], flags = I):
          print("Inverted exclamation mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""[¡]\s""", fields[2], flags = I):
          print("Inverted exclamation mark: succeeded by space", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""^[^¡!]*[!]""", fields[2], flags = I):
          print("Exclamation mark: unopened exclamation mark", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""[¡][^¡!]*$""", fields[2], flags = I):
          print("Exclamation mark: unclosed exclamation mark", line, sep = "\t", end = "", file = write)
        if language not in ("spa",) and findall(r"""[¡]""", fields[2], flags = I):
          print("Inverted exclamation mark: not used", line, sep = "\t", end = "", file = write)

        if language == "kor" and findall(r"""\w[^.…?!‽？~]*$""", fields[2], flags = I):
          print("Final punctuation", line, sep = "\t", end = "", file = write)
        if language != "kor" and findall(r"""\w[^.…?!‽]*$""", fields[2], flags = I):
          print("Final punctuation", line, sep = "\t", end = "", file = write)

        if findall(r"""[a-z][α-ω]|[α-ω][a-z]""", fields[2], flags = I):
          print("Greek characters: possible homoglyphs", line, sep = "\t", end = "", file = write)

        if language in ("fin", "swe"):
          for message in breaksrulesoffinnishguillemets(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("ber", "fra", "kab", "vie"):
          for message in breaksrulesoffrenchguillemets(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("ces", "dan", "deu", "hun", "pol", "slk"):
          for message in breaksrulesofsymmetricwrappingmarks("Guillemets", r"»", r"«", fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("cat", "epo", "est", "glg", "ita", "nob", "por", "ron", "spa", "tur"):
          for message in breaksrulesofsymmetricwrappingmarks("Guillemets", r"«", r"»", fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("eng", "gle", "isl", "kor", "lat", "lit", "lvs", "nld", "tok") and findall(r"""[«»]""", fields[2], flags = I):
          print("Guillemets: not used", line, sep = "\t", end = "", file = write)

        if findall(r"""\u05C1|\u05C2""", fields[2], flags = I):
          print("Hebrew dot", line, sep = "\t", end = "", file = write)

        if findall(r"""\u200E""", fields[2], flags = I):
          print("Left-to-right mark", line, sep = "\t", end = "", file = write)

        if findall(r"""x\d|\dx|\d\s*x\s*\d""", fields[2], flags = I):
          print("Multiplication sign: possible homoglyph", line, sep = "\t", end = "", file = write)

        if language not in ("glg", "ita", "por", "spa") and findall(r"""º""", fields[2], flags = I):
          print("Ordinal indicator: possible homoglyph", line, sep = "\t", end = "", file = write)

        for message in breaksrulesofsymmetricwrappingmarks("Parentheses", r"\(", r"\)", fields[2]):
          print(message, line, sep = "\t", end = "", file = write)

        if language == "eng" and findall(r"""\s[.](?![\d.])""", fields[2], flags = I):
          print("Period: preceeded by space", line, sep = "\t", end = "", file = write)
        if language != "eng" and findall(r"""\s[.](?![.])""", fields[2], flags = I):
          print("Period: preceeded by space", line, sep = "\t", end = "", file = write)
        if language != "eng" and findall(r"""\D[.]\d""", fields[2], flags = I):
          print("Period: not preceeded by digit", line, sep = "\t", end = "", file = write)

        if findall(r"""\u2032""", fields[2], flags = I):
          print("Prime: possible homoglyph", line, sep = "\t", end = "", file = write)

        if language in ("fra",) and findall(r"""\w[?]""", fields[2], flags = I):
          print("Question mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
        if language not in ("fra",) and findall(r"""\s[?]""", fields[2], flags = I):
          print("Question mark: preceeded by space", line, sep = "\t", end = "", file = write)
        if findall(r"""[?]\w""", fields[2], flags = I):
          print("Question mark: succeeded by letter or digit", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""\w[¿]""", fields[2], flags = I):
          print("Inverted question mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""[¿]\s""", fields[2], flags = I):
          print("Inverted question mark: succeeded by space", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""^[^¿?]*[?]""", fields[2], flags = I):
          print("Question mark: unopened question mark", line, sep = "\t", end = "", file = write)
        if language in ("spa",) and findall(r"""[¿][^¿?]*$""", fields[2], flags = I):
          print("Question mark: unclosed question mark", line, sep = "\t", end = "", file = write)
        if language not in ("spa",) and findall(r"""[¿]""", fields[2], flags = I):
          print("Inverted question mark: not used", line, sep = "\t", end = "", file = write)

        if language in ("ber", "cat", "dan", "eng", "fra", "gle", "glg", "ita", "kab", "kor", "lat", "lvs", "nld", "nob", "por", "spa", "tok", "tur", "vie"):
          for message in breaksrulesofenglishquotationmarks(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("fin", "swe"):
          for message in breaksrulesoffinnishquotationmarks(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("hun", "pol", "ron"):
          for message in breaksrulesofpolishquotationmarks(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("ces", "deu", "est", "isl", "lit", "slk"):
          for message in breaksrulesofgermanquotationmarks(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if language in ("ber", "cat", "dan", "eng", "fra", "glg", "ita", "kab", "kor", "lat", "lvs", "nld", "nob", "por", "spa", "tok", "tur", "vie"):
          for message in breaksrulesofstraightquotationmarks(fields[2]):
            print(message, line, sep = "\t", end = "", file = write)
        if findall(r""",,|''""", fields[2], flags = I):
          print("Quotation marks: homoglyphs", line, sep = "\t", end = "", file = write)
        if findall(r"""[‘’“”].*['"]|['"].*[‘’“”]""", fields[2], flags = I):
          print("Quotation marks: mixed curly and straight", line, sep = "\t", end = "", file = write)

        if language in ("ber", "fra", "kab") and findall(r"""\S;""", fields[2], flags = I):
          print("Semicolon: not preceeded by space", line, sep = "\t", end = "", file = write)
        if language not in ("ber", "fra", "kab") and findall(r"""\s;""", fields[2], flags = I):
          print("Semicolon: preceeded by space", line, sep = "\t", end = "", file = write)
        if findall(r""";\w""", fields[2], flags = I):
          print("Semicolon: succeeded by letter or digit", line, sep = "\t", end = "", file = write)

        if findall(r"""\u200B""", fields[2], flags = I):
          print("Zero-width space", line, sep = "\t", end = "", file = write)

        for token in gettokensinlanguage(janome, kkma, language, fields[2]):
          if token in misspelled:
            print("Misspelling: " + token + " -> " + misspelled[token], line, sep = "\t", end = "", file = write)
          elif token in foreign:
            print("Foreign: " + token + " = " + foreign[token], line, sep = "\t", end = "", file = write)
          elif token in sensitive:
            print("Sensitive: " + token, line, sep = "\t", end = "", file = write)
      read.close()
    write.close()

def findsimilar():
  print("Writing similar...")
  seen = {}
  write = {}
  makedirs("similar", exist_ok = True)
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    hashed = hash(cleanupforhashing(fields[2]))
    if hashed in seen:
      if fields[1] != "\\N":
        if fields[1] not in write:
          write[fields[1]] = open("similar/similar-" + fields[1] + ".txt", "w", encoding = "utf-8")
        print(seen[hashed], line, sep = "\t", end = "", file = write[fields[1]])
    else:
      seen[hashed] = int(fields[0])
  read.close()
  for language in write:
    write[language].close()

partitionsentences()
print("")
partitionlinks()
print("")
listlanguages()
print("")
listusers()
print("")
listcharacters()
print("")
listwords()
print("")
counttranslations()
print("")
selectsentences()
print("")
findproblematic()
print("")
findsimilar()
print("")
