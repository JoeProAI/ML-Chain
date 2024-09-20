from graphmemory import GraphMemory, Node

graph_db = GraphMemory(database='graph.db')

def add_node():
    name = input("Enter node name: ")
    title = input("Enter title: ")
    node = Node(properties={"name": name, "title": title})
    node_id = graph_db.insert_node(node)
    print(f"Node added with ID: {node_id}")

def find_node(name):
    result = graph_db.cypher(f"MATCH (n) WHERE n.name = '{name}' RETURN n")
    if result:
        node = result[0]['n']
        print(f"Node found: {node.properties}")
    else:
        print(f"No node found with name: {name}")

def main():
    print("Minimized Graph Database Demo")
    print("=============================")
    
    while True:
        print("\nOperations:")
        print("1. Add a node")
        print("2. Find a node")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            add_node()
        elif choice == '2':
            name = input("Enter node name to find: ")
            find_node(name)
        elif choice == '3':
            print("Thank you for using the Graph Database Demo. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
