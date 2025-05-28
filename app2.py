# Chave Publica: (n, e)
# Chave Privada: (n, d)
# app1 vai criptografar a mensagem usando a chave publica (n, e) do app2
# app2 vai decifrar a mensagem usando a propria chave privada (n, d)
# app2 vai criptografar a mensagem usando a chave publica (n, e) do app1
# app1 vai decifrar a mensagem usando a propria chave privada (n, d)

from rsa import get_keys

keys = get_keys()

N2 = keys[0]
E2 = keys[1]
D = keys[2]

