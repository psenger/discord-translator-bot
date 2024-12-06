import random


class GaySpeakTransformer:
    def __init__(self):
        self.sparkles = [
            "✨", "💅", "💖", "💫", "🌈", "👑", "💁‍♀️",
            "💃", "🦄", "⭐", "💝", "💅", "💋"
        ]

        self.interjections = [
            "yasss", "hunty", "werk", "slay", "periodt", "sis",
            "bestie", "queen", "icon", "legend", "girlboss", "sweetie"
        ]

        self.dramatic_adjectives = [
            "fabulous", "fierce", "iconic", "stunning", "legendary",
            "gorgeous", "sickening", "divine", "absolutely everything",
            "serving"
        ]

        self.endings = [
            "periodt!",
            "and I'm living for it!",
            "*hair flip*",
            "no choice but to stan!",
            "the main character energy!",
            "it's giving everything it needs to give!",
            "mother has mothered!",
            "she ate and left no crumbs!",
            "the girls that get it, get it!",
            "and that's on periodt, bestie!",
            "slay the house down boots!",
            "*tongue pop*",
            "werk dish!",
            "giving very much everything!",
            "we love to see it!"
        ]

        self.extra_flair = [
            "*death drops*",
            "*vogues away*",
            "*serves face*",
            "*splits*",
            "*dips*",
            "*cat walks away*"
        ]

        self.word_replacements = {
            "good": "fierce",
            "great": "sickening",
            "yes": "yaaaaas",
            "amazing": "serving cunt",
            "nice": "fabulous",
            "hello": "heeeeeey",
            "hi": "hiiiiii bestie",
            "bye": "bye gorge",
            "wow": "omg sis",
            "cool": "iconic"
        }

    def _replace_words(self, message: str) -> str:
        """Replace common words with gay culture slang."""
        words = message.lower().split()
        return " ".join(self.word_replacements.get(word, word) for word in words)

    def _elongate_vowels(self, message: str) -> str:
        """Add dramatic emphasis by repeating vowels."""
        for vowel in "aeiou":
            message = message.replace(vowel, vowel * random.randint(2, 4))
        return message

    def transform(self, message: str) -> str:
        """Transform a regular message into gay speak."""
        # Basic word replacements
        transformed = self._replace_words(message)

        # Add dramatic emphasis
        transformed = transformed.replace("!", "!!!")
        transformed = self._elongate_vowels(transformed)

        # Structure the final message
        final_message = (
            f"{random.choice(self.sparkles)} {random.choice(self.interjections).upper()}! "
            f"{random.choice(self.sparkles)} this message is {random.choice(self.dramatic_adjectives)}! "
            f"{random.choice(self.sparkles)}\n"
            f"{transformed} {random.choice(self.sparkles)}\n"
            f"{random.choice(self.endings)} {random.choice(self.sparkles)}"
        )

        # 30% chance to add extra flair
        if random.random() < 0.3:
            final_message += f"\n{random.choice(self.extra_flair)} {random.choice(self.sparkles)}"

        return final_message


# Example usage if run as main script
if __name__ == "__main__":
    transformer = GaySpeakTransformer()
    test_messages = [
        "Hello everyone, how are you?",
        "This is a good day",
        "I'm going to the store",
        "Wow, that's cool!"
    ]

    for msg in test_messages:
        print("\nOriginal:", msg)
        print("Transformed:", transformer.transform(msg))