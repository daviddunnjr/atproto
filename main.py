from atproto import Client
from Login import Login

def main():
    client = Client()
    client.login(Login().Username(), Login().Password())
if __name__ == "__main__":
    main()