# Пример разметки внутри services/qa_orchestrator/features/backend/steps/07_cashbox_prepare_fifo_steps.py

    # Определяем метаданные текущей истории
    STORY_TAG = "07_cashbox_prepare_fifo"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Приёмка первой партии FIFO
            res1 = await client.post(
                "/api/v1/warehouse/receipts", 
                json=receipt_payload_1,
                headers={"X-QA-Story": STORY_TAG, "X-QA-Step": "Генерация первой FIFO-партии товара (100 руб)"} # 🔥 МЕТКА
            )

            await asyncio.sleep(1.1)

            # 2. Приёмка второй партии FIFO
            res2 = await client.post(
                "/api/v1/warehouse/receipts", 
                json=receipt_payload_2,
                headers={"X-QA-Story": STORY_TAG, "X-QA-Step": "Генерация второй FIFO-партии товара (105 руб)"} # 🔥 МЕТКА
            )

            # 3. Открытие кассовой смены
            open_res = await client.post(
                "/api/v1/cash/days/open", 
                json={"date": datetime.now(timezone.utc).isoformat()},
                headers={"X-QA-Story": STORY_TAG, "X-QA-Step": "Регистрация открытия кассового дня"} # 🔥 МЕТКА
            )
