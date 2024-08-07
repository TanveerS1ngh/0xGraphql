import json
import sys
from graphql import build_schema, get_introspection_query, graphql_sync

def generate_query(type_name, fields):
    query = f"query {{\n  {type_name} {{\n"
    for field in fields:
        query += f"    {field}\n"
    query += "  }\n}\n"
    return query

def generate_mutation(type_name, fields):
    mutation = f"mutation {{\n  {type_name} {{\n"
    for field in fields:
        mutation += f"    {field}\n"
    mutation += "  }\n}\n"
    return mutation

def main(schema_file):
    with open(schema_file, 'r') as f:
        schema_data = json.load(f)

    # Build the schema from the introspection result
    schema = build_schema(json.dumps(schema_data['data']))

    # Get all types in the schema
    types = schema.type_map

    # Generate queries and mutations for each type
    for type_name, graphql_type in types.items():
        if type_name.startswith('__') or type_name in ['Query', 'Mutation', 'Subscription']:
            continue
        
        if hasattr(graphql_type, 'fields'):
            fields = graphql_type.fields.keys()
            if fields:
                query = generate_query(type_name, fields)
                with open(f"{type_name}_query.graphql", 'w') as f:
                    f.write(query)
                
                mutation = generate_mutation(type_name, fields)
                with open(f"{type_name}_mutation.graphql", 'w') as f:
                    f.write(mutation)
    
    print("Queries and mutations generated successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_graphql_queries.py schema.json")
        sys.exit(1)

    schema_file = sys.argv[1]
    main(schema_file)
