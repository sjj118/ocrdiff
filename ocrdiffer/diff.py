import difflib


def diff_words(words):
    diff1 = []
    diff2 = []
    for w1, w2 in words:
        differ = difflib.SequenceMatcher(
            lambda x: x in " ,./;\'[]\\-=`<>?:\"{}|_+~!@#$%^&*()，。；‘’“”《》？：【】「」、｜——！¥…（）～·",
            w1.word, w2.word)
        blocks = differ.get_matching_blocks()
        if blocks[0][0]: diff1.append(w1[0: blocks[0][0]])
        if blocks[0][1]: diff2.append(w2[0: blocks[0][1]])
        for i in range(len(blocks) - 1):
            if blocks[i][0] + blocks[i][2] != blocks[i + 1][0]:
                diff1.append(w1[blocks[i][0] + blocks[i][2]: blocks[i + 1][0]])
            if blocks[i][1] + blocks[i][2] != blocks[i + 1][1]:
                diff2.append(w2[blocks[i][1] + blocks[i][2]: blocks[i + 1][1]])
    return diff1, diff2
