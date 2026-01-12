from duckduckgo_search import DDGS

def test_search():
    try:
        results = DDGS().text("Apple stock news", max_results=3)
        print("Search results:")
        for r in results:
            print(r)
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    test_search()
