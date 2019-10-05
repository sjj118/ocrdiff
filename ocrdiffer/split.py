def split_word(ocr):
    spt = []
    for word in ocr:
        s = 0
        for i in range(1, len(word)):
            dis = word.chars[i].left - word.chars[i - 1].right
            wid = (word.chars[i].width + word.chars[i - 1].width) / 2
            if dis / wid > 1.2:
                spt.append(word[s:i])
                s = i
        spt.append(word[s:])
    return spt
