from fastapi import FastAPI

from python_rest_template.api import router

description = """
This is a template for building containerized REST APIs in python with FastAPI
"""

app = FastAPI(
    title="Python REST API Template",
    description=description,
    version="0.0.1",
    # terms_of_service="http://example.com/terms/",
    contact={
        "name": "Jakob Kolb",
        # "url": "http://x-force.example.com/contact/",
        "email": "jakob.j.kolb@gmail.com",
    },
)

app.include_router(router)
