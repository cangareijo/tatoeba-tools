# pip install janome jieba konlpy
# aspell -d en dump master | aspell -l en expand > eng.txt

from janome.tokenizer import Tokenizer
from jieba import cut
from konlpy.tag import Kkma
from os import makedirs
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
    r"""[^\s\u200B\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*•●▲➔][^\s\u200B\uFEFF—―…]*"""
    r"""[^\s\u200B\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*•●▲➔]|"""
    r"""[^\s\u200B\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*•●▲➔]|"""
    r"""[\s\u200B\uFEFF—―…'‚‘’"„“”<>‹›«»「」『』()\[\]{}【】《》〈〉|/,:;.¿?¡!‽*•●▲➔]+""",
    text)

def getwordsinlanguage(janome, kkma, language, text):
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

def loadlanguagemap():
  print("Loading language map...")
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  language = {}
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    language[fields[0]] = fields[1]
  read.close()
  return language

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

def loadlanguagelist():
  print("Loading language list...")
  languages = []
  read = open("languages.txt", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    languages.append(fields[0])
  read.close()
  return languages

def partitionsentences():
  write = {}

  print("Partitioning sentences...")
  makedirs("temporary/sentences", exist_ok = True)
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] != "\\N":
      if fields[1] not in write:
        write[fields[1]] = open("temporary/sentences/" + fields[1] + ".txt", "w", encoding = "utf-8")
      print(line, end = "", file = write[fields[1]])
  read.close()

  for language in write:
    write[language].close()

