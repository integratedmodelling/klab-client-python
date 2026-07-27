""" sample script showing how to use the incremental knowledge search

    This mimics what the k.LAB Modeler's knowledge search view does as the user types: each
    call to KnowledgeSearch.search() sends the text typed so far and returns the current list
    of matches, refining the same expression started by the previous calls. Accepting a match
    commits it to the expression under construction, just like double-clicking a result in the
    Modeler's search box.

    Requires a running local (or remote) k.LAB engine; see example_elevation.py for how to point
    this at a remote engine with credentials.
"""

from klab.klab import Klab


def main():
    klab = Klab.create()
    if not klab.isOnline():
        print("engine is not online")
        return

    search = klab.knowledgeSearch()
    try:
        # first keystroke(s): partial query, as the user types "road..."
        response = search.search("road")
        for match in response.matches:
            print(f"{match.id} ({match.matchType}): {match.description}")

        if not response.matches:
            print("no matches found")
            return

        print("------------------------------------------------------------")
        # keep typing to refine the expression further
        response = search.search("roadn")
        for match in response.matches[:5]:
            print(f"{match.id} ({match.matchType})")

    finally:
        search.close()
        klab.close()


if __name__ == "__main__":
    main()
