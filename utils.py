
import random

# Define the Unicode range for emojis
start = 0x1F600
end = 0x1F64F

# Generate a random Unicode character representing an emoji
random_emoji = chr(random.randint(start, end))
print(random_emoji)


def generate_random_emoji():
    random_emoji = chr(random.randint(start, end))
    print(random_emoji)
    return random_emoji