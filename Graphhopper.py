
import requests
from getpass import getpass

GEOCODE_URL = "https://graphhopper.com/api/1/geocode"
ROUTE_URL = "https://graphhopper.com/api/1/route"


def geocodificar(lugar, clave):
    """Obtiene las coordenadas de una ubicación."""

    while not lugar.strip():
        lugar = input("Ingresa una ubicación válida: ")

    parametros = {
        "q": lugar,
        "limit": 1,
        "locale": "es",
        "key": clave
    }

    try:
        respuesta = requests.get(
            GEOCODE_URL,
            params=parametros,
            timeout=20
        )

        if respuesta.status_code != 200:
            print("Error de geocodificación:",
                  respuesta.status_code)
            print(respuesta.text)
            return None

        datos = respuesta.json()
        resultados = datos.get("hits", [])

        if not resultados:
            print("No se encontró la ubicación:", lugar)
            return None

        resultado = resultados[0]
        punto = resultado["point"]

        nombre = resultado.get("name", lugar)
        estado = resultado.get("state", "")
        pais = resultado.get("country", "")

        partes = [nombre]

        if estado and estado.lower() != nombre.lower():
            partes.append(estado)

        if pais and pais.lower() not in [
            parte.lower() for parte in partes
        ]:
            partes.append(pais)

        nombre_completo = ", ".join(partes)

        return {
            "lat": punto["lat"],
            "lng": punto["lng"],
            "nombre": nombre_completo
        }

    except requests.RequestException as error:
        print("Error de conexión al buscar la ubicación:", error)
        return None
    except (ValueError, KeyError, IndexError) as error:
        print("No se pudo interpretar la respuesta:", error)
        return None


def mostrar_ruta(origen, destino, transporte, clave):
    """Consulta la ruta y muestra sus instrucciones."""

    parametros = {
        "key": clave,
        "vehicle": transporte,
        "locale": "es",
        "instructions": "true",
        "point": [
            f"{origen['lat']},{origen['lng']}",
            f"{destino['lat']},{destino['lng']}"
        ]
    }

    try:
        respuesta = requests.get(
            ROUTE_URL,
            params=parametros,
            timeout=30
        )

        print("\nEstado de la API de rutas:",
              respuesta.status_code)

        if respuesta.status_code != 200:
            print("No se pudo calcular la ruta.")
            print(respuesta.text)
            return

        datos = respuesta.json()
        rutas = datos.get("paths", [])

        if not rutas:
            print("La API no devolvió rutas.")
            return

        ruta = rutas[0]
        distancia_km = ruta["distance"] / 1000
        distancia_millas = distancia_km / 1.609344
        duracion_segundos = int(ruta["time"] / 1000)

        horas = duracion_segundos // 3600
        minutos = (duracion_segundos % 3600) // 60
        segundos = duracion_segundos % 60

        print("\n" + "=" * 50)
        print("RESUMEN DEL VIAJE")
        print("=" * 50)
        print("Origen:", origen["nombre"])
        print("Destino:", destino["nombre"])
        print("Transporte:", transporte)
        print(f"Distancia: {distancia_km:.2f} km")
        print(f"Distancia: {distancia_millas:.2f} millas")
        print(
            f"Duración estimada: {horas:02d}:"
            f"{minutos:02d}:{segundos:02d}"
        )

        print("\nINSTRUCCIONES DEL RECORRIDO")
        print("-" * 50)

        instrucciones = ruta.get("instructions", [])

        if not instrucciones:
            print("La API no devolvió instrucciones detalladas.")
            return

        for numero, instruccion in enumerate(
            instrucciones, start=1
        ):
            texto = instruccion.get(
                "text", "Continuar por la ruta"
            )
            distancia = instruccion.get("distance", 0) / 1000

            print(
                f"{numero}. {texto} "
                f"({distancia:.2f} km)"
            )

        print("=" * 50)

    except requests.RequestException as error:
        print("Error al consultar la ruta:", error)
    except (ValueError, KeyError, IndexError) as error:
        print("Error al procesar los datos de la ruta:", error)


def main():
    print("=" * 50)
    print("SISTEMA DE GEOPOSICIONAMIENTO GRAPHHOPPER")
    print("=" * 50)

    clave = getpass("Ingresa tu clave API de GraphHopper: ").strip()

    if not clave:
        print("No ingresaste una clave API.")
        return

    perfiles = {
        "car": "Automóvil",
        "bike": "Bicicleta",
        "foot": "A pie"
    }

    while True:
        print("\nPerfiles de transporte disponibles:")
        print("car  - Automóvil")
        print("bike - Bicicleta")
        print("foot - A pie")
        print("Escribe 's' o 'salir' para terminar.")

        transporte = input(
            "\nSelecciona el medio de transporte: "
        ).strip().lower()

        if transporte in ("s", "salir"):
            print("Programa finalizado. ¡Hasta pronto!")
            break

        if transporte not in perfiles:
            print("Opción no válida. Selecciona car, bike o foot.")
            continue

        origen_texto = input(
            "Ingresa la ubicación de origen: "
        ).strip()

        if origen_texto.lower() in ("s", "salir"):
            print("Programa finalizado.")
            break

        destino_texto = input(
            "Ingresa la ubicación de destino: "
        ).strip()

        if destino_texto.lower() in ("s", "salir"):
            print("Programa finalizado.")
            break

        print("\nBuscando el origen...")
        origen = geocodificar(origen_texto, clave)

        if origen is None:
            print("No fue posible localizar el origen.")
            continue

        print("Origen encontrado:", origen["nombre"])
        print("\nBuscando el destino...")
        destino = geocodificar(destino_texto, clave)

        if destino is None:
            print("No fue posible localizar el destino.")
            continue

        print("Destino encontrado:", destino["nombre"])

        mostrar_ruta(origen, destino, transporte, clave)


if __name__ == "__main__":
    main()
