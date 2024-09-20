import json
import os
from dotenv import load_dotenv
from graphmemory import GraphMemory, Node, Edge
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up the OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Initialize the GraphMemory database
graph_db = GraphMemory(database='graph.db', vector_length=1536)

def extract_attributes(text):
    """Extract structured data from unstructured text using OpenAI's GPT model."""
    print(f"\nExtracting attributes from: '{text}'")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Extract structured data from this text using the following attributes: name, title, country, term_start, term_end. Return the result as a JSON object."},
            {"role": "user", "content": text}
        ]
    )
    
    try:
        attributes = json.loads(response.choices[0].message.content)
        print(f"Extracted attributes: {attributes}")
        return attributes
    except json.JSONDecodeError:
        print("Failed to parse API response as JSON. Returning default structure.")
        return {
            "name": "Unknown",
            "title": "Unknown",
            "country": "Unknown",
            "term_start": "Unknown",
            "term_end": "Unknown"
        }

def calculate_embedding(input_text):
    """Calculate embedding for a given input using OpenAI's API."""
    print(f"\nCalculating embedding for: '{input_text}'")
    response = client.embeddings.create(
        input=input_text,
        model="text-embedding-3-small"
    )
    print(f"Embedding calculated. Vector length: {len(response.data[0].embedding)}")
    return response.data[0].embedding

def create_node(text):
    """Create a node with attributes extracted from text and embedding."""
    print(f"\nCreating node for: '{text}'")
    attributes = extract_attributes(text)
    embedding = calculate_embedding(text)
    node = Node(properties=attributes, vector=embedding)
    node_id = graph_db.insert_node(node)
    print(f"Node created with ID: {node_id}")
    return node_id

def create_edge(source_id, target_id, relation, weight):
    """Create an edge between two nodes."""
    print(f"\nCreating edge: {source_id} -{relation}-> {target_id} (weight: {weight})")
    edge = Edge(source_id=source_id, target_id=target_id, relation=relation, weight=weight)
    graph_db.insert_edge(edge)
    print("Edge created successfully")

def query_nearest_nodes(query_text, limit=1):
    """Find nearest nodes by vector embedding."""
    print(f"\nQuerying nearest nodes for: '{query_text}'")
    query_embedding = calculate_embedding(query_text)
    nearest_nodes = graph_db.nearest_nodes(query_embedding, limit=limit)
    print(f"Found {len(nearest_nodes)} nearest node(s)")
    return nearest_nodes

def query_nodes_by_attribute(attribute, value):
    """Get node(s) by attribute."""
    print(f"\nQuerying nodes with {attribute} = '{value}'")
    nodes = graph_db.nodes_by_attribute(attribute, value)
    print(f"Found {len(nodes)} node(s)")
    return nodes

def delete_edge(source_id, target_id):
    """Delete an edge by source and target node id."""
    print(f"\nDeleting edge between {source_id} and {target_id}")
    graph_db.delete_edge(source_id, target_id)
    print("Edge deleted successfully")

def run_cypher_query(query):
    """Run a Cypher query on the graph database."""
    print(f"\nRunning Cypher query: {query}")
    result = graph_db.cypher(query)
    print(f"Query result: {result}")
    return result

def main():
    print("Starting Graph Database Demo")
    print("============================")
    input("Press Enter to start the demo...")

    # Sample unstructured texts
    texts = [
        "George Washington was the first President of the United States and served from 1789 to 1797.",
        "Thomas Jefferson was the third President of the United States and served from 1801 to 1809. Before that, he was the first Secretary of State under George Washington from 1790 to 1793.",
        "Alexander Hamilton was the first Secretary of the Treasury of the United States and served from 1789 to 1795 under George Washington.",
        "John Adams was the second President of the United States and served from 1797 to 1801. He was also the first Vice President under George Washington."
    ]

    print("\n\n=== Step 1: Creating nodes from unstructured text ===")
    print("This step will create nodes in the graph database from the given unstructured text.")
    input("Press Enter to continue...")

    node_ids = [create_node(text) for text in texts]

    print("\nNodes created:")
    for node_id in node_ids:
        node = graph_db.get_node(node_id)
        print(f"Node {node_id}: {node.properties}")
    
    input("\nPress Enter to proceed to the next step...")

    print("\n\n=== Step 2: Creating relationships between nodes ===")
    print("This step will create edges (relationships) between the nodes we just created.")
    input("Press Enter to continue...")

    create_edge(node_ids[0], node_ids[1], "succeeded_by", 1.0)  # Washington -> Jefferson
    create_edge(node_ids[0], node_ids[2], "appointed", 0.8)     # Washington -> Hamilton
    create_edge(node_ids[0], node_ids[3], "succeeded_by", 1.0)  # Washington -> Adams
    create_edge(node_ids[3], node_ids[1], "succeeded_by", 1.0)  # Adams -> Jefferson

    print("\nEdges created:")
    print(graph_db.edges_to_json())
    
    input("\nPress Enter to proceed to the next step...")

    print("\n\n=== Step 3: Demonstrating vector similarity search ===")
    print("This step will demonstrate how to find the nearest node to a given query using vector similarity.")
    input("Press Enter to continue...")

    nearest_nodes = query_nearest_nodes("Who was the first President of the United States?", limit=1)
    print(f"Nearest node: {nearest_nodes[0].node.properties}")
    print(f"Distance: {nearest_nodes[0].distance}")
    
    input("\nPress Enter to proceed to the next step...")

    print("\n\n=== Step 4: Querying nodes by attribute ===")
    print("This step will demonstrate how to find nodes by a specific attribute.")
    input("Press Enter to continue...")

    presidents = query_nodes_by_attribute("title", "President of the United States")
    for node in presidents:
        print(f"President: {node.properties.get('name', 'Unknown')}, Served: {node.properties.get('term_start', 'Unknown')} to {node.properties.get('term_end', 'Unknown')}")
    
    input("\nPress Enter to proceed to the next step...")

    print("\n\n=== Step 5: Demonstrating edge deletion ===")
    print("This step will demonstrate how to delete an edge between two nodes.")
    input("Press Enter to continue...")

    delete_edge(node_ids[0], node_ids[1])  # Delete Washington -> Jefferson edge
    print("\nEdges after deletion:")
    print(graph_db.edges_to_json())
    
    input("\nPress Enter to proceed to the final step...")

    print("\n\n=== Step 6: Running a Cypher query ===")
    print("This step will demonstrate how to run a Cypher query on the graph database.")
    input("Press Enter to continue...")

    cypher_query = "MATCH (n:Person) WHERE n.title CONTAINS 'Secretary' RETURN n.name, n.title"
    result = run_cypher_query(cypher_query)
    print("Secretaries found:")
    for record in result:
        print(f"{record.get('n.name', 'Unknown')} - {record.get('n.title', 'Unknown')}")

    print("\nGraph Database Demo Completed")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
