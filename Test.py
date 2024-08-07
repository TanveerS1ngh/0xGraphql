import json
import sys
from graphql import build_client_schema, get_introspection_query, graphql_sync

if len(sys.argv) < 2:
    print("Usage: python Test.py schema.json")
    sys.exit(1)

schema_file = sys.argv[1]

try:
    with open(schema_file, 'r') as f:
        schema_data = json.load(f)

    # Ensure the schema contains the necessary data for introspection
    if 'data' not in schema_data or '__schema' not in schema_data['data']:
        raise ValueError("Invalid or incomplete introspection result.")

    # Debugging: Print schema keys and types
    print("Introspection keys:", schema_data['data'].keys())
    print("Schema types:", [t['name'] for t in schema_data['data']['__schema']['types']])

    # Build the schema from the introspection result
    schema = build_client_schema(schema_data['data'])

    # Get all types in the schema
    types = schema.type_map

    # Open the output file
    with open("all_queries_mutations.graphql", 'w') as output_file:

        # Generate the query function
        def generate_query(schema, type_name):
            # Get the fields of the type
            fields = schema.get_type(type_name).fields.keys()
            # Generate the query string
            query = "query { \n  " + type_name + " { \n" + \
                " \n".join(["    " + field + "\n" for field in fields]) + \
                "  }\n}\n"
            return query

        # Generate queries and mutations for each type
        for type_name, graphql_type in types.items():
            if type_name.startswith('__') or type_name in ['Query', 'Mutation', 'Subscription']:
                continue
            if hasattr(graphql_type, 'fields'):
                # Get all fields of the type
                fields = graphql_type.fields.keys()
                if fields:
                    # Generate the query
                    query = generate_query(schema, type_name)
                    # Write the query to the output file
                    output_file.write(f"# Query for {type_name}\n")
                    output_file.write(query)
                    output_file.write("\n\n")

                    # Generate the mutation
                    # Mutation not supported by the schema
                    mutation = ''
                    # Write the mutation to the output file
                    output_file.write(f"# Mutation for {type_name} (if supported)\n")
                    output_file.write(mutation)
                    output_file.write("\n\n")

    # Print when the generation is done
    print("Queries and mutations generated successfully.")
except FileNotFoundError:
    print(f"Schema file '{schema_file}' not found.")
except json.JSONDecodeError:
    print(f"Schema file '{schema_file}' is not a valid JSON file.")
except ValueError as e:
    print(f"An error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
