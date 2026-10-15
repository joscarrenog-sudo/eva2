
import random
import string
import requests
from getpass import getpass

# Dirección de la API de la biblioteca
BASE_URL = "http://library.demo.local/api/v1/books"


def generar_isbn():
    """Genera un ISBN-13 con dígito de control."""
    base = "978" + "".join(
        random.choices(string.digits, k=9)
    )

    suma = sum(
        int(digito) * (1 if posicion % 2 == 0 else 3)
        for posicion, digito in enumerate(base)
    )

    control = (10 - suma % 10) % 10
    return base + str(control)


def generar_libro(libro_id):
    """Genera los datos aleatorios de un libro."""

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

    return {
        "id": libro_id,
        "title": random.choice(titulos) + " " +
                 str(random.randint(1, 999)),
        "author": random.choice(nombres) + " " +
                  random.choice(apellidos),
        "isbn": generar_isbn()
    }


def consultar_libros(token):
    """Consulta los libros mediante GET."""

    try:
        respuesta = requests.get(
            BASE_URL,
            headers={"X-API-KEY": token},
            timeout=20
        )

        print("Estado HTTP:", respuesta.status_code)

        if respuesta.status_code != 200:
            print("Detalle del error:", respuesta.text)
            return None

        libros = respuesta.json()

        if not isinstance(libros, list):
            print("La API no devolvió una lista de libros.")
            print(respuesta.text)
            return None

        return libros

    except requests.RequestException as error:
        print("Error de conexión:", error)
        return None

    except ValueError as error:
        print("Error al interpretar la respuesta JSON:", error)
        return None


def main():
    print("=== GENERADOR DE 50 LIBROS ===")

    token = getpass("Ingresa tu token X-API-KEY: ").strip()

    if not token:
        print("Debes ingresar el token.")
        return

    # Consultar los libros existentes antes de crear registros.
    libros_existentes = consultar_libros(token)

    if libros_existentes is None:
        print("La consulta inicial falló. No se crearán libros.")
        return

    print("Libros existentes:", len(libros_existentes))

    ids = [
        libro["id"] for libro in libros_existentes
        if isinstance(libro.get("id"), int)
    ]

    siguiente_id = max(ids, default=-1) + 1

    headers = {
        "X-API-KEY": token,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    creados = 0

    print("\n=== CREACIÓN DE LIBROS ===")

    for numero in range(50):
        libro = generar_libro(siguiente_id + numero)

        try:
            respuesta = requests.post(
                BASE_URL,
                headers=headers,
                json=libro,
                timeout=20
            )

            if respuesta.status_code in (200, 201):
                creados += 1
                print(
                    f"[OK] {creados}/50 | "
                    f"ID: {libro['id']} | "
                    f"Título: {libro['title']} | "
                    f"Autor: {libro['author']} | "
                    f"ISBN generado: {libro['isbn']}"
                )

            else:
                print(
                    f"[ERROR] HTTP {respuesta.status_code} "
                    f"al crear el libro ID {libro['id']}"
                )
                print("Respuesta:", respuesta.text)

                # Detenerse para evitar más errores consecutivos.
                break

        except requests.RequestException as error:
            print("Error de conexión al crear el libro:", error)
            break

    print(f"\nLibros creados correctamente: {creados} de 50")

    # Mostrar el catálogo final.
    print("\n=== CATÁLOGO FINAL ===")

    catalogo = consultar_libros(token)

    if catalogo is None:
        print("No se pudo recuperar el catálogo final.")
        return

    for libro in sorted(
        catalogo,
        key=lambda elemento: str(elemento.get("author", "")).lower()
    ):
        print(
            f"ID: {libro.get('id')} | "
            f"Título: {libro.get('title')} | "
            f"Autor: {libro.get('author')} | "
            f"ISBN: {libro.get('isbn', 'No informado')}"
        )

    print("\nTotal de libros listados:", len(catalogo))


if __name__ == "__main__":
    main()
