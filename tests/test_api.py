"""Pruebas de los endpoints de la API."""

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_health_responde_ok():
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_validar_tarjeta_valida():
    respuesta = cliente.post(
        "/validar/tarjeta",
        json={"numero": "4532015112830366"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["valido"] is True


def test_validar_tarjeta_invalida():
    respuesta = cliente.post(
        "/validar/tarjeta",
        json={"numero": "4532015112830367"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["valido"] is False


def test_respuesta_enmascara_el_numero():
    numero = "4532015112830366"
    respuesta = cliente.post("/validar/tarjeta", json={"numero": numero})

    assert numero not in respuesta.text
    assert respuesta.json()["valor"] == "************0366"


def test_validar_iban_valido():
    respuesta = cliente.post(
        "/validar/iban",
        json={"iban": "CR05015202001026284066"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["valido"] is True


def test_peticion_sin_campo_requerido():
    respuesta = cliente.post("/validar/tarjeta", json={})
    assert respuesta.status_code == 422
