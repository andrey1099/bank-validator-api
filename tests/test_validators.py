"""Pruebas de los validadores."""

import pytest

from app.validators import validar_luhn, validar_iban_cr, enmascarar


class TestLuhn:
    """Pruebas del algoritmo de Luhn."""

    @pytest.mark.parametrize(
        "numero",
        [
            "4532015112830366",
            "4539578763621486",
            "5425233430109903",
            "4532 0151 1283 0366",
            "4532-0151-1283-0366",
        ],
    )
    def test_numeros_validos(self, numero):
        assert validar_luhn(numero) is True

    @pytest.mark.parametrize(
        "numero",
        [
            "4532015112830367",
            "1234567812345678",
            "0000000000000000",
        ],
    )
    def test_numeros_invalidos(self, numero):
        assert validar_luhn(numero) is False

    @pytest.mark.parametrize(
        "entrada",
        [
            "",
            "abcd",
            "4532abc112830366",
            "453201511283",
            "45320151128303661234",
        ],
    )
    def test_entradas_mal_formadas(self, entrada):
        assert validar_luhn(entrada) is False

    def test_rechaza_digitos_repetidos(self):
        """Pasan Luhn matematicamente pero no son tarjetas reales."""
        assert validar_luhn("0000000000000000") is False
        assert validar_luhn("1111111111111111") is False


class TestIban:
    """Pruebas del validador de IBAN de Costa Rica."""

    def test_iban_valido(self):
        assert validar_iban_cr("CR05015202001026284066") is True

    def test_iban_con_espacios(self):
        assert validar_iban_cr("CR05 0152 0200 1026 2840 66") is True

    def test_iban_largo_incorrecto(self):
        assert validar_iban_cr("CR0501520200102628") is False

    def test_iban_de_otro_pais(self):
        assert validar_iban_cr("DE89370400440532013000") is False

    def test_iban_con_letras_en_el_numero(self):
        assert validar_iban_cr("CR05015202001026284ABC") is False

    def test_digitos_de_control_incorrectos(self):
        assert validar_iban_cr("CR99015202001026284066") is False


class TestEnmascarar:
    """Pruebas del enmascarado de datos sensibles."""

    def test_deja_visibles_ultimos_cuatro(self):
        assert enmascarar("4532015112830366") == "************0366"

    def test_limpia_espacios(self):
        assert enmascarar("4532 0151 1283 0366") == "************0366"

    def test_numero_muy_corto(self):
        assert enmascarar("123") == "***"

    def test_no_expone_el_numero_original(self):
        original = "4532015112830366"
        resultado = enmascarar(original)
        assert original not in resultado
