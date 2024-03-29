import rdflib
from rdflib import URIRef

TITLE_PREDICATE = URIRef('http://purl.org/dc/terms/title')
PUBLISHER_PREDICATE = URIRef('http://purl.org/dc/terms/publisher')
CREATOR_PREDICATE = URIRef('http://purl.org/dc/terms/creator')
NAME_PREDICATE = URIRef('http://www.gutenberg.org/2009/pgterms/name')
LANGUAGE_PREDICATE = URIRef('http://purl.org/dc/terms/language')
VALUE_PREDICATE = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#value') 
HAS_FORMAT_PREDICATE = URIRef('http://purl.org/dc/terms/hasFormat')
ISSUED_PREDICATE = URIRef('http://purl.org/dc/terms/issued')
SUBJECT_PREDICATE = URIRef('http://purl.org/dc/terms/subject')
SHELF_PREDICATE = URIRef('http://www.gutenberg.org/2009/pgterms/bookshelf')
DOWNLOAD_PREDICATE = URIRef('http://www.gutenberg.org/2009/pgterms/downloads')
RIGHTS_PREDICATE = URIRef('http://purl.org/dc/terms/rights')


SUBJECT_URL = 'http://www.gutenberg.org/ebooks/{}'

g = rdflib.Graph()

def get_ebook(book_number):
    g.load('./cache/epub/{}/pg{}.rdf'.format(book_number, book_number))
    SUBJECT = URIRef(SUBJECT_URL.format(book_number))

    # Title
    title = g.value(SUBJECT, TITLE_PREDICATE).__str__()
    # Author
    author_generator = g.objects(SUBJECT, CREATOR_PREDICATE)
    authors = ""
    for author_node in author_generator:
        author = g.value(author_node, NAME_PREDICATE).__str__()
        authors += author + "/"

    # Language
    language_generator = g.objects(SUBJECT, LANGUAGE_PREDICATE)
    languages = ""
    for language_node in language_generator:
        language = g.value(language_node, VALUE_PREDICATE).__str__()
        languages += language

    # Content URL (.txt)
    contentURL_generator = g.objects(SUBJECT, HAS_FORMAT_PREDICATE)
    contentURL = None
    coverURL = None
    for url in contentURL_generator:
        if url.endswith('.txt'):
            contentURL = url.__str__()
        if url.endswith('medium.jpg'):
            coverURL = url.__str__()
    if(coverURL==None):
        coverURL = f'https://www.gutenberg.org/files/{book_number}/{book_number}-h/images/cover.jpg'
    # Release Date
    release_date = g.value(SUBJECT, ISSUED_PREDICATE).__str__()

    # Subjects 
    subject_generator = g.objects(SUBJECT, SUBJECT_PREDICATE)
    subjects = ""
    for subject_node in subject_generator:
        subject = g.value(subject_node, VALUE_PREDICATE).__str__()
        subjects += subject + "/"

    # Shelves
    shelf_generator = g.objects(SUBJECT, SHELF_PREDICATE)
    shelves = ""
    for shelf_node in shelf_generator:
        shelf = g.value(shelf_node, VALUE_PREDICATE).__str__()
        shelves += shelf + "/"

    # Downloads
    downloads = g.value(SUBJECT, DOWNLOAD_PREDICATE).__str__()

    # Copyrights
    copyrights = g.value(SUBJECT, RIGHTS_PREDICATE).__str__()

    if contentURL == None:
        raise FileNotFoundError

    return {
        "id": book_number,
        "title": title,
        "authors": authors,
        "subjects": subjects,
        "bookshelves": shelves,
        "languages": languages,
        "copyright": copyrights,
        "content_url": contentURL,
        "download_count": downloads,
        "cover_url": coverURL,
        "release_date": release_date,
        "rank" : 2000,
        "neighbors":"",
        "keywords" : ""
    }