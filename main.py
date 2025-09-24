import os
import requests
from dotenv import load_dotenv

# 1. КОНФИГУРАЦИЯ
# ------------------------------------------------------------------------------
# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем секретный токен из переменных окружения
SECRET_TOKEN = os.getenv("FINAM_SECRET_TOKEN")
# Базовый URL для API. Для боевого счета используется этот же URL.
BASE_URL = "https://api.finam.ru"

# Проверяем, что токен существует, иначе прерываем выполнение
if not SECRET_TOKEN:
    raise ValueError("Не найден FINAM_SECRET_TOKEN. Убедитесь, что он есть в .env файле.")


# 2. ФУНКЦИИ ДЛЯ РАБОТЫ С API
# ------------------------------------------------------------------------------

def get_jwt_token() -> str | None:
    """
    Получает временный JWT-токен, обменивая постоянный секретный токен.
    """
    print("Шаг 1: Запрос на получение JWT токена...")
    url = f"{BASE_URL}/v1/sessions"
    payload = {"secret": SECRET_TOKEN}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Проверяем на HTTP ошибки (4xx, 5xx)

        jwt_token = response.json()['token']
        print("   ✅ JWT токен успешно получен!")
        return jwt_token
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка при запросе JWT токена: {e}")
        if e.response is not None:
            print(f"      Статус код: {e.response.status_code}")
            print(f"      Тело ответа: {e.response.text}")
        return None


def get_accounts(jwt_token: str) -> str | None:
    """
    Получает список торговых счетов и возвращает ID первого счета (clientId).
    """
    print("\nШаг 2: Запрос списка торговых счетов...")
    url = f"{BASE_URL}/v1/accounts"
    headers = {'Authorization': f'Bearer {jwt_token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        accounts_data = response.json()
        print(f"   ✅ Счета успешно получены: {accounts_data}")

        if accounts_data and len(accounts_data['accounts']) > 0:
            client_id = accounts_data['accounts'][0]['id']
            print(f"   ✅ Найден clientId: {client_id}")
            return client_id
        else:
            print("   ❌ В ответе не найдено доступных счетов.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка при запросе счетов: {e}")
        if e.response is not None:
            print(f"      Тело ответа: {e.response.text}")
        return None


def place_market_order(jwt_token: str, client_id: str, ticker: str, board: str, quantity: int, direction: str):
    """
    Выставляет рыночный ордер на покупку или продажу.
    :param direction: 'Buy' или 'Sell'
    """
    print(f"\nШаг 3: Попытка выставить ордер: {direction} {quantity} шт. {ticker}@{board}...")
    url = f"{BASE_URL}/v1/orders"
    headers = {'Authorization': f'Bearer {jwt_token}'}

    payload = {
        "clientId": client_id,
        "securityBoard": board,
        "securityCode": ticker,
        "buySell": direction,
        "quantity": quantity,
        # "price" не указываем для рыночной заявки (market order)
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        order_response = response.json()
        transaction_id = order_response.get('transactionId')
        print(f"   ✅ Ордер успешно выставлен! ID транзакции: {transaction_id}")
        return order_response

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка при выставлении ордера: {e}")
        if e.response is not None:
            print(f"      Статус код: {e.response.status_code}")
            print(f"      Тело ответа: {e.response.text}")
        return None



if __name__ == "__main__":
    print("--- Запуск скрипта для взаимодействия с Finam Trade API ---")

    # Шаг 1: Получаем JWT
    my_jwt = get_jwt_token()

    if my_jwt:
        # --- ВРЕМЕННОЕ ИЗМЕНЕНИЕ ДЛЯ ТЕСТИРОВАНИЯ ---
        # Мы "вручную" задаем ваш clientId, чтобы обойти неработающий эндпоинт /accounts

        # my_client_id = get_accounts(my_jwt) # <-- ВРЕМЕННО КОММЕНТИРУЕМ ЭТУ СТРОКУ
        my_client_id = "226874"  # <-- ВСТАВЛЯЕМ ВАШ ID НАПРЯМУЮ
        print(f"\n--- Используется clientId: {my_client_id} (вписан вручную для теста) ---")

        # -----------------------------------------------

        if my_client_id:
            print("\n--- Все данные для торговли получены, можно выставлять ордер ---")

            # Шаг 3: Выставляем тестовый ордер
            place_market_order(
                jwt_token=my_jwt,
                client_id=my_client_id,  # Теперь здесь всегда будет "226874"
                ticker="SBER",
                board="TQBR",
                quantity=1,
                direction="Buy"
            )
        else:
            # Эта часть кода теперь не должна выполниться
            print("\n--- Не удалось получить clientId, дальнейшие операции невозможны ---")
    else:
        print("\n--- Не удалось получить JWT-токен, выполнение скрипта прервано ---")