def crisis_detection(text):
    keywords = ["suicide", "kill myself", "end my life", "hopeless"]
    return any(word in text.lower() for word in keywords)
