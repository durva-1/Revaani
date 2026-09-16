class Conversation:

    def __init__(self, conversation_id, user):
        self.conversation_id = conversation_id
        self.user = user
        self.messages = []

    def add_message(self, role, content):
        message = {
            "role": role,
            "content": content
        }

        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def display_conversation(self):
        print("Conversation ID:", self.conversation_id)

        for message in self.messages:
            print(message["role"], ":", message["content"])
