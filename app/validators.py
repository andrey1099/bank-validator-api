"""Validadores de datos bancarios."""


def validar_luhn(numero: str) -> bool:
    """
    Valida un numero de tarjeta usando el algoritmo de Luhn.

    El algoritmo recorre los digitos de derecha a izquierda,
    duplica uno de cada dos, y si el resultado pasa de 9 le resta 9.
    La suma total debe ser divisible entre 10.
    """
    numero = numero.replace(" ", "").replace("-", "")

    if not numero.isdigit():
        return False

    if len(numero) < 13 or len(numero) > 19:
        return False

    # Un numero de digitos repetidos pasa Luhn pero nunca es
    # una tarjeta real. Se rechaza como regla de negocio.
    if len(set(numero)) == 1:
        return False

    suma = 0
    duplicar = False

    for digito in reversed(numero):
        valor = int(digito)

        if duplicar:
            valor = valor * 2
            if valor > 9:
                valor = valor - 9

        suma += valor
        duplicar = not duplicar

    return suma % 10 == 0


def validar_iban_cr(iban: str) -> bool:
    """
    Valida el formato de un IBAN de Costa Rica.

    Un IBAN costarricense tiene 22 caracteres: CR seguido de
    dos digitos de control y 18 digitos de cuenta.
    """
    iban = iban.replace(" ", "").upper()

    if len(iban) != 22:
        return False

    if not iban.startswith("CR"):
        return False

    if not iban[2:].isdigit():
        return False

    return _validar_digitos_control(iban)


def _validar_digitos_control(iban: str) -> bool:
    """
    Verifica los digitos de control segun el estandar ISO 13616.

    Se mueven los primeros cuatro caracteres al final, se convierten
    las letras a numeros (A=10, B=11, ...) y el resultado debe dar
    resto 1 al dividirlo entre 97.
    """
    reordenado = iban[4:] + iban[:4]

    convertido = ""
    for caracter in reordenado:
        if caracter.isdigit():
            convertido += caracter
        else:
            convertido += str(ord(caracter) - ord("A") + 10)

    return int(convertido) % 97 == 1


def enmascarar(numero: str) -> str:
    """Oculta un numero dejando visibles solo los ultimos cuatro digitos."""
    limpio = numero.replace(" ", "").replace("-", "")

    if len(limpio) <= 4:
        return "*" * len(limpio)

    return "*" * (len(limpio) - 4) + limpio[-4:]