def partitionlinks():
  print("Partitioning links...")

  languageof = loadlanguagemap()
  write = {}

  print("Writing links...")
  makedirs("temporary/links", exist_ok = True)
  for language in loadlanguagelist():
    if language != "\\N":
      write[language] = open("temporary/links/" + language + ".txt", "w", encoding = "utf-8")

  read = open("links.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[0] in languageof and languageof[fields[0]] != "\\N":
      print(fields[0], fields[1], sep = "\t", file = write[languageof[fields[0]]])
  read.close()

  for language in write:
    write[language].close()

def subpartitionlinks():
  print("Subpartitioning links...")

  languages = loadlanguagelist()
  languageof = loadlanguagemap()

  for idiom in languages:
    if idiom != "\\N":
      writes = {}

      print("Writing links (" + idiom + ")...")
      makedirs("temporary/links/" + idiom, exist_ok = True)
      for tongue in languages:
        if tongue != "\\N":
          writes[tongue] = open("temporary/links/" + idiom + "/" + tongue + ".txt", "w", encoding = "utf-8")

      read = open("temporary/links/" + idiom + ".txt", "r", encoding = "utf-8")
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        if fields[1] in languageof and languageof[fields[1]] != "\\N":
          print(fields[0], fields[1], sep = "\t", file = writes[languageof[fields[1]]])
      read.close()

      for tongue in writes:
        writes[tongue].close()

def listusers():
  print("Listing users...")
  makedirs("users", exist_ok = True)
  for language in loadlanguagelist():
    if language != "\\N":
      print("Reading users (" + language + ")...")
      frequencies = {}
      sentences = {}
      read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        if fields[3] not in frequencies:
          frequencies[fields[3]] = 0
        frequencies[fields[3]] += 1
        if randint(1, frequencies[fields[3]]) == 1:
          sentences[fields[3]] = line
      read.close()

      users = list(frequencies)
      shuffle(users)
      users.sort(key = lambda user: frequencies[user], reverse = True)

      print("Writing users (" + language + ")...")
      write = open("users/users-" + language + ".txt", "w", encoding = "utf-8")
      for user in users:
        print(user, frequencies[user], sentences[user], sep = "\t", end = "", file = write)
      write.close()

def listcharacters():
  print("Listing characters...")
  makedirs("characters", exist_ok = True)
  for language in loadlanguagelist():
    if language != "\\N":
      frequencies = {}
      sentences = {}

      print("Reading characters (" + language + ")...")
      read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in read:
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
      read.close()

      characters = list(frequencies)
      characters.sort()
      for character in characters:
        frequencies[character] = sum(frequencies[character][user] for user in frequencies[character])
        sentences[character] = choice([sentences[character][user] for user in sentences[character]])

      print("Writing characters (" + language + ")...")
      write = open("characters/characters-" + language + ".txt", "w", encoding = "utf-8")
      for character in characters:
        print(hex(ord(character)), character, frequencies[character], sentences[character], sep = "\t", end = "", file = write)
      write.close()

def listwords():
  print("Listing words...")
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  languages = loadlanguagelist()
  makedirs("words", exist_ok = True)
  for language in languages:
    if language != "\\N":
      print("Reading words (" + language + ")...")
      frequencies = {}
      sentences = {}
      file = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        sentence = getwordsinlanguage(janome, kkma, language, fields[2])
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

      print("Writing words (" + language + ")...")
      file = open("words/words-" + language + ".txt", "w", encoding = "utf-8")
      for word in words:
        print(word, frequencies[word], sentences[word], sep = "\t", end = "", file = file)
      file.close()

def counttranslations():
  print("Counting translations...")
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  languages = loadlanguagelist()
  for language in languages[: 50]:
    if language != "\\N":
      print("Reading words (" + language + ")...")
      frequencies = {}
      sentencewords = {}
      file = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        sentencewords[int(fields[0])] = getwordsinlanguage(janome, kkma, language, fields[2])
        for word in sentencewords[int(fields[0])]:
          if word not in frequencies:
            frequencies[word] = 0
          frequencies[word] += 1
      file.close()

      words = list(frequencies)
      words.sort()
      words.sort(key = lambda word: cleanupforsorting(word))

      makedirs("translations/" + language, exist_ok = True)
      for idiom in languages[: 50]:
        if idiom != language and idiom != "\\N":
          print("Reading links (" + language + "-" + idiom + ")...")
          translations = {word: 0 for word in words}
          file = open("temporary/links/" + language + "/" + idiom + ".txt", "r", encoding = "utf-8")
          for line in file:
            fields = findall(r"[^\t\n]+", line)
            if int(fields[0]) in sentencewords:
              for word in sentencewords[int(fields[0])]:
                translations[word] += 1
          file.close()

          print("Writing words (" + language + "-" + idiom + ")...")
          write = open("translations/" + language + "/translations-" + language + "-" + idiom + ".txt", "w", encoding = "utf-8")
          for word in words:
            print(word, frequencies[word], translations[word], sep = "\t", file = write)
          write.close()

def selectsentences():
  print("Selecting sentences...")
  languages = loadlanguagelist()
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  makedirs("sentences", exist_ok = True)
  for language in languages:
    if language != "\\N":
      sentences = {}

      print("Reading sentences (" + language + ")...")
      file = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        sentence = getwordsinlanguage(janome, kkma, language, fields[2])
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

      print("Writing sentences (" + language + ")...")
      file = open("sentences/sentences-" + language + ".txt", "w", encoding = "utf-8")
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
  makedirs("problematic", exist_ok = True)
  for language in ("ber", "cat", "ces", "cmn", "dan", "deu", "eng", "epo", "est", "fin", "fra", "gle", "glg", "hun", "isl", "ita", "jpn", "kab", "kor", "lat", "lit", "lvs", "nld", "nob", "pol", "por", "ron", "slk", "spa", "swe", "tgl", "tok", "tur", "vie"):
    misspelled = {}
    try:
      file = open("misspelled/misspelled-" + language + ".txt", "r", encoding = "utf-8")
    except:
      pass
    else:
      print("Loading misspelled (" + language + ")...")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        misspelled[fields[0]] = fields[1]
        misspelled[fields[0].upper()] = fields[1].upper()
        misspelled[fields[0][: 1].upper() + fields[0][1 :]] = fields[1][: 1].upper() + fields[1][1 :]
      file.close()

    foreign = {}
    try:
      file = open("misspelled/foreign-" + language + ".txt", "r", encoding = "utf-8")
    except:
      pass
    else:
      print("Loading foreign (" + language + ")...")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        foreign[fields[0]] = fields[1]
        foreign[fields[0].upper()] = fields[1].upper()
        foreign[fields[0][: 1].upper() + fields[0][1 :]] = fields[1][: 1].upper() + fields[1][1 :]
      file.close()

    print("Writing sentences (" + language + ")...")
    read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
    write = open("problematic/problematic-" + language + ".txt", "w", encoding = "utf-8")
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

      for word in gettokens(fields[2]):
        if word in misspelled:
          print("Misspelling: " + word + " -> " + misspelled[word], line, sep = "\t", end = "", file = write)

      for word in gettokens(fields[2]):
        if word in foreign:
          print("Foreign: " + word + " = " + foreign[word], line, sep = "\t", end = "", file = write)
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

listlanguages()
print("")
partitionsentences()
print("")
partitionlinks()
print("")
subpartitionlinks()
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
