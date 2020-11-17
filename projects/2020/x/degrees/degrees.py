import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for p_id in movies[movie_id]["stars"]:
            if p_id != person_id:
                neighbors.add((movie_id, p_id))

    return neighbors



def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # Check the names
    if(source == None or target == None):
        return False

     # Intitialize frontier and explored lists
    Frontier = QueueFrontier()
    Explored = StackFrontier()
    Explored_persons = set()
    
    node_state = (None, None)
    node_parent = (None, None)
    node_action = (None, source)
    new_node = Node(node_state, node_parent, node_action)
    Frontier.add(new_node)
  
    # Explore
    while not(Frontier.empty()):
        # Pull the next node from the Frontier
        explore_node = Frontier.remove()
        this_person = explore_node.action[1]
 
        if target == this_person: # Found a path that connects source with target
            # Compute the path from the Explored stack.
            action = explore_node.action
            parent = explore_node.parent
            state = explore_node.state
            route = [action]
            while not(Explored.empty()):
                one_node_back = Explored.remove()
                if(state == one_node_back.action and parent == one_node_back.state):
                    route.extend([state])
                    parent = one_node_back.parent
                    state = one_node_back.state
            
            # Reverse and return the path
            route.reverse()
            
            return(route[1:])
        
        elif not(Explored_persons.__contains__(this_person)):
            # Add state to the explored set
            Explored.add(explore_node)
            Explored_persons.add(this_person)
        
            # Add the next nodes to the frontier
            node_state = explore_node.action
            node_parent = explore_node.state
            next_person = explore_node.action[1]
            neighs = list(neighbors_for_person(next_person))
            for n in neighs:
                node_action = n
                new_person = n[1]
                if not(Explored_persons.__contains__(new_person)):
                    new_node = Node(node_state, node_parent, node_action)
                    Frontier.add(new_node)
    
    # Explore all the nodes and found no connection
    return(False)

if __name__ == "__main__":
    main()
