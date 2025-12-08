from neo4j_conn import URI, USER, DATABASE, PASSWORD, run_cypher

print("DEBUG: URI      =", URI)
print("DEBUG: USER     =", USER)
print("DEBUG: DATABASE =", DATABASE)
print("DEBUG: PW-LEN   =", len(PASSWORD) if PASSWORD else None)

try:
    records = run_cypher("RETURN 1 AS n")
    print("Connected! Result:", [r.data() for r in records])
except Exception as e:
    print("Error:", repr(e))
