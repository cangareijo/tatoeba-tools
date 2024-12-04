# pip install janome jieba konlpy
# aspell -d en dump master | aspell -l en expand > eng.txt

from janome.tokenizer import Tokenizer
from jieba import cut
from konlpy.tag import Kkma
from os import makedirs
from os.path import getsize
from random import randint, sample, shuffle
from re import findall, I, search, sub
from regex import findall as find
from secrets import choice
from unicodedata import normalize

minimum = 0
minimumasian = 0

def cleanupforhashing(text):
  text = normalize("NFKC", text)
  text = sub(r"[\Wˈˌǃ]", "", text)
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

def loadlanguagemap():
  print("Loading language map...")
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  language = {}
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    language[fields[0]] = fields[1]
  read.close()
  return language

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

def loadspellchecker(language):
  print("Loading spell checker (" + language + ")...")
  try:
    if getsize("dictionaries/" + language + ".txt") > 10 * 1000 * 1000:
      print("Spell checker: dictionary too large")
      return lambda word: True
    file = open("dictionaries/" + language + ".txt", "r", encoding = "utf-8")
  except:
    print("Spell checker: dictionary not found")
    return lambda word: True
  else:
    dictionary = set()
    for line in file:
      if " " in line or "\t" in line:
        print("Spell checker: dictionary has spaces")
        return lambda word: True
      fields = findall(r"[^\t\n]+", line)
      dictionary.add(fields[0])
      dictionary.add(fields[0].upper())
      dictionary.add(fields[0][: 1].upper() + fields[0][1 :])
    file.close()
    return lambda word: word in dictionary

def listlanguages():
  print("Listing languages...")
  frequency = {}
  sample = {}

  print("Reading languages...")
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] not in frequency:
      frequency[fields[1]] = {}
      sample[fields[1]] = {}
    if fields[3] not in frequency[fields[1]]:
      frequency[fields[1]][fields[3]] = 0
      sample[fields[1]][fields[3]] = line
    frequency[fields[1]][fields[3]] += 1
    if randint(1, frequency[fields[1]][fields[3]]) == 1:
      sample[fields[1]][fields[3]] = line
  read.close()

  for language in frequency:
    frequency[language] = sum(frequency[language][user] for user in frequency[language])
    sample[language] = choice([sample[language][user] for user in sample[language]])

  languages = list(frequency)
  shuffle(languages)
  languages.sort(key = lambda language: frequency[language], reverse = True)

  print("Writing languages...")
  makedirs("temporary", exist_ok = True)
  write = open("temporary/languages.txt", "w", encoding = "utf-8")
  for language in languages:
    print(language, frequency[language], sample[language], sep = "\t", end = "", file = write)
  write.close()

def loadlanguagelist():
  print("Loading language list...")
  languages = []
  read = open("temporary/languages.txt", "r", encoding = "utf-8")
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

  languages = loadlanguagelist()
  languageof = loadlanguagemap()
  write = {}

  print("Writing links...")
  makedirs("temporary/links", exist_ok = True)
  for language in languages:
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

def listcharacters():
  print("Listing characters...")
  languages = loadlanguagelist()
  makedirs("characters", exist_ok = True)
  for language in languages:
    if language != "\\N":
      frequency = {}
      sample = {}

      print("Reading characters (" + language + ")...")
      read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        for character in set(fields[2]):
          if character not in frequency:
            frequency[character] = {}
            sample[character] = {}
          if fields[3] not in frequency[character]:
            frequency[character][fields[3]] = 0
          frequency[character][fields[3]] += 1
          if randint(1, frequency[character][fields[3]]) == 1:
            sample[character][fields[3]] = line
      read.close()

      characters = list(frequency)
      characters.sort()
      for character in characters:
        frequency[character] = sum(frequency[character][user] for user in frequency[character])
        sample[character] = choice([sample[character][user] for user in sample[character]])

      print("Writing characters (" + language + ")...")
      write = open("characters/characters-" + language + ".txt", "w", encoding = "utf-8")
      for character in characters:
        print(hex(ord(character)), character, frequency[character], sample[character], sep = "\t", end = "", file = write)
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
      sentences = {}
      sentencewords = {}
      file = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        sentencewords[int(fields[0])] = getwordsinlanguage(janome, kkma, language, fields[2])
        for word in sentencewords[int(fields[0])]:
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
            print(word, frequencies[word], translations[word], sentences[word], sep = "\t", end = "", file = write)
          write.close()

