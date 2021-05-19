import arcade


letter = []
for y in range(3):
    for x in range(26):
        texture = arcade.load_texture('Sprites/Text and numbers.png', x=x * 16, y=y*32, width=16, height=32)
        letter.append(texture)

LETTERS = tuple(letter)

LETTER_CODE = {
    "a": 0,
    "b": 1,
    "c": 2,
    "d": 3,
    "e": 4,
    "f": 5,
    "g": 6,
    "h": 7,
    "i": 8,
    "j": 9,
    "k": 10,
    "l": 11,
    "m": 12,
    "n": 13,
    "o": 14,
    "p": 15,
    "q": 16,
    "r": 17,
    "s": 18,
    "t": 19,
    "u": 20,
    "v": 21,
    "w": 22,
    "x": 23,
    "y": 24,
    "z": 25,
    "A": 26,
    "B": 27,
    "C": 28,
    "D": 29,
    "E": 30,
    "F": 31,
    "G": 32,
    "H": 33,
    "I": 34,
    "J": 35,
    "K": 36,
    "L": 37,
    "M": 38,
    "N": 39,
    'O': 40,
    'P': 41,
    'Q': 42,
    'R': 43,
    'S': 44,
    'T': 45,
    'U': 46,
    'V': 47,
    'W': 48,
    'X': 49,
    'Y': 50,
    'Z': 51,
    "1": 52,
    "2": 53,
    "3": 54,
    "4": 55,
    "5": 56,
    "6": 57,
    "7": 58,
    "8": 59,
    "9": 60,
    "0": 61,
    '.': 62,
    ',': 63,
    "'": 64,
    ':': 65,
    ';': 66,
    '!': 67,
    '?': 68,
    '/': 69,
    '(': 70,
    ')': 71,
    '[': 72,
    ']': 73,
    '{': 74,
    '}': 75,
    '_': 76,
    '-': 77,
    ' ': 78,


}
LETTER_SIZE = 16


def gen_letter_list(string: str = None, s_x: float = 0, s_y: float = 0, scale: float = 1, gap: int = 1):
    """
    :param string: The actual string that is being converted
    :param s_x: The center x position of the first letter
    :param s_y: The center y position of the first letter
    :param scale: The scale of the sprite going from 0.1 to 1
    :param gap: The gap between the letters that is affected by scale
    :return: It returns a SpriteList with all of the letter as Sprites
    """
    letter_list = arcade.SpriteList()
    for index, char in enumerate(string):
        if char != " ":
            texture = LETTERS[LETTER_CODE[char]]
            cur_letter = arcade.Sprite(scale=scale,
                                       center_x=s_x + (((gap + LETTER_SIZE) * scale) * index),
                                       center_y=s_y)
            cur_letter.texture = texture
            letter_list.append(cur_letter)
    return letter_list
