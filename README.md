# social-network-api
A simple REST API based social network in Django.

# Endpoints:

    - user signup:
        /api/sign-up/
        method POST

    - user login:
        /api/login/
        method POST

    - users:
        /api/users/
            method GET

    - posts:
        /api/posts/
            methods (GET, POST, PATCH)

        /api/posts/{id}/like/
        method GET

        /api/posts/{id}/unlike/
        method GET

# Third party Apps:

    - emailhunter - verify email existence on sign-up
    - clearbit/enrichment - get additional data on user sign-up
    - JWT - user authentication
