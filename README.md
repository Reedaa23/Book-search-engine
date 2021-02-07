# Gutenberg clone project

## To run the full stack (frontend, backend and elasticsearch)

    -   In docker-compose.yml file replace ES_HOST and API_HOST variables with your host ip address (192.168.1.4 is given as example)
    -   Run ' docker-compose up '
    Ebooks database is empty, to fill it by giving ebook ids interval (62350< id <64150):
    -   Fill with ebooks: ' docker exec book-search-engine_api_1 python manage.py init_ebooks 62350 62400 '
    -   Fill with keywords, ranks and jaccard neighbors: ' docker exec book-search-engine_api_1 python manage.py fill_matrix 62350 62400 '
    -   Fill with autocomplete field: ' docker exec book-search-engine_api_1 python manage.py fill_completion 62350 62400 '
    -   Enjoy on: http://localhost:3000