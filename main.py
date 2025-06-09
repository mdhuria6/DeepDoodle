from graph.comic_graph import graph

if __name__ == "__main__":
    story = open("data/samples/example_story.txt").read()
    result = graph.invoke({"story": story})
    print(result["output"])