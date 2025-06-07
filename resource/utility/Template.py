class Template:
    def __init__(self, message):
        self.message = message

    def show_message(self):
        print(f"Message: {self.message}")


# Example usage
if __name__ == "__main__":
    demo = Template("Hello, world!")
    demo.show_message()
