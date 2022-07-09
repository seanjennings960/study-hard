# python3

class Query:
    def __init__(self, query):
        self.type = query[0]
        self.number = int(query[1])
        if self.type == 'add':
            self.name = query[2]

def read_queries():
    n = int(input())
    return [Query(input().split()) for i in range(n)]

def write_responses(result):
    print('\n'.join(result))

def process_queries(queries):
    responses = []
    # Keep list of all existing (i.e. not deleted yet) contacts.
    contacts = {}
    for query in queries:
        if query.type == 'add':
            # if we already have contact with such number,
            # we should rewrite contact's name
            contacts[query.number] = query.name
        elif query.type == 'del':
            if query.number in contacts:
                contacts.pop(query.number)
        else:
            responses.append(
                contacts.get(query.number, 'not found'))
    return responses

if __name__ == '__main__':
    write_responses(process_queries(read_queries()))

