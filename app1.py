# Chave Publica: (n, e)
# Chave Privada: (n, d)
# app1 vai criptografar a mensagem usando a chave publica (n, e) do app2
# app2 vai decifrar a mensagem usando a propria chave privada (n, d)
# app2 vai criptografar a mensagem usando a chave publica (n, e) do app1
# app1 vai decifrar a mensagem usando a propria chave privada (n, d)

from rsa import get_keys, encrypt, decrypt
from flask import Flask, request, jsonify
import requests as req
from time import sleep

app = Flask(__name__)

keys = get_keys()

N_app1 = keys[0]
E_app1 = keys[1]
D = keys[2]

URL_APP2 = 'http://localhost:5001'

N_app2 = None
E_app2 = None


@app.route('/share_keys', methods=['POST'])
def share_keys():
    global N_app2, E_app2
    data = request.get_json()
    if not data or 'N' not in data or 'E' not in data:
        return jsonify({"error": "Chaves N e E não fornecidas"}), 400

    N_app2 = data['N']
    E_app2 = data['E']
    print(f"Chaves recebidas da outra aplicação: N={N_app2}, E={E_app2}")
    return jsonify({"message": "Chaves recebidas com sucesso!"}), 200


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Mensagem não fornecida"}), 400

    message_to_send = data['message']

    if not N_app2 or not E_app2:
        return jsonify({"error": "Chaves da outra aplicação não conhecidas. Envie as chaves primeiro."}), 400

    try:
        encrypted_message = encrypt(message_to_send, E_app2, N_app2)
        print(f"Mensagem original: {message_to_send}")
        print(f"Mensagem criptografada para enviar: {encrypted_message}")

        payload = {"encrypted_message": encrypted_message}
        response = req.post(f"{URL_APP2}/receive_message", json=payload)
        response.raise_for_status()

        return jsonify({"message": "Mensagem criptografada enviada com sucesso!", "response_other_app": response.json()}), 200
    except req.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")
        return jsonify({"error": f"Erro ao comunicar com a outra aplicação: {e}"}), 500
    except Exception as e:
        print(f"Erro durante a criptografia ou envio: {e}")
        return jsonify({"error": f"Erro interno: {e}"}), 500
    

@app.route('/receive_message', methods=['POST'])
def receive_message():
    data = request.get_json()
    if not data or 'encrypted_message' not in data:
        return jsonify({"error": "Mensagem criptografada não fornecida"}), 400

    encrypted_message_received = data['encrypted_message']
    print(f"Mensagem criptografada recebida: {encrypted_message_received}")

    try:
        decrypted_message = decrypt(encrypted_message_received, N_app1, D)
        print(f"Mensagem descriptografada: {decrypted_message}")
        return jsonify({"message": "Mensagem recebida e descriptografada com sucesso!", "decrypted_content": decrypted_message}), 200
    except Exception as e:
        print(f"Erro durante a descriptografia: {e}")
        return jsonify({"error": f"Erro ao descriptografar mensagem: {e}"}), 500


def initiate_key_exchange():
    if not URL_APP2:
        print("URL da outra aplicação não configurada. Não foi possível trocar chaves.")
        return

    payload = {"N": N_app1, "E": E_app1}
    try:
        print(f"Enviando minhas chaves N e E para {URL_APP2}/share_keys...")
        response = req.post(f"{URL_APP2}/share_keys", json=payload)
        response.raise_for_status()
        print(f"Resposta da outra aplicação ao compartilhar chaves: {response.json()}")
    except req.exceptions.RequestException as e:
        print(f"Erro ao enviar chaves para a outra aplicação: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


@app.route('/start_key_exchange', methods=['GET'])
def start_key_exchange_endpoint():
    print("Iniciando troca de chaves...")

    try:
        response_data = initiate_key_exchange() # Certifique-se que initiate_key_exchange envia suas chaves e recebe as da outra app
        return jsonify({"status": "Key exchange initiated", "response_from_other_app": response_data}), 200
    except Exception as e:
        return jsonify({"status": "Error during key exchange", "error": str(e)}), 500

if __name__ == '__main__':
    port = 5000

    sleep(5)

    print(f"Minhas chaves: N={N_app1}, E={E_app1}, D={D}")
    print(f"Aplicação rodando na porta {port}")
    print(f"A outra aplicação está em: {URL_APP2}")

    app.run(debug=True, port=port, use_reloader=False)

    initiate_key_exchange()