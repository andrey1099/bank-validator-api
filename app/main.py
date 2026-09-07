"""API REST de validacion de datos bancarios."""

from fastapi import FastAPI
from pydantic import BaseModel

from app.validators import validar_luhn, validar_iban_cr, enmascarar

app = FastAPI(
    title="Bank Validator API",
    description="Servicio de validacion de datos bancarios",
    version="1.0.0",
)


class SolicitudTarjeta(BaseModel):
    numero: str


class SolicitudIban(BaseModel):
    iban: str


class Respuesta(BaseModel):
    valido: bool
    valor: str
    mensaje: str


@app.get("/health")
def health():
    """Endpoint de salud para monitoreo."""
    return {"estado": "ok"}


@app.post("/validar/tarjeta", response_model=Respuesta)
def validar_tarjeta(solicitud: SolicitudTarjeta):
    """Valida un numero de tarjeta con el algoritmo de Luhn."""
    es_valido = validar_luhn(solicitud.numero)

    return Respuesta(
        valido=es_valido,
        valor=enmascarar(solicitud.numero),
        mensaje="Numero valido" if es_valido else "Numero invalido",
    )


@app.post("/validar/iban", response_model=Respuesta)
def validar_iban(solicitud: SolicitudIban):
    """Valida el formato de un IBAN de Costa Rica."""
    es_valido = validar_iban_cr(solicitud.iban)

    return Respuesta(
        valido=es_valido,
        valor=enmascarar(solicitud.iban),
        mensaje="IBAN valido" if es_valido else "IBAN invalido",
    )