def counttranslationsuser(source, target, user):
  print("Counting translations...")
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  spellchecks = loadspellchecker(source)

  print("Reading links (" + source + ")...")
  linked = {}
  read = open("temporary/links/" + source + "/" + target + ".txt", "r", encoding = "utf-8")
  linked[target] = set()
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    linked[target].add(fields[0])
  read.close()

  print("Reading words (" + source + ")...")
  read = open("temporary/sentences/" + source + ".txt", "r", encoding = "utf-8")
  words = set()
  sentences = {}
  translations = {}
  identification = {}
  owner = {}
  translations[target] = {}
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    sentence = getwordsinlanguage(janome, kkma, source, fields[2].lower())
    for word in sentence:
      words.add(word)
      if word not in sentences:
        sentences[word] = 0
      sentences[word] += 1
      if randint(1, sentences[word]) == 1:
        identification[word] = fields[0]
        owner[word] = fields[3]
      if fields[3] == user:
        if fields[0] in linked[target]:
          if word not in translations[target]:
            translations[target][word] = 0
          translations[target][word] += 1
  read.close()
  words = list(words)
  words.sort()
  words.sort(key = lambda word: cleanupforsorting(word))

  print("Writing words (" + source + ")...")
  makedirs("translations-user/" + source, exist_ok = True)
  write = open("translations-user/" + source + "/translations-" + source + "-" + target + ".txt", "w", encoding = "utf-8")
  for word in words:
    print(word, sentences[word], translations[target][word] if word in translations[target] else 0, "+" if spellchecks(word) else "−", identification[word], owner[word], sep = "\t", file = write)
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
  for language in ("ber", "cat", "ces", "dan", "deu", "eng", "epo", "est", "fin", "fra", "gle", "glg", "hun", "isl", "ita", "kab", "kor", "lat", "lit", "lvs", "nld", "nob", "pol", "por", "ron", "slk", "spa", "swe", "tgl", "tok", "tur", "vie"):
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

      if findall(r"""[0-9].*[０-９]|[０-９].*[0-9]""", fields[2], flags = I):
        print("Digits: both normal and full-width digits are being used", line, sep = "\t", end = "", file = write)

      if findall(r"""\u2033""", fields[2], flags = I):
        print("Double prime: possible homoglyph", line, sep = "\t", end = "", file = write)

      if findall(r"""([^.]|^)\.\.([^.]|$)""", fields[2], flags = I):
        print("Ellipsis: too short", line, sep = "\t", end = "", file = write)

      # if findall(r"""--|(\s|^)-(\s|$)""", fields[2], flags = I):
      #   print("Em dash: homoglyph", line, sep = "\t", end = "", file = write)

      # if findall(r"""\d-\d""", fields[2], flags = I):
      #   print("En dash or figure dash: possible homoglyph", line, sep = "\t", end = "", file = write)

      if language in ("ber", "fra", "kab") and findall(r"""\w[!]""", fields[2], flags = I):
        print("Exclamation mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language not in ("ber", "fra", "kab") and findall(r"""\s[!]""", fields[2], flags = I):
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

      if language in ("ber", "fra", "kab") and findall(r"""\w[?]""", fields[2], flags = I):
        print("Question mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language not in ("ber", "fra", "kab") and findall(r"""\s[?]""", fields[2], flags = I):
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

      if language in ("ber", "cat", "dan", "eng", "epo", "fra", "gle", "glg", "ita", "kab", "kor", "lat", "lvs", "nld", "nob", "por", "spa", "tok", "tur", "vie"):
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
      if language in ("ber", "cat", "dan", "eng", "epo", "fra", "glg", "ita", "kab", "kor", "lat", "lvs", "nld", "nob", "por", "spa", "tok", "tur", "vie"):
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
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  language = {}
  user = {}
  seen = {}
  makedirs("similar", exist_ok = True)
  write = {}
  write["!"] = open("similar/similar.txt", "w", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] not in language:
      language[fields[1]] = fields[1]
    if fields[3] not in user:
      user[fields[3]] = fields[3]
    sentence = hash(cleanupforhashing(fields[2]))
    if sentence in seen:
      if seen[sentence][1] == fields[1]:
        if fields[1] not in write:
          write[fields[1]] = open("similar/similar-" + fields[1] + ".txt", "w", encoding = "utf-8")
        print(str(seen[sentence][0]), seen[sentence][2], fields[0], fields[3], sep = "\t", file = write[fields[1]])
      else:
        print(str(seen[sentence][0]), seen[sentence][1], seen[sentence][2], fields[0], fields[1], fields[3], sep = "\t", file = write["!"])
    else:
      seen[sentence] = (int(fields[0]), language[fields[1]], user[fields[3]])
  read.close()
  for tongue in write:
    write[tongue].close()

listlanguages()
print("")
partitionsentences()
print("")
partitionlinks()
print("")
subpartitionlinks()
print("")
listcharacters()
print("")
listwords()
print("")
counttranslations()
print("")
counttranslationsuser("eng", "por", "Cangarejo")
print("")
selectsentences()
print("")
findproblematic()
print("")
findsimilar()
print("")
