
import random
import string
import requests
from getpass import getpass

# API de la biblioteca
BASE_URL = "http://library.demo.local/api/v1/books"
HEADERS = {"Accept": "application/json"}

def generar_isbn():
    """Genera un ISBN-13 con dígito de control válido."""
    primeros = "978" + "".join(
        random.choices(string.digits, k=9)
    )
    suma = sum(
        int(digito) * (1 if i % 2 == 0 else 3)
        for i, digito in enumerate(primeros)
    )
    control = (10 - suma % 10) % 10
    return primeros + str(control)


def generar_libro(libro_id):
    """Genera un libro con datos aleatorios."""
    titulos = [
        "Fundamentos de redes",
        "Python para principiantes",
        "Seguridad informática",
        "Administración de servidores",
        "Introducción a Linux",
        "Bases de datos modernas",
        "Programación avanzada",
        "Inteligencia artificial",
        "Ciberseguridad práctica",
        "Desarrollo de aplicaciones"
    ]

    nombres = [
        "Ana", "Carlos", "María", "Javier", "Camila",
        "Diego", "Valentina", "Andrés", "Sofía", "Felipe"
    ]

    apellidos = [
        "González", "Muñoz", "Rojas", "Díaz", "Pérez",
        "Soto", "Contreras", "Silva", "Martínez", "López"
    ]

    titulo = random.choice(titulos) + " " + str(
        random.randint(1, 999)
    )
    autor = random.choice(nombres) + " " + random.choice(apellidos)

    return {
        "id": libro_id,
        "title": titulo,
        "author": autor,
        "isbn": generar_isbn()
    }


def main():
    print("=== GENERADOR DE 50 LIBROS ===")
    token = getpass("Ingresa tu token X-API-KEY: ").strip()

    if not token:
        print("Error: debes ingresar el token.")
        return

    headers = {
        **HEADERS,
        "X-API-KEY": token,
        "Content-Type": "application/json"
    }

    # Consultar los libros actuales para evitar reutilizar IDs
    try:
        respuesta = requests.get(
            BASE_URL,
            params={"includeISBN": "true"},
            headers=headers,
            timeout=20
        )
        respuesta.raise_for_status()
        libros = respuesta.json()

        if not isinstance(libros, list):
            print("La API no devolvió una lista de libros.")
            return

        ids = [
            libro["id"] for libro in libros
            if isinstance(libro.get("id"), int)
        ]
        siguiente_id = max(ids, default=-1) + 1

    except requests.RequestException as error:
        print(f"No se pudo consultar la API: {error}")
        return

    creados = 0

    for numero in range(50):
        libro = generar_libro(siguiente_id + numero)

        try:
            respuesta = requests.post(
                BASE_URL,
                json=libro,
                headers=headers,
                timeout=20
            )

            if respuesta.status_code in (200, 201):
                creados += 1
                print(
                    f"[OK] {creados}/50: "
                    f"{libro['title']} - {libro['author']} "
                    f"- ISBN {libro['isbn']}"
                )
            else:
                print(
                    f"[ERROR] ID {libro['id']}: "
                    f"HTTP {respuesta.status_code} - "
                    f"{respuesta.text}"
                )

        except requests.RequestException as error:
            print(f"Error al enviar el libro {libro['id']}: {error}")

    print(f"\nLibros creados correctamente: {creados} de 50")

    # Listar el catálogo completo, incluyendo ISBN
    print("\n=== CATÁLOGO COMPLETO DE LIBROS ===")

    try:
        respuesta = requests.get(
            BASE_URL,
            params={
                "includeISBN": "true",
                "sortBy": "author"
            },
            headers=headers,
            timeout=20
        )
        respuesta.raise_for_status()

        catalogo = respuesta.json()

        if isinstance(catalogo, list):
            for libro in catalogo:
                print(
                    f"ID: {libro.get('id')} | "
                    f"Título: {libro.get('title')} | "
                    f"Autor: {libro.get('author')} | "
                    f"ISBN: {libro.get('isbn', 'No informado')}"
                )

            print(f"\nTotal de libros listados: {len(catalogo)}")
        else:
            print("La respuesta no contiene una lista de libros.")

    except requests.RequestException as error:
        print(f"No se pudo listar el catálogo: {error}")


if __name__ == "__main__":
    main()
